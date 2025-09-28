#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sysinfo.py
-----------
Cihazın temel donanım/işletim sistemi/network bilgilerini toplar ve
konsola okunabilir tablolar halinde yazdırır.

Özellikler:
- Host / OS / Kernel / Uptime
- CPU: model (varsa), logical/physical count, load average
- Bellek & Swap
- Disk partition usage
- Network interfaces (IP, family, MAC)
- Dinleyen (listening) TCP/UDP portlar (opsiyonel, psutil ile)
- Basit process sayısı özetleri

Gereksinimler:
- Python 3.8+
- (Opsiyonel ama tavsiye) psutil: `pip install psutil`
"""

import argparse
import json
import os
import platform
import socket
import subprocess
import sys
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Tuple


# Try import psutil (recommended). If yoksa, script sınırlı çalışır. 
try:
    import psutil
except Exception:
    psutil = None  # type: ignore

# ----------------------
# Helper pretty printing
# ----------------------
def print_title(title: str):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)

def print_kv_table(items: List[Tuple[str, str]], col1_w: int = 30):
    for k, v in items:
        k_display = (k[:col1_w - 3] + "...") if len(k) > col1_w - 1 else k
        print(f"{k_display:<{col1_w}} : {v}")
    print()

def human_bytes(n: int) -> str:
    # Nicely format bytes
    for unit in ['B', 'KB', 'MB', 'GB', 'TB', 'PB']:
        if abs(n) < 1024.0:
            return f"{n:3.1f} {unit}"
        n /= 1024.0
    return f"{n:.1f} PB"

# ----------------------
# Gather functions
# ----------------------
def gather_basic() -> Dict[str, Any]:
    info = {}
    try:
        uname = platform.uname()
        info["hostname"] = socket.gethostname()
        info["fqdn"] = socket.getfqdn()
        info["system"] = uname.system
        info["node"] = uname.node
        info["release"] = uname.release
        info["version"] = uname.version
        info["machine"] = uname.machine
        info["processor"] = uname.processor or platform.processor()
    except Exception as e:
        info["error"] = f"gather_basic failed: {e}"
    return info

def gather_uptime() -> Dict[str, Any]:
    data = {}
    try:
        if psutil:
            boot = datetime.fromtimestamp(psutil.boot_time())
            data["boot_time"] = boot.isoformat(sep=" ")
            data["uptime"] = str(datetime.now() - boot).split(".")[0]
        else:
            # Fallback: try /proc/uptime on linux
            if os.path.exists("/proc/uptime"):
                with open("/proc/uptime", "r") as f:
                    up_seconds = float(f.readline().split()[0])
                    up_td = timedelta(seconds=int(up_seconds))
                    data["uptime"] = str(up_td)
            else:
                data["uptime"] = "unknown (install psutil for accurate uptime)"
    except Exception as e:
        data["error"] = str(e)
    return data

def gather_cpu() -> Dict[str, Any]:
    info = {}
    try:
        if psutil:
            info["logical_cpus"] = psutil.cpu_count(logical=True)
            info["physical_cpus"] = psutil.cpu_count(logical=False)
            info["cpu_freq"] = f"{psutil.cpu_freq().current:.1f} MHz" if psutil.cpu_freq() else "n/a"
            loads = os.getloadavg() if hasattr(os, "getloadavg") else (0.0, 0.0, 0.0)
            info["load_avg_1m_5m_15m"] = f"{loads[0]:.2f}, {loads[1]:.2f}, {loads[2]:.2f}"
        else:
            info["logical_cpus"] = os.cpu_count()
            info["load_avg"] = "n/a (install psutil for more)"
        # try to detect model on Linux with /proc/cpuinfo or platform
        cpu_model = None
        if platform.system().lower() == "linux":
            try:
                with open("/proc/cpuinfo", "r", encoding="utf-8", errors="ignore") as f:
                    for line in f:
                        if line.lower().startswith("model name"):
                            cpu_model = line.split(":", 1)[1].strip()
                            break
            except Exception:
                cpu_model = None
        if not cpu_model:
            cpu_model = platform.processor() or "unknown"
        info["model"] = cpu_model
    except Exception as e:
        info["error"] = str(e)
    return info

def gather_memory() -> Dict[str, Any]:
    info = {}
    try:
        if psutil:
            vm = psutil.virtual_memory()
            sw = psutil.swap_memory()
            info["total"] = human_bytes(vm.total)
            info["available"] = human_bytes(vm.available)
            info["used"] = human_bytes(vm.used)
            info["percent_used"] = f"{vm.percent}%"
            info["swap_total"] = human_bytes(sw.total)
            info["swap_used"] = human_bytes(sw.used)
            info["swap_percent"] = f"{sw.percent}%"
        else:
            info["mem"] = "psutil missing - install psutil for detailed memory stats"
    except Exception as e:
        info["error"] = str(e)
    return info

def gather_disks() -> List[Dict[str, Any]]:
    parts = []
    try:
        if psutil:
            for p in psutil.disk_partitions(all=False):
                try:
                    usage = psutil.disk_usage(p.mountpoint)
                    parts.append({
                        "device": p.device,
                        "mountpoint": p.mountpoint,
                        "fstype": p.fstype,
                        "total": human_bytes(usage.total),
                        "used": human_bytes(usage.used),
                        "free": human_bytes(usage.free),
                        "percent": f"{usage.percent}%"
                    })
                except PermissionError:
                    parts.append({
                        "device": p.device,
                        "mountpoint": p.mountpoint,
                        "fstype": p.fstype,
                        "error": "permission denied"
                    })
        else:
            parts.append({"disks": "psutil not installed; disk info not available"})
    except Exception as e:
        parts.append({"error": str(e)})
    return parts

def gather_network() -> Dict[str, Any]:
    info = {}
    try:
        if psutil:
            addrs = psutil.net_if_addrs()
            stats = psutil.net_if_stats()
            interfaces = {}
            for ifname, addrlist in addrs.items():
                interfaces[ifname] = {"addresses": [], "isup": stats.get(ifname).isup if stats.get(ifname) else "n/a"}
                for a in addrlist:
                    addr = {}
                    addr["family"] = str(a.family).split(".")[-1]
                    addr["address"] = a.address
                    addr["netmask"] = a.netmask
                    addr["broadcast"] = a.broadcast
                    addr["ptp"] = a.ptp
                    interfaces[ifname]["addresses"].append(addr)
            info["interfaces"] = interfaces
            # DNS servers (platform dependent)
            dns_servers = []
            if platform.system().lower() == "linux":
                try:
                    with open("/etc/resolv.conf") as f:
                        for line in f:
                            if line.startswith("nameserver"):
                                dns_servers.append(line.split()[1].strip())
                except Exception:
                    pass
            info["dns_servers"] = dns_servers
            # default gateway (best-effort)
            try:
                gws = psutil.net_if_stats()  # placeholder; psutil doesn't give gw directly in cross-platform
                # try `ip route` on linux
                if platform.system().lower() == "linux":
                    try:
                        out = subprocess.check_output(["ip", "route"], stderr=subprocess.DEVNULL).decode()
                        for ln in out.splitlines():
                            if ln.startswith("default"):
                                parts = ln.split()
                                if "via" in parts:
                                    gw_idx = parts.index("via") + 1
                                    info["default_gateway"] = parts[gw_idx]
                                    break
                    except Exception:
                        pass
            except Exception:
                pass
        else:
            info["network"] = "psutil not installed; basic network info may be unavailable"
    except Exception as e:
        info["error"] = str(e)
    return info

def gather_listening_ports() -> List[Dict[str, Any]]:
    out = []
    if not psutil:
        return [{"note": "psutil not installed; cannot list listening ports"}]
    try:
        conns = psutil.net_connections(kind='inet')
        for c in conns:
            # status can be LISTEN, ESTABLISHED, etc.
            if c.status == psutil.CONN_LISTEN or (c.laddr and (c.status == 'LISTEN' or c.status == psutil.CONN_LISTEN)):
                laddr = f"{c.laddr.ip}:{c.laddr.port}" if c.laddr else ""
                raddr = f"{c.raddr.ip}:{c.raddr.port}" if c.raddr else ""
                proto = "tcp" if c.type == socket.SOCK_STREAM else "udp"
                pid = c.pid
                pname = None
                try:
                    pname = psutil.Process(pid).name() if pid else None
                except Exception:
                    pname = None
                out.append({
                    "proto": proto,
                    "local_address": laddr,
                    "remote_address": raddr,
                    "pid": pid,
                    "process": pname
                })
    except Exception as e:
        out.append({"error": str(e)})
    return out

def gather_process_summary(top_n: int = 5) -> Dict[str, Any]:
    summary = {}
    if not psutil:
        summary["note"] = "psutil not installed; process summary unavailable"
        return summary
    try:
        procs = []
        for p in psutil.process_iter(attrs=['pid', 'name', 'cpu_percent', 'memory_info']):
            info = p.info
            mem = info.get('memory_info')
            mem_rss = mem.rss if mem else 0
            procs.append((info['pid'], info['name'], info.get('cpu_percent', 0.0), mem_rss))
        # sort by memory desc
        procs.sort(key=lambda x: x[3], reverse=True)
        summary['top_by_memory'] = procs[:top_n]
        procs.sort(key=lambda x: x[2], reverse=True)
        summary['top_by_cpu'] = procs[:top_n]
        summary['total_processes'] = len(procs)
    except Exception as e:
        summary['error'] = str(e)
    return summary

# ----------------------
# Main assemble & print
# ----------------------
def collect_all(include_ports: bool = False) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    out['basic'] = gather_basic()
    out['uptime'] = gather_uptime()
    out['cpu'] = gather_cpu()
    out['memory'] = gather_memory()
    out['disks'] = gather_disks()
    out['network'] = gather_network()
    out['process_summary'] = gather_process_summary()
    if include_ports:
        out['listening_ports'] = gather_listening_ports()
    return out

def pretty_print_all(data: Dict[str, Any], include_ports: bool = False):
    # Basic
    print_title("SYSTEM - BASIC")
    basic = data.get('basic', {})
    kv = [
        ("Hostname", basic.get('hostname', '')),
        ("FQDN", basic.get('fqdn', '')),
        ("OS", f"{basic.get('system','')} {basic.get('release','')} {basic.get('version','')}"),
        ("Machine", basic.get('machine','')),
        ("Processor", basic.get('processor','')),
    ]
    print_kv_table(kv)

    # Uptime
    print_title("UPTIME")
    up = data.get('uptime', {})
    print_kv_table([
        ("Boot time", up.get('boot_time', up.get('uptime', 'unknown'))),
        ("Uptime", up.get('uptime', 'unknown')),
    ])

    # CPU
    print_title("CPU")
    cpu = data.get('cpu', {})
    cpu_kv = [
        ("Model", cpu.get('model','')),
        ("Logical CPUs", str(cpu.get('logical_cpus',''))),
        ("Physical CPUs", str(cpu.get('physical_cpus',''))),
        ("Freq", cpu.get('cpu_freq','')),
        ("Load avg (1,5,15)", cpu.get('load_avg_1m_5m_15m', cpu.get('load_avg','n/a'))),
    ]
    print_kv_table(cpu_kv)

    # Memory
    print_title("MEMORY")
    mem = data.get('memory', {})
    mem_kv = [
        ("Total", mem.get('total', mem.get('mem',''))),
        ("Available", mem.get('available','')),
        ("Used", mem.get('used','')),
        ("Used %", mem.get('percent_used','')),
        ("Swap total", mem.get('swap_total','')),
        ("Swap used", mem.get('swap_used','')),
        ("Swap %", mem.get('swap_percent','')),
    ]
    print_kv_table(mem_kv)

    # Disks
    print_title("DISKS")
    for d in data.get('disks', []):
        if 'error' in d:
            print(f" - {d.get('device','?')}: {d['error']}")
        else:
            print(f" {d['device']:<20} {d['mountpoint']:<20} {d['fstype']:<8} {d['total']:>8} used:{d['percent']:>5}")
    print()

    # Network
    print_title("NETWORK INTERFACES")
    net = data.get('network', {})
    if 'interfaces' in net and isinstance(net['interfaces'], dict):
        for ifname, detail in net['interfaces'].items():
            print(f"- {ifname} (up: {detail.get('isup')})")
            for addr in detail.get('addresses', []):
                fam = addr.get('family')
                addr_str = addr.get('address')
                nm = addr.get('netmask') or ""
                bc = addr.get('broadcast') or ""
                print(f"    {fam:>6} : {addr_str:<22} netmask: {nm:<15} broadcast: {bc}")
    else:
        print(net.get('network','No interface info (psutil missing)'))
    if net.get('dns_servers'):
        print("\nDNS servers: " + ", ".join(net.get('dns_servers')))
    if net.get('default_gateway'):
        print("Default gateway: " + net.get('default_gateway'))
    print()

    # Processes
    print_title("PROCESS SUMMARY")
    ps = data.get('process_summary', {})
    print(f"Total processes (approx): {ps.get('total_processes','n/a')}")
    print("\nTop by memory:")
    for pid, name, cpu_percent, mem_rss in ps.get('top_by_memory', []):
        print(f"  PID {pid:<6} {name[:25]:<25} mem: {human_bytes(mem_rss)} cpu%: {cpu_percent}")
    print("\nTop by CPU:")
    for pid, name, cpu_percent, mem_rss in ps.get('top_by_cpu', []):
        print(f"  PID {pid:<6} {name[:25]:<25} mem: {human_bytes(mem_rss)} cpu%: {cpu_percent}")
    print()

    # Listening ports
    if include_ports:
        print_title("LISTENING PORTS")
        for p in data.get('listening_ports', []):
            if 'error' in p:
                print(f" - Error: {p['error']}")
            elif 'note' in p:
                print(" - " + p['note'])
            else:
                print(f" {p.get('proto', '?'):<4} {p.get('local_address', ''):<22} pid:{str(p.get('pid','')):<6} proc:{p.get('process','')}")
        print()

# ----------------------
# CLI
# ----------------------
def main():
    parser = argparse.ArgumentParser(description="Cihaz bilgilerini toplayıp tablo halinde gösterir.")
    parser.add_argument("--json", "-j", help="Çıktıyı JSON dosyası olarak kaydet (örn out.json)")
    parser.add_argument("--ports", action="store_true", help="Dinleyen portları da listele (psutil gerektirir)")
    args = parser.parse_args()

    if psutil is None:
        print("UYARI: 'psutil' kütüphanesi yüklenmemiş. Daha ayrıntılı bilgiler için:")
        print("  pip install psutil")
        print("Script sınırlı biçimde çalışmaya devam edecektir.\n")

    data = collect_all(include_ports=args.ports)
    pretty_print_all(data, include_ports=args.ports)

    if args.json:
        try:
            with open(args.json, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"\n[+] JSON çıktı kaydedildi: {args.json}")
        except Exception as e:
            print(f"[!] JSON kaydedilemedi: {e}")

if __name__ == "__main__":
    main()
