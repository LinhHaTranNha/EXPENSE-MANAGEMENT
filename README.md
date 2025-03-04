# 🌟 FinMan - Financial Management

## 📌 Introduction
**FinMan (Financial Management)** is a web application designed to help users manage their personal finances effectively. Built with a simple and user-friendly interface, FinMan allows users to track expenses, set savings goals, and receive alerts when exceeding daily spending limits.

## 🚀 Key Features
- **Expense Tracking**: Record and monitor daily income and expenses.
- **Spending Limits**: Set daily spending limits and receive notifications when exceeding them.
- **Savings Goals**: Set financial goals and track progress towards achieving them.
- **Financial Reports**: Visualized insights with charts and statistics.
- **User-Friendly Interface**: Minimalist design for easy navigation.

## 🛠️ Technologies Used
FinMan is developed using the following technologies:
- **Backend**: Flask (Python)
- **Database**: PostgreSQL
- **Frontend**: HTML, CSS, JavaScript

## 📂 Directory Structure
```
└── linhhatrannha-expense-management/
    ├── Procfile
    ├── app.py
    ├── database.py
    ├── forms.py
    ├── models.py
    ├── requirements.txt
    ├── static/
    │   ├── css/
    │   │   ├── add_transaction.css
    │   │   ├── animate.css
    │   │   ├── dashboard.css
    │   │   ├── fin_dashboard.css
    │   │   ├── login.css
    │   │   └── register.css
    │   ├── image/
    │   │   └── google-icon.webp
    │   └── js/
    │       ├── dashboard.js
    │       └── fin_dashboard.js
    └── templates/
        ├── add_post.html
        ├── add_transaction.html
        ├── dashboard.html
        ├── edit_post.html
        ├── edit_profile.html
        ├── fin_dashboard.html
        ├── login.html
        └── register.html
```

## 🔧 Installation & Setup
### Prerequisites
- Python 3.x
- PostgreSQL
- Virtual environment (optional)

### Installation Steps
1. **Clone the repository**:
   ```bash
   git clone https://github.com/LinhHaTranNha/EXPENSE-MANAGEMENT.git
   cd EXPENSE-MANAGEMENT
   ```
2. **Create a virtual environment and install dependencies**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # (Linux/macOS)
   venv\Scripts\activate     # (Windows)
   pip install -r requirements.txt
   ```
3. **Configure the database**:
   - Install PostgreSQL and create a new database.
   - Update the database connection details in the `.env` configuration file.
   
4. **Run the application**:
   ```bash
   flask run
   ```
   Then, visit `http://127.0.0.1:5000/` in your web browser.

## 🤝 Contribution
If you would like to contribute to this project, please follow these steps:
- Fork this repository.
- Create a new branch (`git checkout -b feature-name`).
- Make changes and commit (`git commit -m "Short description"`).
- Push to GitHub (`git push origin feature-name`).
- Create a Pull Request to merge into the main branch.

## 📞 Contact
If you have any questions or suggestions, feel free to reach out via GitHub or the development team's email.

GitHub Repository: [EXPENSE-MANAGEMENT](https://github.com/LinhHaTranNha/EXPENSE-MANAGEMENT)

