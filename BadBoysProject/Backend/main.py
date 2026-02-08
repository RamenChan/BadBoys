import eventlet
eventlet.monkey_patch()
from flask import Flask, request, jsonify, make_response, session
from flask_cors import CORS
from flask_socketio import SocketIO
from flask_jwt_extended import (
    create_access_token, 
    create_refresh_token,
    jwt_required, 
    get_jwt_identity,
    get_jwt,
    set_access_cookies,
    set_refresh_cookies,
    unset_jwt_cookies
)
from config import Config
from user_enterance import user_exists, user_add_check
from core import validate_payload
from system_utilities import ResultCode, system_handshake
from key_rotation import rotate_master_key
from services.api import get_stories, get_data_by_api, get_data_by_html
from rate_limiter import(
    init_limiter, 
    login_limit, 
    register_limit, 
    api_limit, 
    exempt_from_limit
)
from redis_connection import RedisConnection
from jwt_manager import init_jwt, add_token_to_blacklist
import threading
import time
from datetime import timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = Config.SECRET_KEY


app.config['JWT_SECRET_KEY'] = Config.JWT_SECRET_KEY
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(seconds=Config.JWT_ACCESS_TOKEN_EXPIRES)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(seconds=Config.JWT_REFRESH_TOKEN_EXPIRES)
app.config['JWT_TOKEN_LOCATION'] = Config.JWT_TOKEN_LOCATION
app.config['JWT_COOKIE_SECURE'] = Config.JWT_COOKIE_SECURE
app.config['JWT_COOKIE_CSRF_PROTECT'] = Config.JWT_COOKIE_CSRF_PROTECT
app.config['JWT_COOKIE_SAMESITE'] = Config.JWT_COOKIE_SAMESITE


app.config['SESSION_TYPE'] = Config.SESSION_TYPE
app.config['SESSION_COOKIE_SECURE'] = Config.SESSION_COOKIE_SECURE
app.config['SESSION_COOKIE_HTTPONLY'] = Config.SESSION_COOKIE_HTTPONLY
app.config['SESSION_COOKIE_SAMESITE'] = Config.SESSION_COOKIE_SAMESITE
app.config['PERMANENT_SESSION_LIFETIME'] = Config.PERMANENT_SESSION_LIFETIME


CORS(app, origins=["http://localhost:5173"], supports_credentials=True)

init_limiter(app)
init_jwt(app) 

socketio = SocketIO(
    app,
    cors_allowed_origins=Config.SOCKETIO_CORS_ALLOWED_ORIGINS,
    async_mode=Config.SOCKETIO_ASYNC_MODE
)


@app.route("/user_check", methods=["POST"])
@login_limit()
def user_check():
    
    data = request.get_json()
    responce = validate_payload(data)
    
    if responce['code'] != ResultCode.SUCCESS:
        return jsonify({"result": responce})
    
    result = user_exists(data.get("username"), data.get("password"), ip=request.remote_addr)
    if result['code'] == ResultCode.SUCCESS:
        username = data.get("username")

        access_token = create_access_token(identity=username)
        refresh_token = create_refresh_token(identity=username)

        response = make_response(jsonify({"result": result}))

        set_access_cookies(response, access_token)
        set_refresh_cookies(response, refresh_token)

        return response
    else:
        return jsonify({"result": result})



@app.route("/user_add", methods=["POST"])
@register_limit()
def user_add():
    
    data = request.get_json()
    responce = validate_payload(data)
    
    if responce['code'] == ResultCode.SUCCESS: 
        result = user_add_check(data.get("username"), data.get("password"), data.get("confirmPassword"), data.get("email"))
        return jsonify({"result": result})
    else:
        return jsonify({"result": responce})


@app.route("/logout", methods=["POST"])
@jwt_required(optional=False, verify_type=False)
def logout():
    try:
        jwt_data = get_jwt()
        jti = jwt_data["jti"]
        token_type = jwt_data.get("type", "access")
        
        if token_type == "refresh":
            expires = app.config["JWT_REFRESH_TOKEN_EXPIRES"]
        else:
            expires = app.config["JWT_ACCESS_TOKEN_EXPIRES"]
        
        add_token_to_blacklist(jti, int(expires.total_seconds()))
        
        response = make_response(
            jsonify({"result": system_handshake(ResultCode.SUCCESS, "Çıkış yapıldı")})
        )
        
        unset_jwt_cookies(response)
        
        return response
    except Exception as e:
        return jsonify({
            "result": system_handshake(ResultCode.ERROR, error_message=str(e))
        }), 500




@app.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    """Access token yenileme"""
    try:
        current_user = get_jwt_identity()
        
        new_access_token = create_access_token(identity=current_user)
        
        response = make_response(jsonify({
            "result": system_handshake(ResultCode.SUCCESS, "Token yenilendi")
        }))
        
        set_access_cookies(response, new_access_token)
        
        return response
    except Exception as e:
        return jsonify({
            "result": system_handshake(ResultCode.ERROR, error_message=str(e))
        }), 500


@app.route("/api/stories", methods=["GET"])
@jwt_required() 
@api_limit()
def api_get_stories():
    """Stories endpoint - JWT ile korunuyor"""
    current_user = get_jwt_identity()  
    print(f"Stories istendi: {current_user}")
    
    source = request.args.get("source", "api")
    result = get_stories(source)
    return jsonify({"result": result})


@app.route("/user/me", methods=["GET"])
@jwt_required()
def get_current_user():
    """Mevcut kullanıcı bilgisi"""
    current_user = get_jwt_identity()
    
    from db_connection import client
    db = client["BadBoys"]
    user = db["users"].find_one({"username": current_user}, {"password_hash": 0, "salt": 0})
    
    if user:
        user['_id'] = str(user['_id'])
        return jsonify({
            "result": system_handshake(ResultCode.SUCCESS, data=user)
        })
    else:
        return jsonify({
            "result": system_handshake(ResultCode.ERROR, "Kullanıcı bulunamadı")
        }), 404




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
    socketio.run(app, debug=Config.DEBUG, port=8000, host="0.0.0.0", use_reloader=False)
