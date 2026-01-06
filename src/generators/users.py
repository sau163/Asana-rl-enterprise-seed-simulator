# Generate organizations and users for the simulation.
import sqlite3
import uuid
from faker import Faker
from datetime import datetime, timedelta
import random

fake = Faker()


def _gid():
    return str(uuid.uuid4())


def generate_organization_and_users(conn: sqlite3.Connection, number_of_users: int = 7000):
    # Generate organization and all users.
    cur = conn.cursor()
    org_gid = _gid()
    org_name = fake.company() + " Inc"
    domain = org_name.lower().replace(" ", "") + ".com"
    created_at = datetime.utcnow().isoformat()

    cur.execute(
        "INSERT INTO organizations (gid, name, domain, created_at) VALUES (?, ?, ?, ?)",
        (org_gid, org_name, domain, created_at),
    )
    org_id = cur.lastrowid

    # create users
    roles = ["Engineer", "Product", "Designer", "Marketing", "Sales", "Ops", "HR"]
    now = datetime.fromisoformat(created_at)
    print(f"  Generating {number_of_users} users...")
    for i in range(number_of_users):
        u_gid = _gid()
        name = fake.name()
        email = f"{name.lower().replace(' ', '.')}.{i}@{domain}"
        role = random.choices(roles, weights=[0.35, 0.12, 0.06, 0.12, 0.08, 0.15, 0.12])[0]
        created = (now - timedelta(days=random.randint(0, 365))).isoformat()
        cur.execute(
            "INSERT INTO users (gid, organization_id, full_name, email, role, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (u_gid, org_id, name, email, role, created),
        )
        
        if (i + 1) % 1000 == 0:
            print(f"    Created {i + 1}/{number_of_users} users")

    conn.commit()
    print(f"  ✓ Created {number_of_users} users")
    return org_id


def populate_team_memberships(conn: sqlite3.Connection):
    """Populate team_memberships table by assigning users to teams."""
    cur = conn.cursor()
    
    # Get all teams
    cur.execute("SELECT id FROM teams")
    team_ids = [r[0] for r in cur.fetchall()]
    
    # Get all users grouped by role
    cur.execute("SELECT id, role FROM users")
    users_by_role = {}
    for user_id, role in cur.fetchall():
        users_by_role.setdefault(role, []).append(user_id)
    
    print(f"  Assigning users to {len(team_ids)} teams...")
    membership_count = 0
    
    for team_id in team_ids:
        # Each team gets 5-20 members
        team_size = random.randint(5, 20)
        
        # Assign members with role affinity (engineering teams get more engineers, etc.)
        members = []
        
        # Determine team type based on random selection
        team_type = random.choices(
            ["engineering", "product", "marketing", "ops"],
            weights=[0.5, 0.15, 0.2, 0.15]
        )[0]
        
        # Build member list based on team type
        if team_type == "engineering" and "Engineer" in users_by_role:
            # 70% engineers, 30% others
            eng_count = int(team_size * 0.7)
            members.extend(random.sample(users_by_role["Engineer"], 
                                       min(eng_count, len(users_by_role["Engineer"]))))
            remaining = team_size - len(members)
            if remaining > 0:
                other_users = [u for role, users in users_by_role.items() 
                             if role != "Engineer" for u in users]
                members.extend(random.sample(other_users, min(remaining, len(other_users))))
        else:
            # Mix of roles
            all_users = [u for users in users_by_role.values() for u in users]
            members = random.sample(all_users, min(team_size, len(all_users)))
        
        # Insert memberships
        for user_id in members:
            role_in_team = random.choice(["member", "member", "member", "lead"])
            joined = (datetime.utcnow() - timedelta(days=random.randint(30, 730))).isoformat()
            try:
                cur.execute(
                    "INSERT INTO team_memberships (team_id, user_id, role, joined_at) VALUES (?, ?, ?, ?)",
                    (team_id, user_id, role_in_team, joined)
                )
                membership_count += 1
            except sqlite3.IntegrityError:
                # Skip duplicates (unique constraint)
                pass
    
    conn.commit()
    print(f"  ✓ Created {membership_count} team memberships")

