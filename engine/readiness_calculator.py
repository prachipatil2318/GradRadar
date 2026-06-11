def calculate_readiness(user_id, target_role, cursor):
    # Get student's skill ratings
    cursor.execute("""
        SELECT ss.skill_id, ss.self_rating, sm.skill_name
        FROM student_skills ss
        JOIN skills_master sm ON ss.skill_id = sm.skill_id
        WHERE ss.user_id = %s
    """, (user_id,))
    student_skills = {r['skill_id']: {'rating': r['self_rating'], 'name': r['skill_name']}
                      for r in cursor.fetchall()}

    # Get benchmarks for target role
    cursor.execute("""
        SELECT rb.skill_id, rb.minimum_rating, rb.weightage, sm.skill_name
        FROM role_benchmarks rb
        JOIN skills_master sm ON rb.skill_id = sm.skill_id
        WHERE rb.role_name = %s
    """, (target_role,))
    benchmarks = cursor.fetchall()

    if not benchmarks:
        return {'score': 0, 'level': 'No Benchmark', 'breakdown': []}

    total_weight   = 0
    weighted_score = 0
    skill_breakdown = []

    for row in benchmarks:
        skill_id    = row['skill_id']
        min_rating  = row['minimum_rating']
        weightage   = float(row['weightage'])
        skill_name  = row['skill_name']

        student_rating = student_skills.get(skill_id, {}).get('rating', 0)
        skill_score    = min(student_rating / min_rating, 1.0) if min_rating > 0 else 1.0

        weighted_score += skill_score * weightage
        total_weight   += weightage

        skill_breakdown.append({
            'skill':        skill_name,
            'your_rating':  student_rating,
            'required':     min_rating,
            'score_pct':    round(skill_score * 100),
            'gap':          max(0, min_rating - student_rating)
        })

    readiness_score = round((weighted_score / total_weight) * 100) if total_weight > 0 else 0

    if readiness_score >= 80:
        level = 'Ready'
    elif readiness_score >= 55:
        level = 'Almost Ready'
    else:
        level = 'Needs Work'

    return {
        'score':     readiness_score,
        'level':     level,
        'breakdown': skill_breakdown
    }