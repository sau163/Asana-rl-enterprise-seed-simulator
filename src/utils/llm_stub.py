#LLM integration via OpenRouter API.
import os
import requests
from typing import Optional
import random

def generate_text(prompt: str, temperature: float = 0.7, max_tokens: int = 200, model: str = "openai/gpt-3.5-turbo") -> str:
    
    api_key = os.getenv("OPENROUTER_API_KEY")
    
    # If no API key, return fallback (template-based)
    if not api_key:
        return _fallback_generation(prompt, max_tokens)
    
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "HTTP-Referer": "https://github.com/yourusername/asana-rl-seed-data",  # Optional
                "X-Title": "Asana RL Seed Data Generator",  # Optional
            },
            json={
                "model": model,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": temperature,
                "max_tokens": max_tokens
            },
            timeout=30  # 30 second timeout
        )
        
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"].strip()
        else:
            print(f"Warning: OpenRouter API error {response.status_code}, using fallback generation")
            return _fallback_generation(prompt, max_tokens)
            
    except Exception as e:
        print(f"Warning: LLM call failed ({str(e)}), using fallback generation")
        return _fallback_generation(prompt, max_tokens)


def _fallback_generation(prompt: str, max_tokens: int) -> str:
 
    prompt_lower = prompt.lower()
    
    # Task name generation fallback
    if "task title" in prompt_lower or "task name" in prompt_lower:
        if "engineering" in prompt_lower:
            components = ["API", "Backend", "Frontend", "Database", "Auth"]
            actions = ["Implement", "Fix", "Refactor", "Add", "Update"]
            details = ["feature", "bug", "integration", "endpoint", "validation"]
            return f"{random.choice(components)} - {random.choice(actions)} {random.choice(details)}"
        elif "marketing" in prompt_lower:
            campaigns = ["Product Launch", "Brand Campaign", "Lead Generation"]
            deliverables = ["landing page", "email campaign", "social media assets"]
            return f"{random.choice(campaigns)} - Create {random.choice(deliverables)}"
        else:
            return "Update process and documentation"
    
    # Description generation fallback
    elif "description" in prompt_lower:
        return "This task requires attention and should be completed according to project requirements."
    
    # Comment generation fallback
    elif "comment" in prompt_lower:
        comments = [
            "Looks good, approved!",
            "Can you provide more details?",
            "Working on this now.",
            "Blocked by dependency.",
            "Ready for review."
        ]
        return random.choice(comments)
    
    # Generic fallback
    return (prompt[:max_tokens] + "...") if len(prompt) > max_tokens else prompt
