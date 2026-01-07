from __future__ import annotations
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional, Tuple
import random

from src import config

PRIORITIES = ["low", "medium", "high", "critical"]

ENGINEERING_TITLES = [
    "Fix {topic} bug in {component}",
    "Implement {topic} feature flag",
    "Refactor {component} module",
    "Add logging for {topic}",
    "Write unit tests for {component}",
    "Investigate intermittent failure in {component}",
    "Optimize query performance for {topic}",
]
MARKETING_TITLES = [
    "Draft copy for {topic} landing page",
    "Publish blog post: {topic}",
    "Design creatives for {topic} campaign",
    "Schedule social posts for {topic}",
    "Finalize webinar deck: {topic}",
]
OPS_TITLES = [
    "Review vendor contract for {topic}",
    "Prepare onboarding checklist updates",
    "Update SOP for {topic}",
    "Coordinate stakeholder review for {topic}",
    "Create internal FAQ: {topic}",
]
PRODUCT_TITLES = [
    "Write PRD for {topic}",
    "Triage feedback related to {topic}",
    "Define success metrics for {topic}",
    "Review roadmap dependencies for {topic}",
]
DESIGN_TITLES = [
    "Create wireframes for {topic}",
    "Run usability test for {topic}",
    "Update design system component: {topic}",
    "Accessibility review for {topic}",
]

TOPICS = [
    "Billing", "SSO", "Search", "Notifications", "Mobile", "Analytics", "CI/CD",
    "Observability", "Onboarding", "Pricing", "Referral", "CRM", "Security", "Incident",
]
COMPONENTS = ["API", "Backend", "Frontend", "Mobile App", "Data Pipeline", "Auth Service", "Payments Service"]


def _rand_datetime(start: datetime, end: datetime) -> datetime:
    delta = end - start
    seconds = int(delta.total_seconds())
    return start + timedelta(seconds=random.randint(0, max(seconds, 1)))


def _weekend_adjust(d: date) -> date:
    # Push weekend due dates to Monday (simple realism)
    if d.weekday() == 5:   # Sat
        return d + timedelta(days=2)
    if d.weekday() == 6:   # Sun
        return d + timedelta(days=1)
    return d


def _pick_status() -> str:
    r = random.random()
    cum = 0.0
    for k, p in config.TASK_STATUS_PROBS.items():
        cum += p
        if r <= cum:
            return k
    return "completed"


def _make_title(project_name: str) -> str:
    p = project_name.lower()
    topic = random.choice(TOPICS)
    component = random.choice(COMPONENTS)

    # Choose templates based on project keywords
    if "campaign" in p or "content" in p or "webinar" in p or "seo" in p or "comms" in p:
        tpl = random.choice(MARKETING_TITLES)
    elif "design" in p or "ux" in p or "accessibility" in p or "prototype" in p:
        tpl = random.choice(DESIGN_TITLES)
    elif "prd" in p or "roadmap" in p or "discovery" in p or "feedback" in p:
        tpl = random.choice(PRODUCT_TITLES)
    elif "vendor" in p or "onboarding" in p or "compliance" in p or "okr" in p or "internal tools" in p:
        tpl = random.choice(OPS_TITLES)
    else:
        tpl = random.choice(ENGINEERING_TITLES)

    return tpl.format(topic=topic, component=component)


def _make_description() -> str:
    # short, realistic-ish descriptions; keep many empty to reflect real usage
    if random.random() < 0.55:
        return ""
    lines = [
        "Context: align with current sprint goals.",
        "Acceptance criteria: documented and reviewed.",
        "Dependencies: confirm with stakeholders if needed.",
        "Notes: update status regularly.",
    ]
    k = random.randint(1, 3)
    return " ".join(random.sample(lines, k))


