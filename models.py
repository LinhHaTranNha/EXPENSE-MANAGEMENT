from database import db
from flask_login import UserMixin  # 🟢 Import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="user")  # 🆕 Thêm cột role

    profile = db.relationship("UserProfile", backref="user", uselist=False)

class UserProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, unique=True)
    name = db.Column(db.String(150), nullable=False)
    avatar = db.Column(db.String(255), default="https://t4.ftcdn.net/jpg/05/49/98/39/360_F_549983970_bRCkYfk0P6PP5fKbMhZMIb07mCJ6esXL.jpg")  # 🆕 Lưu URL ảnh

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

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(255), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    user = db.relationship("User", backref="posts")
    
    # ✅ Sử dụng `back_populates` thay vì `backref` để tránh xung đột
    likes = db.relationship("Like", back_populates="post", lazy="dynamic", cascade="all, delete-orphan")
    comments = db.relationship("Comment", back_populates="post", lazy="dynamic", cascade="all, delete-orphan")

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"), nullable=False)

    user = db.relationship("User", backref="likes")
    
    # ✅ Sử dụng `back_populates` thay vì `backref`
    post = db.relationship("Post", back_populates="likes")

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    user = db.relationship("User", backref="comments")
    
    # ✅ Sử dụng `back_populates` thay vì `backref`
    post = db.relationship("Post", back_populates="comments")