import sqlite3
import requests

def init_db():
    conn = sqlite3.connect('visa_wlb_jobs.db')
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS jobs')
    cursor.execute('''
        CREATE TABLE jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT,
            title TEXT,
            role_level TEXT,
            location TEXT,
            wlb_tier TEXT,
            visa_sponsored TEXT,
            requirements TEXT,
            apply_link TEXT,
            is_india INTEGER,
            UNIQUE(company, title, location)
        )
    ''')
    conn.commit()
    conn.close()

def is_visa_or_relocation(content_text, location_text):
    text = (content_text + " " + location_text).lower()
    # Strictly check for actual visa/relocation terms, excluding generic terms like "anywhere"
    visa_keywords = [
        'visa', 'sponsorship', 'relocation', 'work permit', 
        'relocate', 'visa support', 'h1b', 'h-1b', 'immigration'
    ]
    return any(kw in text for kw in visa_keywords)

def extract_tech_stack(content_text):
    text = content_text.lower()
    tech_keywords = [
        'python', 'java', 'c++', 'golang', 'go', 'rust', 'typescript', 'javascript', 
        'react', 'node', 'vue', 'angular', 'django', 'flask', 'spring', 
        'aws', 'gcp', 'azure', 'kubernetes', 'docker', 'terraform', 
        'sql', 'postgresql', 'mysql', 'mongodb', 'redis', 'kafka',
        'graphql', 'rest', 'distributed systems', 'microservices'
    ]
    found_tech = [tech.title() if tech not in ['aws', 'gcp', 'sql', 'rest', 'c++'] else tech.upper() for tech in tech_keywords if kw_in_text(tech, text)]
    
    if found_tech:
        return ", ".join(list(set(found_tech))[:6])
    return "Software Engineering, CS Fundamentals"

def kw_in_text(kw, text):
    # Word boundary match helper to prevent partial matches like 'go' in 'algorithm'
    import re
    return bool(re.search(r'\b' + re.escape(kw) + r'\b', text))

def fetch_greenhouse_jobs(company_slug, company_name, wlb_tier):
    url = f"https://boards-api.greenhouse.io/v1/boards/{company_slug}/jobs?content=true"
    jobs_added = []
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            data = res.json()
            for job in data.get('jobs', []):
                title = job.get('title', '')
                title_lower = title.lower()

                # Filter engineering roles
                if any(kw in title_lower for kw in ['software', 'engineer', 'developer', 'backend', 'frontend', 'full stack', 'systems']) and not any(kw in title_lower for kw in ['staff', 'principal', 'director', 'manager', 'lead']):
                    location = job.get('location', {}).get('name', 'Remote')
                    content = job.get('content', '')

                    # Strict Visa Check
                    has_visa = is_visa_or_relocation(content, location)
                    visa_status = "Yes (Relocation / Sponsorship)" if has_visa else "Check Job Description"

                    # Role Level Check
                    role_level = "SDE-2 / Mid"
                    if any(kw in title_lower for kw in ['junior', 'associate', ' i', 'entry', 'grad', 'sde 1', 'sde-1', 'sde1']):
                        role_level = "SDE-1 / Entry"

                    # Fix Apply Link Resolution
                    apply_link = job.get('absolute_url') or f"https://boards.greenhouse.io/{company_slug}/jobs/{job.get('id')}"

                    # Requirements Extraction
                    tech_requirements = extract_tech_stack(content)

                    # Location Check
                    is_india = 1 if any(loc in location.lower() for loc in ['india', 'bengaluru', 'bangalore', 'pune', 'hyderabad', 'gurugram', 'mumbai', 'noida']) else 0

                    jobs_added.append((
                        company_name, title, role_level, location, wlb_tier, visa_status,
                        tech_requirements, apply_link, is_india
                    ))
    except Exception as e:
        print(f"Error fetching Greenhouse for {company_name}: {e}")
    return jobs_added

def scrape_visa_jobs():
    init_db()
    conn = sqlite3.connect('visa_wlb_jobs.db')
    cursor = conn.cursor()

    all_jobs = []
    # Core tracked companies
    companies = [
        ("stripe", "Stripe", "Tier 1 (High WLB)"),
        ("databricks", "Databricks", "Tier 1 (High WLB)"),
        ("gitlab", "GitLab", "Tier 1 (High WLB)"),
        ("coinbase", "Coinbase", "Tier 1 (High WLB)"),
        ("cloudflare", "Cloudflare", "Tier 1 (High WLB)"),
        ("airbnb", "Airbnb", "Tier 1 (High WLB)"),
        ("nutanix", "Nutanix", "Tier 1 (High WLB)")
    ]

    for slug, name, tier in companies:
        all_jobs.extend(fetch_greenhouse_jobs(slug, name, tier))

    for job in all_jobs:
        cursor.execute('''
            INSERT OR IGNORE INTO jobs (company, title, role_level, location, wlb_tier, visa_sponsored, requirements, apply_link, is_india)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', job)

    conn.commit()
    conn.close()
    print(f"Loaded {len(all_jobs)} parsed jobs into SQLite.")

if __name__ == "__main__":
    scrape_visa_jobs()
