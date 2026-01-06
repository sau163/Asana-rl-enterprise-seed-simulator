# Small source lists and scraper placeholders.

from faker import Faker

fake = Faker()


def sample_company_names(n=50):
    return [fake.company() for _ in range(n)]


def sample_project_templates():
    return [
        "Sprint Planning",
        "Quarterly Roadmap",
        "Bug Triage",
        "Product Launch",
        "Marketing Campaign",
        "Customer Onboarding",
    ]
