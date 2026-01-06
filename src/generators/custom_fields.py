# Generate custom field definitions and values.
import sqlite3
import uuid
import random
import json


def _gid():
    return str(uuid.uuid4())


# Custom field templates by project type
ENGINEERING_CUSTOM_FIELDS = [
    ("Priority", "enum", ["Low", "Medium", "High", "Critical"]),
    ("Story Points", "number", None),
    ("Sprint", "text", None),
    ("Component", "enum", ["Frontend", "Backend", "Database", "API", "DevOps"]),
    ("Bug Severity", "enum", ["Minor", "Major", "Critical", "Blocker"]),
]

MARKETING_CUSTOM_FIELDS = [
    ("Campaign Status", "enum", ["Planning", "In Progress", "Review", "Live", "Complete"]),
    ("Target Audience", "text", None),
    ("Budget", "number", None),
    ("Channel", "enum", ["Email", "Social", "Web", "Events", "Paid Ads"]),
]

OPS_CUSTOM_FIELDS = [
    ("Priority", "enum", ["Low", "Medium", "High", "Urgent"]),
    ("Department", "enum", ["HR", "Finance", "IT", "Legal", "Operations"]),
    ("Status", "enum", ["Not Started", "In Progress", "Blocked", "Complete"]),
]


def generate_custom_fields_for_projects(conn: sqlite3.Connection, projects_info: list):
    # Generate custom field definitions and populate values for tasks.
    cur = conn.cursor()
    
    print("  Generating custom fields...")
    field_count = 0
    value_count = 0
    
    for proj in projects_info:
        proj_id = proj["project_id"]
        proj_type = proj.get("project_type", "engineering")
        
        # Select appropriate custom field templates
        if proj_type == "engineering":
            templates = ENGINEERING_CUSTOM_FIELDS
        elif proj_type == "marketing":
            templates = MARKETING_CUSTOM_FIELDS
        else:
            templates = OPS_CUSTOM_FIELDS
        
        # Create 2-4 custom fields per project
        n_fields = random.randint(2, min(4, len(templates)))
        selected_templates = random.sample(templates, n_fields)
        
        project_field_ids = []
        
        for field_name, field_type, options in selected_templates:
            f_gid = _gid()
            options_json = json.dumps(options) if options else None
            
            cur.execute(
                "INSERT INTO custom_field_defs (gid, project_id, name, field_type, options) VALUES (?, ?, ?, ?, ?)",
                (f_gid, proj_id, field_name, field_type, options_json)
            )
            field_def_id = cur.lastrowid
            project_field_ids.append((field_def_id, field_type, options))
            field_count += 1
        
        # Get all tasks for this project
        cur.execute("SELECT id FROM tasks WHERE project_id = ?", (proj_id,))
        task_ids = [r[0] for r in cur.fetchall()]
        
        # Populate custom field values for 60-80% of tasks
        for task_id in task_ids:
            if random.random() < 0.7:  # 70% of tasks get custom field values
                # Fill 1-3 fields per task
                fields_to_fill = random.sample(project_field_ids, 
                                             min(random.randint(1, 3), len(project_field_ids)))
                
                for field_def_id, field_type, options in fields_to_fill:
                    # Generate appropriate value based on field type
                    if field_type == "enum" and options:
                        value = random.choice(options)
                    elif field_type == "number":
                        value = str(random.choice([1, 2, 3, 5, 8, 13]))
                    elif field_type == "text":
                        value = f"Sprint {random.randint(1, 20)}" if "Sprint" in str(field_def_id) else "Notes"
                    else:
                        value = "N/A"
                    
                    cur.execute(
                        "INSERT INTO custom_field_values (custom_field_def_id, task_id, value) VALUES (?, ?, ?)",
                        (field_def_id, task_id, value)
                    )
                    value_count += 1
    
    conn.commit()
    print(f"  ✓ Created {field_count} custom field definitions and {value_count} values")
