from flask import Flask, request, jsonify
from flask_cors import CORS
from sezarV2 import to_hash  
from user_enterance import user_exists, user_add_check

app = Flask(__name__)
CORS(app) 

@app.route("/user_check", methods=["POST"])
def encrypt():
    data = request.get_json()
    result = user_exists(data.get("username"),data.get("password"))

    return jsonify({"result": result})

@app.route("/user_add", methods=["POST"])
def add():
    data = request.get_json()
    result = user_add_check(data.get("username"),data.get("password"),data.get("confirmPassword"),data.get("email"))

    return jsonify({"result": result})



if __name__ == "__main__":
    app.run(debug=True, port=8000)
