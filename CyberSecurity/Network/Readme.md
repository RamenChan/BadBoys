netscan — Hafif ağ güvenlik tarayıcı (README.md)

Kısa: Bu repo yerel veya izinli kurumsal ağlarda hızlı, düşük ayak iziyle TCP port taraması + hafif banner/probe yapar; yaygın servisleri tespit edip basit risk ipuçları üretir. Aktif sömürü (exploit) içermez — sadece keşif/öncesi bilgi sağlar.

Önemli — Yasal uyarı: Bu aracı sadece sahibi/işletmecisi olduğunuz veya açıkça izin aldığınız ağlarda kullanın. İzinsiz kullanım yasa dışıdır ve cezai sorumluluk doğurur.

İçerik

netscan.py — ana tarayıcı script'i

README.md — bu dosya

Çalıştırınca oluşan raporlar: _\_report.csv, _\_report.json

Özellikler

CIDR ile ağ hedefleme (ör. 192.168.1.0/24)

Eşzamanlı, thread-pool tabanlı port tarama

Yaygın servisler için hafif probe/banner alma (HTTP, FTP, SMTP, Redis, Memcached vb.)

Basit risk-hint üretme (ör. Redis auth yok, SMB açık, RDP açık)

CSV ve JSON çıktısı

CLI ile konfigüre edilebilir: port listesi, worker sayısı, timeout, ping seçeneği

Gereksinimler

Python 3.8+ (öneri: 3.10+)

Sadece Python standart kütüphaneleri (extra paket gerektirmez)

(Opsiyonel) Büyük ağlarda ulimit ve işletim sistemi thread/FD sınırlarını kontrol edin

Kurulum

Repo'yu klonla veya netscan.py dosyasını al:

git clone <repo-url>
cd netscan

# veya sadece netscan.py'yi kopyala

(Opsiyonel) İzole bir virtualenv oluştur:

python3 -m venv .venv
source .venv/bin/activate

Not: Script yalnızca Python stdlib ile çalışır; ekstra paket gerekmez.

Hızlı Kullanım

Genel format:

python3 netscan.py --net <CIDR> [--ports <ports>] [--workers N] [--timeout S] [--ping] [--out-prefix PREFIX]

Örnekler:

# 1) Ev/ofis ağı - yaygın portlar

python3 netscan.py --net 192.168.1.0/24 --ports common --out-prefix ev_tarama

# 2) Özel port listesi

python3 netscan.py --net 10.0.0.0/24 --ports 22,80,443,445,3389,6379 --workers 500

# 3) Port aralığı

python3 netscan.py --net 172.16.0.0/24 --ports 1-1024 --workers 300 --timeout 0.6 --out-prefix fullscan

# 4) Ping kontrolü aktif (daha yavaş olabilir)

python3 netscan.py --net 192.168.10.0/24 --ping

CLI seçenekleri (özet)

--net (zorunlu): hedef ağ, CIDR formatı (ör. 192.168.1.0/24)

--ports: "common" veya 22,80,443 veya 1-1024

--workers: eşzamanlı işçi sayısı (default 500)

--timeout: socket timeout (sn), default 0.8

--ping: her host için ön ping (opsiyonel)

--out-prefix: çıktı isimlendirme öneki (default netscan)

Çıktılar ve Anlamları

CSV — <out_prefix>\_report.csv

Sütunlar: host, port, service_hint, risk_hints

service_hint: alınabilen banner/özet (kısaltılmış)

risk_hints: otomatik heuristiklerle üretilen risk notları (pipe ile ayrılmış)

JSON — <out_prefix>\_report.json

Her kayıt örneği:

{
"host": "192.168.1.5",
"port": 6379,
"service_hint": "PONG",
"risk_hints": [
"Redis authsuz PONG verdi → AUTH zorunlu değil; yüksek risk."
]
}

Kısa örnek CSV satırı:

192.168.1.5,6379,"PONG","Redis authsuz PONG verdi → AUTH zorunlu değil; yüksek risk."

Risk-hint (heuristik) örnekleri ve önerilen aksiyonlar

Redis authsuz PONG verdi

Aksiyon: Redis yapılandırmasını requirepass ile koruyun; portu yalnızca iç ağa açın; firewall ile kısıtlayın.

SMB (445) açık

Aksiyon: Gerekmiyorsa kapatın; paylaşımlarda güçlü izinler uygulayın; SMB signing ve NTLMv2 zorunlu kılın.

RDP (3389) açık

Aksiyon: Gateway/Jump host/VPN kullanın; NLA etkinleştirin; brute-force koruması uygulayın.

HTTP açık (TLS yok)

Aksiyon: TLS/HTTPS zorunlu kılın; yönetim panellerini HTTPS + auth ile koruyun.

Elasticsearch/Kibana (9200/5601) erişimi

