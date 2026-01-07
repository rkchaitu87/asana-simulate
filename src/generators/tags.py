from typing import List
import random

DEFAULT_TAGS = [
    "blocked", "urgent", "customer-request", "tech-debt", "bug",
    "performance", "security", "documentation", "design", "release",
    "follow-up", "needs-review", "nice-to-have"
]

def generate_tags(conn, tags: List[str] = None) -> List[int]:
    if tags is None:
        tags = DEFAULT_TAGS

    cur = conn.cursor()
    cur.executemany("INSERT INTO tags (name) VALUES (?)", [(t,) for t in tags])
    conn.commit()

    cur.execute("SELECT id FROM tags ORDER BY id")
    return [r[0] for r in cur.fetchall()]

def generate_task_tags(conn, tag_ids: List[int], max_tags_per_task: int = 3) -> int:
    cur = conn.cursor()
    cur.execute("SELECT id FROM tasks ORDER BY id")
    task_ids = [r[0] for r in cur.fetchall()]

    rows = []
    for tid in task_ids:
        # Most tasks have 0–1 tags; some have multiple
        if random.random() < 0.55:
            continue
        k = random.choice([1, 1, 1, 2, 2, 3])
        k = min(k, max_tags_per_task)
        chosen = random.sample(tag_ids, k)
        for tag_id in chosen:
            rows.append((tid, tag_id))

    cur.executemany("INSERT OR IGNORE INTO task_tags (task_id, tag_id) VALUES (?, ?)", rows)
    conn.commit()
    return len(rows)
