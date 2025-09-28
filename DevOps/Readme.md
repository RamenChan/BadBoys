## Kullanım için
> pip install psutil
> python3 sysinfo.py --ports --json myhost_info.json

# sysinfo — Cihaz Bilgi Toplayıcı (README.md)

Kısa: sysinfo.py çalıştırıldığı makineden donanım, işletim sistemi, disk, bellek, ağ ve (opsiyonel) dinleyen port bilgilerini toplar ve konsola okunabilir tablolar halinde yazdırır. Ayrıca istersen JSON olarak çıktı verebilir. Öğrenciler için cihaz keşfi / inventory / ön güvenlik kontrolü amaçlı kullanışlı bir araçtır.

Uyarı: Bu script yerel veya izinli sistemlerde çalıştırılmalıdır. Başka makinelerde izinsiz bilgi toplamak etik ve yasal sorunlara yol açar.

İçerik

sysinfo.py — ana script (Python)

Bu README.md — kullanım bilgisi, örnekler, öğrenci görevleri ve genişletme fikirleri

Özellikler

Hostname, FQDN, OS, kernel bilgisi

Sistem açılış zamanı ve uptime

CPU: model, logical/physical CPU sayısı, frekans, load average

Bellek & swap (toplam, kullanılabilir, kullanım yüzdesi)

Disk partition bilgileri (mountpoint, fstype, toplam, kullanım %)

Ağ arayüzleri: IP adresleri, MAC, netmask, broadcast, DNS sunucuları, varsayılan gateway (best-effort)

(Opsiyonel) Dinleyen TCP/UDP bağlantıları ve onları açan process (gerekli: psutil)

Proses özetleri: en çok CPU ve belleği kullanan processler

--json <file> ile JSON çıktısı kaydetme

--ports ile dinleyen portları listeleme (opsiyonel)

Gereksinimler

Python 3.8 veya üstü (öneri: 3.10+)

psutil (opsiyonel ama tavsiye edilir; ayrıntılı donanım/port/process bilgileri için gerekli)

Yüklemek için: pip install psutil

psutil yüklü değilse script çalışır ama bazı bölümler sınırlı bilgi döndürür.

Kurulum / Hazırlık

sysinfo.py dosyasını proje klasörüne kopyalayın.

(Opsiyonel) İzole bir virtualenv oluşturun:

python3 -m venv .venv
source .venv/bin/activate
pip install psutil


psutil yoksa script çalıştırıldığı zaman kısa bir uyarı gösterir ve sınırlı çalışır.

Kullanım
# Basit: konsola yazdırır
python3 sysinfo.py

# Dinleyen portları da listele ve JSON kaydet
python3 sysinfo.py --ports --json out.json

# Yardım
python3 sysinfo.py -h

CLI Seçenekleri

--json <file> veya -j <file>: Toplanan bilgileri belirtilen JSON dosyasına kaydet.

--ports: Dinleyen (listening) TCP/UDP portlarını da topla (gerektirir: psutil).

-h, --help: Yardım mesajı.

Örnek Çıktı (konsol — özet)
================================================================================
SYSTEM - BASIC
================================================================================
Hostname                       : myhost
FQDN                           : myhost.example.local
OS                             : Linux 5.15.0-... #1 SMP ...
Machine                        : x86_64
Processor                      : Intel(R) Core(TM) i7-...

================================================================================
UPTIME
================================================================================
Boot time                      : 2025-09-25 08:12:03
Uptime                         : 2 days, 3:41:22

================================================================================
CPU
================================================================================
Model                          : Intel(R) Core(TM) i7-...
Logical CPUs                   : 8
Physical CPUs                  : 4
Freq                           : 2400.0 MHz
Load avg (1,5,15)              : 0.23, 0.18, 0.15

================================================================================
MEMORY
================================================================================
Total                          : 15.6 GB
Available                      : 8.4 GB
Used                           : 6.5 GB
Used %                         : 41%
Swap total                     : 2.0 GB
Swap used                      : 128.0 MB
Swap %                         : 6%

... (disks, network, process summary, listening ports vb.)