Aksiyon: IP allowlist, temel auth veya reverse-proxy + SSO ile koruyun.

Docker API (2375) açık

Aksiyon: 2375'i kapatın veya TLS ile koruyun; yönetici erişimini sınırlandırın.

Her bulgu için Trello/Jira’da: Sorumlu / Öncelik / Son tarih / Öneri bilgileriyle ticket açılması önerilir.

Entegrasyon & Otomasyon Önerileri
Trello / Ticket otomasyonu (manuel CSV import)

CSV’yi Trello/Jira’ya import ederek her satır için kart oluşturabilirsiniz.

Alternatif: küçük bir Python script ile Trello API / Jira API’ye otomatik kart açma yapılır (CSV parse → API call).

Pseudo-örnek Trello kart açma mantığı:

title = f"{host}:{port} - {risk_summary}"
desc = f"banner: {service_hint}\nrisks: {' | '.join(risk_hints)}\nscan: {out_prefix}\_report.json"
POST https://api.trello.com/1/cards?key=...&token=...&idList=...&name=title&desc=desc

Cron ile periyodik tarama

/etc/cron.d/netscan örneği:

0 3 \* \* 1 root /usr/bin/python3 /opt/netscan/netscan.py --net 192.168.1.0/24 --ports common --out-prefix /var/reports/netscan_weekly

GitHub Actions örneği (rapor artifact olarak sakla)
name: Weekly netscan
on:
schedule: - cron: '0 0 \* _ 1' # Pazartesi UTC
jobs:
scan:
runs-on: ubuntu-latest
steps: - uses: actions/checkout@v4 - name: Run netscan
run: python3 netscan.py --net 10.0.0.0/24 --ports common --out-prefix report_weekly - name: Upload report
uses: actions/upload-artifact@v4
with:
name: netscan-report
path: report_weekly_report._

Performans & Tuning

Büyük ağlarda --workers değerini ağ büyüklüğüne ve hedef makine kaynaklarına göre ayarlayın. Çok yüksek değer ulimit/FD sorununa sebep olabilir.

--timeout çok düşükse (0.3–0.8) tarama hızlı olur ama ağ gecikmesi yüksekse false-negative alabilirsiniz.

--ping bazı ağlarda engellenir; ping başarısız olsa da TCP denemesini bırakmayın (script bu davranışı destekler).

Güvenlik / Etik Kurallar (zorunlu)

Yalnızca izin verilen ağlarda tarama yapın.

Tarama kapsamını, zamanlamasını ve amacı ilgili yöneticilere bildirin.

Hassas sonuçları şifreli / korumalı kanallarda paylaşın.

Exploit veya saldırı içerikli eylemler yapmayın — bu araç keşif amaçlıdır.

Hata Giderme (Troubleshooting)

"Geçersiz ağ" hatası
CIDR formatını kontrol edin (192.168.1.0/24). Script strict=False ile toleranslıdır ama girişin doğru olduğundan emin olun.

Hiç sonuç gelmiyor, fakat bildiğiniz servisler açık

Ping engellenmiş olabilir → --ping opsiyonunu kaldırıp yeniden deneyin.

Timeout çok kısa olabilir → --timeout 1.5 deneyin.

Hedef firewall/IPS port probing’i engelliyor olabilir; daha düşük eşzamanlılık (--workers) deneyin.

Too many open files / OSError: [Errno 24]

OS ulimit -n değerini yükseltin veya --workers sayısını azaltın.

Ping için izin/permission denied

Ping bazı platformlarda sudo/root izni gerektirebilir; --ping opsiyonunu kaldırın veya uygun izinle çalıştırın.

Geliştirme & Katkı

Yeni probe’lar eklenebilir (TLS handshake, HTTP header parsing, SMB detaylı banner parsing).

Servise özgü read-only kontroller (Kibana/ES auth check gibi) eklenebilir — fakat exploit içeremez.

PR ve issue’lar için repo’yu kullanın. Contributing rehberi eklenebilir.

Örnek çalışma akışı (tavsiyem — adım adım)

Küçük kapsama: --net 192.168.1.0/28 --ports common ile başla, false positives/negatives değerlendirmesi yap.

Önceliklendirme: CSV’ye göre 1–2 kritik bulgu için hızlı aksiyon belirle (SMB/RDP/DB dış erişimleri).

Trello entegrasyonu: CSV → Trello/Jira ile otomatik ticket aç.

Periyodik tarama: Haftalık tarama + diff ile değişimleri takip et.

Derin tarama: Kritik bulgularda ilgili ekiplerle birlikte daha derin inceleme (passive fingerprinting, konfigürasyon kontrolü).

Lisans

Tercihinize göre: örn. MIT. (Bu README lisans tavsiyesi içerir; kullanım sırasında yasal sorumluluk sizin tarafınızdadır.)
