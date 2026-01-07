from datetime import datetime
from typing import Dict, List
import random
from faker import Faker
from src import config

fake = Faker()
fake.seed_instance(config.SEED)

ROLES = [
    "Software Engineer",
    "Senior Software Engineer",
    "Engineering Manager",
    "Product Manager",
    "Product Designer",
    "UX Researcher",
    "QA Engineer",
    "SRE",
    "Data Engineer",
    "ML Engineer",
    "Marketing Manager",
    "Content Strategist",
    "Sales Ops Analyst",
    "Program Manager",
    "Finance Analyst",
    "People Ops Specialist",
    "IT Support Engineer",
]

def generate_users(conn, organization_id: int, n_users: int, email_domain: str = "scalardemo.com") -> List[Dict]:
    """
    Generates realistic enterprise users with roles and unique emails.
    """
    now = datetime.now().isoformat(timespec="seconds")
    rows = []
    used_emails = set()

    for _ in range(n_users):
        name = fake.name()

        # Build a simple email handle from the name
        handle = "".join([c for c in name.lower() if c.isalpha() or c == " "]).strip().replace(" ", ".")
        email = f"{handle}@{email_domain}"

        # Ensure uniqueness
        if email in used_emails:
            email = f"{handle}{random.randint(1, 9999)}@{email_domain}"
        used_emails.add(email)

        role = random.choice(ROLES)

        # Mostly active users, small percentage inactive
        is_active = 1 if random.random() < 0.93 else 0

        rows.append((organization_id, name, email, role, is_active, now))

    cur = conn.cursor()
    cur.executemany(
        """
        INSERT INTO users (organization_id, full_name, email, role, is_active, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        rows,
    )
    conn.commit()

    cur.execute(
        "SELECT id, full_name, email, role, is_active FROM users WHERE organization_id = ? ORDER BY id",
        (organization_id,),
    )
    users = [
        {"id": r[0], "full_name": r[1], "email": r[2], "role": r[3], "is_active": r[4]}
        for r in cur.fetchall()
    ]
    return users
