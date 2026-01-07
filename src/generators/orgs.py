from datetime import datetime
from typing import Dict, List
import random

def generate_organizations(conn, org_names: List[str]) -> List[Dict]:
    now = datetime.now().isoformat(timespec="seconds")

    rows = []
    for name in org_names:
        rows.append({"name": name, "created_at": now})

    cur = conn.cursor()
    cur.executemany(
        "INSERT INTO organizations (name, created_at) VALUES (?, ?)",
        [(r["name"], r["created_at"]) for r in rows],
    )
    conn.commit()

    # Fetch IDs back (SQLite autoincrement by row insertion order)
    cur.execute("SELECT id, name FROM organizations ORDER BY id")
    orgs = [{"id": oid, "name": oname} for (oid, oname) in cur.fetchall()]
    return orgs


def generate_teams(conn, organization_id: int, team_names: List[str]) -> List[Dict]:
    now = datetime.now().isoformat(timespec="seconds")

    rows = [{"organization_id": organization_id, "name": n, "created_at": now} for n in team_names]

    cur = conn.cursor()
    cur.executemany(
        "INSERT INTO teams (organization_id, name, created_at) VALUES (?, ?, ?)",
        [(r["organization_id"], r["name"], r["created_at"]) for r in rows],
    )
    conn.commit()

    cur.execute(
        "SELECT id, name FROM teams WHERE organization_id = ? ORDER BY id",
        (organization_id,),
    )
    teams = [{"id": tid, "name": tname} for (tid, tname) in cur.fetchall()]
    return teams


def default_enterprise_team_names(n: int) -> List[str]:
    """
    Produces realistic team names across Eng/Product/Design/Marketing/Ops.
    n is approximate; we will slice to exact.
    """
    base = [
        # Engineering
        "Platform Engineering",
        "Infrastructure & SRE",
        "Backend Engineering",
        "Frontend Engineering",
        "Mobile Engineering",
        "Data Engineering",
        "ML Platform",
        "Security Engineering",
        "QA & Release",
        # Product/Design
        "Product Management",
        "UX Research",
        "Product Design",
        # Marketing
        "Growth Marketing",
        "Content Marketing",
        "Performance Marketing",
        "Field Marketing",
        "Brand & Communications",
        # Business/Ops
        "Sales Operations",
        "Revenue Operations",
        "Customer Success Ops",
        "People Operations",
        "Finance Operations",
        "IT Operations",
        "Procurement",
        "Legal Ops",
        "Program Management Office",
    ]

    # Add some realistic variants if we need more
    variants = []
    for suffix in ["(APAC)", "(EMEA)", "(US)", " - India", " - Enterprise", " - SMB"]:
        variants.extend([f"{t} {suffix}" for t in base[:8]])

    all_names = base + variants

    # Ensure uniqueness and exact length
    uniq = []
    seen = set()
    for name in all_names:
        if name not in seen:
            uniq.append(name)
            seen.add(name)
    return uniq[:n]
