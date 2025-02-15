from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from models import Goal
from database import db

# Khởi tạo Blueprint cho goals
bp = Blueprint("goals", __name__)

@bp.route('/get_goal', methods=['GET'])
@login_required
def get_goal():
    """Lấy mục tiêu tiết kiệm của người dùng"""
    goal = Goal.query.filter_by(user_id=current_user.id).first()
    return jsonify({"goal_amount": goal.goal_amount if goal else 10000000})  # Mặc định nếu chưa đặt mục tiêu

@bp.route('/set_goal', methods=['POST'])
@login_required
def set_goal():
    """Cập nhật mục tiêu tiết kiệm của người dùng"""
    data = request.get_json()
    new_goal = data.get("goal_amount")

    # Kiểm tra dữ liệu hợp lệ
    if not isinstance(new_goal, (int, float)) or new_goal <= 0:
        return jsonify({"error": "Mục tiêu không hợp lệ"}), 400

    # Cập nhật hoặc tạo mới mục tiêu
    goal = Goal.query.filter_by(user_id=current_user.id).first()
    if goal:
        goal.goal_amount = new_goal
    else:
        goal = Goal(user_id=current_user.id, goal_amount=new_goal)
        db.session.add(goal)

    db.session.commit()
    return jsonify({"message": "Mục tiêu đã được cập nhật!", "goal_amount": new_goal})
