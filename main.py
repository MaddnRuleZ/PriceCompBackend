from flask import Flask, jsonify, request
from flask_cors import CORS
from Database import Database

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes


@app.route('/getData/<tablename>')
def get_all_data(tablename):
    try:
        db = Database()
        return db.get_all_data(tablename)
    except Exception as e:
        return jsonify({"error": str(e)})


@app.route('/getItem/<tablename>/<item_category>')
def get_item_category(tablename, item_category):
    try:
        db = Database()
        return db.get_item_category(tablename, item_category)
    except Exception as e:
        return jsonify({"error": str(e)})


@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required."}), 400
    try:
        db = Database()
        if not db.insert_user(username, password):
            return jsonify({"error": "Username already exists."}), 409
        else:
            return jsonify({"message": "User registered successfully."}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required."}), 400
    try:
        db = Database()
        userIdent = db.check_login(username, password)
        if userIdent is not None:
            return jsonify({"identifier": userIdent}), 200
        else:
            return jsonify({"error": "Invalid credentials."}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
