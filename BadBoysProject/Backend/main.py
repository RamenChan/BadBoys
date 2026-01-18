import eventlet
eventlet.monkey_patch()
import os
import secrets
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from flask_socketio import SocketIO
from config import Config
from user_enterance import user_exists, user_add_check
from core import validate_payload
from system_utilities import ResultCode, system_handshake
from key_rotation import rotate_master_key
from services.api import get_stories, get_data_by_api, get_data_by_html
from werkzeug.exceptions import BadRequest
import threading
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = Config.SECRET_KEY

CORS(app, origins=["http://localhost:5173"], supports_credentials=True)


socketio = SocketIO(
    app,
    cors_allowed_origins=Config.SOCKETIO_CORS_ALLOWED_ORIGINS,
    async_mode=Config.SOCKETIO_ASYNC_MODE
)

@app.route("/csrf-token", methods=["GET"])
def get_csrf_token():
    token = secrets.token_hex(32)

    response = make_response(jsonify({"status": "ok"}))
    response.set_cookie(
        "csrf_token",
        token,
        httponly=Config.CSRF_COOKIE_HTTPONLY,     
        samesite=Config.CSRF_COOKIE_SAMESITE, 
        secure=Config.CSRF_COOKIE_SECURE     
    )
    return response


def validate_csrf_token():
    csrf_cookie = request.cookies.get("csrf_token")
    csrf_header = request.headers.get("X-CSRF-Token")

    if not csrf_cookie or not csrf_header:
        raise BadRequest("CSRF token eksik")

    if csrf_cookie != csrf_header:
        raise BadRequest("CSRF token geçersiz")

    print("CSRF token geçerli")

@app.route("/user_check", methods=["POST"])
def user_check():
    try:
        validate_csrf_token()
    except BadRequest as e:
        return jsonify({"result": system_handshake(ResultCode.ERROR, str(e))}), 400
    
    data = request.get_json()
    responce = validate_payload(data)
    
    if responce['code'] == ResultCode.SUCCESS: 
        result = user_exists(data.get("username"), data.get("password"), ip=request.remote_addr)
        return jsonify({"result": result})
    else:
        return jsonify({"result": responce})


@app.route("/user_add", methods=["POST"])
def user_add():
    try:
        validate_csrf_token()
    except BadRequest as e:
        return jsonify({"result": system_handshake(ResultCode.ERROR, str(e))}), 400
    
    data = request.get_json()
    responce = validate_payload(data)
    
    if responce['code'] == ResultCode.SUCCESS: 
        result = user_add_check(data.get("username"), data.get("password"), data.get("confirmPassword"), data.get("email"))
        return jsonify({"result": result})
    else:
        return jsonify({"result": responce})


@app.route("/logout", methods=["POST"])
def logout():
    response = make_response(
        jsonify({"result": system_handshake(ResultCode.SUCCESS, "Çıkış yapıldı")})
    )
    response.delete_cookie("csrf_token")
    return response

@app.route("/api/stories", methods=["GET"])
def api_get_stories():
    source = request.args.get("source", "api")
    result = get_stories(source)
    return jsonify({"result": result})


@app.route("/", methods=["GET"])
def index():
    return jsonify({"status": "OK"})


def key_rotation_scheduler():
    while True:
        try:
            rotate_master_key()
        except:
            pass
        time.sleep(Config.KEY_ROTATION_INTERVAL)

def databot_fetch_scheduler():
    while True:
        try:
            get_data_by_api()
            latest_api = get_stories('api')
            socketio.emit("new_stories", latest_api)
            
            get_data_by_html()
            latest_html = get_stories('html')
            socketio.emit("new_stories_html", latest_html)
        except:
            pass
        time.sleep(Config.DATA_FETCH_INTERVAL)

def start_background_tasks():
    time.sleep(2)
    threading.Thread(target=key_rotation_scheduler, daemon=True).start()
    time.sleep(2)
    threading.Thread(target=databot_fetch_scheduler, daemon=True).start()


if __name__ == "__main__":
    #threading.Thread(target=start_background_tasks, daemon=True).start()
    socketio.run(app, debug=Config.DEBUG, port=8000, host="0.0.0.0")
