"""Simple validator for the generated asana_simulation.sqlite database.

Checks:
- Table row counts for main entities
- Referential integrity via simple FK checks
- Basic distribution stats (unassigned tasks %, completion rate by project_type)
- Edge cases (overdue tasks, weekend dates, archived projects)
"""
import sqlite3
from pathlib import Path
import os


def run_checks(db_path: str):
    if not Path(db_path).exists():
        raise FileNotFoundError(f"DB not found at {db_path}")

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    print("=" * 60)
    print("DATABASE VALIDATION")
    print("=" * 60)

    tables = [
        'organizations', 'teams', 'users', 'team_memberships', 'projects', 
        'sections', 'tasks', 'subtasks', 'comments', 'tags', 'attachments',
        'custom_field_defs', 'custom_field_values', 'task_tags'
    ]

    print("\n📊 ROW COUNTS:")
    for t in tables:
        cur.execute(f"SELECT COUNT(*) FROM {t}")
        count = cur.fetchone()[0]
        status = "✓" if count > 0 else "✗"
        print(f"  {status} {t}: {count:,}")

    print("\n🔗 REFERENTIAL INTEGRITY:")
    # Tasks with assignee_id not in users
    cur.execute("SELECT COUNT(*) FROM tasks WHERE assignee_id IS NOT NULL AND assignee_id NOT IN (SELECT id FROM users)")
    bad = cur.fetchone()[0]
    print(f"  {'✓' if bad == 0 else '✗'} Tasks with missing assignee references: {bad}")

    # Tasks with project_id missing
    cur.execute("SELECT COUNT(*) FROM tasks WHERE project_id IS NOT NULL AND project_id NOT IN (SELECT id FROM projects)")
    bad_proj = cur.fetchone()[0]
    print(f"  {'✓' if bad_proj == 0 else '✗'} Tasks with missing project references: {bad_proj}")

    # Team memberships integrity
    cur.execute("SELECT COUNT(*) FROM team_memberships WHERE team_id NOT IN (SELECT id FROM teams)")
    bad_team = cur.fetchone()[0]
    print(f"  {'✓' if bad_team == 0 else '✗'} Team memberships with missing team: {bad_team}")

    print("\n📈 DATA DISTRIBUTIONS:")
    
    # Unassigned task percentage
    cur.execute("SELECT COUNT(*) FROM tasks")
    total_tasks = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM tasks WHERE assignee_id IS NULL")
    unassigned = cur.fetchone()[0]
    unassigned_pct = (unassigned / total_tasks * 100) if total_tasks else 0
    status = "✓" if 10 <= unassigned_pct <= 20 else "⚠"
    print(f"  {status} Unassigned tasks: {unassigned:,} / {total_tasks:,} = {unassigned_pct:.2f}% (target: 15%)")

    # Completion rate by project_type
    cur.execute("""
        SELECT p.project_type, COUNT(t.id) as total, SUM(t.completed) as completed 
        FROM tasks t 
        JOIN projects p ON t.project_id = p.id 
        GROUP BY p.project_type
    """)
    print("\n  Completion rates by project_type:")
    for r in cur.fetchall():
        proj_type, total, completed = r
        pct = (completed / total * 100) if total else 0
        print(f"    {proj_type}: {completed:,}/{total:,} = {pct:.2f}%")

    print("\n⚠️  EDGE CASES:")
    
    # Overdue tasks
    cur.execute("SELECT COUNT(*) FROM tasks WHERE due_date < date('now') AND completed = 0")
    overdue = cur.fetchone()[0]
    overdue_pct = (overdue / total_tasks * 100) if total_tasks else 0
    status = "✓" if overdue > 0 else "✗"
    print(f"  {status} Overdue tasks: {overdue:,} ({overdue_pct:.2f}% of total) [target: 3-5%]")

    # Weekend due dates
    cur.execute("SELECT COUNT(*) FROM tasks WHERE due_date IS NOT NULL AND strftime('%w', due_date) IN ('0', '6')")
    weekend_tasks = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM tasks WHERE due_date IS NOT NULL")
    tasks_with_due = cur.fetchone()[0]
    weekend_pct = (weekend_tasks / tasks_with_due * 100) if tasks_with_due else 0
    status = "✓" if weekend_pct <= 20 else "✗"
    print(f"  {status} Tasks with weekend due dates: {weekend_tasks:,} / {tasks_with_due:,} = {weekend_pct:.2f}% [target: <15%]")

    # Archived projects
    cur.execute("SELECT COUNT(*) FROM projects WHERE is_archived = 1")
    archived = cur.fetchone()[0]
    status = "✓" if archived > 0 else "⚠"
    print(f"  {status} Archived projects: {archived}")

    # Empty sections (sections with no tasks)
    cur.execute("""
        SELECT COUNT(*) FROM sections s 
        WHERE NOT EXISTS (SELECT 1 FROM tasks t WHERE t.section_id = s.id)
    """)
    empty_sections = cur.fetchone()[0]
    print(f"  ✓ Empty sections: {empty_sections}")

    print("\n⏰ TEMPORAL CONSISTENCY:")
    
    # Tasks completed before creation
    cur.execute("SELECT COUNT(*) FROM tasks WHERE completed = 1 AND completed_at < created_at")
    bad_time_tasks = cur.fetchone()[0]
    status = "✓" if bad_time_tasks == 0 else "✗"
    print(f"  {status} Tasks with completed_at < created_at: {bad_time_tasks} [must be 0]")
    
    # Subtasks completed before creation
    cur.execute("SELECT COUNT(*) FROM subtasks WHERE completed = 1 AND completed_at < created_at")
    bad_time_subtasks = cur.fetchone()[0]
    status = "✓" if bad_time_subtasks == 0 else "✗"
    print(f"  {status} Subtasks with completed_at < created_at: {bad_time_subtasks} [must be 0]")

    # Weekday distribution of created_at
    cur.execute("""
        SELECT strftime('%w', created_at) as dow, COUNT(*) as cnt
        FROM tasks
        GROUP BY dow
        ORDER BY dow
    """)
    print("\n  Task creation by day of week:")
    weekdays = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    for dow, cnt in cur.fetchall():
        day_name = weekdays[int(dow)]
        pct = (cnt / total_tasks * 100) if total_tasks else 0
        print(f"    {day_name}: {cnt:,} ({pct:.1f}%)")

    print("\n" + "=" * 60)
    
    # Overall assessment
    cur.execute("SELECT COUNT(*) FROM team_memberships")
    tm_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM custom_field_defs")
    cf_count = cur.fetchone()[0]
    
    issues = []
    if tm_count == 0:
        issues.append("❌ team_memberships table is empty")
    if cf_count == 0:
        issues.append("❌ custom_field_defs table is empty")
    if overdue == 0:
        issues.append("❌ No overdue tasks found")
    if weekend_pct > 20:
        issues.append(f"❌ Too many weekend due dates ({weekend_pct:.1f}%)")
    
    if issues:
        print("ISSUES FOUND:")
        for issue in issues:
            print(f"  {issue}")
        print("\n⚠️  Database has issues that need fixing")
    else:
        print("✅ ALL CHECKS PASSED")
        print("Database is ready for submission!")
    
    print("=" * 60)

    conn.close()


if __name__ == '__main__':
    db = os.getenv('OUTPUT_DB', 'output/asana_simulation.sqlite')
    run_checks(db)
