from src.db import connect, exec_schema
from src.generators.orgs import generate_organizations, generate_teams, default_enterprise_team_names
from src import config
from pathlib import Path
from src.generators.users import generate_users
from src.generators.memberships import generate_team_memberships
from src.generators.projects import generate_projects, generate_sections
from src.generators.tasks import generate_tasks_and_subtasks
from src.generators.comments import generate_comments
from src.generators.tags import generate_tags, generate_task_tags
from src.generators.custom_fields import generate_custom_field_definitions, generate_custom_field_values
from src.validate import run_validations


DB_PATH = "output/asana_simulation.sqlite"

def main() -> None:
        # If DB exists from a previous run, delete it so schema can be recreated cleanly
    db_file = Path(DB_PATH)
    if db_file.exists():
        db_file.unlink()
    conn = connect(DB_PATH)
    exec_schema(conn, "schema.sql")

    # 1) Organization (single enterprise workspace)
    orgs = generate_organizations(conn, ["ScalarDemo Enterprise Workspace"])
    org_id = orgs[0]["id"]

    # 2) Teams
    team_names = default_enterprise_team_names(config.NUM_TEAMS)
    teams = generate_teams(conn, org_id, team_names)

    # 3) Users
    users = generate_users(conn, org_id, config.NUM_USERS)

    # 4) Memberships
    attempted_memberships = generate_team_memberships(conn, teams, users)
    # 5) Projects
    projects = generate_projects(conn, teams, config.NUM_PROJECTS)
    # 6) Sections
    sections = generate_sections(conn, projects)
    # 7) Tasks + Subtasks
    parent_info, sub_info = generate_tasks_and_subtasks(conn, projects, sections, users)
    # 8) Comments
    comment_rows = generate_comments(conn, users)
    # 9) Tags
    tag_ids = generate_tags(conn)
    # 10) Task-Tag mapping
    task_tag_rows = generate_task_tags(conn, tag_ids)
    # 11) Custom field definitions
    field_defs = generate_custom_field_definitions(conn, projects, config.CUSTOM_FIELDS_PER_PROJECT)
    # 12) Custom field values
    cf_value_rows = generate_custom_field_values(conn, field_defs)





    # Quick summary
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM organizations")
    org_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM teams")
    team_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM users")
    user_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM team_memberships")
    membership_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM projects")
    project_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM sections")
    section_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM tasks")
    task_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM tasks WHERE parent_task_id IS NULL")
    parent_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM tasks WHERE parent_task_id IS NOT NULL")
    sub_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM comments")
    comment_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM tags")
    tag_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM task_tags")
    task_tag_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM custom_field_definitions")
    cfd_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM custom_field_values")
    cfv_count = cur.fetchone()[0]
    run_validations(conn)









    conn.close()
    print(f"✅ DB created at: {DB_PATH}")
    print(f"✅ organizations: {org_count}")
    print(f"✅ teams: {team_count}")
    print(f"✅ users: {user_count}")
    print(f"✅ team_memberships: {membership_count} (attempted inserts: {attempted_memberships})")
    print(f"Sample teams: {[t['name'] for t in teams[:5]]}")
    print(f"Sample user: {users[0]}")
    print(f"✅ projects: {project_count}")
    print(f"✅ sections: {section_count}")
    print(f"Sample project: {projects[0]['name']}")
    print(f"✅ tasks total: {task_count} (parents: {parent_count}, subtasks: {sub_count})")
    print(f"✅ comments: {comment_count} (inserted rows: {comment_rows})")
    print(f"✅ tags: {tag_count}")
    print(f"✅ task_tags: {task_tag_count} (inserted rows: {task_tag_rows})")
    print(f"✅ custom_field_definitions: {cfd_count}")
    print(f"✅ custom_field_values: {cfv_count} (inserted rows: {cf_value_rows})")


if __name__ == "__main__":
    main()
