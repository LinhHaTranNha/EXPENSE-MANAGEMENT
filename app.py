from flask import Flask, render_template, redirect, url_for, request, jsonify, flash
from database import db, app
from models import User, Expense, Transaction, Category, Goal
from forms import LoginForm, RegisterForm, TransactionForm, ExpenseForm
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
from datetime import datetime, timedelta
from sqlalchemy import func, cast, Date, extract

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
    categories = Category.query.filter_by(user_id=current_user.id).all()

    if request.method == "POST":
        transaction_date = request.form.get("transaction_date")
        transaction_type = request.form.get("transaction_type")
        transaction_amount = request.form.get("transaction_amount")
        selected_category = request.form.get("category_name")
        new_category_name = request.form.get("new_category", "").strip()

        # Debug dữ liệu gửi lên
        print(f"📥 Received Data: {transaction_date}, {transaction_type}, {transaction_amount}, {selected_category}")

        if not transaction_date or not transaction_type or not transaction_amount:
            flash("⚠️ Missing required fields.", "danger")
            return redirect(url_for("add_transaction"))

        # Chuyển đổi số tiền từ chuỗi sang float
        try:
            transaction_amount = float(transaction_amount.replace(",", ""))
        except ValueError:
            flash("⚠️ Invalid amount format.", "danger")
            return redirect(url_for("add_transaction"))

        # Xác định danh mục cuối cùng
        category_name = new_category_name if selected_category == "other" else selected_category

        # Kiểm tra xem danh mục đã tồn tại chưa
        category = Category.query.filter_by(name=category_name, user_id=current_user.id).first()
        if not category:
            category = Category(name=category_name, user_id=current_user.id)
            db.session.add(category)
            db.session.commit()

        # Tạo giao dịch mới
        new_transaction = Transaction(
            transaction_date=datetime.strptime(transaction_date, "%Y-%m-%d"),
            transaction_type=transaction_type,
            category_id=category.id,
            user_id=current_user.id,
            transaction_amount=transaction_amount
        )

        db.session.add(new_transaction)
        db.session.commit()

        # Nếu là "saving", cập nhật tổng số tiền tiết kiệm
        if transaction_type == "saving":
            update_saving(current_user.id)

        flash("✅ Transaction added successfully!", "success")
        return redirect(url_for("fin_dashboard"))

    return render_template("add_transaction.html", form=form, categories=categories)

# 📌 Hàm cập nhật tổng saving
def update_saving(user_id):
    total_saving = db.session.query(
        db.func.sum(Transaction.transaction_amount)
    ).filter(
        Transaction.user_id == user_id,
        Transaction.transaction_type == "saving"
    ).scalar() or 0

    print(f"✅ Cập nhật saving: {total_saving} VND")


