from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from models import Transaction, Category
from database import db
from datetime import datetime
from sqlalchemy import func, extract, cast, Date
from calendar import monthrange  # 📌 Import thêm module calendar

# Khởi tạo Blueprint cho dashboard
bp = Blueprint("dashboard", __name__)

@bp.route("/fin_dashboard", methods=["GET", "POST"])
@login_required
def fin_dashboard():
    """Trang phân tích tài chính chi tiết"""
    today = datetime.today()
    current_month = today.month
    current_year = today.year

    # 🛠 Xác định tháng trước
    if current_month == 1:
        previous_month = 12
        previous_year = current_year - 1
    else:
        previous_month = current_month - 1
        previous_year = current_year

    # 📌 Lấy số ngày trong tháng trước
    last_day_previous_month = monthrange(previous_year, previous_month)[1]
    days_previous_month = list(range(1, last_day_previous_month + 1))

    # 📌 Nhận ngày bắt đầu & kết thúc từ form (nếu có)
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

    # 📌 Lấy giao dịch trong khoảng ngày đã chọn
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

    # 🛠 Tạo dictionary lưu dữ liệu giao dịch theo ngày
    revenue_current = {day: 0 for day in range(start_date.day, end_date.day + 1)}
    expense_current = {day: 0 for day in range(start_date.day, end_date.day + 1)}
    revenue_previous = {day: 0 for day in days_previous_month}
    expense_previous = {day: 0 for day in days_previous_month}

    # 📌 Cập nhật dữ liệu tháng hiện tại
    for t in transactions_current:
        day = t.transaction_date.day
        if t.transaction_type == "income":
            revenue_current[day] += t.transaction_amount
        elif t.transaction_type == "expense":
            expense_current[day] += abs(t.transaction_amount)

    # 📌 Đảm bảo ngày tồn tại trước khi cộng dữ liệu từ tháng trước
    for t in transactions_previous:
        day = t.transaction_date.day
        if day not in revenue_previous:
            revenue_previous[day] = 0  # 🛠 Nếu chưa có, khởi tạo với giá trị 0
            expense_previous[day] = 0

        if t.transaction_type == "income":
            revenue_previous[day] += t.transaction_amount
        elif t.transaction_type == "expense":
            expense_previous[day] += abs(t.transaction_amount)

    # 📊 Dữ liệu để vẽ biểu đồ
    revenue_data = {
        "income": [revenue_current[day] for day in range(start_date.day, end_date.day + 1)],
        "expense": [expense_current[day] for day in range(start_date.day, end_date.day + 1)]
    }

    expense_data = {
        "current": [expense_current[day] for day in range(start_date.day, end_date.day + 1)],
        "previous": [expense_previous[day] for day in days_previous_month]
    }

    # 📊 Tổng hợp chi tiêu theo danh mục
    category_summary = {}
    for t in transactions_current:
        if t.transaction_type == "expense":
            category_name = t.category.name
            category_summary[category_name] = category_summary.get(category_name, 0) + abs(t.transaction_amount)

    summary_data = {
        "labels": list(category_summary.keys()),
        "values": list(category_summary.values())
    }

    # 📌 Tính tổng thu nhập và chi tiêu trong ngày
    today_date = datetime.today().date()
    total_income_today = db.session.query(func.sum(Transaction.transaction_amount)).filter(
        Transaction.user_id == current_user.id,
        Transaction.transaction_type == "income",
        cast(Transaction.transaction_date, Date) == today_date
    ).scalar() or 0

    total_expense_today = db.session.query(func.sum(Transaction.transaction_amount)).filter(
        Transaction.user_id == current_user.id,
        Transaction.transaction_type == "expense",
        cast(Transaction.transaction_date, Date) == today_date
    ).scalar() or 0

    total_expense_today = abs(total_expense_today)
    over_limit_amount = max(0, total_expense_today - total_income_today)

    return render_template(
        "fin_dashboard.html",
        revenue_data=revenue_data,
        expense_data=expense_data,
        transactions=transactions_current,
        summary_data=summary_data,
        labels=list(range(start_date.day, end_date.day + 1)),
        selected_start_date=start_date.strftime("%Y-%m-%d"),
        selected_end_date=end_date.strftime("%Y-%m-%d"),
        total_income_today=total_income_today,
        total_expense_today=total_expense_today,
        over_limit_amount=over_limit_amount
    )
