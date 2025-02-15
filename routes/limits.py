from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from models import DailyLimit
from database import db

# Khởi tạo Blueprint cho limits
bp = Blueprint("limits", __name__)

@bp.route("/get_daily_limit", methods=["GET"])
@login_required
def get_daily_limit():
    """Lấy giới hạn chi tiêu hàng ngày của người dùng"""
    limit = DailyLimit.query.filter_by(user_id=current_user.id).first()
    if limit:
        return jsonify({"limit_amount": limit.limit_amount})
    return jsonify({"limit_amount": 500000})  # Mặc định nếu chưa đặt

@bp.route("/set_daily_limit", methods=["POST"])
@login_required
def set_daily_limit():
    """Cập nhật giới hạn chi tiêu hàng ngày"""
    data = request.get_json()
    new_limit = data.get("limit_amount")

    if new_limit is None or not isinstance(new_limit, (int, float)) or new_limit <= 0:
        return jsonify({"error": "Giới hạn không hợp lệ"}), 400

    limit = DailyLimit.query.filter_by(user_id=current_user.id).first()
    if limit:
        limit.limit_amount = new_limit
    else:
        limit = DailyLimit(user_id=current_user.id, limit_amount=new_limit)
        db.session.add(limit)

    db.session.commit()
    return jsonify({"message": "Giới hạn chi tiêu đã được cập nhật!", "limit_amount": new_limit})
