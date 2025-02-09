from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, FloatField, SubmitField, RadioField, SelectField
from wtforms.validators import DataRequired, EqualTo

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):  #  Form đăng ký mới
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

class ExpenseForm(FlaskForm):
    category = StringField('Category', validators=[DataRequired()])
    amount = FloatField('Amount', validators=[DataRequired()])
    submit = SubmitField('Add Expense')

class TransactionForm(FlaskForm):
    transaction_date = StringField('Ngày giao dịch (YYYY-MM-DD)', validators=[DataRequired()])
    transaction_type = RadioField('Loại giao dịch', choices=[('income', 'Thu nhập'), ('expense', 'Chi tiêu')], validators=[DataRequired()])
    category_id = SelectField('Danh mục', coerce=int, validators=[DataRequired()])  # Lấy từ database
    transaction_amount = FloatField('Số tiền', validators=[DataRequired()])
    submit = SubmitField('Thêm giao dịch')