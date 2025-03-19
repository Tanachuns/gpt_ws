from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# 🔹 ใช้ PostgreSQL บน Neon
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://neondb_owner:npg_atxyPUzG4k5W@ep-autumn-pond-a1edw8i1-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# 🔹 โมเดลผู้ใช้ (User Table)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

# 🔹 สร้างตารางในฐานข้อมูล (ถ้ายังไม่มี)
with app.app_context():
    db.create_all()

@app.route("/")
def home():
    return "Flask + Neon PostgreSQL is working!"

if __name__ == "__main__":
    app.run(debug=True)
