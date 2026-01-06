#!/usr/bin/env python3
"""Orchestrator for generating the Asana simulation SQLite DB."""
import os
import sqlite3
from pathlib import Path
from dotenv import load_dotenv
import random
import sys

load_dotenv()

# Ensure the workspace root is on sys.path so `from src...` imports work when running this script
BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))
OUTPUT_DB = Path(os.getenv("OUTPUT_DB", BASE_DIR / "output" / "asana_simulation.sqlite"))
SCHEMA_SQL = BASE_DIR / "schema.sql"

NUMBER_OF_USERS = int(os.getenv("NUMBER_OF_USERS", "7000"))
SEED = int(os.getenv("SEED", "42"))

random.seed(SEED)

from src.generators import users as users_gen
from src.generators import projects as projects_gen
from src.generators import tasks as tasks_gen
from src.generators import custom_fields as custom_fields_gen


def ensure_dirs():
    out_dir = OUTPUT_DB.parent
    out_dir.mkdir(parents=True, exist_ok=True)


def run_schema(conn: sqlite3.Connection):
    sql = SCHEMA_SQL.read_text()
    conn.executescript(sql)
    conn.commit()


def main():
    print("=" * 60)
    print("ASANA SIMULATION DATA GENERATOR")
    print("=" * 60)
    print(f"Target: {NUMBER_OF_USERS} users, SEED={SEED}")
    print()
    
    ensure_dirs()
    if OUTPUT_DB.exists():
        print(f"Removing existing DB at {OUTPUT_DB}")
        OUTPUT_DB.unlink()

    conn = sqlite3.connect(str(OUTPUT_DB))
    conn.row_factory = sqlite3.Row

    print("\n[1/6] Applying schema...")
    run_schema(conn)
    print("  ✓ Schema applied")

    print("\n[2/6] Generating organizations and users...")
    org_id = users_gen.generate_organization_and_users(conn, number_of_users=NUMBER_OF_USERS)

    print("\n[3/6] Generating teams and projects...")
    projects_info = projects_gen.generate_teams_and_projects(conn, organization_id=org_id)

    print("\n[4/6] Populating team memberships...")
    users_gen.populate_team_memberships(conn)

    print("\n[5/6] Generating tasks and related entities...")
    tasks_gen.generate_tasks_for_projects(conn, projects_info=projects_info)

    print("\n[6/6] Generating custom fields...")
    custom_fields_gen.generate_custom_fields_for_projects(conn, projects_info)

    print("\n" + "=" * 60)
    print("✓ GENERATION COMPLETE")
    print("=" * 60)
    print(f"Database written to: {OUTPUT_DB}")
    print(f"Size: {OUTPUT_DB.stat().st_size / 1024 / 1024:.2f} MB")
    print()
    
    # Quick stats
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM users")
    print(f"  Users: {cur.fetchone()[0]:,}")
    cur.execute("SELECT COUNT(*) FROM teams")
    print(f"  Teams: {cur.fetchone()[0]:,}")
    cur.execute("SELECT COUNT(*) FROM team_memberships")
    print(f"  Team Memberships: {cur.fetchone()[0]:,}")
    cur.execute("SELECT COUNT(*) FROM projects")
    print(f"  Projects: {cur.fetchone()[0]:,}")
    cur.execute("SELECT COUNT(*) FROM tasks")
    print(f"  Tasks: {cur.fetchone()[0]:,}")
    cur.execute("SELECT COUNT(*) FROM custom_field_defs")
    print(f"  Custom Field Definitions: {cur.fetchone()[0]:,}")
    cur.execute("SELECT COUNT(*) FROM custom_field_values")
    print(f"  Custom Field Values: {cur.fetchone()[0]:,}")
    print()
    
    conn.close()


if __name__ == "__main__":
    main()
