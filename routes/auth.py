from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required
from models import User
from database import db
from forms import LoginForm, RegisterForm

# Khởi tạo Blueprint cho auth
bp = Blueprint("auth", __name__)

@bp.route("/", methods=["GET", "POST"])
def login():
    """Xử lý đăng nhập người dùng"""
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.password == form.password.data:
            login_user(user)
            flash("Đăng nhập thành công!", "success")
            return redirect(url_for("dashboard.dashboard"))
        else:
            flash("Sai tên đăng nhập hoặc mật khẩu!", "danger")
    return render_template("login.html", form=form)

@bp.route("/register", methods=["GET", "POST"])
def register():
    """Xử lý đăng ký người dùng mới"""
    form = RegisterForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash("Tên đăng nhập đã tồn tại!", "danger")
            return redirect(url_for("auth.register"))

        new_user = User(username=form.username.data, password=form.password.data)
        db.session.add(new_user)
        db.session.commit()

        flash("Tạo tài khoản thành công! Vui lòng đăng nhập.", "success")
        return redirect(url_for("auth.login"))
    return render_template("register.html", form=form)

@bp.route("/logout")
@login_required
def logout():
    """Xử lý đăng xuất người dùng"""
    logout_user()
    flash("Bạn đã đăng xuất!", "info")
    return redirect(url_for("auth.login"))
