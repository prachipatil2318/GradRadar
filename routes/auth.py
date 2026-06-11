from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.db import get_db_connection

auth_bp = Blueprint('auth', __name__)


# ── Student Register ──────────────────────────────────────────
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name   = request.form['full_name']
        email  = request.form['email']
        pwd    = request.form['password']
        branch = request.form['branch']
        sem    = request.form['semester']
        cgpa   = request.form['cgpa']
        conn   = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (full_name, email, password, branch, semester, cgpa) VALUES (%s,%s,%s,%s,%s,%s)",
                (name, email, pwd, branch, sem, cgpa)
            )
            conn.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('auth.login'))
        except Exception:
            flash('Email already registered. Try logging in.', 'danger')
        finally:
            cursor.close()
            conn.close()
    return render_template('auth/register.html')


# ── Student Login ─────────────────────────────────────────────
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        pwd   = request.form['password']
        conn   = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        if user and user['password'] == pwd:
            session['user_id'] = user['user_id']
            session['role']    = 'student'
            session['name']    = user['full_name']
            return redirect(url_for('student.dashboard'))
        flash('Invalid email or password.', 'danger')
    return render_template('auth/login.html')


# ── Admin Login ───────────────────────────────────────────────
@auth_bp.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form['email']
        pwd   = request.form['password']
        conn   = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM admin WHERE email = %s", (email,))
        admin  = cursor.fetchone()
        cursor.close()
        conn.close()
        if admin and admin['password'] == pwd:
            session['admin_id']    = admin['admin_id']
            session['role']        = 'admin'
            session['name']        = admin['full_name']
            session['designation'] = admin['designation']
            return redirect(url_for('admin.dashboard'))
        flash('Invalid admin credentials.', 'danger')
    return render_template('admin/admin_login.html')


# ── Admin Register ────────────────────────────────────────────
@auth_bp.route('/admin-register', methods=['GET', 'POST'])
def admin_register():
    if request.method == 'POST':
        name        = request.form['full_name']
        email       = request.form['email']
        pwd         = request.form['password']
        phone       = request.form['phone']
        designation = request.form['designation']
        secret_code = request.form['secret_code']

        # Only allow registration with correct secret code
        if secret_code != 'GRADRADER@ADMIN':
            flash('Invalid secret code. Contact system administrator.', 'danger')
            return render_template('admin/admin_register.html')

        conn   = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO admin (full_name, email, password, phone, designation) VALUES (%s,%s,%s,%s,%s)",
                (name, email, pwd, phone, designation)
            )
            conn.commit()
            flash('Admin registered successfully! Please login.', 'success')
            return redirect(url_for('auth.admin_login'))
        except Exception:
            flash('Email already registered.', 'danger')
        finally:
            cursor.close()
            conn.close()
    return render_template('admin/admin_register.html')


# ── Logout ────────────────────────────────────────────────────
@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))