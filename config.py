import os

class Config:
    SECRET_KEY = os.urandom(24)  # ใช้สำหรับเซสชันและ JWT
    SQLALCHEMY_DATABASE_URI = 'sqlite:///users.db'  # เปลี่ยนเป็น PostgreSQL ได้
    SQLALCHEMY_TRACK_MODIFICATIONS = False
