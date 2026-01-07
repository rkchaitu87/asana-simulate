def run_validations(conn) -> None:
    cur = conn.cursor()

    # 1) completed_at must not be before created_at
    cur.execute("""
        SELECT COUNT(*)
        FROM tasks
        WHERE completed_at IS NOT NULL
          AND completed_at < created_at
    """)
    bad_completion = cur.fetchone()[0]

    # 2) subtasks must have parent_task_id
    cur.execute("SELECT COUNT(*) FROM tasks WHERE parent_task_id IS NOT NULL AND parent_task_id = id")
    bad_self_parent = cur.fetchone()[0]

    # 3) section must belong to same project (when section_id is set)
    cur.execute("""
        SELECT COUNT(*)
        FROM tasks t
        JOIN sections s ON t.section_id = s.id
        WHERE t.section_id IS NOT NULL
          AND t.project_id != s.project_id
    """)
    bad_section = cur.fetchone()[0]

    print("✅ VALIDATION SUMMARY")
    print(f" - completed_at before created_at: {bad_completion}")
    print(f" - self-referential parent_task_id: {bad_self_parent}")
    print(f" - task.project_id != section.project_id: {bad_section}")

    if bad_completion or bad_self_parent or bad_section:
        raise ValueError("Validation failed. Fix generation logic.")
