from datetime import datetime
from typing import Dict, List
import random

def generate_team_memberships(conn, teams: List[Dict], users: List[Dict]) -> int:
    """
    Realistic membership pattern:
    - Most users belong to 1 primary team
    - ~20% belong to a secondary team (cross-functional work)
    """
    now = datetime.now().isoformat(timespec="seconds")
    cur = conn.cursor()

    team_ids = [t["id"] for t in teams]

    rows = []
    for u in users:
        primary_team = random.choice(team_ids)
        rows.append((primary_team, u["id"], now))

        # 20% users are cross-functional
        if random.random() < 0.20:
            secondary_team = random.choice([tid for tid in team_ids if tid != primary_team])
            rows.append((secondary_team, u["id"], now))

    cur.executemany(
        "INSERT OR IGNORE INTO team_memberships (team_id, user_id, joined_at) VALUES (?, ?, ?)",
        rows,
    )
    conn.commit()
    return len(rows)