@app.route("/fin_dashboard", methods=["GET", "POST"])
@login_required
def fin_dashboard():
    today = datetime.today()
    current_month = today.month
    current_year = today.year

    # 🟢 Xác định tháng trước chính xác
    if current_month == 1:
        previous_month = 12
        previous_year = current_year - 1
    else:
        previous_month = current_month - 1
        previous_year = current_year

    # 🟢 Nhận ngày bắt đầu & kết thúc từ form
    start_date = request.form.get("start_date")
    end_date = request.form.get("end_date")

    if not start_date:
        start_date = datetime(current_year, current_month, 1)
    else:
        start_date = datetime.strptime(start_date, "%Y-%m-%d")

    if not end_date:
        end_date = today
    else:
        end_date = datetime.strptime(end_date, "%Y-%m-%d")

    # 🟢 Lấy giao dịch trong khoảng ngày đã chọn
    transactions_current = Transaction.query.filter(
        Transaction.user_id == current_user.id,
        Transaction.transaction_date >= start_date,
        Transaction.transaction_date <= end_date
    ).all()

    transactions_previous = Transaction.query.filter(
        Transaction.user_id == current_user.id,
        extract('month', Transaction.transaction_date) == previous_month,
        extract('year', Transaction.transaction_date) == previous_year
    ).all()

    # 🟢 Tạo danh sách ngày từ start_date → end_date
    days = list(range(start_date.day, end_date.day + 1))

    # 🟢 Tạo dictionary lưu tổng income và expense theo từng ngày
    revenue_current = {day: 0 for day in days}
    expense_current = {day: 0 for day in days}
    revenue_previous = {day: 0 for day in days}
    expense_previous = {day: 0 for day in days}

    # 🟢 Cập nhật dữ liệu từng ngày (KIỂM TRA `day` TRƯỚC KHI CỘNG)
    for t in transactions_current:
        day = t.transaction_date.day
        if day not in revenue_current:  # 🔥 Nếu ngày chưa có, thêm vào dictionary
            revenue_current[day] = 0
            expense_current[day] = 0
        revenue_current[day] += max(0, t.transaction_amount)  # Thu nhập
        expense_current[day] += abs(min(0, t.transaction_amount))  # Chi tiêu

    for t in transactions_previous:
        day = t.transaction_date.day
        if day not in revenue_previous:  # 🔥 Nếu ngày chưa có, thêm vào dictionary
            revenue_previous[day] = 0
            expense_previous[day] = 0
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

        # 🟢 Tổng hợp chi tiêu theo danh mục (Chỉ tính Expense)
    category_summary = {}
    for t in transactions_current:
        if t.transaction_type == "expense":
            category_name = t.category.name
            category_summary[category_name] = category_summary.get(category_name, 0) + abs(t.transaction_amount)

    # 🟢 Chuyển dữ liệu thành danh sách JSON để render trong frontend
    summary_data = {
        "labels": list(category_summary.keys()),  # Danh sách danh mục
        "values": list(category_summary.values())  # Tổng chi tiêu từng danh mục
    }

    today = datetime.today().date()

    # 🟢 Tính tổng thu nhập (income) trong ngày (Mức tối đa)
    total_income_today = db.session.query(func.sum(Transaction.transaction_amount)).filter(
        Transaction.user_id == current_user.id,
        Transaction.transaction_type == "income",
        cast(Transaction.transaction_date, Date) == today
    ).scalar() or 0  # Nếu None, gán 0

    # 🟢 Tính tổng chi tiêu (expense) trong ngày (Mức đã tiêu)
    total_expense_today = db.session.query(func.sum(Transaction.transaction_amount)).filter(
        Transaction.user_id == current_user.id,
        Transaction.transaction_type == "expense",
        cast(Transaction.transaction_date, Date) == today
    ).scalar() or 0  # Nếu None, gán 0

     # ✅ Chuyển Expense thành số dương nếu cần
    total_expense_today = abs(total_expense_today)

    # 🛑 Tính số tiền vượt quá (nếu có)
    over_limit_amount = max(0, total_expense_today - total_income_today)

    print(f"DEBUG: Income Today = {total_income_today}, Expense Today = {total_expense_today}, Over Limit = {over_limit_amount}")

    return render_template(
        "fin_dashboard.html",
        revenue_data=revenue_data,
        expense_data=expense_data,
        transactions=transactions_current,
        summary_data=summary_data,  # ✅ Gửi dữ liệu xuống frontend
        labels=days,
        selected_start_date=start_date.strftime("%Y-%m-%d"),
        selected_end_date=end_date.strftime("%Y-%m-%d"),
        total_income_today=total_income_today,
        total_expense_today=total_expense_today,
        over_limit_amount=over_limit_amount  # Gửi số tiền vượt quá xuống frontend
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

# 📌 Lấy mục tiêu tiết kiệm
@app.route('/get_goal', methods=['GET'])
@login_required
def get_goal():
    goal = Goal.query.filter_by(user_id=current_user.id).first()
    if goal:
        return jsonify({"goal_amount": goal.goal_amount})
    return jsonify({"goal_amount": 10000000})  # Mặc định nếu chưa đặt mục tiêu

# 📌 Cập nhật mục tiêu tiết kiệm
@app.route('/set_goal', methods=['POST'])
@login_required
def set_goal():
    data = request.get_json()
    new_goal = data.get("goal_amount")

    goal = Goal.query.filter_by(user_id=current_user.id).first()
    if goal:
        goal.goal_amount = new_goal
    else:
        goal = Goal(user_id=current_user.id, goal_amount=new_goal)
        db.session.add(goal)

    db.session.commit()
    return jsonify({"message": "Goal updated successfully!"})

# 📌 Lấy tổng số tiền đã tiết kiệm
@app.route('/get_saving', methods=['GET'])
@login_required
def get_saving():
    total_saving = db.session.query(
        db.func.sum(Transaction.transaction_amount)
    ).filter(
        Transaction.user_id == current_user.id,
        Transaction.transaction_type == "saving"
    ).scalar() or 0

    print(f"✅ Tổng saving hiện tại: {total_saving} VND")
    return jsonify({"current_saving": total_saving})


# 🟢 Khởi tạo database trước khi chạy app
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
