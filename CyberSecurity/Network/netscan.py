#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import concurrent.futures as cf
import csv
import ipaddress
import json
import platform
import socket
import subprocess
import sys
import time
from typing import Dict, List, Optional, Tuple

# -- Varsayılan "yaygın" port seti (riske duyarlı servisler dahil) --
COMMON_PORTS = [
    21,   # FTP
    22,   # SSH
    23,   # Telnet
    25,   # SMTP
    53,   # DNS
    80,   # HTTP
    110,  # POP3
    139,  # NetBIOS
    143,  # IMAP
    389,  # LDAP
    443,  # HTTPS
    445,  # SMB
    465,  # SMTPS
    587,  # SMTP Submission
    631,  # IPP/Print
    8080, # HTTP alt
    8443, # HTTPS alt
    1433, # MS SQL
    1521, # Oracle
    2049, # NFS
    2375, # Docker (TLS'siz risk!)
    3000, # Dev web
    3306, # MySQL
    3389, # RDP
    5000, # Flask/dev
    5432, # PostgreSQL
    5601, # Kibana
    5900, # VNC
    6379, # Redis
    8000, # Dev web
    9000, # Portainer/Sonarr vb.
    9200, # Elasticsearch
    11211,# Memcached
    27017 # MongoDB
]

# -- Portlara özel basit "probe" davranışı (banner/cevap alma) --
def probe_payload_for(port: int, host: str) -> Optional[bytes]:
    if port in (80, 8080, 8000, 3000):
        return f"HEAD / HTTP/1.0\r\nHost: {host}\r\n\r\n".encode()
    if port in (443, 8443):
        # TLS el sıkışması yapmıyoruz (yalın banner almak riskli),
        # sadece boş bırakıp pasif banner deneyeceğiz.
        return None
    if port == 22:  # SSH
        return None  # genelde bağlanınca banner verir
    if port == 21:  # FTP
        return b"FEAT\r\n"
    if port == 25 or port == 587 or port == 465:  # SMTP family
        return b"EHLO scanner.local\r\n"
    if port == 6379:  # Redis
        return b"PING\r\n"
    if port == 27017: # MongoDB (karmaşık el sıkışması var; pas geç)
        return None
    if port == 11211: # Memcached
        return b"version\r\n"
    return None

def parse_ports(ports_arg: str) -> List[int]:
    if ports_arg.lower() == "common":
        return COMMON_PORTS
    ports: List[int] = []
    for part in ports_arg.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            a, b = part.split("-", 1)
            ports.extend(range(int(a), int(b) + 1))
        else:
            ports.append(int(part))
    # unique + sort
    return sorted(set(ports))

def is_alive_by_ping(host: str, timeout: float = 1.0) -> bool:
    # Not: Ping bazı ağlarda engelli olabilir; başarısızlık "kapalı" anlamına gelmez.
    count_flag = "-n" if platform.system().lower().startswith("win") else "-c"
    timeout_flag = "-w" if platform.system().lower().startswith("win") else "-W"
    try:
        completed = subprocess.run(
            ["ping", count_flag, "1", timeout_flag, str(int(timeout)), host],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False
        )
        return completed.returncode == 0
    except Exception:
        return False

def try_connect(host: str, port: int, timeout: float = 0.8) -> Tuple[bool, Optional[str]]:
    """
    Port açık mı? + basit banner/probe.
    Döner: (open_bool, excerpt/banner_str or None)
    """
    try:
        with socket.create_connection((host, port), timeout=timeout) as s:
            s.settimeout(timeout)
            payload = probe_payload_for(port, host)
            banner = b""
            try:
                if payload:
                    s.sendall(payload)
                # Her durumda küçük bir recv denemesi (ör. SSH/FTP banner)
                try:
                    chunk = s.recv(512)
                    banner += chunk
                except socket.timeout:
                    pass
            except Exception:
                pass

            excerpt = banner.decode(errors="ignore").strip()
            if excerpt:
                excerpt = " ".join(excerpt.split())
            return True, excerpt if excerpt else None
    except Exception:
        return False, None

