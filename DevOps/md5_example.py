# md5_example.py
import hashlib

# 1) Basit metin -> MD5
text = "merhaba dünya "
m = hashlib.md5()              # md5 nesnesi oluştur
m.update(text.encode('utf-8')) # veriyi ekle
digest_hex = m.hexdigest()     # hex string olarak al
print("MD5(merhaba dünya) =", digest_hex)
# örn. çıktı: MD5(merhaba dünya) = 6f5902ac237024bdd0c176cb93063dc4

# 2) Büyük dosya için parça parça hesaplama (bellek dostu)
def md5_of_file(path, chunk_size=8192):
    h = hashlib.md5()
    with open(path, 'rb') as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()

# usage:
# print("Dosya MD5:", md5_of_file("büyük_dosya.zip"))