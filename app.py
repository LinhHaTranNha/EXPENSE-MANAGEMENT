from flask import Flask, render_template, redirect, url_for, request
from database import db, app
from models import User, Expense, Transaction, Category
from forms import LoginForm, RegisterForm, TransactionForm, ExpenseForm
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
from datetime import datetime

app.config['SECRET_KEY'] = 'linh31052004'

# Cấu hình Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

class UserLogin(UserMixin):
    def __init__(self, user):
        self.id = user.id

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.password == form.password.data:
            login_user(UserLogin(user))
            return redirect(url_for("dashboard"))
    return render_template("login.html", form=form)

@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # Kiểm tra nếu username đã tồn tại
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            return "Tên đăng nhập đã tồn tại, hãy chọn tên khác."

        # Tạo người dùng mới
        new_user = User(username=form.username.data, password=form.password.data)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for("login"))  # Chuyển hướng về trang đăng nhập
    return render_template("register.html", form=form)

@app.route("/add_transaction", methods=["GET", "POST"])
@login_required
def add_transaction():
    form = TransactionForm()
    
    # 🟢 Lấy danh mục từ database
    form.category_id.choices = [(c.id, c.name) for c in Category.query.filter_by(user_id=current_user.id).all()]
    
    if form.validate_on_submit():
        amount = form.transaction_amount.data
        if form.transaction_type.data == "expense":  # Nếu là chi tiêu, số tiền là âm
            amount = -abs(amount)

        new_transaction = Transaction(
            transaction_date=form.transaction_date.data,
            transaction_type=form.transaction_type.data,
            category_id=form.category_id.data,
            user_id=current_user.id,
            transaction_amount=amount
        )
        db.session.add(new_transaction)
        db.session.commit()

        return redirect(url_for("dashboard"))

    return render_template("add_transaction.html", form=form)

from forms import TransactionForm  # 🟢 Import TransactionForm

@app.route("/dashboard")
@login_required
def dashboard():
    form = TransactionForm()  # 🟢 Tạo form và truyền vào template
    expenses = Transaction.query.filter_by(user_id=current_user.id).all()

    total_spent = sum(expense.transaction_amount for expense in expenses)
    categories = [expense.category.name for expense in expenses]
    amounts = [expense.transaction_amount for expense in expenses]

    return render_template("dashboard.html", form=form, categories=categories, amounts=amounts, total_spent=total_spent)

@app.route("/add_expense", methods=["POST"])
@login_required
def add_expense():
    form = ExpenseForm()
    if form.validate_on_submit():
        new_expense = Expense(
            user_id=current_user.id,
            category=form.category.data,
            amount=form.amount.data,
            date=datetime.utcnow()
        )
        db.session.add(new_expense)
        db.session.commit()
    return redirect(url_for("dashboard"))

# 🟢 Khởi tạo database trước khi chạy app
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
