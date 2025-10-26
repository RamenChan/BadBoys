import math, hashlib, os
from Crypto.Cipher import DES3
from Crypto.Util.Padding import pad
from dotenv import dotenv_values
from system_utilities import system_handshake, ResultCode
from db_connection import client 

def get_env():
    config = dotenv_values() 
    masterkey = bytes.fromhex(config["MASTER_3DES_KEY"])
    return masterkey

def sezar_algorithm(text, type, time = 2 ):
    
    alfabe_kucuk = "ğüıjçzköybşrhdalvmtnepsuocfgi̇"
    alfabe_buyuk = "ŞZÜKÇYIRĞJHİTVDMÖEALONBPGSUFC"
    
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

def des3_algorithm(text, master_key, dek_key) -> bytes:
    
    master_key = des3_algorithm_decrypt(master_key, dek_key) 
    cipher = DES3.new(master_key, DES3.MODE_ECB)
    encrypted = cipher.encrypt(pad(text.encode(), DES3.block_size))
    return encrypted

def des3_algorithm_decrypt(encrypted_hex, key_hex) -> bytes:
    cipher = DES3.new(bytes.fromhex(key_hex), DES3.MODE_ECB)
    decrypted = cipher.decrypt(encrypted_hex)
    return decrypted

def to_hash(text, salt= None , iterations: int = 100_000):
    try:
        cipher_text = sezar_algorithm(text, 'encrypt')

        db = client["BadBoys"]
        dek_key_collection = db["DES3_DEKS"]
        oldest_dek_doc = dek_key_collection.find_one(sort=[("_id", -1)])
        oldest_dek_doc = oldest_dek_doc["dek"]

        cipher_text = des3_algorithm(cipher_text, get_env(), oldest_dek_doc)

        if salt is None:
            salt = os.urandom(16)

        cipher_text = hashlib.pbkdf2_hmac('sha256', cipher_text, salt, iterations)    

        data = {
            "cipher_text": cipher_text.hex(),
            "salt": salt.hex()
        }

        return system_handshake(ResultCode.SUCCESS, "Hash oluşturuldu.", data)
    
    except Exception as e:
        return system_handshake(ResultCode.ERROR, error_message=str(e), function_name="sezarV2/to_hash")
    