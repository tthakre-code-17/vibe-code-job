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

def is_visa_or_remote(content_text, location_text):
    text = (content_text + " " + location_text).lower()
    visa_keywords = ['visa', 'sponsorship', 'relocation', 'work permit', 'anywhere', 'remote']
    return any(kw in text for kw in visa_keywords)

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

                if any(kw in title_lower for kw in ['software', 'engineer', 'developer', 'backend', 'frontend']) and not any(kw in title_lower for kw in ['staff', 'principal', 'director', 'manager', 'lead']):
                    location = job.get('location', {}).get('name', 'Remote')
                    content = job.get('content', '')

                    # Check for explicit visa/relocation/remote
                    has_visa = is_visa_or_remote(content, location)
                    visa_status = "Yes (Relocation / Sponsorship / Remote)" if has_visa else "Check Job Description"

                    role_level = "SDE-2 / Mid"
                    if any(kw in title_lower for kw in ['junior', 'associate', 'i', 'entry', 'grad', 'sde 1', 'sde-1']):
                        role_level = "SDE-1 / Entry"

                    apply_link = job.get('absolute_url', '#')
                    is_india = 1 if 'india' in location.lower() or 'bengaluru' in location.lower() or 'pune' in location.lower() or 'hyderabad' in location.lower() else 0

                    jobs_added.append((
                        company_name, title, role_level, location, wlb_tier, visa_status,
                        "Core CS, Data Structures, System Design", apply_link, is_india
                    ))
    except Exception as e:
        print(f"Error fetching Greenhouse for {company_name}: {e}")
    return jobs_added

def scrape_visa_jobs():
    init_db()
    conn = sqlite3.connect('visa_wlb_jobs.db')
    cursor = conn.cursor()

    all_jobs = []
    all_jobs.extend(fetch_greenhouse_jobs("stripe", "Stripe", "Tier 1 (High WLB)"))
    all_jobs.extend(fetch_greenhouse_jobs("databricks", "Databricks", "Tier 1 (High WLB)"))
    all_jobs.extend(fetch_greenhouse_jobs("gitlab", "GitLab", "Tier 1 (High WLB)"))
    all_jobs.extend(fetch_greenhouse_jobs("coinbase", "Coinbase", "Tier 1 (High WLB)"))
    all_jobs.extend(fetch_greenhouse_jobs("cloudflare", "Cloudflare", "Tier 1 (High WLB)"))

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
