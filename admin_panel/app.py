from flask import Flask, render_template, redirect, url_for, flash, session
import mysql.connector

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Database connection
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Shra@0303',
    'database': 'regear_db'
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

# Admin authentication decorator
def admin_required(f):
    def wrap(*args, **kwargs):
        if 'admin' not in session:
            flash('Admin login required', 'danger')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    wrap.__name__ = f.__name__
    return wrap

# Routes
@app.route('/')
@admin_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    # Placeholder for admin login logic
    return render_template('admin_login.html')

if __name__ == '__main__':
    app.run(debug=True)