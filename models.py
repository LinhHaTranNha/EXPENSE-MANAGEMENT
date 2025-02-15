from database import db
from flask_login import UserMixin  # 🟢 Import UserMixin

class User(db.Model, UserMixin):  # 🟢 Kế thừa UserMixin
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, nullable=False)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(100), nullable=False)  # 🔥 Đổi String thành Unicode
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    transaction_date = db.Column(db.DateTime, nullable=False)
    transaction_type = db.Column(db.Unicode(20), nullable=False)  # 🔥 Unicode cho transaction_type nếu cần
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    transaction_amount = db.Column(db.Float, nullable=False)

    # 🟢 Mối quan hệ với bảng Category
    category = db.relationship("Category", backref="transactions")

class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    goal_amount = db.Column(db.Float, nullable=False)  # Số tiền mục tiêu tiết kiệm

    # 🔥 Liên kết với User
    user = db.relationship("User", backref=db.backref("goal", uselist=False))

class DailyLimit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, unique=True)
    limit_amount = db.Column(db.Float, nullable=False, default=500000)  # Mặc định 500,000 VND

    user = db.relationship("User", backref=db.backref("daily_limit", uselist=False))