def generate_tasks_and_subtasks(
    conn,
    projects: List[Dict],
    sections: List[Dict],
    users: List[Dict],
) -> Tuple[List[Dict], List[Dict]]:
    """
    Generates parent tasks and subtasks with:
    - temporal consistency
    - section consistency
    - optional due dates
    - unassigned tasks fraction
    """
    cur = conn.cursor()

    # Pre-index sections per project
    sections_by_project: Dict[int, List[Dict]] = {}
    for s in sections:
        sections_by_project.setdefault(s["project_id"], []).append(s)
    for pid in sections_by_project:
        sections_by_project[pid].sort(key=lambda x: x["position"])

    user_ids = [u["id"] for u in users if u["is_active"] == 1]

    parent_rows = []
    parent_meta = []  # store for generating subtasks later (id will be fetched)

    # --- Parent tasks ---
    for p in projects:
        # non-uniform project sizes: some small, some large
        base = config.AVG_TASKS_PER_PROJECT
        multiplier = random.choice([0.25, 0.5, 1.0, 1.5, 2.5])
        n_tasks = max(8, int(random.gauss(base * multiplier, base * 0.35)))

        proj_sections = sections_by_project.get(p["id"], [])
        for _ in range(n_tasks):
            created_at = _rand_datetime(config.START_DATE, config.END_DATE)

            # Assign section sometimes; allow NULL section for backlog-like tasks
            section_id = None
            if proj_sections and random.random() < 0.92:
                section_id = random.choice(proj_sections)["id"]

            # Assignee logic (some unassigned)
            assignee_id = None
            if user_ids and random.random() > config.UNASSIGNED_TASK_PROB:
                assignee_id = random.choice(user_ids)

            status = _pick_status()

            # Due date logic
            due_date = None
            if random.random() < config.TASK_HAS_DUE_DATE_PROB:
                if random.random() < config.OVERDUE_TASK_PROB:
                    # overdue: due before END_DATE
                    dd = (config.END_DATE - timedelta(days=random.randint(1, 30))).date()
                else:
                    dd = (created_at + timedelta(days=random.randint(1, 45))).date()
                due_date = _weekend_adjust(dd).isoformat()

            completed_at = None
            if status == "completed":
                completed_at_dt = created_at + timedelta(days=random.randint(0, 20), hours=random.randint(0, 12))
                # ensure completed_at not after END_DATE
                if completed_at_dt > config.END_DATE:
                    completed_at_dt = config.END_DATE
                completed_at = completed_at_dt.isoformat(timespec="seconds")

            title = _make_title(p["name"])
            description = _make_description()
            priority = random.choices(PRIORITIES, weights=[0.25, 0.45, 0.22, 0.08])[0]

            parent_rows.append((
                p["id"], section_id, None, assignee_id,
                title, description,
                status, priority, due_date,
                created_at.isoformat(timespec="seconds"),
                completed_at
            ))

            parent_meta.append({"project_id": p["id"], "section_id": section_id, "created_at": created_at})

    cur.executemany(
        """
        INSERT INTO tasks (
            project_id, section_id, parent_task_id, assignee_id,
            title, description,
            status, priority, due_date,
            created_at, completed_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        parent_rows
    )
    conn.commit()

    # Fetch parent task IDs back
    cur.execute("SELECT id, project_id, section_id, created_at FROM tasks WHERE parent_task_id IS NULL ORDER BY id")
    parents = [{"id": r[0], "project_id": r[1], "section_id": r[2], "created_at": r[3]} for r in cur.fetchall()]

    # --- Subtasks ---
    sub_rows = []
    for parent in parents:
        if random.random() > config.SUBTASK_RATIO:
            continue
        n_sub = max(1, int(random.gauss(config.AVG_SUBTASKS_PER_TASK, 1.0)))
        n_sub = min(n_sub, 8)

        parent_created = datetime.fromisoformat(parent["created_at"])
        for _ in range(n_sub):
            created_at = parent_created + timedelta(hours=random.randint(0, 72))
            # Clamp: never allow task timestamps after END_DATE
            if created_at > config.END_DATE:
                created_at = config.END_DATE


            assignee_id = None
            if user_ids and random.random() > (config.UNASSIGNED_TASK_PROB + 0.05):
                assignee_id = random.choice(user_ids)

            status = _pick_status()
            due_date = None
            if random.random() < 0.60:
                dd = (created_at + timedelta(days=random.randint(1, 21))).date()
                due_date = _weekend_adjust(dd).isoformat()

            completed_at = None
            if status == "completed":
                completed_at_dt = created_at + timedelta(days=random.randint(0, 10))
                if completed_at_dt > config.END_DATE:
                    completed_at_dt = config.END_DATE
                if completed_at_dt < created_at:
                    completed_at_dt = created_at
                completed_at = completed_at_dt.isoformat(timespec="seconds")


            title = "Subtask: " + _make_title("subtask")
            description = _make_description()
            priority = random.choices(PRIORITIES, weights=[0.30, 0.50, 0.16, 0.04])[0]

            sub_rows.append((
                parent["project_id"], parent["section_id"], parent["id"], assignee_id,
                title, description,
                status, priority, due_date,
                created_at.isoformat(timespec="seconds"),
                completed_at
            ))

    cur.executemany(
        """
        INSERT INTO tasks (
            project_id, section_id, parent_task_id, assignee_id,
            title, description,
            status, priority, due_date,
            created_at, completed_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        sub_rows
    )
    conn.commit()

    # Return both parent and total tasks counts for logging
    cur.execute("SELECT COUNT(*) FROM tasks")
    total_tasks = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM tasks WHERE parent_task_id IS NULL")
    parent_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM tasks WHERE parent_task_id IS NOT NULL")
    sub_count = cur.fetchone()[0]

    return (
        [{"count_parent": parent_count, "count_total": total_tasks}],
        [{"count_sub": sub_count}],
    )
