from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__)

# Cấu hình database
app.config['SQLALCHEMY_DATABASE_URI'] = "mssql+pyodbc://@localhost/ExpenseDB?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes&charset=utf8"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = "linh31052004"

# Chỉ khởi tạo db, không gán app ngay lập tức
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.init_app(app)

# Khởi tạo database sau khi app hoàn tất import models
def init_app():
    """Hàm khởi tạo database, tránh vòng lặp import"""
    from models import User  # Import tại đây để tránh lỗi vòng lặp
    db.init_app(app)
    with app.app_context():
        db.create_all()

# Định nghĩa user_loader để Flask-Login có thể tìm người dùng
@login_manager.user_loader
def load_user(user_id):
    from models import User  # Import tại đây để tránh lỗi vòng lặp
    return User.query.get(int(user_id))
