from flask import Blueprint, request, jsonify
from app import db, limiter
from app.models import User
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

main = Blueprint("main", __name__)

@main.route("/")
@limiter.limit("10 per minute")
def home():
    return "Flask API is working!"

@main.route("/register", methods=["POST"])
@limiter.limit("3 per minute")
def register():
    data = request.json
    if not data or not data.get("username") or not data.get("email") or not data.get("password"):
        return jsonify({"error": "Missing required fields"}), 400

    # ✅ เช็กว่า Username หรือ Email มีอยู่แล้วหรือไม่
    existing_user = User.query.filter(
        (User.username == data['username']) | (User.email == data['email'])
    ).first()

    if existing_user:
        if existing_user.username == data['username']:
            return jsonify({"error": "Username already exists"}), 400
        if existing_user.email == data['email']:
            return jsonify({"error": "Email already exists"}), 400

    # ✅ สร้าง User ใหม่
    new_user = User(username=data['username'], email=data['email'])
    new_user.set_password(data['password'])

    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({"message": "User registered successfully"}), 201

@main.route("/login", methods=["POST"])
@limiter.limit("5 per minute")
def login():
    data = request.json
    if not data or not data.get("username") or not data.get("password"):
        return jsonify({"error": "Missing username or password"}), 400

    user = User.query.filter_by(username=data['username']).first()
    if not user or not user.check_password(data['password']):
        return jsonify({"error": "Invalid username or password"}), 401

    access_token = create_access_token(identity=user.id)
    return jsonify({"access_token": access_token}), 200

@main.route("/profile", methods=["GET"])
@jwt_required()
def profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    return jsonify({"username": user.username, "email": user.email}), 200
