from datetime import datetime, timedelta
import random

# ==========================
# RANDOM SEED (REPRODUCIBLE)
# ==========================
SEED = 42
random.seed(SEED)

# ==========================
# TIME RANGE
# ==========================
END_DATE = datetime.now()
START_DATE = END_DATE - timedelta(days=180)

# ==========================
# ORGANIZATION SCALE
# ==========================
NUM_ORGANIZATIONS = 1
NUM_TEAMS = 25
NUM_USERS = 1200
NUM_PROJECTS = 400

# ==========================
# TASK SCALE
# ==========================
AVG_TASKS_PER_PROJECT = 120
SUBTASK_RATIO = 0.25   # 25% of tasks have subtasks
AVG_SUBTASKS_PER_TASK = 3

# ==========================
# TASK ASSIGNMENT
# ==========================
UNASSIGNED_TASK_PROB = 0.15

# ==========================
# TASK STATUS DISTRIBUTION
# ==========================
TASK_STATUS_PROBS = {
    "completed": 0.55,
    "in_progress": 0.30,
    "not_started": 0.15
}

# ==========================
# DUE DATES
# ==========================
TASK_HAS_DUE_DATE_PROB = 0.75
OVERDUE_TASK_PROB = 0.20

# ==========================
# COMMENTS
# ==========================
AVG_COMMENTS_PER_TASK = 1.8

# ==========================
# CUSTOM FIELDS
# ==========================
CUSTOM_FIELDS_PER_PROJECT = 3
PROJECT_STATUS_PROBS = {
    "active": 0.85,
    "archived": 0.15
}

# Typical Asana section templates per project type
SECTION_TEMPLATES = {
    "engineering": ["Backlog", "In Progress", "In Review", "Blocked", "Done"],
    "marketing": ["Ideas", "Planned", "In Progress", "Waiting", "Launched"],
    "operations": ["To Do", "Doing", "Waiting", "Done"]
}

# Mix of project categories across the company
PROJECT_TYPE_PROBS = {
    "engineering": 0.55,
    "marketing": 0.25,
    "operations": 0.20
}