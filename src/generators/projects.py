from datetime import datetime
from typing import Dict, List
import random

DEFAULT_SECTIONS = ["Backlog", "In Progress", "In Review", "Blocked", "Done"]

TOPICS = [
    "Billing & Payments", "Auth & SSO", "Search", "Notifications", "Mobile UX",
    "Analytics Pipeline", "CI/CD", "Observability", "Data Warehouse", "API Gateway",
    "Customer Onboarding", "Pricing Page", "Referral Program", "CRM Hygiene",
    "Security Review", "Incident Response", "Performance Baseline",
]
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
RELEASES = ["2026.1", "2026.2", "2026.3", "2026.4"]

def _team_category(team_name: str) -> str:
    t = team_name.lower()
    if "marketing" in t or "brand" in t or "content" in t or "growth" in t:
        return "Marketing"
    if "design" in t or "ux" in t:
        return "Design"
    if "product" in t:
        return "Product"
    if "ops" in t or "operations" in t or "finance" in t or "people" in t or "legal" in t or "procurement" in t:
        return "Ops"
    return "Engineering"

def _project_name(team_name: str) -> str:
    cat = _team_category(team_name)
    topic = random.choice(TOPICS)
    if cat == "Engineering":
        templates = [
            f"Release {random.choice(RELEASES)} Hardening",
            f"Tech Debt Cleanup: {topic}",
            f"Performance Optimization: {topic}",
            f"Service Migration: {topic}",
            f"Security Patch Sprint {random.choice(MONTHS)}",
        ]
    elif cat == "Marketing":
        templates = [
            f"Campaign Launch: {topic}",
            f"{random.choice(MONTHS)} Content Calendar",
            f"Webinar: {topic}",
            f"Product Launch Comms: {topic}",
            f"SEO Refresh: {topic}",
        ]
    elif cat == "Design":
        templates = [
            "Design System Updates",
            f"UX Audit: {topic}",
            f"Prototype: {topic}",
            "Accessibility Improvements",
        ]
    elif cat == "Product":
        templates = [
            f"Product Discovery: {topic}",
            "Roadmap Planning",
            f"PRD: {topic}",
            f"User Feedback Triage {random.choice(MONTHS)}",
        ]
    else:  # Ops
        templates = [
            "Onboarding Process Improvements",
            f"Vendor Renewal: {topic}",
            "Quarterly OKR Planning",
            f"Internal Tools Rollout: {topic}",
            f"Compliance Readiness: {topic}",
        ]

    name = random.choice(templates)
    if random.random() < 0.10:
        name = f"{name} (Phase {random.randint(1,3)})"
    return name

def generate_projects(conn, teams: List[Dict], n_projects: int, archive_prob: float = 0.12) -> List[Dict]:
    now = datetime.now().isoformat(timespec="seconds")
    cur = conn.cursor()

    rows = []
    for _ in range(n_projects):
        team = random.choice(teams)
        name = _project_name(team["name"])
        status = "archived" if random.random() < archive_prob else "active"
        archived_at = now if status == "archived" else None
        created_at = now
        rows.append((team["id"], name, status, created_at, archived_at))

    cur.executemany(
        "INSERT INTO projects (team_id, name, status, created_at, archived_at) VALUES (?, ?, ?, ?, ?)",
        rows,
    )
    conn.commit()

    cur.execute("SELECT id, team_id, name, status FROM projects ORDER BY id")
    return [{"id": r[0], "team_id": r[1], "name": r[2], "status": r[3]} for r in cur.fetchall()]

def generate_sections(conn, projects: List[Dict]) -> List[Dict]:
    cur = conn.cursor()
    rows = []

    for p in projects:
        sections = list(DEFAULT_SECTIONS)

        # small realistic variations
        if random.random() < 0.20 and "In Review" in sections:
            sections.remove("In Review")
        if random.random() < 0.15 and "Ready" not in sections:
            sections.insert(1, "Ready")

        for pos, name in enumerate(sections, start=1):
            rows.append((p["id"], name, pos))

    cur.executemany(
        "INSERT INTO sections (project_id, name, position) VALUES (?, ?, ?)",
        rows,
    )
    conn.commit()

    cur.execute("SELECT id, project_id, name, position FROM sections ORDER BY id")
    return [{"id": r[0], "project_id": r[1], "name": r[2], "position": r[3]} for r in cur.fetchall()]
