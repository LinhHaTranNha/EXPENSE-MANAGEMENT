from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import Transaction, Category
from database import db
from forms import TransactionForm
from datetime import datetime

# Khởi tạo Blueprint cho transactions
bp = Blueprint("transactions", __name__)

@bp.route("/transactions", methods=["GET"])
@login_required
def transactions():
    """Hiển thị danh sách giao dịch của người dùng"""
    transactions = Transaction.query.filter_by(user_id=current_user.id).order_by(Transaction.transaction_date.desc()).all()
    return render_template("transactions.html", transactions=transactions)

@bp.route("/add_transaction", methods=["GET", "POST"])
@login_required
def add_transaction():
    """Thêm giao dịch mới"""
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
            flash("⚠️ Vui lòng điền đầy đủ thông tin.", "danger")
            return redirect(url_for("transactions.add_transaction"))

        # Chuyển đổi số tiền từ chuỗi sang float
        try:
            transaction_amount = float(transaction_amount.replace(",", ""))
        except ValueError:
            flash("⚠️ Định dạng số tiền không hợp lệ.", "danger")
            return redirect(url_for("transactions.add_transaction"))

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

        flash("✅ Giao dịch đã được thêm!", "success")
        return redirect(url_for("transactions.transactions"))

    return render_template("add_transaction.html", form=form, categories=categories)

@bp.route("/delete_transaction/<int:transaction_id>", methods=["POST"])
@login_required
def delete_transaction(transaction_id):
    """Xóa giao dịch"""
    transaction = Transaction.query.get(transaction_id)
    if transaction and transaction.user_id == current_user.id:
        db.session.delete(transaction)
        db.session.commit()
        flash("🗑️ Giao dịch đã bị xóa!", "success")
    else:
        flash("⚠️ Không tìm thấy giao dịch hoặc không có quyền xóa!", "danger")
    return redirect(url_for("transactions.transactions"))

@bp.route("/update_transaction/<int:transaction_id>", methods=["GET", "POST"])
@login_required
def update_transaction(transaction_id):
    """Cập nhật giao dịch"""
    transaction = Transaction.query.get(transaction_id)
    if not transaction or transaction.user_id != current_user.id:
        flash("⚠️ Không tìm thấy giao dịch hoặc không có quyền chỉnh sửa!", "danger")
        return redirect(url_for("transactions.transactions"))

    form = TransactionForm(obj=transaction)
    categories = Category.query.filter_by(user_id=current_user.id).all()

    if form.validate_on_submit():
        transaction.transaction_date = datetime.strptime(form.transaction_date.data, "%Y-%m-%d")
        transaction.transaction_type = form.transaction_type.data
        transaction.transaction_amount = form.transaction_amount.data
        transaction.category_id = form.category.data

        db.session.commit()
        flash("✅ Giao dịch đã được cập nhật!", "success")
        return redirect(url_for("transactions.transactions"))

    return render_template("update_transaction.html", form=form, categories=categories, transaction=transaction)
