PRAGMA foreign_keys = ON;

-- Organizations / Workspaces
CREATE TABLE organizations (
    id INTEGER PRIMARY KEY,
    gid TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    domain TEXT,
    created_at TEXT
);

-- Teams
CREATE TABLE teams (
    id INTEGER PRIMARY KEY,
    gid TEXT UNIQUE NOT NULL,
    organization_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT,
    FOREIGN KEY(organization_id) REFERENCES organizations(id) ON DELETE CASCADE
);

-- Users
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    gid TEXT UNIQUE NOT NULL,
    organization_id INTEGER NOT NULL,
    full_name TEXT NOT NULL,
    email TEXT NOT NULL,
    role TEXT,
    created_at TEXT,
    is_active INTEGER DEFAULT 1,
    FOREIGN KEY(organization_id) REFERENCES organizations(id) ON DELETE CASCADE
);

-- Team memberships
CREATE TABLE team_memberships (
    id INTEGER PRIMARY KEY,
    team_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    role TEXT,
    joined_at TEXT,
    FOREIGN KEY(team_id) REFERENCES teams(id) ON DELETE CASCADE,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Projects
CREATE TABLE projects (
    id INTEGER PRIMARY KEY,
    gid TEXT UNIQUE NOT NULL,
    team_id INTEGER,
    organization_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT,
    is_archived INTEGER DEFAULT 0,
    project_type TEXT,
    FOREIGN KEY(team_id) REFERENCES teams(id) ON DELETE SET NULL,
    FOREIGN KEY(organization_id) REFERENCES organizations(id) ON DELETE CASCADE
);

-- Sections
CREATE TABLE sections (
    id INTEGER PRIMARY KEY,
    gid TEXT UNIQUE NOT NULL,
    project_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    position INTEGER,
    FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
);

-- Tasks
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY,
    gid TEXT UNIQUE NOT NULL,
    project_id INTEGER,
    section_id INTEGER,
    name TEXT NOT NULL,
    description TEXT,
    assignee_id INTEGER,
    created_at TEXT,
    due_date TEXT,
    completed INTEGER DEFAULT 0,
    completed_at TEXT,
    priority TEXT,
    effort INTEGER,
    FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE SET NULL,
    FOREIGN KEY(section_id) REFERENCES sections(id) ON DELETE SET NULL,
    FOREIGN KEY(assignee_id) REFERENCES users(id) ON DELETE SET NULL
);

-- Subtasks
CREATE TABLE subtasks (
    id INTEGER PRIMARY KEY,
    gid TEXT UNIQUE NOT NULL,
    parent_task_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    assignee_id INTEGER,
    created_at TEXT,
    due_date TEXT,
    completed INTEGER DEFAULT 0,
    completed_at TEXT,
    FOREIGN KEY(parent_task_id) REFERENCES tasks(id) ON DELETE CASCADE,
    FOREIGN KEY(assignee_id) REFERENCES users(id) ON DELETE SET NULL
);

-- Comments / Stories
CREATE TABLE comments (
    id INTEGER PRIMARY KEY,
    gid TEXT UNIQUE NOT NULL,
    task_id INTEGER NOT NULL,
    author_id INTEGER,
    text TEXT,
    created_at TEXT,
    FOREIGN KEY(task_id) REFERENCES tasks(id) ON DELETE CASCADE,
    FOREIGN KEY(author_id) REFERENCES users(id) ON DELETE SET NULL
);

-- Custom field definitions (project-scoped)
CREATE TABLE custom_field_defs (
    id INTEGER PRIMARY KEY,
    gid TEXT UNIQUE NOT NULL,
    project_id INTEGER,
    name TEXT NOT NULL,
    field_type TEXT NOT NULL,
    options TEXT,
    FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
);

-- Custom field values (task-scoped)
CREATE TABLE custom_field_values (
    id INTEGER PRIMARY KEY,
    custom_field_def_id INTEGER NOT NULL,
    task_id INTEGER NOT NULL,
    value TEXT,
    FOREIGN KEY(custom_field_def_id) REFERENCES custom_field_defs(id) ON DELETE CASCADE,
    FOREIGN KEY(task_id) REFERENCES tasks(id) ON DELETE CASCADE
);

-- Tags
CREATE TABLE tags (
    id INTEGER PRIMARY KEY,
    gid TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    color TEXT
);

-- Task-Tag association
CREATE TABLE task_tags (
    id INTEGER PRIMARY KEY,
    task_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    FOREIGN KEY(task_id) REFERENCES tasks(id) ON DELETE CASCADE,
    FOREIGN KEY(tag_id) REFERENCES tags(id) ON DELETE CASCADE
);

-- Attachments (record metadata only)
CREATE TABLE attachments (
    id INTEGER PRIMARY KEY,
    gid TEXT UNIQUE NOT NULL,
    task_id INTEGER NOT NULL,
    filename TEXT,
    url TEXT,
    uploaded_by INTEGER,
    created_at TEXT,
    FOREIGN KEY(task_id) REFERENCES tasks(id) ON DELETE CASCADE,
    FOREIGN KEY(uploaded_by) REFERENCES users(id) ON DELETE SET NULL
);

-- Performance indexes
CREATE INDEX idx_users_org ON users(organization_id);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_teams_org ON teams(organization_id);
CREATE INDEX idx_team_memberships_team ON team_memberships(team_id);
CREATE INDEX idx_team_memberships_user ON team_memberships(user_id);
CREATE INDEX idx_projects_team ON projects(team_id);
CREATE INDEX idx_projects_org ON projects(organization_id);
CREATE INDEX idx_projects_type ON projects(project_type);
CREATE INDEX idx_sections_project ON sections(project_id);
CREATE INDEX idx_tasks_project ON tasks(project_id);
CREATE INDEX idx_tasks_section ON tasks(section_id);
CREATE INDEX idx_tasks_assignee ON tasks(assignee_id);
CREATE INDEX idx_tasks_due_date ON tasks(due_date);
CREATE INDEX idx_tasks_completed ON tasks(completed);
CREATE INDEX idx_subtasks_parent ON subtasks(parent_task_id);
CREATE INDEX idx_subtasks_assignee ON subtasks(assignee_id);
CREATE INDEX idx_comments_task ON comments(task_id);
CREATE INDEX idx_comments_author ON comments(author_id);
CREATE INDEX idx_custom_field_defs_project ON custom_field_defs(project_id);
CREATE INDEX idx_custom_field_values_task ON custom_field_values(task_id);
CREATE INDEX idx_custom_field_values_def ON custom_field_values(custom_field_def_id);
CREATE INDEX idx_task_tags_task ON task_tags(task_id);
CREATE INDEX idx_task_tags_tag ON task_tags(tag_id);
CREATE INDEX idx_attachments_task ON attachments(task_id);
CREATE INDEX idx_attachments_uploader ON attachments(uploaded_by);

-- Unique constraints for junction tables
CREATE UNIQUE INDEX idx_task_tags_unique ON task_tags(task_id, tag_id);
CREATE UNIQUE INDEX idx_team_memberships_unique ON team_memberships(team_id, user_id);
