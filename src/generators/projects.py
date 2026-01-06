# Generate teams and projects and sections.
import sqlite3
import uuid
from faker import Faker
import random
from datetime import datetime, timedelta

fake = Faker()


def _gid():
    return str(uuid.uuid4())


def generate_teams_and_projects(conn: sqlite3.Connection, organization_id: int):
    cur = conn.cursor()
    # Create a distribution of team sizes and counts appropriate for a large org
    num_teams = 200  # reasonable for large org
    projects_info = []
    print(f"  Generating {num_teams} teams and projects...")
    
    for t in range(num_teams):
        t_gid = _gid()
        team_name = f"{fake.bs().title()} Team"
        desc = fake.sentence(nb_words=8)
        created = datetime.utcnow().isoformat()
        cur.execute(
            "INSERT INTO teams (gid, organization_id, name, description, created_at) VALUES (?, ?, ?, ?, ?)",
            (t_gid, organization_id, team_name, desc, created),
        )
        team_id = cur.lastrowid

        # Projects per team: 2-8
        n_projects = random.randint(2, 8)
        for p in range(n_projects):
            p_gid = _gid()
            project_type = random.choices(["engineering", "marketing", "ops"], [0.6, 0.25, 0.15])[0]
            project_name = _project_name_for_type(project_type)
            project_desc = fake.paragraph(nb_sentences=2)
            created = (datetime.utcnow() - timedelta(days=random.randint(0, 365))).isoformat()
            
            # 2-3% of projects are archived (edge case)
            is_archived = 1 if random.random() < 0.025 else 0
            
            cur.execute(
                "INSERT INTO projects (gid, team_id, organization_id, name, description, created_at, project_type, is_archived) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (p_gid, team_id, organization_id, project_name, project_desc, created, project_type, is_archived),
            )
            project_id = cur.lastrowid

            # Create standard sections
            sections = ["Backlog", "To Do", "In Progress", "Review", "Done"]
            for idx, s in enumerate(sections):
                s_gid = _gid()
                cur.execute(
                    "INSERT INTO sections (gid, project_id, name, position) VALUES (?, ?, ?, ?)",
                    (s_gid, project_id, s, idx),
                )

            projects_info.append({
                "project_id": project_id,
                "project_type": project_type,
                "is_archived": is_archived
            })
        
        if (t + 1) % 50 == 0:
            print(f"    Created {t + 1}/{num_teams} teams")

    conn.commit()
    print(f"  ✓ Created {num_teams} teams and {len(projects_info)} projects")
    return projects_info


def _project_name_for_type(project_type: str) -> str:
    if project_type == "engineering":
        return f"{fake.word().title()} Platform Revamp"
    if project_type == "marketing":
        return f"{fake.catch_phrase()} Campaign"
    return f"{fake.word().title()} Ops Initiative"
