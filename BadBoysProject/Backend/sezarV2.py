import math, hashlib, os, binascii
from Crypto.Cipher import DES3
from Crypto.Random import get_random_bytes

alfabe_kucuk = "ğüıjçzköybşrhdalvmtnepsuocfgi̇"
alfabe_buyuk = "ŞZÜKÇYIRĞJHİTVDMÖEALONBPGSUFC"

def sezar_algorithm(text, type, time = 2 ):
    cipher_text = ""
    counter = 1
    
    if type == 'encrypt':
        for r in text:
            if r.isupper():
                cipher_text += alfabe_buyuk[((alfabe_buyuk.index(r)) + tri(counter))%29]
                counter += 1
            elif r.islower():
                cipher_text += alfabe_kucuk[((alfabe_kucuk.index(r)) + tri(counter))%29]
                counter += 1
            else:
                cipher_text+=r
                counter += 1
        
        if time > 1:
            return sezar_algorithm(cipher_text, 'encrypt', time - 1)
        else:        
            return cipher_text
        
    elif type == 'decrypt':
        for r in text:
            if r.isupper():
                cipher_text += alfabe_buyuk[((alfabe_buyuk.index(r)) - tri(counter))%29]
                counter += 1
            elif r.islower():
                cipher_text += alfabe_kucuk[((alfabe_kucuk.index(r)) - tri(counter))%29]
                counter += 1
            else:
                cipher_text+=r
                counter += 1

        if time > 1:
            return sezar_algorithm(cipher_text, 'decrypt', time - 1)
        else:        
            return cipher_text 
    else:
        return 'geçerli işlem giriniz. encrypt ,  decrypt'

def tri(i):
    return round((math.sin(i) + 1) * 15)

def padding(text):
    padding_lenght = 8 - len(text) % 8
    return text + bytes([padding_lenght] * padding_lenght)

def des3_algorithm(text, key):
    cipher = DES3.new(key, DES3.MODE_ECB)
    return cipher.encrypt(padding(text.encode()))

def unpadding(text):
    padding_lenght = text[-1]
    return text[:-padding_lenght]

def des3_algorithm_decrypt(text, key):
    cipher = DES3.new(key, DES3.MODE_ECB)
    return unpadding(cipher.decrypt(text)).decode()

def to_hash(text, key = DES3.adjust_key_parity(os.urandom(24)) , salt= None , iterations: int = 100_000):
    
    cipher_text = sezar_algorithm(text, 'encrypt')

    cipher_text = des3_algorithm(cipher_text, key)

    if salt is None:
        salt = os.urandom(16)

    cipher_text = hashlib.pbkdf2_hmac('sha256', cipher_text, salt, iterations)    

    return cipher_text.hex(), salt.hex()

 


"""

salt, cipher_text = to_hash('deneme')

print(salt.hex() +' '+ cipher_text.hex())
print(sezar_algorithm('deneme','encrypt'))
print(sezar_algorithm('reoind','decrypt'))


print(des3_algorithm('deneme', des3_key).hex())
deger = des3_algorithm('deneme', des3_key)
decryptted = des3_algorithm_decrypt(deger, des3_key)
print(decryptted)



salt, cipher_text = to_hash('deneme', des3_key)

girdi = input("Şifreyi giriniz: ")

salt2, user_cipher = to_hash(girdi, des3_key, salt=salt)

if user_cipher == cipher_text:
    print("Şifre aynı")
else:
    print("Şifre farklı")
"""