def risk_hints(host: str, port: int, banner: Optional[str]) -> List[str]:
    hints = []
    # Basit ve zararsız heuristikler
    if port == 445:
        hints.append("SMB (445) açık → yerel ağda paylaşımlar/NTLM sızıntısı riski.")
    if port == 3389:
        hints.append("RDP (3389) açık → yetkisiz erişim/deneme saldırılarına açık olabilir.")
    if port in (80, 8080, 8000, 3000) and port not in (443, 8443):
        hints.append("HTTP açık (TLS yok) → yönetim panelleri/servisler şifrelenmemiş olabilir.")
    if port == 22 and banner and "OpenSSH" in banner:
        hints.append("SSH banner görüldü → versiyon sızıntısı; güncelliği kontrol edin.")
    if port == 6379 and banner and "PONG" in banner:
        hints.append("Redis authsuz PONG verdi → AUTH zorunlu değil; yüksek risk.")
    if port == 11211 and banner and "VERSION" in banner.upper():
        hints.append("Memcached banner → public erişim varsa veri sızıntısı riski.")
    if port == 9200 and banner and ("ELASTIC" in banner.upper() or "ELASTIC" in (banner or "").upper()):
        hints.append("Elasticsearch muhtemel → auth yoksa indeksler açıktır.")
    if port == 21 and banner:
        hints.append("FTP banner → TLS yoksa şifreler düz metin gidebilir.")
    return hints

def scan_host(host: str, ports: List[int], do_ping: bool, timeout: float) -> List[Dict]:
    results = []
    if do_ping:
        alive = is_alive_by_ping(host)
        if not alive:
            # Ping'e yanıt vermeyebilir; yine de TCP dene (light footprint için kısa bir deneme)
            pass
    for port in ports:
        open_, banner = try_connect(host, port, timeout=timeout)
        if open_:
            hints = risk_hints(host, port, banner)
            results.append({
                "host": host,
                "port": port,
                "service_hint": banner or "",
                "risk_hints": hints
            })
    return results

def write_reports(rows: List[Dict], out_prefix: str):
    # CSV
    csv_path = f"{out_prefix}_report.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["host", "port", "service_hint", "risk_hints"])
        for r in rows:
            writer.writerow([r["host"], r["port"], r["service_hint"], " | ".join(r["risk_hints"])])
    # JSON
    json_path = f"{out_prefix}_report.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)
    return csv_path, json_path

def main():
    parser = argparse.ArgumentParser(
        description="Yerel/izinli ağlarda hafif güvenlik taraması (TCP port + banner/probe)."
    )
    parser.add_argument("--net", required=True, help="CIDR (örn: 192.168.1.0/24)")
    parser.add_argument("--ports", default="common",
                        help='Tarama portları: "common" veya "22,80,443" veya "1-1024"')
    parser.add_argument("--workers", type=int, default=500, help="Eşzamanlı işçi sayısı (default: 500)")
    parser.add_argument("--timeout", type=float, default=0.8, help="Socket timeout sn (default: 0.8)")
    parser.add_argument("--ping", action="store_true", help="Öncesinde ping dene (isteğe bağlı).")
    parser.add_argument("--out-prefix", default="netscan", help="Çıktı dosyası öneki (default: netscan)")
    args = parser.parse_args()

    try:
        net = ipaddress.ip_network(args.net, strict=False)
    except Exception as e:
        print(f"[HATA] Geçersiz ağ: {e}", file=sys.stderr)
        sys.exit(1)

    ports = parse_ports(args.ports)
    hosts = [str(h) for h in net.hosts()]
    print(f"[+] Ağ: {net}  | Hedef IP sayısı: {len(hosts)}  | Port sayısı: {len(ports)}")
    print(f"[+] Başlıyor... (workers={args.workers}, timeout={args.timeout}s)")
    t0 = time.time()

    rows: List[Dict] = []
    # Host başına tarama işini paralelleştir
    with cf.ThreadPoolExecutor(max_workers=args.workers) as ex:
        futures = []
        for host in hosts:
            futures.append(ex.submit(scan_host, host, ports, args.ping, args.timeout))
        for fut in cf.as_completed(futures):
            try:
                rows.extend(fut.result())
            except Exception as e:
                # tekil host hataları taramayı durdurmasın
                print(f"[uyarı] bir iş hata verdi: {e}", file=sys.stderr)

    elapsed = time.time() - t0
    print(f"[+] Tamamlandı: {len(rows)} açık servis kaydı bulundu | Süre: {elapsed:.1f}s")

    # Basit tablo görünümü
    if rows:
        print("\nHost              Port   Service/Excerpt                     Risk Hints")
        print("-"*90)
        for r in sorted(rows, key=lambda x: (x["host"], x["port"])):
            hints = " | ".join(r["risk_hints"])
            excerpt = (r["service_hint"][:40] + "...") if len(r["service_hint"]) > 43 else r["service_hint"]
            print(f"{r['host']:<17} {r['port']:<6} {excerpt:<35} {hints}")

    csv_path, json_path = write_reports(rows, args.out_prefix)
    print(f"\n[+] Raporlar yazıldı: {csv_path}  |  {json_path}")
    print("[!] Not: Bu araç yalnızca izinli/kurumsal iç ağlarda kullanılmalıdır.")

if __name__ == "__main__":
    main()
