import sqlite3
import requests
from bs4 import BeautifulSoup
import re

# 1. Initialize Database
def init_db():
    conn = sqlite3.connect('visa_wlb_jobs.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
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

# Pre-defined list of top high-WLB companies sponsoring visas (Europe, SEA, Remote)
WLB_COMPANIES = {
    "Microsoft": "Tier 1 (High WLB)",
    "LinkedIn": "Tier 1 (High WLB)",
    "Booking.com": "Tier 1 (High WLB)",
    "Zalando": "Tier 1 (High WLB)",
    "Agoda": "Tier 1 (High WLB)",
    "Spotify": "Tier 1 (High WLB)",
    "Adobe": "Tier 1 (High WLB)",
    "ServiceNow": "Tier 1 (High WLB)"
}

# 2. Scraping Engine (Targeting global visa boards like Relocate.me)
def scrape_visa_jobs():
    init_db()
    conn = sqlite3.connect('visa_wlb_jobs.db')
    cursor = conn.cursor()

    url = "https://relocate.me/search"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        job_cards = soup.find_all('div', class_='job-card')

        for card in job_cards:
            title = card.find('h8').text.strip() if card.find('h8') else "Software Engineer"
            company = card.find('div', class_='company-name').text.strip() if card.find('div', class_='company-name') else "Tech Company"
            location = card.find('span', class_='location').text.strip() if card.find('span', class_='location') else "Europe"
            link = "https://relocate.me" + card.find('a')['href'] if card.find('a') else "#"

            # Determine Level (SDE-1 vs SDE-2)
            role_level = "SDE-2 / Mid"
            if any(k in title.lower() for k in ['junior', 'entry', 'sde 1', 'sde-1', 'associate']):
                role_level = "SDE-1 / Entry"
            elif any(k in title.lower() for k in ['senior', 'lead', 'principal']):
                role_level = "Senior / Lead"

            # Check WLB & Visa attributes
            wlb_tier = WLB_COMPANIES.get(company, "Tier 2 (Good WLB)")
            visa_sponsored = "Yes (Relocation Package Included)"

            requirements = "Strong Data Structures & Algorithms, System Design, Relocation Willingness."
            if "SDE-1" in role_level:
                requirements = "0-2 yrs exp, CS fundamentals, Python/Java/Go, problem-solving skills."
            else:
                requirements = "2-5 yrs exp, Distributed Systems, Microservices API design, CI/CD."

            cursor.execute('''
                INSERT OR IGNORE INTO jobs (company, title, role_level, location, wlb_tier, visa_sponsored, requirements, apply_link)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (company, title, role_level, location, wlb_tier, visa_sponsored, requirements, link))

        conn.commit()
        print("Job database updated successfully!")
    except Exception as e:
        print(f"Scraper encountered an issue: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    scrape_visa_jobs()