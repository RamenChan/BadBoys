import math, hashlib, os
from Crypto.Cipher import DES3
from Crypto.Util.Padding import pad, unpad
from dotenv import load_dotenv


alfabe_kucuk = "ğüıjçzköybşrhdalvmtnepsuocfgi̇"
alfabe_buyuk = "ŞZÜKÇYIRĞJHİTVDMÖEALONBPGSUFC"

dotenv_path = r"C:\Users\Mehme\Masaüstü\Projects\BadBoysProject\Backend\.env"
load_dotenv(dotenv_path)

MASTER_3DES_KEY = os.getenv("MASTER_3DES_KEY")
MASTER_3DES_KEY = bytes.fromhex(MASTER_3DES_KEY)



def sezar_algorithm(text, type, time = 2 ):
    cipher_text = ""
    counter = 1
    
    if type == 'encrypt':
        for r in text:
            if r.isupper() and r in alfabe_buyuk:
                cipher_text += alfabe_buyuk[((alfabe_buyuk.index(r)) + tri(counter))%29]
                counter += 1
            elif r.islower() and r in alfabe_kucuk:
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
            if r.isupper() and r in alfabe_buyuk:
                cipher_text += alfabe_buyuk[((alfabe_buyuk.index(r)) - tri(counter))%29]
                counter += 1
            elif r.islower() and r in alfabe_kucuk:
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

def des3_algorithm(text):
    cipher = DES3.new(MASTER_3DES_KEY, DES3.MODE_ECB)
    return cipher.encrypt(pad(text.encode(), DES3.block_size))

def des3_algorithm_decrypt(text):
    cipher = DES3.new(MASTER_3DES_KEY, DES3.MODE_ECB)
    return unpad(cipher, DES3.block_size).decode()


def to_hash(text, salt= None , iterations: int = 100_000):
    
    cipher_text = sezar_algorithm(text, 'encrypt')

    cipher_text = des3_algorithm(cipher_text)

    if salt is None:
        salt = os.urandom(16)

    cipher_text = hashlib.pbkdf2_hmac('sha256', cipher_text, salt, iterations)    

    return cipher_text.hex(), salt.hex()









