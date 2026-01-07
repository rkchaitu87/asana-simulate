from datetime import datetime, timedelta
from typing import Dict, List
import random

from src import config

COMMENT_TEMPLATES = [
    "Can you confirm the latest status on this?",
    "Blocked on dependency—will update once resolved.",
    "Shared an update in the channel; please review.",
    "This is ready for review when you get a chance.",
    "Adding notes from today’s sync.",
    "I’ll take this and post progress by EOD.",
    "Need clarification on scope/acceptance criteria.",
    "Looks good—minor changes pending.",
]

def generate_comments(conn, users: List[Dict]) -> int:
    """
    Generate comments for a subset of tasks.
    Many tasks have 0 comments; some have multiple.
    """
    cur = conn.cursor()

    # active users only for comment authors
    user_ids = [u["id"] for u in users if u["is_active"] == 1]
    if not user_ids:
        return 0

    # Pull task ids and created_at for temporal consistency
    cur.execute("SELECT id, created_at FROM tasks ORDER BY id")
    tasks = cur.fetchall()

    rows = []
    for task_id, created_at_str in tasks:
        # Probability of having any comment
        if random.random() < 0.60:
            continue

        n = max(1, int(random.gauss(config.AVG_COMMENTS_PER_TASK, 1.2)))
        n = min(n, 8)

        task_created = datetime.fromisoformat(created_at_str)
        for _ in range(n):
            author_id = random.choice(user_ids)
            content = random.choice(COMMENT_TEMPLATES)

            # comment time after task creation
            created_at = task_created + timedelta(hours=random.randint(1, 240))
            if created_at > config.END_DATE:
                created_at = config.END_DATE

            rows.append((task_id, author_id, content, created_at.isoformat(timespec="seconds")))

    cur.executemany(
        "INSERT INTO comments (task_id, user_id, content, created_at) VALUES (?, ?, ?, ?)",
        rows,
    )
    conn.commit()
    return len(rows)
