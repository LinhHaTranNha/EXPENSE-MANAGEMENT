from flask import Blueprint

# Khởi tạo Blueprint cho từng module
from .auth import bp as auth_bp
from .transactions import bp as transactions_bp
from .dashboard import bp as dashboard_bp
from .goals import bp as goals_bp
from .limits import bp as limits_bp
from .export import bp as export_bp

# Danh sách blueprint để đăng ký trong app.py
all_blueprints = [
    auth_bp,
    transactions_bp,
    dashboard_bp,
    goals_bp,
    limits_bp,
    export_bp
]
