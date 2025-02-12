from flask import Flask, render_template, redirect, url_for, request
from database import db, app
from models import User, Expense, Transaction, Category
from forms import LoginForm, RegisterForm, TransactionForm, ExpenseForm
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
from datetime import datetime, timedelta
from sqlalchemy import extract

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

    if form.validate_on_submit():
        category_name = form.category_name.data.strip().lower()
        transaction_date = datetime.combine(form.transaction_date.data, datetime.min.time())  # Kết hợp ngày và thời gian (00:00:00)
        transaction_type = form.transaction_type.data
        transaction_amount = abs(form.transaction_amount.data)

        if transaction_type == "expense":
            transaction_amount = -transaction_amount

        category = Category.query.filter_by(name=category_name, user_id=current_user.id).first()
        if not category:
            category = Category(name=category_name, user_id=current_user.id)
            db.session.add(category)
            db.session.commit()

        new_transaction = Transaction(
            transaction_date=transaction_date,
            transaction_type=transaction_type,
            category_id=category.id,
            user_id=current_user.id,
            transaction_amount=transaction_amount
        )

        db.session.add(new_transaction)
        db.session.commit()

        return redirect(url_for("fin_dashboard"))

    return render_template("add_transaction.html", form=form)


@app.route("/fin_dashboard")
@login_required
def fin_dashboard():
    today = datetime.today()
    current_day = today.day  # 🟢 Lấy ngày hiện tại (VD: 12)
    current_month = today.month
    current_year = today.year

    # 🟢 Xác định tháng trước chính xác
    if current_month == 1:
        previous_month = 12
        previous_year = current_year - 1
    else:
        previous_month = current_month - 1
        previous_year = current_year

    # 🟢 Lấy tất cả giao dịch trong tháng hiện tại và tháng trước (tính tới ngày hiện tại)
    transactions_current = Transaction.query.filter(
        Transaction.user_id == current_user.id,
        extract('month', Transaction.transaction_date) == current_month,
        extract('year', Transaction.transaction_date) == current_year,
        extract('day', Transaction.transaction_date) <= current_day  # 🔥 Chỉ lấy tới ngày hiện tại
    ).all()

    transactions_previous = Transaction.query.filter(
        Transaction.user_id == current_user.id,
        extract('month', Transaction.transaction_date) == previous_month,
        extract('year', Transaction.transaction_date) == previous_year,
        extract('day', Transaction.transaction_date) <= current_day  # 🔥 Chỉ lấy tới ngày hiện tại
    ).all()

    # 🟢 Tạo danh sách ngày từ 1 → ngày hiện tại
    days = list(range(1, current_day + 1))

    # 🟢 Tổng hợp thu nhập và chi tiêu của tháng hiện tại
    total_income = sum(t.transaction_amount for t in transactions_current if t.transaction_amount > 0)
    total_expense = abs(sum(t.transaction_amount for t in transactions_current if t.transaction_amount < 0))

    # 🟢 Tạo dictionary lưu tổng income và expense theo từng ngày (chỉ từ 1 → ngày hiện tại)
    revenue_current = {day: 0 for day in days}
    expense_current = {day: 0 for day in days}
    revenue_previous = {day: 0 for day in days}
    expense_previous = {day: 0 for day in days}

    # 🟢 Duyệt qua giao dịch để tổng hợp dữ liệu từng ngày
    for t in transactions_current:
        day = t.transaction_date.day
        revenue_current[day] += max(0, t.transaction_amount)  # Thu nhập
        expense_current[day] += abs(min(0, t.transaction_amount))  # Chi tiêu

    for t in transactions_previous:
        day = t.transaction_date.day
        revenue_previous[day] += max(0, t.transaction_amount)  # Thu nhập tháng trước
        expense_previous[day] += abs(min(0, t.transaction_amount))  # Chi tiêu tháng trước

    # 🟢 Chuyển dữ liệu thành danh sách để hiển thị trên biểu đồ
    revenue_data = {
        "income": [revenue_current[day] for day in days],
        "expense": [expense_current[day] for day in days]
    }

    expense_data = {
        "current": [expense_current[day] for day in days],
        "previous": [expense_previous[day] for day in days]
    }

    return render_template(
        "fin_dashboard.html",
        revenue_data=revenue_data,
        expense_data=expense_data,
        transactions=transactions_current,  # ✅ Truyền danh sách giao dịch
        total_income=total_income,
        total_expense=total_expense,
        labels=days
    )


@app.route("/dashboard", methods=["GET", "POST"])
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
