def check_drive_eligibility(user_id, drive_id, cursor):
    # Get student info
    cursor.execute("SELECT cgpa, branch FROM users WHERE user_id = %s", (user_id,))
    student = cursor.fetchone()
    if not student:
        return 'not_ready'

    # Get drive requirements
    cursor.execute("""
        SELECT pd.min_cgpa, pd.eligible_branches,
               drs.skill_id, drs.minimum_rating
        FROM placement_drives pd
        LEFT JOIN drive_required_skills drs ON pd.drive_id = drs.drive_id
        WHERE pd.drive_id = %s
    """, (drive_id,))
    requirements = cursor.fetchall()

    if not requirements:
        return 'ready'

    min_cgpa          = requirements[0]['min_cgpa']
    eligible_branches = requirements[0]['eligible_branches']

    # Check CGPA
    if student['cgpa'] and float(student['cgpa']) < float(min_cgpa):
        return 'not_ready'

    # Check branch eligibility
    if eligible_branches:
        branches = [b.strip() for b in eligible_branches.split(',')]
        if student['branch'] not in branches:
            return 'not_ready'

    # Check skill requirements
    met   = 0
    total = 0
    for row in requirements:
        if row['skill_id'] is None:
            continue
        total += 1
        cursor.execute("""
            SELECT self_rating FROM student_skills
            WHERE user_id = %s AND skill_id = %s
        """, (user_id, row['skill_id']))
        result = cursor.fetchone()
        student_rating = result['self_rating'] if result else 0
        if student_rating >= row['minimum_rating']:
            met += 1

    if total == 0:
        return 'ready'

    match_pct = (met / total) * 100
    if match_pct >= 80:
        return 'ready'
    elif match_pct >= 50:
        return 'almost_ready'
    else:
        return 'not_ready'
