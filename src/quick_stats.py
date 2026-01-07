import sqlite3

DB_PATH = "output/asana_simulation.sqlite"

def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    tables = ["organizations","teams","users","team_memberships","projects","sections",
              "tasks","comments","tags","task_tags","custom_field_definitions","custom_field_values"]

    print("=== TABLE COUNTS ===")
    for t in tables:
        cur.execute(f"SELECT COUNT(*) FROM {t}")
        print(f"{t}: {cur.fetchone()[0]}")

    print("\n=== TASK STATUS DISTRIBUTION ===")
    cur.execute("SELECT status, COUNT(*) FROM tasks GROUP BY status ORDER BY COUNT(*) DESC")
    for s,c in cur.fetchall():
        print(s, c)

    print("\n=== UNASSIGNED TASKS % ===")
    cur.execute("SELECT SUM(CASE WHEN assignee_id IS NULL THEN 1 ELSE 0 END)*1.0 / COUNT(*) FROM tasks")
    print(round(cur.fetchone()[0]*100, 2), "%")

    conn.close()

if __name__ == "__main__":
    main()
