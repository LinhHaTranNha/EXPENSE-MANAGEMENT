from flask_sqlalchemy import SQLAlchemy
from flask import Flask

app = Flask(__name__)

# Cấu hình kết nối SQL Server
app.config['SQLALCHEMY_DATABASE_URI'] = "mssql+pyodbc://@localhost/ExpenseDB?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes&charset=utf8"
# app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://expensedb_plg9_user:5ZuAb9BqYPod5ofrJOYBc7jiJjlnlPZE@dpg-cuu3c6qj1k6c738i0h6g-a.oregon-postgres.render.com/expensedb_plg9"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)