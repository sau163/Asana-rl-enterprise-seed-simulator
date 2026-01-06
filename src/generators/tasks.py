# Generate tasks, subtasks, comments, tags, custom fields, and attachments.
import sqlite3
import uuid
from faker import Faker
import random
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add utils to path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from src.utils.date_utils import generate_due_date, generate_created_at, generate_completed_at
from src.utils.task_naming import generate_task_name

fake = Faker()


def _gid():
    return str(uuid.uuid4())


def generate_tasks_for_projects(conn: sqlite3.Connection, projects_info: list):
    cur = conn.cursor()

    # Load some user ids to assign
    cur.execute("SELECT id FROM users")
    user_ids = [r[0] for r in cur.fetchall()]
    if not user_ids:
        raise RuntimeError("No users found; generate users first.")

    # Get team memberships for realistic assignment
    cur.execute("""
        SELECT tm.team_id, tm.user_id 
        FROM team_memberships tm
    """)
    team_user_map = {}
    for team_id, user_id in cur.fetchall():
        team_user_map.setdefault(team_id, []).append(user_id)

    # Create a modest number of tags
    colors = ["red", "green", "blue", "purple", "orange", "teal"]
    tags = []
    for name in ["bug", "feature", "urgent", "low-effort", "research", "customer"]:
        t_gid = _gid()
        color = random.choice(colors)
        cur.execute("INSERT INTO tags (gid, name, color) VALUES (?, ?, ?)", (t_gid, name, color))
        tags.append(cur.lastrowid)

    print(f"  Generating tasks for {len(projects_info)} projects...")
    base_time = datetime.utcnow()
    task_count = 0
    
    # For each project, create tasks: engineering projects more tasks
    for idx, p in enumerate(projects_info):
        p_id = p["project_id"]
        p_type = p.get("project_type", "engineering")
        is_archived = p.get("is_archived", 0)
        
        # Archived projects have fewer tasks
        if is_archived:
            n_tasks = random.randint(5, 15)
        elif p_type == "engineering":
            n_tasks = random.randint(30, 120)
        elif p_type == "marketing":
            n_tasks = random.randint(10, 40)
        else:
            n_tasks = random.randint(8, 30)

        # Get team_id for this project to assign from team members
        cur.execute("SELECT team_id FROM projects WHERE id = ?", (p_id,))
        result = cur.fetchone()
        team_id = result[0] if result else None
        team_members = team_user_map.get(team_id, user_ids) if team_id else user_ids

        # fetch sections for project
        cur.execute("SELECT id FROM sections WHERE project_id=?", (p_id,))
        sections = [r[0] for r in cur.fetchall()]
        
        for _ in range(n_tasks):
            t_gid = _gid()
            name = generate_task_name(p_type)
            desc = _task_description(p_type)
            
            # Assign to team member (15% unassigned)
            assignee = random.choice(team_members) if random.random() > 0.15 else None
            
            # Use realistic created_at with weekday clustering
            created_at = generate_created_at(base_time, days_ago_max=365)
            created_dt = datetime.fromisoformat(created_at)
            
            # Generate due date with weekend avoidance and overdue possibility
            allow_overdue = random.random() < 0.05  # 5% chance of overdue
            due_date = generate_due_date(created_dt, p_type, allow_overdue=allow_overdue)

            completed = 0
            completed_at = None
            # completion probability varies by project type
            comp_prob = 0.6 if p_type == "engineering" else (0.5 if p_type == "marketing" else 0.45)
            if random.random() < comp_prob:
                completed = 1
                completed_at = generate_completed_at(created_at, base_time.isoformat())

            section_id = random.choice(sections) if sections else None
            priority = random.choices(["low", "medium", "high", "urgent"], [0.4, 0.4, 0.15, 0.05])[0]
            effort = random.choice([1, 2, 3, 5, 8])

            cur.execute(
                "INSERT INTO tasks (gid, project_id, section_id, name, description, assignee_id, created_at, due_date, completed, completed_at, priority, effort) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (t_gid, p_id, section_id, name, desc, assignee, created_at, due_date, completed, completed_at, priority, effort),
            )
            task_id = cur.lastrowid
            task_count += 1

            # probabilistically add subtasks
            if random.random() < 0.25:
                n_sub = random.randint(1, 5)
                for i in range(n_sub):
                    s_gid = _gid()
                    s_name = fake.sentence(nb_words=4)
                    # Subtasks often assigned to same person as parent
                    if assignee and random.random() < 0.6:
                        s_assignee = assignee
                    else:
                        s_assignee = random.choice(team_members) if random.random() > 0.3 else None
                    
                    s_created = (created_dt + timedelta(days=random.randint(0, 5))).isoformat()
                    s_created_dt = datetime.fromisoformat(s_created)
                    s_due = (s_created_dt + timedelta(days=random.randint(3, 30))).date().isoformat()
                    s_completed = 1 if random.random() < 0.5 else 0
                    s_completed_at = generate_completed_at(s_created) if s_completed else None
                    cur.execute(
                        "INSERT INTO subtasks (gid, parent_task_id, name, assignee_id, created_at, due_date, completed, completed_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                        (s_gid, task_id, s_name, s_assignee, s_created, s_due, s_completed, s_completed_at),
                    )

            # comments
            if random.random() < 0.6:
                n_comments = random.randint(1, 5)
                for _ in range(n_comments):
                    c_gid = _gid()
                    author = random.choice(team_members)
                    text = fake.paragraph(nb_sentences=random.randint(1, 3))
                    comment_created = (created_dt + timedelta(days=random.randint(0, 20))).isoformat()
                    cur.execute(
                        "INSERT INTO comments (gid, task_id, author_id, text, created_at) VALUES (?, ?, ?, ?, ?)",
                        (c_gid, task_id, author, text, comment_created),
                    )

            # attach some tags
            if random.random() < 0.5:
                n_tag = random.randint(1, 2)
                chosen = random.sample(tags, n_tag)
                for tid in chosen:
                    try:
                        cur.execute("INSERT INTO task_tags (task_id, tag_id) VALUES (?, ?)", (task_id, tid))
                    except sqlite3.IntegrityError:
                        pass  # Duplicate tag, skip

            # attach an attachment occasionally
            if random.random() < 0.05:
                a_gid = _gid()
                filename = f"{fake.word()}.pdf"
                url = f"https://files.example.com/{filename}"
                uploaded_by = random.choice(team_members)
                attach_created = (created_dt + timedelta(days=random.randint(0, 15))).isoformat()
                cur.execute("INSERT INTO attachments (gid, task_id, filename, url, uploaded_by, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                          (a_gid, task_id, filename, url, uploaded_by, attach_created))
        
        if (idx + 1) % 200 == 0:
            print(f"    Generated tasks for {idx + 1}/{len(projects_info)} projects")

    conn.commit()
    print(f"  ✓ Created {task_count} tasks with subtasks, comments, and attachments")


def _task_name_for_type(project_type: str) -> str:
    if project_type == "engineering":
        return f"{fake.bs().capitalize()} - Fix {fake.word()}"
    if project_type == "marketing":
        return f"{fake.catch_phrase()} - Create assets"
    return f"{fake.word().title()} ops task"


def _task_description(project_type: str) -> str:
    # Mix lengths: 20% empty, 50% short, 30% long
    r = random.random()
    if r < 0.2:
        return ""
    if r < 0.7:
        return fake.sentence(nb_words=random.randint(6,18))
    # long with bullets
    bullets = "\n".join([f"- {fake.sentence(nb_words=6)}" for _ in range(random.randint(2,5))])
    return f"{fake.paragraph(nb_sentences=2)}\n{bullets}"
