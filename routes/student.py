from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.db import get_db_connection
from engine.readiness_calculator import calculate_readiness
from engine.plan_generator import generate_action_plan
from engine.eligibility_checker import check_drive_eligibility
from functools import wraps

student_bp = Blueprint('student', __name__)

# ── Login required decorator ──────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'student':
            flash('Please login first.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


# ── Dashboard ─────────────────────────────────────────────────
@student_bp.route('/dashboard')
@login_required
def dashboard():
    user_id = session['user_id']
    conn    = get_db_connection()
    cursor  = conn.cursor(dictionary=True)

    # Get profile
    cursor.execute("SELECT * FROM student_profile WHERE user_id = %s", (user_id,))
    profile = cursor.fetchone()

    # Get readiness score if profile exists
    readiness = None
    if profile and profile['target_role']:
        readiness = calculate_readiness(user_id, profile['target_role'], cursor)

    # Count upcoming drives
    cursor.execute("SELECT COUNT(*) as cnt FROM placement_drives WHERE status = 'upcoming'")
    drives_count = cursor.fetchone()['cnt']

    # Count completed action plan tasks
    cursor.execute("SELECT COUNT(*) as cnt FROM action_plans WHERE user_id=%s AND status='completed'", (user_id,))
    completed_tasks = cursor.fetchone()['cnt']

    cursor.execute("SELECT COUNT(*) as cnt FROM action_plans WHERE user_id=%s", (user_id,))
    total_tasks = cursor.fetchone()['cnt']

    cursor.close()
    conn.close()

    return render_template('student/dashboard.html',
                           profile=profile,
                           readiness=readiness,
                           drives_count=drives_count,
                           completed_tasks=completed_tasks,
                           total_tasks=total_tasks)


# ── Profile ───────────────────────────────────────────────────
@student_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user_id = session['user_id']
    conn    = get_db_connection()
    cursor  = conn.cursor(dictionary=True)

    if request.method == 'POST':
        target_role   = request.form['target_role']
        projects      = request.form['projects_count']
        internships   = request.form['internships_count']
        certifications= request.form['certifications_count']
        github        = request.form.get('github_link', '')
        linkedin      = request.form.get('linkedin_link', '')

        cursor.execute("""
            INSERT INTO student_profile
                (user_id, target_role, projects_count, internships_count, certifications_count, github_link, linkedin_link)
            VALUES (%s,%s,%s,%s,%s,%s,%s)
            ON DUPLICATE KEY UPDATE
                target_role=%s, projects_count=%s,
                internships_count=%s, certifications_count=%s,
                github_link=%s, linkedin_link=%s
        """, (user_id, target_role, projects, internships, certifications, github, linkedin,
              target_role, projects, internships, certifications, github, linkedin))

        # Save skill ratings
        for key, value in request.form.items():
            if key.startswith('skill_'):
                skill_id = key.split('_')[1]
                cursor.execute("""
                    INSERT INTO student_skills (user_id, skill_id, self_rating)
                    VALUES (%s,%s,%s)
                    ON DUPLICATE KEY UPDATE self_rating=%s
                """, (user_id, skill_id, value, value))

        conn.commit()
        flash('Profile saved successfully!', 'success')
        cursor.close()
        conn.close()
        return redirect(url_for('student.readiness'))

    # GET — load existing profile and all skills
    cursor.execute("SELECT * FROM student_profile WHERE user_id = %s", (user_id,))
    profile = cursor.fetchone()

    cursor.execute("SELECT * FROM skills_master ORDER BY category, skill_name")
    skills = cursor.fetchall()

    # Get existing ratings
    cursor.execute("SELECT skill_id, self_rating FROM student_skills WHERE user_id = %s", (user_id,))
    ratings_raw = cursor.fetchall()
    ratings = {r['skill_id']: r['self_rating'] for r in ratings_raw}

    cursor.close()
    conn.close()

    return render_template('student/profile.html',
                           profile=profile,
                           skills=skills,
                           ratings=ratings)


# ── Readiness Score ───────────────────────────────────────────
@student_bp.route('/readiness')
@login_required
def readiness():
    user_id = session['user_id']
    conn    = get_db_connection()
    cursor  = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM student_profile WHERE user_id = %s", (user_id,))
    profile = cursor.fetchone()

    if not profile or not profile['target_role']:
        flash('Please complete your profile first.', 'warning')
        cursor.close()
        conn.close()
        return redirect(url_for('student.profile'))

    result = calculate_readiness(user_id, profile['target_role'], cursor)
    cursor.close()
    conn.close()

    return render_template('student/readiness.html',
                           result=result,
                           target_role=profile['target_role'])


# ── Action Plan ───────────────────────────────────────────────
@student_bp.route('/action-plan')
@login_required
def action_plan():
    user_id = session['user_id']
    conn    = get_db_connection()
    cursor  = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM student_profile WHERE user_id = %s", (user_id,))
    profile = cursor.fetchone()

    if not profile:
        flash('Please complete your profile first.', 'warning')
        return redirect(url_for('student.profile'))

    result = calculate_readiness(user_id, profile['target_role'], cursor)

    # Delete old plan and regenerate
    cursor.execute("DELETE FROM action_plans WHERE user_id = %s", (user_id,))
    conn.commit()

    plan = generate_action_plan(user_id, result['breakdown'], cursor)
    conn.commit()
    cursor.close()
    conn.close()

    return render_template('student/action_plan.html', plan=plan)


# ── Update Task Status (AJAX) ─────────────────────────────────
@student_bp.route('/update-task', methods=['POST'])
@login_required
def update_task():
    from flask import jsonify
    plan_id = request.form.get('plan_id')
    status  = request.form.get('status')
    conn    = get_db_connection()
    cursor  = conn.cursor()
    cursor.execute("UPDATE action_plans SET status=%s WHERE plan_id=%s AND user_id=%s",
                   (status, plan_id, session['user_id']))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'success': True})

