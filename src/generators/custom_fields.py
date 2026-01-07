from typing import Dict, List
import random

FIELD_TEMPLATES = [
    ("Effort", "number"),
    ("Risk", "enum"),
    ("Sprint", "text"),
    ("Priority (Project)", "enum"),
    ("Owner Group", "text"),
]

RISK_LEVELS = ["low", "medium", "high"]
PRIORITY_LEVELS = ["P0", "P1", "P2", "P3"]

def generate_custom_field_definitions(conn, projects: List[Dict], fields_per_project: int) -> List[Dict]:
    cur = conn.cursor()
    rows = []

    for p in projects:
        chosen = random.sample(FIELD_TEMPLATES, k=min(fields_per_project, len(FIELD_TEMPLATES)))
        for name, ftype in chosen:
            rows.append((p["id"], name, ftype))

    cur.executemany(
        "INSERT INTO custom_field_definitions (project_id, name, field_type) VALUES (?, ?, ?)",
        rows
    )
    conn.commit()

    cur.execute("SELECT id, project_id, name, field_type FROM custom_field_definitions ORDER BY id")
    return [{"id": r[0], "project_id": r[1], "name": r[2], "field_type": r[3]} for r in cur.fetchall()]

def generate_custom_field_values(conn, field_defs: List[Dict]) -> int:
    """
    Assign custom field values to tasks within the same project.
    Not all tasks have all fields -> realistic sparsity.
    """
    cur = conn.cursor()

    # Index fields by project
    fields_by_project = {}
    for f in field_defs:
        fields_by_project.setdefault(f["project_id"], []).append(f)

    # Pull tasks
    cur.execute("SELECT id, project_id FROM tasks ORDER BY id")
    tasks = cur.fetchall()

    rows = []
    for task_id, project_id in tasks:
        proj_fields = fields_by_project.get(project_id, [])
        for f in proj_fields:
            # Sparsity: only some tasks get a value for each field
            if random.random() < 0.55:
                continue

            if f["field_type"] == "number":
                value = str(random.choice([1,2,3,5,8,13]))
            elif f["name"].lower().startswith("risk"):
                value = random.choice(RISK_LEVELS)
            elif f["name"].lower().startswith("priority"):
                value = random.choice(PRIORITY_LEVELS)
            else:
                value = random.choice(["alpha", "beta", "gamma", "delta"])

            rows.append((task_id, f["id"], value))

    cur.executemany(
        "INSERT OR IGNORE INTO custom_field_values (task_id, field_id, value) VALUES (?, ?, ?)",
        rows
    )
    conn.commit()
    return len(rows)
