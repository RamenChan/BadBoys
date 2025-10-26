import os
from datetime import datetime
from dotenv import set_key, find_dotenv, dotenv_values
from Crypto.Cipher import DES3
from db_connection import client

# =============================
#  CONFIGURATION
# =============================

DB_NAME = "BadBoys"
DEK_COLLECTION = "DES3_DEKS"
DEK_LOG_COLLECTION = "DES3_DEKS_LOGS"
ENV_PATH = find_dotenv()


# =============================
#  DATABASE OPERATIONS
# =============================

def get_latest_dek(collection):
    """Veritabanından en son oluşturulan DEK kaydını getirir."""
    return collection.find_one(sort=[("_id", -1)])


def insert_dek(collection, dek_hex, dek_id):
    """Yeni DEK kaydını MongoDB'ye ekler."""
    dek_doc = {
        "dek": dek_hex,
        "create_date": datetime.now(),
        "status": "A",
        "rotate_date": None,
        "3DES_DEK_ID": dek_id
    }
    collection.insert_one(dek_doc)

def deactivate_old_dek(collection, dek_id):
    """Eski aktif DEK kaydını pasif hale getirir."""
    collection.update_one(
        {"3DES_DEK_ID": dek_id},
        {"$set": {"status": "P", "rotate_date": datetime.now()}}
    )


def logger(collection, ID=None, stepcode= None, stepname=None, message=None):

    try:
        db = client["BadBoys"]
        db["DES3_DEKS_LOGS"].insert_one({
            "3DES_DEKS_ID": ID,
            "stepcode": stepcode,
            "stepname": stepname,
            "message": message
        })
    except Exception as e:
        print("Logger hatası:", e)

# =============================
#  ENCRYPTION UTILITIES
# =============================

def des3_encrypt(key: bytes, data: bytes) -> bytes:
    """3DES ile veri şifreleme"""
    cipher = DES3.new(key, DES3.MODE_ECB)
    return cipher.encrypt(data)


def des3_decrypt(key: bytes, data: bytes) -> bytes:
    """3DES ile veri çözme"""
    cipher = DES3.new(key, DES3.MODE_ECB)
    return cipher.decrypt(data)


# =============================
#  ENVIRONMENT UTILITIES
# =============================

def get_master_key() -> bytes:
    """Env dosyasından MASTER_3DES_KEY değerini okur."""
    config = dotenv_values()
    return bytes.fromhex(config["MASTER_3DES_KEY"])


def update_env_master_key(new_key_hex: str):
    """Yeni master key'i .env dosyasına yazar."""
    set_key(ENV_PATH, "MASTER_3DES_KEY", new_key_hex)
    print(".env dosyası güncellendi: MASTER_3DES_KEY")



# =============================
#  ROTATION PROCESS
# =============================

def rotate_master_key():
    """Master key rotasyon işlemini gerçekleştirir."""
    db = client[DB_NAME]
    dek_col = db[DEK_COLLECTION]
    log_col = db[DEK_LOG_COLLECTION]
    
    # En son DEK'i getir
    latest_dek = get_latest_dek(dek_col)
    new_dek_id = latest_dek["3DES_DEK_ID"] + 1

    # MASTER KEY'i oku
    master_key = get_master_key()
    print("Mevcut MASTER_3DES_KEY:", master_key.hex())

    logger(log_col, new_dek_id, 1, "Başlangıç", f"{new_dek_id-1} id'li Eski DEK alındı. MASTER_3DES_KEY alındı.")

    # MASTER KEY çöz
    decrypted_master = des3_decrypt(bytes.fromhex(latest_dek["dek"]), master_key)
    print("Çözülmüş MASTER_3DES_KEY:", decrypted_master.hex())

    logger(log_col, new_dek_id, 2, "Master Key Şifresini Çöz", f"Ham Master Key: {decrypted_master.hex()[-3:]}")

    # Yeni DEK oluştur
    new_dek = os.urandom(24)

    # Yeni DEK ile master key'i yeniden şifrele
    encrypted_master = des3_encrypt(new_dek, decrypted_master)
    encrypted_master_hex = encrypted_master.hex()

    print("Yeni şifrelenmiş MASTER_3DES_KEY:", encrypted_master_hex)

    logger(log_col, new_dek_id, 3, "Master Key Şifrele",
           f"Master key şifrelendi. Yeni DEK: {new_dek.hex()[-3:]}")

    # Yeni master key'i .env'ye yaz
    update_env_master_key(encrypted_master_hex)
    logger(log_col, new_dek_id, 4, "Şifrelenmiş Master Keyi yaz", "Yeni Master Key .env dosyasına yazıldı.")

    # Yeni DEK loglarını kaydet
    insert_dek(dek_col, new_dek.hex(), new_dek_id)

    print("DEK ve encrypted MASTER key başarıyla kaydedildi.")
    logger(log_col, new_dek_id, 5, "Master Key Rotasyonunu Tamamla.", "Master key rotasyonu başarıyla tamamlandı.")

    # Eski dek kayıdını pasife al.
    deactivate_old_dek(dek_col, new_dek_id-1)
    
    print(f"{new_dek_id-1} id'li Eski DEK kayıdı pasife alındı.")
    logger(log_col, new_dek_id, 5, "Tamamlandı", f"{new_dek_id-1} id'li Eski DEK kayıdı pasife alındı.")

    return encrypted_master_hex, new_dek.hex()


# =============================
#  MAIN
# =============================

if __name__ == "__main__":
    new_master_key, new_dek = rotate_master_key()
    print(f"\nYeni Master Key: {new_master_key}")
    print(f"\nYeni DEK: {new_dek}")
