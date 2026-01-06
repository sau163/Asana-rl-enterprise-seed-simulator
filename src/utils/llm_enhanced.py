# LLM-enhanced content generation with fallback to templates.
import os
import random
from src.utils.llm_stub import generate_text
from src.utils.task_naming import generate_task_name as template_task_name

def should_use_llm() -> bool:
    # Determine if LLM should be used based on configuration.
    llm_percentage = int(os.getenv("LLM_PERCENTAGE", "0"))
    return random.random() * 100 < llm_percentage

def generate_task_name_llm(project_type: str, project_name: str = "", component: str = "") -> str:
    """
    Generate task name using LLM if configured, otherwise use templates.
    
    Args:
        project_type: Type of project (engineering, marketing, ops)
        project_name: Optional project name for context
        component: Optional component name for engineering tasks
    
    Returns:
        Task name string
    """
    if not should_use_llm():
        # Use template-based generation (fast, deterministic)
        return template_task_name(project_type)
    
    # Use LLM generation
    if project_type == "engineering":
        prompt = f"""Generate a concise Asana-style task title for an engineering team.
Project: {project_name or 'Platform Development'}
Component: {component or 'Backend'}

Examples:
- "Auth API - Fix token refresh bug"
- "Frontend UI - Add pagination to user list"
- "Database Layer - Optimize query performance"

Generate ONE task title (3-8 words), format: "[Component] - [Action] [Detail]"
Task title:"""
    
    elif project_type == "marketing":
        prompt = f"""Generate a concise Asana-style task title for a marketing team.
Project: {project_name or 'Q1 Campaign'}

Examples:
- "Product Launch - Create landing page"
- "Brand Awareness - Write blog posts"
- "Lead Generation - Design email campaign"

Generate ONE task title (3-8 words), format: "[Campaign] - Create [Deliverable]"
Task title:"""
    
    else:  # ops
        prompt = f"""Generate a concise Asana-style task title for an operations team.
Project: {project_name or 'Process Improvement'}

Examples:
- "Update onboarding process"
- "Review vendor contracts"
- "Setup new workspace"

Generate ONE task title (3-6 words)
Task title:"""
    
    model = os.getenv("LLM_MODEL", "openai/gpt-3.5-turbo")
    temperature = random.uniform(0.7, 1.0)  # Random temperature for variety
    
    result = generate_text(prompt, temperature=temperature, max_tokens=50, model=model)
    
    # Clean up result (remove quotes, extra whitespace)
    result = result.strip().strip('"').strip("'").strip()
    
    # Fallback to template if result is empty or too long
    if not result or len(result) > 100:
        return template_task_name(project_type)
    
    return result


def generate_task_description_llm(task_name: str, project_type: str) -> str:
    """
    Generate task description using LLM if configured.
    
    Args:
        task_name: The task name
        project_type: Type of project
    
    Returns:
        Task description (can be empty, short, or detailed)
    """
    # Description variety: 20% empty, 50% short, 30% detailed
    rand = random.random()
    
    if rand < 0.2:
        return ""  # Empty description
    
    if not should_use_llm():
        # Template-based fallback
        from faker import Faker
        fake = Faker()
        Faker.seed(random.randint(0, 10000))
        
        if rand < 0.7:  # Short description
            return fake.text(max_nb_chars=150)
        else:  # Detailed description
            desc = fake.paragraph(nb_sentences=4)
            desc += "\n\nAcceptance Criteria:\n"
            desc += "\n".join([f"- {fake.sentence()}" for _ in range(random.randint(2, 4))])
            return desc
    
    # LLM-based generation
    if rand < 0.7:  # Short description
        prompt = f"""Write a brief 1-2 sentence task description for: "{task_name}"
Keep it concise and professional.
Description:"""
        max_tokens = 100
    else:  # Detailed description
        prompt = f"""Write a detailed task description for: "{task_name}"

Include:
1. Brief overview (1-2 sentences)
2. Acceptance criteria (2-4 bullet points)

Format:
[Overview paragraph]

Acceptance Criteria:
- [Criterion 1]
- [Criterion 2]
- [Criterion 3]

Description:"""
        max_tokens = 250
    
    model = os.getenv("LLM_MODEL", "openai/gpt-3.5-turbo")
    result = generate_text(prompt, temperature=0.8, max_tokens=max_tokens, model=model)
    
    return result.strip()


def generate_comment_llm(task_name: str) -> str:
    """
    Generate a comment using LLM if configured.
    
    Args:
        task_name: The task name for context
    
    Returns:
        Comment text
    """
    if not should_use_llm():
        # Template-based fallback
        comments = [
            "Looks good, approved!",
            "Can you provide more details on this?",
            "Working on this now.",
            "This is blocked by another task.",
            "Ready for review.",
            "LGTM, merging.",
            "Let's discuss this in the standup.",
            "Added some notes in the description.",
            "Can we prioritize this?",
            "Moving to next sprint."
        ]
        return random.choice(comments)
    
    prompt = f"""Write a brief realistic comment a team member might leave on task: "{task_name}"

Examples:
- "Looks good, approved!"
- "Can you clarify the requirements?"
- "Working on this now"
- "This is blocked by X"
- "Ready for review"

Generate ONE short comment (1-2 sentences):
Comment:"""
    
    model = os.getenv("LLM_MODEL", "openai/gpt-3.5-turbo")
    result = generate_text(prompt, temperature=0.9, max_tokens=50, model=model)
    
    return result.strip().strip('"').strip("'").strip()
