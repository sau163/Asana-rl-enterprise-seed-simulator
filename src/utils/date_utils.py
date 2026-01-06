# Date and temporal utilities for realistic timestamp generation.
import random
from datetime import datetime, timedelta


def snap_to_weekday(date):
    #Snap a date to the nearest weekday (Mon-Fri).
    weekday = date.weekday()
    if weekday == 5:  # Saturday
        date = date + timedelta(days=2)
    elif weekday == 6:  # Sunday
        date = date + timedelta(days=1)
    return date


def generate_due_date(created_at_dt, project_type="engineering", allow_overdue=False):
    """Generate realistic due date with distributions and weekend avoidance.
    
    Distribution:
    - 25% within 7 days (urgent)
    - 40% within 30 days (current sprint)
    - 20% 30-90 days (backlog)
    - 10% no due date
    - 5% overdue (if allow_overdue=True)
    """
    roll = random.random()
    
    if roll < 0.10:
        return None  # No due date
    
    now = datetime.utcnow()
    
    if allow_overdue and roll < 0.20:  # Higher chance for overdue: 5-10%
        days_overdue = random.randint(1, 60)
        due = now - timedelta(days=days_overdue)
    elif roll < 0.45:  # 25% within 7 days
        due = now + timedelta(days=random.randint(1, 7))
    elif roll < 0.85:  # 40% within 30 days
        due = now + timedelta(days=random.randint(8, 30))
    else:  # 15% 30-90 days
        due = now + timedelta(days=random.randint(31, 120))
    
    # 85% chance to snap to weekday
    if random.random() < 0.85:
        due = snap_to_weekday(due)
    
    # Sprint boundary clustering for engineering projects
    if project_type == "engineering" and random.random() < 0.3:
        # Snap to nearest sprint boundary (every 14 days)
        days_diff = (due - created_at_dt).days
        sprint_boundary = ((days_diff // 14) + 1) * 14
        due = created_at_dt + timedelta(days=sprint_boundary)
        due = snap_to_weekday(due)
    
    return due.date().isoformat()


def generate_created_at(base_date, days_ago_max=365):
  
    days_ago = random.randint(0, days_ago_max)
    created = base_date - timedelta(days=days_ago)
    
    # Adjust to prefer weekdays
    weekday = created.weekday()
    if weekday >= 5:  # Weekend
        # 70% chance to move to Friday
        if random.random() < 0.7:
            if weekday == 5:  # Saturday
                created = created - timedelta(days=1)
            else:  # Sunday
                created = created - timedelta(days=2)
    
    # Add time component with work hours bias (8am-6pm)
    hour = int(random.triangular(8, 18, 14))  # Peak at 2pm
    minute = random.randint(0, 59)
    created = created.replace(hour=hour, minute=minute, second=0, microsecond=0)
    
    return created.isoformat()


def generate_completed_at(created_at_str, now_str=None):
    created_dt = datetime.fromisoformat(created_at_str)
    now_dt = datetime.fromisoformat(now_str) if now_str else datetime.utcnow()
    
    # Log-normal approximation: most tasks 1-14 days, some longer
    completion_days = random.choices(
        [1, 2, 3, 5, 7, 10, 14, 21, 30],
        weights=[0.05, 0.15, 0.20, 0.20, 0.15, 0.10, 0.08, 0.05, 0.02]
    )[0]
    
    completed_dt = created_dt + timedelta(days=completion_days, hours=random.randint(1, 23))
    
    # Ensure not in future
    if completed_dt > now_dt:
        # Complete sometime between creation and now
        max_days = max(1, (now_dt - created_dt).days)
        actual_days = min(completion_days, max_days)
        completed_dt = created_dt + timedelta(days=actual_days, hours=random.randint(1, 23))
    
    return completed_dt.isoformat()