Örnek JSON Kaydı (kısaltılmış)
{
  "basic": {
    "hostname": "myhost",
    "fqdn": "myhost.example.local",
    "system": "Linux",
    "release": "5.15.0-xx",
    "machine": "x86_64",
    "processor": "Intel(R) Core(TM) i7-..."
  },
  "uptime": {
    "boot_time": "2025-09-25 08:12:03",
    "uptime": "2 days, 3:41:22"
  },
  "cpu": {
    "logical_cpus": 8,
    "physical_cpus": 4,
    "cpu_freq": "2400.0 MHz",
    "model": "Intel(R) Core(TM) i7-..."
  },
  "memory": {
    "total": "15.6 GB",
    "available": "8.4 GB",
    "used": "6.5 GB",
    "percent_used": "41%"
  }
}

Güvenlik & İzinler

Dinleyen portları ve bazı process bilgilerini almak için script psutil kullanır; belirli sistemlerde ek izin gerektirebilir (özellikle Linux üzerinde net ya da root izinleri ile daha tam bilgi).

Ping/port tarama gibi aktif ağ testleri içermez; yalnızca lokal bilgi toplar. Yine de kurumsal politikalara göre çalıştırılmadan önce izin alınması önerilir.

Toplanan JSON içeriği hassas bilgi içerebilir (hostnames, IPs, açık portlar, process isimleri). Raporları güvenli kanallarda paylaşın.

Öğrenci için Ödev / Görev Önerileri

Aşağıdaki görevleri öğrencine vererek pratik yapmasını sağlayabilirsin. Her maddeyi Trello kartı / küçük sprint şeklinde atamak iyi olur.

Çalıştırma ve Rapor İncelemesi

psutil kurup sysinfo.py --ports --json report.json çalıştır.

JSON çıktısını inceleyip güvenlik-risklerini listele (ör: açık RDP/SSH, Docker API, yüksek bellek kullanımı vs.)

Trello Ticket Oluşturma

Bulunan kritik servisleri (ör. 2375, 6379, 9200) Trello’ya manuel veya otomatik (basit script) olarak ticket aç.

Filtre & Özet Modülü

Script’e --summary argümanı ekleyip yalnızca kritik ipuçlarını (açık riskli portlar, disk %90+, swap yüksek kullanımı) gösteren bir özet ekle.

Periyodik Envanter

Cron ile günlük/haftalık çalıştırma, toplanan JSON’ları S3/Share veya bir klasörde saklama.

Saklanan JSON’lar arasında diff alıp değişimleri (yeni açık portar vs.) raporla.

Basit Güvenlik Analizi

Script çıktısına göre otomatik öneriler üret (ör. “Redis açık, öneri: requirepass ekle” şeklinde).

Öğrenci Genişletmeleri (zorluk arttır)

--upload argümanı: JSON çıktısını güvenli bir API’ye (ör. öğrenci kendi küçük inventory servisine) gönder.

Web arayüzü: Basit Flask app ile toplanan envanteri göster.

Geliştirme & Genişletme Fikirleri

Servis fingerprinting: Açık portlarda basit banner okuma / HTTP server header kontrolü (read-only, pasif).

JSON şeması: Toplanan veriler için JSON Schema tanımlayıp doğrulama yap.

Merkezi inventory: Tüm makinelerden toplanan JSON’ları toplayan küçük bir merkezi servis (ör. SQLite/Flask).

Otomatik ticket: Kritik bulgu oluşunca Jira/Trello’ya otomatik ticket açma.

Güvenlik check-list: CVE/versiyon eşleştirmesi ile bildirim (örn OpenSSH versiyon CVE kontrolü) — dikkat: tehlikeli değil, sadece versiyon eşleştirme.

Hata Giderme (Troubleshooting)

psutil yüklü değil uyarısı

pip install psutil komutunu çalıştırın; virtualenv kullanmayı öneririm.

Dinleyen portlar listelenmiyor / eksik bilgiler

Root/sudo ile çalıştırmayı deneyin (ör. sudo python3 sysinfo.py --ports) — bazı platformlarda sınırlı izinler yüzünden eksik bilgi alınır.

JSON kaydedilemiyor

Yazma izinlerini kontrol edin; dosya yolunun geçerli olduğundan emin olun.

/proc veya ip komutu bulunamıyor

Windows veya farklı bir UNIX varyantı kullanıyorsanız bazı best-effort alanlar boş dönebilir; psutil daha taşınabilir bilgi sağlar.

Lisans

Bu proje örnek amaçlıdır. İstiyorsanız MIT lisansı ile yayınlayabilirsiniz. Kullanım ve dağıtım yerel yasalara ve kurum politikalarına tabidir.