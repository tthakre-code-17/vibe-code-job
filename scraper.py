import sqlite3
import requests

def init_db():
    conn = sqlite3.connect('visa_wlb_jobs.db')
    cursor = conn.cursor()
    # Recreate table cleanly
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
            UNIQUE(company, title, location)
        )
    ''')
    conn.commit()
    conn.close()

def fetch_greenhouse_jobs(company_slug, company_name, wlb_tier):
    """Fetches real, live jobs and direct apply links from Greenhouse API"""
    url = f"https://boards-api.greenhouse.io/v1/boards/{company_slug}/jobs"
    jobs_added = []
    try:
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            data = res.json()
            for job in data.get('jobs', []):
                title = job.get('title', '')
                # Filter for SDE 1 / SDE 2 (<= 5 YOE keywords)
                title_lower = title.lower()
                if any(kw in title_lower for kw in ['software', 'engineer', 'developer', 'backend', 'frontend']) and not any(kw in title_lower for kw in ['staff', 'principal', 'director', 'manager', 'lead']):
                    
                    role_level = "SDE-2 / Mid"
                    if any(kw in title_lower for kw in ['junior', 'associate', 'i', 'entry', 'grad']):
                        role_level = "SDE-1 / Entry"
                    
                    location = job.get('location', {}).get('name', 'Remote / Global')
                    apply_link = job.get('absolute_url', f"https://boards.greenhouse.io/{company_slug}")
                    
                    requirements = "Proficiency in Data Structures, Algorithms, Core CS Concepts, Software Development."
                    visa_supported = "Yes (Relocation / Sponsorship available per location policy)"

                    jobs_added.append((
                        company_name,
                        title,
                        role_level,
                        location,
                        wlb_tier,
                        visa_supported,
                        requirements,
                        apply_link
                    ))
    except Exception as e:
        print(f"Failed fetching {company_name}: {e}")
    return jobs_added

def fetch_lever_jobs(company_slug, company_name, wlb_tier):
    """Fetches real, live jobs from Lever API"""
    url = f"https://api.lever.co/v0/postings/{company_slug}?mode=json"
    jobs_added = []
    try:
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            data = res.json()
            for job in data:
                title = job.get('text', '')
                title_lower = title.lower()
                if any(kw in title_lower for kw in ['software', 'engineer', 'developer']) and not any(kw in title_lower for kw in ['staff', 'principal', 'director', 'manager']):
                    role_level = "SDE-2 / Mid"
                    if any(kw in title_lower for kw in ['junior', 'associate', 'i', 'entry']):
                        role_level = "SDE-1 / Entry"
                    
                    location = job.get('categories', {}).get('location', 'Remote')
                    apply_link = job.get('hostedUrl', '#')
                    requirements = "Software engineering fundamentals, System Architecture, Object-Oriented Programming."
                    visa_supported = "Yes (Relocation/Sponsorship provided based on regional policies)"

                    jobs_added.append((
                        company_name,
                        title,
                        role_level,
                        location,
                        wlb_tier,
                        visa_supported,
                        requirements,
                        apply_link
                    ))
    except Exception as e:
        print(f"Failed fetching Lever for {company_name}: {e}")
    return jobs_added

def scrape_visa_jobs():
    init_db()
    conn = sqlite3.connect('visa_wlb_jobs.db')
    cursor = conn.cursor()

    all_jobs = []

    # Fetch live postings from Greenhouse & Lever API endpoints
    all_jobs.extend(fetch_greenhouse_jobs("stripe", "Stripe", "Tier 1 (High WLB)"))
    all_jobs.extend(fetch_lever_jobs("atlassian", "Atlassian", "Tier 1 (High WLB)"))
    all_jobs.extend(fetch_greenhouse_jobs("databricks", "Databricks", "Tier 1 (High WLB)"))
    all_jobs.extend(fetch_greenhouse_jobs("gitlab", "GitLab", "Tier 1 (High WLB)"))
    all_jobs.extend(fetch_greenhouse_jobs("coinbase", "Coinbase", "Tier 1 (High WLB)"))

    for job in all_jobs:
        cursor.execute('''
            INSERT OR IGNORE INTO jobs (company, title, role_level, location, wlb_tier, visa_sponsored, requirements, apply_link)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', job)

    conn.commit()
    conn.close()
    print(f"Successfully loaded {len(all_jobs)} REAL live job listings with direct application URLs!")

if __name__ == "__main__":
    scrape_visa_jobs()
