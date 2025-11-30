from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO
from sezarV2 import to_hash  
from user_enterance import user_exists, user_add_check
from core import validate_payload
from system_utilities import ResultCode, system_handshake
from key_rotation import rotate_master_key
from services.api import get_stories, get_data_by_api, get_data_by_html
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
    source = request.args.get("source", "api")
    result = get_stories(source)
    return jsonify({"result": result})



def databot_fetch_scheduler():
    while True:
        print("[DATA_BOT] Veri çekimi başlatılıyor...")
        try:
            print("[API_DATA] Veri çekimi başlatılıyor...")
            get_data_by_api()
            latest_api = get_stories('api')
            socketio.emit("new_stories", latest_api)
            print("[API_DATA] Veri çekimi tamamlandı...")


            print("[HTML_DATA] Veri çekimi başlatılıyor...")
            get_data_by_html()
            latest_html = get_stories('html')
            socketio.emit("new_stories_html", latest_html)
            print("[HTML_DATA] Veri çekimi tamamlandı...")


            print("[DATA_BOT] API ve HTML veri çekimi tamamlandı.")
        except Exception as e:
            print("[DATA_BOT] Veri çekim hatası. DB kayıt atıldı.")
            system_handshake(ResultCode.ERROR, error_message=str(e), function_name="main/databot_fetch_scheduler")
        time.sleep(60)




"""
def api_fetch_scheduler():
    while True:
        print("[DATA_BOT] API veri çekimi başlatılıyor...")
        try:
            get_data_by_api()   
            print("[API_DATA] API veri çekimi başarıyla tamamlandı.")

            latest = get_stories('api')
            socketio.emit("new_stories", latest) 



        except Exception as e:
            print("[DATA_BOT] DATA_BOT veri çekim hatası. DB kayıt atıldı.")
            system_handshake(ResultCode.ERROR, error_message=str(e), function_name="main/api_fetch_scheduler")
        time.sleep(600)
"""




if __name__ == "__main__":
    threading.Thread(target=key_rotation_scheduler, daemon=True).start()

    threading.Thread(target=databot_fetch_scheduler, daemon=True).start()

    app.run(debug=True, use_reloader=False, port=8000)
