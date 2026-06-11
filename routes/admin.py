from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.db import get_db_connection
from functools import wraps

admin_bp = Blueprint('admin', __name__)


# ── Admin login required ──────────────────────────────────────
def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'admin_id' not in session or session.get('role') != 'admin':
            flash('Admin access only.', 'danger')
            return redirect(url_for('auth.admin_login'))
        return f(*args, **kwargs)
    return decorated


# ── Admin Dashboard ───────────────────────────────────────────
@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    conn   = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) as cnt FROM users")
    total_students = cursor.fetchone()['cnt']

    cursor.execute("SELECT COUNT(*) as cnt FROM placement_drives WHERE status='upcoming'")
    active_drives = cursor.fetchone()['cnt']

    cursor.execute("SELECT * FROM users ORDER BY created_at DESC LIMIT 10")
    recent_students = cursor.fetchall()

    cursor.execute("""
        SELECT sm.skill_name, COUNT(*) as gap_count
        FROM student_skills ss
        JOIN skills_master sm ON ss.skill_id = sm.skill_id
        JOIN role_benchmarks rb ON ss.skill_id = rb.skill_id
        WHERE ss.self_rating < rb.minimum_rating
        GROUP BY sm.skill_name
        ORDER BY gap_count DESC LIMIT 5
    """)
    skill_gaps = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('admin/admin_dashboard.html',
                           total_students=total_students,
                           active_drives=active_drives,
                           recent_students=recent_students,
                           skill_gaps=skill_gaps)


# ── Manage Drives ─────────────────────────────────────────────
@admin_bp.route('/drives', methods=['GET', 'POST'])
@admin_required
def manage_drives():
    conn   = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        cursor.execute("""
            INSERT INTO placement_drives
                (company_name, role_offered, drive_date, last_apply_date,
                 package_lpa, eligible_branches, min_cgpa, job_description, created_by)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            request.form['company_name'],
            request.form['role_offered'],
            request.form['drive_date'],
            request.form['last_apply_date'],
            request.form['package_lpa'],
            request.form['eligible_branches'],
            request.form['min_cgpa'],
            request.form.get('job_description', ''),
            session['admin_id']
        ))
        conn.commit()
        flash('Drive added successfully!', 'success')
        return redirect(url_for('admin.manage_drives'))

    cursor.execute("SELECT * FROM placement_drives ORDER BY drive_date DESC")
    drives = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('admin/manage_drives.html', drives=drives)


# ── Delete Drive ──────────────────────────────────────────────
@admin_bp.route('/drives/delete/<int:drive_id>')
@admin_required
def delete_drive(drive_id):
    conn   = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM placement_drives WHERE drive_id = %s", (drive_id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash('Drive deleted.', 'info')
    return redirect(url_for('admin.manage_drives'))


# ── Student Reports ───────────────────────────────────────────
@admin_bp.route('/reports')
@admin_required
def student_reports():
    conn   = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT u.user_id, u.full_name, u.email, u.branch, u.cgpa,
               sp.target_role, sp.projects_count
        FROM users u
        LEFT JOIN student_profile sp ON u.user_id = sp.user_id
        ORDER BY u.full_name
    """)
    students = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('admin/student_reports.html', students=students)


# ── Manage Skills ─────────────────────────────────────────────
@admin_bp.route('/skills', methods=['GET', 'POST'])
@admin_required
def manage_skills():
    conn   = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        form_type = request.form.get('form_type')
        if form_type == 'add_skill':
            cursor.execute(
                "INSERT INTO skills_master (skill_name, category) VALUES (%s,%s)",
                (request.form['skill_name'], request.form['category'])
            )
            conn.commit()
            flash('Skill added successfully!', 'success')

    cursor.execute("SELECT * FROM skills_master ORDER BY category, skill_name")
    skills = cursor.fetchall()

    cursor.execute("""
        SELECT rb.*, sm.skill_name
        FROM role_benchmarks rb
        JOIN skills_master sm ON rb.skill_id = sm.skill_id
        ORDER BY rb.role_name
    """)
    benchmarks = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('admin/manage_skills.html',
                           skills=skills,
                           benchmarks=benchmarks)