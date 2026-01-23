import eventlet
eventlet.monkey_patch()
import secrets
from flask import Flask, request, jsonify, make_response, session
from flask_cors import CORS
from flask_socketio import SocketIO
from config import Config
from user_enterance import user_exists, user_add_check
from core import validate_payload
from system_utilities import ResultCode, system_handshake
from key_rotation import rotate_master_key
from services.api import get_stories, get_data_by_api, get_data_by_html
from werkzeug.exceptions import BadRequest
from rate_limiter import(
    init_limiter, 
    login_limit, 
    register_limit, 
    api_limit, 
    csrf_limit,
    exempt_from_limit
)
from redis_connection import RedisConnection
import threading
import time


app = Flask(__name__)
app.config['SECRET_KEY'] = Config.SECRET_KEY
app.config['SESSION_TYPE'] = Config.SESSION_TYPE
app.config['SESSION_COOKIE_SECURE'] = Config.SESSION_COOKIE_SECURE
app.config['SESSION_COOKIE_HTTPONLY'] = Config.SESSION_COOKIE_HTTPONLY
app.config['SESSION_COOKIE_SAMESITE'] = Config.SESSION_COOKIE_SAMESITE
app.config['PERMANENT_SESSION_LIFETIME'] = Config.PERMANENT_SESSION_LIFETIME


CORS(app, origins=["http://localhost:5173"], supports_credentials=True)

init_limiter(app)

socketio = SocketIO(
    app,
    cors_allowed_origins=Config.SOCKETIO_CORS_ALLOWED_ORIGINS,
    async_mode=Config.SOCKETIO_ASYNC_MODE
)

@app.route("/csrf-token", methods=["GET"])
@csrf_limit()
def get_csrf_token():
    """CSRF token endpoint - existing cookie varsa geri döndür"""
    
    existing_token = request.cookies.get("csrf_token")
    
    if existing_token and len(existing_token) == 64:  
        response = make_response(jsonify({"status": "ok"}))
        return response
    
    token = secrets.token_hex(32)
    
    response = make_response(jsonify({"status": "ok"}))
    response.set_cookie(
        "csrf_token",
        token,
        httponly=Config.CSRF_COOKIE_HTTPONLY,
        samesite=Config.CSRF_COOKIE_SAMESITE,
        secure=Config.CSRF_COOKIE_SECURE,
        max_age=3600  
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
@login_limit()
def user_check():
    try:
        validate_csrf_token()
    except BadRequest as e:
        return jsonify({"result": system_handshake(ResultCode.ERROR, str(e))}), 400
    
    data = request.get_json()
    responce = validate_payload(data)
    
    if responce['code'] == ResultCode.SUCCESS: 
        result = user_exists(data.get("username"), data.get("password"), ip=request.remote_addr)
        if result['code'] == ResultCode.SUCCESS:
            session['username'] = data.get("username")
            session.permanent = True
        return jsonify({"result": result})
    else:
        return jsonify({"result": responce})


@app.route("/user_add", methods=["POST"])
@register_limit()
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
    session.pop('username', None)

    response = make_response(
        jsonify({"result": system_handshake(ResultCode.SUCCESS, "Çıkış yapıldı")})
    )
    response.delete_cookie("csrf_token")
    return response

@app.route("/api/stories", methods=["GET"])
@api_limit()
def api_get_stories():
    source = request.args.get("source", "api")
    result = get_stories(source)
    return jsonify({"result": result})


@app.route("/", methods=["GET"])
@exempt_from_limit()
def index():
    return jsonify({"status": "OK"})

@app.route("/admin/redis-stats", methods=["GET"])
@api_limit()
def redis_stats():
    """Redis istatistiklerini döndür"""
    stats = RedisConnection.get_stats()
    return jsonify({"result": stats})

@app.route("/admin/redis-health", methods=["GET"])
@exempt_from_limit()
def redis_health():
    """Redis health check"""
    health = RedisConnection.health_check()
    return jsonify({"result": health})

def key_rotation_scheduler():
    while True:
        try:
            rotate_master_key()
        except:
            pass
        time.sleep(Config.KEY_ROTATION_INTERVAL)

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
        except:
            pass
        print("[DATA_BOT] API ve HTML veri çekimi tamamlandı.")
        time.sleep(Config.DATA_FETCH_INTERVAL)

def start_background_tasks():
    time.sleep(2)
    threading.Thread(target=key_rotation_scheduler, daemon=True).start()
    time.sleep(2)
    threading.Thread(target=databot_fetch_scheduler, daemon=True).start()


if __name__ == "__main__":

    try:
        redis_health = RedisConnection.health_check()
        if redis_health['code'] != ResultCode.SUCCESS:
            print("Redis bağlantısı yok, rate limiting çalışmayabilir!")
    except Exception as e:
        print(f"Redis hatası: {str(e)}")


    threading.Thread(target=start_background_tasks, daemon=True).start()
    socketio.run(app, debug=Config.DEBUG, port=8000, host="0.0.0.0")
