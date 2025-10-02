from flask import Flask, request, jsonify
from flask_cors import CORS
from sezarV2 import to_hash  

app = Flask(__name__)
CORS(app) 

@app.route("/encrypt", methods=["POST"])
def encrypt():
    data = request.get_json()
    value = data.get("value")

    cipher_text, salt= to_hash(value)
    return jsonify({"cipher_text": cipher_text, "salt": salt})

if __name__ == "__main__":
    app.run(debug=True, port=8000)
