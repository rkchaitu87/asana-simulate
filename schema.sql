-- ============================
-- ORGANIZATION
-- ============================
CREATE TABLE organizations (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    created_at DATETIME NOT NULL
);

-- ============================
-- TEAMS
-- ============================
CREATE TABLE teams (
    id INTEGER PRIMARY KEY,
    organization_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    created_at DATETIME NOT NULL,
    FOREIGN KEY (organization_id) REFERENCES organizations(id)
);

-- ============================
-- USERS
-- ============================
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    organization_id INTEGER NOT NULL,
    full_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    role TEXT,
    is_active BOOLEAN NOT NULL,
    created_at DATETIME NOT NULL,
    FOREIGN KEY (organization_id) REFERENCES organizations(id)
);

-- ============================
-- TEAM MEMBERSHIPS
-- ============================
CREATE TABLE team_memberships (
    team_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    joined_at DATETIME NOT NULL,
    PRIMARY KEY (team_id, user_id),
    FOREIGN KEY (team_id) REFERENCES teams(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- ============================
-- PROJECTS
-- ============================
CREATE TABLE projects (
    id INTEGER PRIMARY KEY,
    team_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at DATETIME NOT NULL,
    archived_at DATETIME,
    FOREIGN KEY (team_id) REFERENCES teams(id)
);

-- ============================
-- SECTIONS
-- ============================
CREATE TABLE sections (
    id INTEGER PRIMARY KEY,
    project_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    position INTEGER NOT NULL,
    FOREIGN KEY (project_id) REFERENCES projects(id)
);

-- ============================
-- TASKS (PARENT + SUBTASKS)
-- ============================
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY,
    project_id INTEGER NOT NULL,
    section_id INTEGER,
    parent_task_id INTEGER,
    assignee_id INTEGER,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT NOT NULL,
    priority TEXT,
    due_date DATE,
    created_at DATETIME NOT NULL,
    completed_at DATETIME,
    FOREIGN KEY (project_id) REFERENCES projects(id),
    FOREIGN KEY (section_id) REFERENCES sections(id),
    FOREIGN KEY (parent_task_id) REFERENCES tasks(id),
    FOREIGN KEY (assignee_id) REFERENCES users(id)
);

-- ============================
-- COMMENTS
-- ============================
CREATE TABLE comments (
    id INTEGER PRIMARY KEY,
    task_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    created_at DATETIME NOT NULL,
    FOREIGN KEY (task_id) REFERENCES tasks(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- ============================
-- TAGS
-- ============================
CREATE TABLE tags (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

-- ============================
-- TASK-TAG MAPPING
-- ============================
CREATE TABLE task_tags (
    task_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    PRIMARY KEY (task_id, tag_id),
    FOREIGN KEY (task_id) REFERENCES tasks(id),
    FOREIGN KEY (tag_id) REFERENCES tags(id)
);

-- ============================
-- CUSTOM FIELD DEFINITIONS
-- ============================
CREATE TABLE custom_field_definitions (
    id INTEGER PRIMARY KEY,
    project_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    field_type TEXT NOT NULL,
    FOREIGN KEY (project_id) REFERENCES projects(id)
);

-- ============================
-- CUSTOM FIELD VALUES
-- ============================
CREATE TABLE custom_field_values (
    task_id INTEGER NOT NULL,
    field_id INTEGER NOT NULL,
    value TEXT,
    PRIMARY KEY (task_id, field_id),
    FOREIGN KEY (task_id) REFERENCES tasks(id),
    FOREIGN KEY (field_id) REFERENCES custom_field_definitions(id)
);
