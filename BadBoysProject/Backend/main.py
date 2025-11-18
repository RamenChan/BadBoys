from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO
from sezarV2 import to_hash  
from user_enterance import user_exists, user_add_check
from core import validate_payload
from system_utilities import ResultCode, system_handshake
from key_rotation import rotate_master_key
from services.api import get_stories, get_data_by_api
import threading
import time



app = Flask(__name__)
CORS(app) 
socketio = SocketIO(app, cors_allowed_origins="*")



@app.route("/user_check", methods=["POST"])
def encrypt():
    data = request.get_json()

    responce = validate_payload(data)
    if responce['code'] == ResultCode.SUCCESS: 
        result = user_exists(
            data.get("username"),
            data.get("password"),
            ip=request.remote_addr
            )
        return jsonify({"result": result})
    else:
        return jsonify({"result": responce})

@app.route("/user_add", methods=["POST"])
def add():
    data = request.get_json()

    responce = validate_payload(data)
    if responce['code'] == ResultCode.SUCCESS: 
        result = user_add_check(
            data.get("username"),
            data.get("password"),
            data.get("confirmPassword"),
            data.get("email")
        )
        return jsonify({"result": result})
    else:
        return jsonify({"result": responce})

def key_rotation_scheduler():
    while True:
        print("[ROTATION] Key rotation başlatılıyor...")
        try:
            rotate_master_key()
            print("[ROTATION] Key rotation başarıyla tamamlandı.")
        except Exception as e:
            print('[ROTATION] Key rotation hatası alındı. DB kayıt atıldı.')
            system_handshake(ResultCode.ERROR, error_message=str(e), function_name='main/key_rotation_scheduler')
        time.sleep(600)


@app.route("/api/stories", methods=["GET"])
def api_get_stories():
    result = get_stories()
    return jsonify({"result": result})



def api_fetch_scheduler():
    while True:
        print("[API_DATA] API veri çekimi başlatılıyor...")
        try:
            get_data_by_api()   
            print("[API_DATA] API veri çekimi başarıyla tamamlandı.")


            # Yeni veri çekildiğinde frontend'e gönder
            latest = get_stories()
            socketio.emit("new_stories", latest)  # "new_stories" event’i



        except Exception as e:
            print("[API_DATA] API veri çekim hatası. DB kayıt atıldı.")
            system_handshake(ResultCode.ERROR, error_message=str(e), function_name="main/api_fetch_scheduler")
        time.sleep(600)





if __name__ == "__main__":
    threading.Thread(target=key_rotation_scheduler, daemon=True).start()

    threading.Thread(target=api_fetch_scheduler, daemon=True).start()

    app.run(debug=True, use_reloader=False, port=8000)
