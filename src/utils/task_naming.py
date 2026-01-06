#Realistic task name generation based on project types.
import random

# Engineering components and actions
ENGINEERING_COMPONENTS = [
    "Auth API", "User Service", "Payment Gateway", "Database Layer", "Frontend UI",
    "Backend API", "CI/CD Pipeline", "Monitoring", "Analytics", "Search Engine",
    "Cache Layer", "Message Queue", "File Storage", "Email Service", "Notification System",
    "Admin Dashboard", "Mobile App", "Web App", "GraphQL API", "REST API"
]

ENGINEERING_ACTIONS = [
    ("Implement", ["authentication flow", "endpoint", "feature", "integration", "validation"]),
    ("Fix", ["bug in", "memory leak in", "race condition in", "performance issue in", "security vulnerability in"]),
    ("Refactor", ["codebase for", "module to improve", "legacy code in", "architecture of"]),
    ("Optimize", ["query performance in", "loading time for", "memory usage in", "API response for"]),
    ("Add", ["unit tests for", "logging to", "monitoring for", "documentation to", "error handling to"]),
    ("Update", ["dependencies in", "configuration for", "schema for", "documentation for"]),
    ("Debug", ["failing tests in", "timeout issues in", "crash in", "error in"]),
    ("Migrate", ["database schema for", "users to", "service to", "infrastructure to"]),
]

# Marketing campaign types and deliverables
MARKETING_CAMPAIGNS = [
    "Q1 Product Launch", "Summer Sale", "Brand Awareness", "Lead Generation",
    "Customer Retention", "Email Campaign", "Social Media", "Content Marketing",
    "Webinar Series", "Trade Show", "Partner Marketing", "Referral Program"
]

MARKETING_DELIVERABLES = [
    "landing page", "email templates", "social media assets", "blog posts",
    "video content", "infographics", "case studies", "whitepapers",
    "ad creative", "press release", "event materials", "survey"
]

# Operations tasks
OPS_CATEGORIES = [
    "Onboarding", "Compliance", "Security", "Infrastructure", "Vendor Management",
    "Budget Planning", "Team Training", "Process Improvement", "Documentation"
]

OPS_ACTIONS = [
    "Review", "Update", "Implement", "Audit", "Schedule", "Coordinate",
    "Analyze", "Prepare", "Execute", "Monitor"
]


def generate_engineering_task_name():
    """Generate realistic engineering task name."""
    component = random.choice(ENGINEERING_COMPONENTS)
    action, details = random.choice(ENGINEERING_ACTIONS)
    detail = random.choice(details)
    
    # Pattern: [Component] - [Action] [detail]
    return f"{component} - {action} {detail}"


def generate_marketing_task_name():
    """Generate realistic marketing task name."""
    campaign = random.choice(MARKETING_CAMPAIGNS)
    deliverable = random.choice(MARKETING_DELIVERABLES)
    
    # Pattern: [Campaign] - Create [deliverable]
    return f"{campaign} - Create {deliverable}"


def generate_ops_task_name():
    """Generate realistic ops task name."""
    category = random.choice(OPS_CATEGORIES)
    action = random.choice(OPS_ACTIONS)
    
    return f"{action} {category.lower()} process"


def generate_task_name(project_type="engineering"):
    """Generate realistic task name based on project type."""
    if project_type == "engineering":
        return generate_engineering_task_name()
    elif project_type == "marketing":
        return generate_marketing_task_name()
    else:
        return generate_ops_task_name()
