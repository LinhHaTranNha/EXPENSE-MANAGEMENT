from flask import Flask, render_template, redirect, url_for, request, jsonify, flash
from database import db, app
from models import User, Expense, Transaction, Category, Goal, DailyLimit, UserProfile, Post, Comment
from forms import LoginForm, RegisterForm, TransactionForm, ExpenseForm
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
from datetime import datetime, timedelta
from sqlalchemy import func, cast, Date, extract
import pandas as pd
from flask import send_file
import numpy as np
from io import BytesIO
from sqlalchemy.sql import case
from collections import defaultdict
from flask import session
import json
from flask import session, send_file
from io import BytesIO
import pandas as pd
import json
from flask import request, jsonify
from flask_login import login_required, current_user
from database import db
from models import Like, Post

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

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Bạn đã đăng xuất thành công!", "success")
    return redirect(url_for("login"))

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

        # Đảm bảo selected_category có giá trị hợp lệ
        selected_category = request.form.get("category_name", "").strip()
        new_category_name = request.form.get("new_category", "").strip()

        # Debug dữ liệu gửi lên
        print(f"📥 Received Data: {transaction_date}, {transaction_type}, {transaction_amount}, {selected_category}, {new_category_name}")

        if not transaction_date or not transaction_type or not transaction_amount:
            flash("⚠️ Missing required fields.", "danger")
            return redirect(url_for("add_transaction"))

        # Chuyển đổi số tiền từ chuỗi sang float
        try:
            transaction_amount = float(transaction_amount.replace(",", ""))
        except ValueError:
            flash("⚠️ Invalid amount format.", "danger")
            return redirect(url_for("add_transaction"))

        # Xác định danh mục cuối cùng và chuẩn hóa chữ cái đầu của mỗi từ
        if selected_category == "other" and new_category_name:
            category_name = new_category_name
        else:
            category_name = selected_category

        category_name = (category_name or "").strip().title()  # Sửa lỗi khi category_name là None

        # Kiểm tra xem danh mục đã tồn tại chưa
        category = Category.query.filter_by(name=category_name, user_id=current_user.id).first()

        if not category:
            category = Category(name=category_name, user_id=current_user.id)
            db.session.add(category)
            db.session.commit()
            db.session.refresh(category)  # Đảm bảo lấy được category.id

        print(f"📌 Final Category: {category.name} (ID: {category.id})")  # Debug xem có bị None không

        # Đảm bảo category_id không bị NULL khi lưu giao dịch
        new_transaction = Transaction(
            transaction_date=datetime.strptime(transaction_date, "%Y-%m-%d"),
            transaction_type=transaction_type,
            category_id=category.id,  # Đảm bảo category.id hợp lệ
            user_id=current_user.id,
            transaction_amount=transaction_amount
        )

        db.session.add(new_transaction)
        db.session.commit()

        print(f"✅ Saved Transaction: ID {new_transaction.id}, Category ID: {new_transaction.category_id}")  # Debug giao dịch

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


