from database import app, init_app
from routes import all_blueprints  # Giả sử routes được gom trong `routes/__init__.py`

# Khởi tạo database sau khi ứng dụng đã được định nghĩa
init_app()

# Đăng ký tất cả routes (Blueprints)
for bp in all_blueprints:
    app.register_blueprint(bp)

if __name__ == "__main__":
    app.run(debug=True)
