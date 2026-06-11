def generate_action_plan(user_id, skill_breakdown, cursor):
    # Only work on skills with gaps
    gaps = [s for s in skill_breakdown if s['gap'] > 0]
    gaps_sorted = sorted(gaps, key=lambda x: x['gap'], reverse=True)

    plan = {1: [], 2: [], 3: [], 4: []}
    week = 1

    for gap_skill in gaps_sorted:
        if week > 4:
            break

        cursor.execute("""
            SELECT r.resource_id, r.resource_title, r.resource_url,
                   r.resource_type, r.duration_days, r.is_free
            FROM learning_resources r
            JOIN skills_master sm ON r.skill_id = sm.skill_id
            WHERE sm.skill_name = %s
            ORDER BY r.is_free DESC
            LIMIT 3
        """, (gap_skill['skill'],))
        resources = cursor.fetchall()

        for resource in resources:
            plan[week].append({
                'skill':          gap_skill['skill'],
                'resource_title': resource['resource_title'],
                'resource_url':   resource['resource_url'],
                'resource_type':  resource['resource_type'],
                'duration':       resource['duration_days'],
                'is_free':        resource['is_free']
            })

            cursor.execute("""
                INSERT INTO action_plans (user_id, skill_id, resource_id, week_number)
                SELECT %s, skill_id, %s, %s
                FROM skills_master WHERE skill_name = %s
            """, (user_id, resource['resource_id'], week, gap_skill['skill']))

        week += 1

    return plan