from collections import defaultdict
from datetime import datetime, date
from sqlalchemy import func, extract, cast
from sqlalchemy.sql.sqltypes import Date

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

    # 🟢 Nhận ngày bắt đầu & kết thúc từ form (Dùng cho transactions_current)
    start_date = request.form.get("start_date")
    end_date = request.form.get("end_date")

    if not start_date:
        start_date = datetime(current_year, current_month, 1)  # Mặc định lấy từ ngày 1 của tháng hiện tại
    else:
        start_date = datetime.strptime(start_date, "%Y-%m-%d")

    if not end_date:
        end_date = today  # Mặc định lấy đến ngày hiện tại
    else:
        end_date = datetime.strptime(end_date, "%Y-%m-%d")

    # 🟢 Tạo khoảng thời gian chỉ tính revenue & expense từ ngày 1 → hôm nay
    revenue_start_date = datetime(current_year, current_month, 1)
    revenue_end_date = today  # Chỉ lấy đến ngày hiện tại

    # 🟢 Lấy giao dịch trong khoảng ngày FE gửi lên (KHÔNG ẢNH HƯỞNG revenue & expense)
    transactions_current = Transaction.query.filter(
        Transaction.user_id == current_user.id,
        Transaction.transaction_date >= start_date,
        Transaction.transaction_date <= end_date
    ).all()

    # 🟢 Lấy giao dịch chỉ cho revenue & expense từ ngày 1 → hôm nay
    revenue_expense_transactions = Transaction.query.filter(
        Transaction.user_id == current_user.id,
        Transaction.transaction_date >= revenue_start_date,
        Transaction.transaction_date <= revenue_end_date
    ).all()

    # 🟢 Lấy giao dịch của tháng trước (toàn bộ tháng)
    transactions_previous = Transaction.query.filter(
        Transaction.user_id == current_user.id,
        extract('month', Transaction.transaction_date) == previous_month,
        extract('year', Transaction.transaction_date) == previous_year
    ).all()

    # 🟢 Tạo danh sách ngày từ ngày 1 → hôm nay (chỉ áp dụng cho revenue & expense)
    days = list(range(1, today.day + 1))

    # 🟢 Dùng defaultdict để tránh KeyError
    revenue_current = defaultdict(int)
    expense_current = defaultdict(int)
    revenue_previous = defaultdict(int)
    expense_previous = defaultdict(int)

    # 🟢 Cập nhật dữ liệu revenue & expense từ ngày 1 đến hôm nay
    for t in revenue_expense_transactions:
        day = t.transaction_date.day
        if t.transaction_type == "income":
            revenue_current[day] += t.transaction_amount  # Thu nhập từ ngày 1 → hôm nay
        elif t.transaction_type == "expense":
            expense_current[day] += abs(t.transaction_amount)  # Chi tiêu từ ngày 1 → hôm nay

    # 🟢 Cập nhật dữ liệu tháng trước (LẤY TOÀN BỘ)
    for t in transactions_previous:
        day = t.transaction_date.day
        if t.transaction_type == "income":
            revenue_previous[day] += t.transaction_amount  # Thu nhập tháng trước
        elif t.transaction_type == "expense":
            expense_previous[day] += abs(t.transaction_amount)  # Chi tiêu tháng trước

    # 🟢 Chuyển dữ liệu thành danh sách để hiển thị trên biểu đồ
    revenue_data = {
        "income": [revenue_current[day] for day in days],  # Chỉ lấy từ ngày 1 → hôm nay
        "expense": [expense_current[day] for day in days]  # Chỉ lấy từ ngày 1 → hôm nay
    }

    expense_data = {
        "current": [expense_current[day] for day in days],  # Chỉ từ ngày 1 đến hôm nay
        "previous": [expense_previous[day] for day in range(1, 32)]  # Toàn bộ tháng trước
    }

    # 🟢 Tổng hợp chi tiêu theo danh mục (Chỉ tính Expense từ ngày 1 → hôm nay)
    category_summary = defaultdict(int)
    for t in revenue_expense_transactions:
        if t.transaction_type == "expense":
            category_summary[t.category.name] += abs(t.transaction_amount)

    # 🟢 Chuyển dữ liệu thành danh sách JSON để render trong frontend
    summary_data = {
        "labels": list(category_summary.keys()),  # Danh sách danh mục
        "values": list(category_summary.values())  # Tổng chi tiêu từng danh mục
    }

    today_date = datetime.today().date()

    # 🟢 Tính tổng thu nhập (income) trong ngày (Mức tối đa)
    total_income_today = db.session.query(func.sum(Transaction.transaction_amount)).filter(
        Transaction.user_id == current_user.id,
        Transaction.transaction_type == "income",
        cast(Transaction.transaction_date, Date) == today_date
    ).scalar() or 0  # Nếu None, gán 0

    # 🟢 Tính tổng chi tiêu (expense) trong ngày (Mức đã tiêu)
    total_expense_today = db.session.query(func.sum(Transaction.transaction_amount)).filter(
        Transaction.user_id == current_user.id,
        Transaction.transaction_type == "expense",
        cast(Transaction.transaction_date, Date) == today_date
    ).scalar() or 0  # Nếu None, gán 0

    # ✅ Chuyển Expense thành số dương nếu cần
    total_expense_today = abs(total_expense_today)

    # 🛑 Tính số tiền vượt quá (nếu có)
    over_limit_amount = max(0, total_expense_today - total_income_today)

    print(f"DEBUG: Income Today = {total_income_today}, Expense Today = {total_expense_today}, Over Limit = {over_limit_amount}")


    # 🟢 Lưu `transactions_current` vào `session`
    session["transactions_current"] = json.dumps([
        {
            "Date": t.transaction_date.strftime("%Y-%m-%d"),
            "Type": t.transaction_type,
            "Category": t.category.name,
            "Amount": float(t.transaction_amount)
        }
        for t in transactions_current
    ])

    return render_template(
        "fin_dashboard.html",
        revenue_data=revenue_data,
        expense_data=expense_data,
        transactions=transactions_current,  # ✅ Giao dịch vẫn lấy theo start_date → end_date từ FE
        summary_data=summary_data,  # ✅ Chỉ lấy từ ngày 1 → hôm nay
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
    form = TransactionForm()

    # ✅ Kiểm tra nếu user chưa có profile, thì tạo mới
    if not current_user.profile:
        new_profile = UserProfile(user_id=current_user.id, name=current_user.username)
        db.session.add(new_profile)
        db.session.commit()

    # ✅ Truy vấn số lượng likes và comments trước
    like_subquery = (
        db.session.query(Like.post_id, db.func.count(Like.id).label("like_count"))
        .group_by(Like.post_id)
        .subquery()
    )

    comment_subquery = (
        db.session.query(Comment.post_id, db.func.count(Comment.id).label("comment_count"))
        .group_by(Comment.post_id)
        .subquery()
    )

    # ✅ Truy vấn bài viết + JOIN subqueries
    posts = (
        db.session.query(
            Post.id,
            Post.content,
            Post.image_url,
            Post.created_at,
            db.func.coalesce(UserProfile.name, "Người dùng").label("name"),  # ✅ Nếu NULL thì thay bằng "Người dùng"
            db.func.coalesce(UserProfile.avatar, "https://via.placeholder.com/40").label("avatar"),  # ✅ Ảnh mặc định
            db.func.coalesce(like_subquery.c.like_count, 0).label("like_count"),
            db.func.coalesce(comment_subquery.c.comment_count, 0).label("comment_count")
        )
        .join(User, User.id == Post.user_id)
        .outerjoin(UserProfile, UserProfile.user_id == User.id)  # ✅ Dùng outerjoin để tránh lỗi nếu profile không tồn tại
        .outerjoin(like_subquery, like_subquery.c.post_id == Post.id)
        .outerjoin(comment_subquery, comment_subquery.c.post_id == Post.id)
        .order_by(Post.created_at.desc())
        .all()
    )

    return render_template(
        "dashboard.html",
        form=form,
        posts=posts,
        current_user_avatar=current_user.profile.avatar if current_user.profile else "https://via.placeholder.com/40",
        current_user_name=current_user.profile.name if current_user.profile else "Người dùng"
    )

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


@app.route("/export_revenue", methods=["GET"])
@login_required
def export_revenue():
    today = datetime.today().date()
    current_month = today.month
    current_year = today.year

    # 🟢 Truy vấn tổng thu nhập và chi tiêu theo ngày
    revenue = db.session.query(
        Transaction.transaction_date,
        func.sum(
            case(
                (Transaction.transaction_type == "income", Transaction.transaction_amount),
                else_=0
            )
        ).label("Total Income"),
        func.sum(
            case(
                (Transaction.transaction_type == "expense", Transaction.transaction_amount),
                else_=0
            )
        ).label("Total Expense")
    ).filter(
        Transaction.user_id == current_user.id,
        Transaction.transaction_date >= today.replace(day=1)  # Chỉ lấy dữ liệu tháng này
    ).group_by(Transaction.transaction_date).all()

    # 🟢 Chuyển kết quả thành DataFrame
    df = pd.DataFrame(revenue, columns=["Date", "Income", "Expense"])

    # 🟢 Điền giá trị 0 cho ngày không có giao dịch
    df = df.set_index("Date").reindex(pd.date_range(start=today.replace(day=1), end=today), fill_value=0).reset_index()
    df.rename(columns={"index": "Date"}, inplace=True)

    # 🟢 Xuất ra file Excel
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False)

    output.seek(0)

    return send_file(output, as_attachment=True, download_name="Revenue.xlsx", mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


@app.route("/export_expense", methods=["GET"])
@login_required
def export_expense():
    today = datetime.today().date()
    current_month = today.month
    current_year = today.year

    # 🔵 Xác định tháng trước
    if current_month == 1:
        previous_month = 12
        previous_year = current_year - 1
    else:
        previous_month = current_month - 1
        previous_year = current_year

    # 🟢 Xác định ngày đầu của tháng hiện tại và tháng trước
    first_day_current = datetime(current_year, current_month, 1).date()
    first_day_previous = datetime(previous_year, previous_month, 1).date()

    # 🟢 Xác định số ngày tối đa cần lấy (dựa trên tháng hiện tại)
    max_days = (first_day_current.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
    max_days = max_days.day  # Lấy số ngày trong tháng hiện tại

    # 🟢 Truy vấn tổng chi tiêu của tháng hiện tại
    expense_current = db.session.query(
        func.day(Transaction.transaction_date),
        func.sum(Transaction.transaction_amount).label("Current Month Expense")
    ).filter(
        Transaction.user_id == current_user.id,
        Transaction.transaction_type == "expense",
        extract("month", Transaction.transaction_date) == current_month,
        extract("year", Transaction.transaction_date) == current_year
    ).group_by(func.day(Transaction.transaction_date)).all()

    # 🟢 Truy vấn tổng chi tiêu của tháng trước
    expense_previous = db.session.query(
        func.day(Transaction.transaction_date),
        func.sum(Transaction.transaction_amount).label("Previous Month Expense")
    ).filter(
        Transaction.user_id == current_user.id,
        Transaction.transaction_type == "expense",
        extract("month", Transaction.transaction_date) == previous_month,
        extract("year", Transaction.transaction_date) == previous_year
    ).group_by(func.day(Transaction.transaction_date)).all()

    # 🟢 Chuyển kết quả thành DataFrame
    df_current = pd.DataFrame(expense_current, columns=["Day", "Current Month Expense"])
    df_previous = pd.DataFrame(expense_previous, columns=["Day", "Previous Month Expense"])

    # 🟢 Tạo danh sách ngày từ 1 → max_days
    all_days = pd.DataFrame({"Day": range(1, max_days + 1)})

    # 🟢 Điền giá trị 0 cho ngày không có giao dịch
    df_current = all_days.merge(df_current, on="Day", how="left").fillna(0)
    df_previous = all_days.merge(df_previous, on="Day", how="left").fillna(0)

    # 🟢 Gộp hai bảng để so sánh chi tiêu giữa tháng này và tháng trước
    df = pd.merge(df_current, df_previous, on="Day", how="outer").fillna(0)

    # 🟢 Tính phần trăm thay đổi và giữ dưới dạng số (float)
    df["Change (%)"] = df.apply(
        lambda row: ((row["Current Month Expense"] - row["Previous Month Expense"]) / row["Previous Month Expense"])
        if row["Previous Month Expense"] != 0 else 0,
        axis=1
    ).round(2)  # Giữ nguyên kiểu float

    # 🟢 Xuất ra file Excel
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Expense Comparison")

    output.seek(0)

    return send_file(output, as_attachment=True, download_name="Expense_Comparison.xlsx", mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


@app.route("/export_summary", methods=["GET"])
@login_required
def export_summary():
    today = datetime.today().date()

    # 🟢 Truy vấn tổng chi tiêu theo từng danh mục
    summary = db.session.query(
        Category.name.label("Category"),
        func.sum(Transaction.transaction_amount).label("Total Expense")
    ).join(Category, Transaction.category_id == Category.id) .filter(
        Transaction.user_id == current_user.id,
        Transaction.transaction_type == "expense",
        Transaction.transaction_date >= today.replace(day=1)  # Chỉ lấy dữ liệu trong tháng này
    ).group_by(Category.name).all()

    # 🟢 Chuyển kết quả thành DataFrame
    df = pd.DataFrame(summary, columns=["Category", "Total Expense"])

    # 🟢 Tính tổng chi tiêu của tất cả danh mục
    total_expense = df["Total Expense"].sum()

    # 🟢 Tạo cột "% Total Expense"
    df["% Total Expense"] = (df["Total Expense"] / total_expense * 100).round(2)

    # 🟢 Xuất ra file Excel
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False)

    output.seek(0)

    return send_file(output, as_attachment=True, download_name="Expense_Summary.xlsx", mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")



@app.route("/export_transactions", methods=["GET"])
@login_required
def export_transactions():
    # 🟢 Lấy dữ liệu từ `session`
    transactions_data = session.get("transactions_current")

    if not transactions_data:
        flash("No transactions found to export.", "danger")
        return redirect(url_for("fin_dashboard"))

    # 🟢 Chuyển từ JSON về danh sách Python
    transactions = json.loads(transactions_data)

    # 🟢 Chuyển dữ liệu thành DataFrame
    df = pd.DataFrame(transactions)

    # 🟢 Xuất ra file Excel
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Transactions")

    output.seek(0)

    return send_file(output, as_attachment=True, download_name="Transactions.xlsx", mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

@app.route("/get_daily_limit", methods=["GET"])
@login_required
def get_daily_limit():
    limit = DailyLimit.query.filter_by(user_id=current_user.id).first()
    if limit:
        return jsonify({"limit_amount": limit.limit_amount})
    return jsonify({"limit_amount": 500000})  # Mặc định nếu chưa đặt

@app.route("/set_daily_limit", methods=["POST"])
@login_required
def set_daily_limit():
    data = request.get_json()
    new_limit = data.get("limit_amount", 500000)

    limit = DailyLimit.query.filter_by(user_id=current_user.id).first()
    if limit:
        limit.limit_amount = new_limit
    else:
        limit = DailyLimit(user_id=current_user.id, limit_amount=new_limit)
        db.session.add(limit)

    db.session.commit()
    return jsonify({"new_limit": new_limit})


# 📌 Route hiển thị trang chỉnh sửa thông tin
@app.route("/edit_profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    # 🔹 Tìm hồ sơ người dùng
    user_profile = UserProfile.query.filter_by(user_id=current_user.id).first()

    # 🔹 Nếu chưa có, tạo mới UserProfile
    if not user_profile:
        user_profile = UserProfile(user_id=current_user.id, name=current_user.username, avatar="https://example.com/default-avatar.jpg")
        db.session.add(user_profile)
        db.session.commit()

    if request.method == "POST":
        new_name = request.form.get("name")
        avatar_url = request.form.get("avatar_url")

        # 🔹 Cập nhật tên
        if new_name:
            user_profile.name = new_name
        
        # 🔹 Cập nhật URL avatar
        if avatar_url:
            user_profile.avatar = avatar_url

        db.session.commit()
        flash("Cập nhật thông tin thành công!", "success")
        return redirect(url_for("edit_profile"))

    return render_template("edit_profile.html", user_profile=user_profile)

@app.route("/add_post", methods=["GET", "POST"])
@login_required
def add_post():
    if request.method == "POST":
        content = request.form.get("content")
        image_url = request.form.get("image_url")  # Lấy URL ảnh

        if not content:
            flash("Nội dung bài viết không được để trống!", "danger")
            return redirect(url_for("add_post"))

        new_post = Post(content=content, image_url=image_url, user_id=current_user.id)
        db.session.add(new_post)
        db.session.commit()

        flash("Bài viết đã được đăng!", "success")
        return redirect(url_for("dashboard"))

    return render_template("add_post.html")


@app.route("/like_post/<int:post_id>", methods=["POST"])
@login_required
def like_post(post_id):
    post = Post.query.get_or_404(post_id)
    
    like = Like.query.filter_by(user_id=current_user.id, post_id=post_id).first()

    if like:
        db.session.delete(like)  # Bỏ like nếu đã like trước đó
        db.session.commit()
        like_count = post.likes.count()
        return jsonify({"status": "unliked", "like_count": like_count})
    
    new_like = Like(user_id=current_user.id, post_id=post_id)
    db.session.add(new_like)
    db.session.commit()
    like_count = post.likes.count()
    
    return jsonify({"status": "liked", "like_count": like_count})


@app.route("/add_comment/<int:post_id>", methods=["POST"])
@login_required
def add_comment(post_id):
    post = Post.query.get_or_404(post_id)
    content = request.form.get("content")

    if not content or content.strip() == "":
        return jsonify({"error": "Nội dung bình luận không được để trống!"}), 400

    new_comment = Comment(
        user_id=current_user.id,
        post_id=post_id,
        content=content.strip()
    )
    db.session.add(new_comment)
    db.session.commit()

    return jsonify({
        "user": current_user.profile.name,
        "avatar": current_user.profile.avatar,
        "content": new_comment.content,
        "created_at": new_comment.created_at.strftime('%H:%M - %d/%m/%Y')
    })


@app.route('/get_comments/<int:post_id>', methods=['GET'])
def get_comments(post_id):
    """
    API lấy danh sách bình luận của một bài viết dựa trên post_id
    """
    comments = (
        db.session.query(Comment, UserProfile)
        .join(User, Comment.user_id == User.id)
        .join(UserProfile, User.id == UserProfile.user_id)
        .filter(Comment.post_id == post_id)
        .order_by(Comment.created_at.asc())  # 🔥 Sắp xếp cũ trước, mới sau
        .all()
    )

    if not comments:
        return jsonify({"comments": []})  # Trả về danh sách rỗng nếu không có bình luận nào

    result = []
    for comment, profile in comments:
        result.append({
            "user": profile.name,
            "avatar": profile.avatar,
            "content": comment.content,
            "created_at": comment.created_at.strftime('%H:%M - %d/%m/%Y')
        })

    return jsonify({"comments": result})

# 🟢 Khởi tạo database trước khi chạy app
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
