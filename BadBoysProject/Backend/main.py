from flask import Flask, request, jsonify
from flask_cors import CORS
from sezarV2 import to_hash  
from user_enterance import user_exists, user_add_check
from core import validate_payload
from system_utilities import ResultCode, system_handshake

app = Flask(__name__)
CORS(app) 

@app.route("/user_check", methods=["POST"])
def encrypt():
    data = request.get_json()

    responce = validate_payload(data)

    if responce['code'] == ResultCode.SUCCESS: 
        result = user_exists(
            data.get("username"),
            data.get("password")
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



if __name__ == "__main__":
    app.run(debug=True, port=8000)
