from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
from dotenv import load_dotenv



load_dotenv()
app = Flask(__name__)

# 🔹 โหลดค่าจาก .env
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# ✅ ตั้งค่า Limiter ให้ใช้ get_remote_address
limiter = Limiter(key_func=get_remote_address)
limiter.init_app(app)

# 🔹 โมเดลผู้ใช้
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

# ✅ API ลงทะเบียน (REGISTER) - มี Rate Limit
@app.route("/register", methods=["POST"])
@limiter.limit("3 per minute")  # ❗ จำกัดให้เรียกได้ 3 ครั้งต่อนาที
def register():
    data = request.json
    if not data or not data.get("username") or not data.get("email") or not data.get("password"):
        return jsonify({"error": "Missing required fields"}), 400

    if User.query.filter_by(username=data['username']).first():
        return jsonify({"error": "Username already exists"}), 400

    new_user = User(username=data['username'], email=data['email'])
    new_user.set_password(data['password'])

    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({"message": "User registered successfully"}), 201

# ✅ API เข้าสู่ระบบ (LOGIN) - มี Rate Limit
@app.route("/login", methods=["POST"])
@limiter.limit("5 per minute")  # ❗ จำกัดให้เรียกได้ 5 ครั้งต่อนาที
def login():
    data = request.json
    if not data or not data.get("username") or not data.get("password"):
        return jsonify({"error": "Missing username or password"}), 400

    user = User.query.filter_by(username=data['username']).first()
    if not user or not user.check_password(data['password']):
        return jsonify({"error": "Invalid username or password"}), 401

    # ✅ สร้าง JWT Token
    access_token = create_access_token(identity=user.id)
    
    return jsonify({"access_token": access_token}), 200

# ✅ API ตรวจสอบว่าระบบทำงานอยู่
@app.route("/")
@limiter.limit("10 per minute")  # ❗ จำกัดการเข้าถึงหน้าแรก
def home():
    return "Flask API with Rate Limit is working!"

# 🔹 สร้างฐานข้อมูลอัตโนมัติ
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)