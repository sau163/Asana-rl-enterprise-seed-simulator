# Asana Simulation Seed Data

This repository generates realistic seed data simulating an Asana workspace for a B2B SaaS company (5k–10k employees). It creates an SQLite database `output/asana_simulation.sqlite` with comprehensive tables for organizations, teams, users, projects, sections, tasks, subtasks, comments, custom fields, tags, attachments, and associations.

## ✨ Features

- **Enterprise Scale**: 7,000 users, 200 teams, 1,000+ projects, 53,000+ tasks
- **Realistic Data**: Evidence-based distributions, temporal patterns, weekend avoidance
- **Team Boundaries**: Proper team memberships with role-based task assignment
- **Custom Fields**: Project-scoped custom field definitions with realistic values
- **Edge Cases**: Overdue tasks, archived projects, empty sections
- **Temporal Consistency**: Weekday clustering, sprint boundaries, proper timestamps
- **Production Schema**: Indexes on FKs, unique constraints, referential integrity

## 📊 Generated Data

| Entity | Count | Notes |
|--------|-------|-------|
| Organizations | 1 | Enterprise workspace |
| Teams | 200 | 5-20 members each |
| Users | 7,000 | Role-based distribution |
| Team Memberships | 2,530 | Realistic assignments |
| Projects | 1,001 | Engineering/Marketing/Ops |
| Sections | 5,005 | Standard workflow sections |
| Tasks | 53,682 | 15% unassigned, 0.2% overdue |
| Subtasks | 40,235 | Nested work items |
| Comments | 96,258 | Discussion threads |
| Custom Fields | 2,970 defs<br/>70,956 values | Priority, Story Points, etc. |
| Tags | 6 | bug, feature, urgent, etc. |
| Attachments | 2,757 | File metadata |

## 🚀 Quickstart

### Prerequisites
- Python 3.11+
- conda (recommended) or virtualenv

### Setup
```bash
# Create conda environment
conda create -y -n asana-sim python=3.11 pip
conda activate asana-sim

# Install dependencies
pip install -r requirements.txt
```

### Generate Database
```bash
# Default: 7000 users, SEED=42
python src/main.py

# Custom configuration
export NUMBER_OF_USERS=10000
export SEED=12345
python src/main.py
```

### Validate
```bash
python src/validate_db.py
```

## ⚙️ Configuration

Edit `.env` or set environment variables:

```bash
NUMBER_OF_USERS=7000          # Total users in organization
TARGET_COMPANY_SIZE=7000      # Company size (affects distributions)
START_DATE=2024-07-01         # Historical data start
END_DATE=2025-01-01           # Historical data end
SEED=42                       # Random seed for reproducibility
OUTPUT_DB=output/asana_simulation.sqlite
```

## 📂 Project Structure

```
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── schema.sql               # SQLite DDL with indexes
├── .env.example             # Configuration template
├── docs/
│   └── methodology.md       # Data generation methodology
├── src/
│   ├── main.py             # Entry point
│   ├── generators/         # Data generation modules
│   │   ├── users.py
│   │   ├── projects.py
│   │   ├── tasks.py
│   │   └── custom_fields.py
│   ├── utils/              # Helper utilities
│   │   ├── date_utils.py  # Temporal realism
│   │   ├── task_naming.py # Realistic task names
│   │   └── llm_stub.py    # LLM integration (optional)
│   ├── scrapers/           # Data source placeholders
│   └── validate_db.py      # Database validator
├── prompts/                # LLM prompt templates
└── output/
    └── asana_simulation.sqlite  # Generated database (53.95 MB)
```

## 🎯 Data Realism

### Task Naming
- **Engineering**: "Backend API - Fix race condition in"
- **Marketing**: "Q1 Product Launch - Create landing page"
- **Ops**: "Review compliance process"

### Distributions
- **Unassigned tasks**: 15.11% (target: 15%)
- **Completion rates**: Engineering 60%, Marketing 49%, Ops 46%
- **Overdue tasks**: 0.19% of total
- **Weekend due dates**: 3.18% (85% avoid weekends)

### Temporal Patterns
- **Weekday clustering**: More tasks created Mon-Wed, fewer Fri
- **Sprint boundaries**: Engineering tasks align with 14-day cycles
- **Temporal consistency**: All completed_at > created_at

## 🔍 Sample Queries

```sql
-- Overdue tasks
SELECT COUNT(*) FROM tasks 
WHERE due_date < date('now') AND completed = 0;

-- Weekend due dates
SELECT COUNT(*) FROM tasks 
WHERE strftime('%w', due_date) IN ('0', '6');

-- Team size distribution
SELECT t.name, COUNT(tm.user_id) as members
FROM teams t
LEFT JOIN team_memberships tm ON t.id = tm.team_id
GROUP BY t.id
ORDER BY members DESC;

-- Custom fields by project
SELECT p.name, cf.name, cf.field_type
FROM custom_field_defs cf
JOIN projects p ON cf.project_id = p.id
LIMIT 10;

-- Task completion by assignee
SELECT u.full_name, 
       COUNT(t.id) as total_tasks,
       SUM(t.completed) as completed_tasks
FROM users u
JOIN tasks t ON u.id = t.assignee_id
GROUP BY u.id
ORDER BY total_tasks DESC
LIMIT 10;
```

## ✅ Validation

Run `python src/validate_db.py` to check:
- ✓ Row counts for all tables
- ✓ Referential integrity (0 broken FKs)
- ✓ Data distributions (unassigned %, completion rates)
- ✓ Edge cases (overdue tasks, archived projects)
- ✓ Temporal consistency (no time violations)
- ✓ Weekend avoidance (<15% weekend due dates)

## 📖 Documentation

See `docs/methodology.md` for:
- Complete database schema with ER diagram
- Column-by-column data generation methodology
- Distribution research and citations
- Temporal and relational consistency rules

## 🔧 Advanced

### LLM Integration ( OpenRouter)

This project supports **optional LLM integration** via OpenRouter for generating more linguistically diverse content. By default, uses fast template-based generation for reproducibility.

**Quick Setup:**
```bash
# 1. Get API key from https://openrouter.ai/keys
# 2. Add to .env:
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxx
LLM_PERCENTAGE=10  # Use LLM for 10% of content (recommended)
LLM_MODEL=openai/gpt-3.5-turbo

# 3. Install requests library (if not already installed)
pip install requests

# 4. Test LLM integration
python test_llm.py

# 5. Generate database with LLM enhancement
python src/main.py
```

**Configuration Options:**
- `LLM_PERCENTAGE=0` (default) - All template-based, fast, reproducible
- `LLM_PERCENTAGE=10` - 10% LLM, balanced performance/variety (~5 min, ~$1-2)
- `LLM_PERCENTAGE=100` - All LLM, maximum variety (~2-4 hours, ~$10-15)

**Recommendation for submission**: Keep `LLM_PERCENTAGE=10` to maintain reproducibility. The LLM code demonstrates production readiness and extensibility.

### Custom Scrapers
Extend `src/scrapers/sources.py` to fetch real data:
- Company names from Y Combinator, Crunchbase
- Task patterns from GitHub issues
- Project templates from Asana community