# ── Placement Drives ──────────────────────────────────────────
@student_bp.route('/drives')
@login_required
def drives():
    user_id = session['user_id']
    conn    = get_db_connection()
    cursor  = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM placement_drives ORDER BY drive_date ASC")
    all_drives = cursor.fetchall()

    # Get drives student already applied for
    cursor.execute("""
        SELECT drive_id FROM drive_applications WHERE user_id = %s
    """, (user_id,))
    applied_ids = {row['drive_id'] for row in cursor.fetchall()}

    drives_with_status = []
    for drive in all_drives:
        eligibility = check_drive_eligibility(user_id, drive['drive_id'], cursor)
        drives_with_status.append({
            **drive,
            'eligibility': eligibility,
            'already_applied': drive['drive_id'] in applied_ids
        })

    cursor.close()
    conn.close()

    return render_template('student/drives.html',
                           drives=drives_with_status)

# ── Apply for Drive ───────────────────────────────────────────
@student_bp.route('/drives/apply/<int:drive_id>', methods=['POST'])
@login_required
def apply_drive(drive_id):
    user_id = session['user_id']
    conn    = get_db_connection()
    cursor  = conn.cursor(dictionary=True)

    # Get eligibility status
    eligibility = check_drive_eligibility(user_id, drive_id, cursor)

    try:
        cursor.execute("""
            INSERT INTO drive_applications (user_id, drive_id, readiness_status)
            VALUES (%s, %s, %s)
        """, (user_id, drive_id, eligibility))
        conn.commit()
        flash('Successfully applied for the drive!', 'success')
    except Exception:
        flash('You have already applied for this drive.', 'warning')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('student.drives'))


# ── My Applications ───────────────────────────────────────────
@student_bp.route('/my-applications')
@login_required
def my_applications():
    user_id = session['user_id']
    conn    = get_db_connection()
    cursor  = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT da.*, pd.company_name, pd.role_offered,
               pd.drive_date, pd.package_lpa, pd.status as drive_status
        FROM drive_applications da
        JOIN placement_drives pd ON da.drive_id = pd.drive_id
        WHERE da.user_id = %s
        ORDER BY da.applied_at DESC
    """, (user_id,))
    applications = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('student/my_applications.html',
                           applications=applications)