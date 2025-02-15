from flask import Blueprint, send_file
from flask_login import login_required, current_user
from models import Transaction, Category
from database import db
import pandas as pd
from io import BytesIO
from sqlalchemy import func, extract, case

# Khởi tạo Blueprint cho export
bp = Blueprint("export", __name__)

def generate_excel(df, filename):
    """Tạo file Excel từ DataFrame và trả về file để tải xuống"""
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    return send_file(output, as_attachment=True, download_name=filename, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

@bp.route("/export_transactions", methods=["GET"])
@login_required
def export_transactions():
    """Xuất danh sách giao dịch thành file Excel"""
    transactions = Transaction.query.filter_by(user_id=current_user.id).all()

    data = [{
        "Date": t.transaction_date.strftime("%d/%m/%Y"),
        "Type": t.transaction_type,
        "Category": t.category.name,
        "Amount": t.transaction_amount
    } for t in transactions]

    df = pd.DataFrame(data)
    return generate_excel(df, "Transactions.xlsx")

@bp.route("/export_revenue", methods=["GET"])
@login_required
def export_revenue():
    """Xuất báo cáo thu nhập theo ngày/tháng"""
    today = pd.Timestamp.today().date()
    revenue = db.session.query(
        Transaction.transaction_date,
        func.sum(case((Transaction.transaction_type == "income", Transaction.transaction_amount), else_=0)).label("Total Income"),
        func.sum(case((Transaction.transaction_type == "expense", Transaction.transaction_amount), else_=0)).label("Total Expense")
    ).filter(
        Transaction.user_id == current_user.id,
        Transaction.transaction_date >= today.replace(day=1)
    ).group_by(Transaction.transaction_date).all()

    df = pd.DataFrame(revenue, columns=["Date", "Income", "Expense"])
    df = df.set_index("Date").reindex(pd.date_range(start=today.replace(day=1), end=today), fill_value=0).reset_index()
    df.rename(columns={"index": "Date"}, inplace=True)

    return generate_excel(df, "Revenue_Report.xlsx")

@bp.route("/export_expense", methods=["GET"])
@login_required
def export_expense():
    """Xuất báo cáo chi tiêu so sánh giữa các tháng"""
    today = pd.Timestamp.today().date()
    current_month = today.month
    current_year = today.year
    previous_month = current_month - 1 if current_month > 1 else 12
    previous_year = current_year if current_month > 1 else current_year - 1

    expense_current = db.session.query(
        Transaction.transaction_date,
        func.sum(Transaction.transaction_amount).label("Current Month Expense")
    ).filter(
        Transaction.user_id == current_user.id,
        Transaction.transaction_type == "expense",
        extract("month", Transaction.transaction_date) == current_month,
        extract("year", Transaction.transaction_date) == current_year
    ).group_by(Transaction.transaction_date).all()

    expense_previous = db.session.query(
        Transaction.transaction_date,
        func.sum(Transaction.transaction_amount).label("Previous Month Expense")
    ).filter(
        Transaction.user_id == current_user.id,
        Transaction.transaction_type == "expense",
        extract("month", Transaction.transaction_date) == previous_month,
        extract("year", Transaction.transaction_date) == previous_year
    ).group_by(Transaction.transaction_date).all()

    df_current = pd.DataFrame(expense_current, columns=["Date", "Current Month Expense"])
    df_previous = pd.DataFrame(expense_previous, columns=["Date", "Previous Month Expense"])

    all_dates = pd.date_range(start=today.replace(day=1), end=today)
    df_current = df_current.set_index("Date").reindex(all_dates, fill_value=0).reset_index().rename(columns={"index": "Date"})
    df_previous = df_previous.set_index("Date").reindex(all_dates, fill_value=0).reset_index().rename(columns={"index": "Date"})

    df = pd.merge(df_current, df_previous, on="Date", how="outer").fillna(0)
    df["Change (%)"] = df.apply(lambda row: ((row["Current Month Expense"] - row["Previous Month Expense"]) / row["Previous Month Expense"] * 100)
        if row["Previous Month Expense"] != 0 else 0, axis=1).round(2).astype(str) + " %"

    return generate_excel(df, "Expense_Comparison.xlsx")

@bp.route("/export_summary", methods=["GET"])
@login_required
def export_summary():
    """Xuất tổng hợp chi tiêu theo danh mục"""
    today = pd.Timestamp.today().date()
    summary = db.session.query(
        Category.name.label("Category"),
        func.sum(Transaction.transaction_amount).label("Total Expense")
    ).join(Category, Transaction.category_id == Category.id).filter(
        Transaction.user_id == current_user.id,
        Transaction.transaction_type == "expense",
        Transaction.transaction_date >= today.replace(day=1)
    ).group_by(Category.name).all()

    df = pd.DataFrame(summary, columns=["Category", "Total Expense"])
    total_expense = df["Total Expense"].sum()
    df["% Total Expense"] = (df["Total Expense"] / total_expense * 100).round(2).astype(str) + " %"

    return generate_excel(df, "Expense_Summary.xlsx")
