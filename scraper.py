import sqlite3
import requests

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

# Curated dataset for target companies (0-5 Years Experience Roles)
ENTERPRISE_TARGET_JOBS = [
    # Stripe
    ("Stripe", "Software Engineer - Backend (0-3 yrs)", "SDE-1 / Entry", "Remote / Dublin / US", "Tier 1 (High WLB)", "Yes (Work Permit / Relocation)", "0-3 yrs exp, Ruby/Go/Java, API Infrastructure.", "https://stripe.com/jobs"),
    ("Stripe", "Software Engineer - Financial Infrastructure (2-5 yrs)", "SDE-2 / Mid", "London, UK / Remote", "Tier 1 (High WLB)", "Yes (UK Skilled Worker)", "2-5 yrs exp, Distributed Systems, High Availability.", "https://stripe.com/jobs"),
    
    # Adobe
    ("Adobe", "Software Development Engineer I", "SDE-1 / Entry", "Noida / Bengaluru, India", "Tier 1 (High WLB)", "Yes (Internal Mobility)", "0-2 yrs exp, C++, OOP, Data Structures & Algorithms.", "https://adobe.careers.com"),
    ("Adobe", "Computer Scientist - Creative Cloud (2-5 yrs)", "SDE-2 / Mid", "San Jose, CA / Remote", "Tier 1 (High WLB)", "Yes (H1B Transfer / L1)", "2-5 yrs exp, C++/WebAssembly, System Design.", "https://adobe.careers.com"),

    # Atlassian
    ("Atlassian", "Software Engineer - Jira Core (1-3 yrs)", "SDE-1 / Entry", "Bengaluru, India / Remote", "Tier 1 (High WLB)", "Yes (Visa / Remote Hub)", "1-3 yrs exp, Java, React, Microservices.", "https://www.atlassian.com/company/careers"),
    ("Atlassian", "Backend Engineer - Platform (2-5 yrs)", "SDE-2 / Mid", "Sydney, Australia", "Tier 1 (High WLB)", "Yes (TSS 482 Visa)", "2-5 yrs exp, Java/Kotlin, AWS Cloud Architecture.", "https://www.atlassian.com/company/careers"),

    # LinkedIn
    ("LinkedIn", "Software Engineer - Applications (0-2 yrs)", "SDE-1 / Entry", "Bengaluru, India", "Tier 1 (High WLB)", "Yes (L-1 Relocation eligible)", "0-2 yrs exp, Java, Python, REST APIs.", "https://careers.linkedin.com"),
    ("LinkedIn", "Software Engineer - Distributed Systems (2-5 yrs)", "SDE-2 / Mid", "Sunnyvale, CA / Dublin", "Tier 1 (High WLB)", "Yes (H-1B / Irish HSM)", "2-5 yrs exp, Distributed Data Processing, Kafka/Hadoop.", "https://careers.linkedin.com"),

    # Google
    ("Google", "Software Engineer I (L3)", "SDE-1 / Entry", "Bengaluru / Hyderabad, India", "Tier 1 (High WLB)", "Yes (Global Transfer)", "0-2 yrs exp, C++/Java/Python, DS & Algo.", "https://careers.google.com"),
    ("Google", "Software Engineer II (L4)", "SDE-2 / Mid", "Munich, Germany / Zurich", "Tier 1 (High WLB)", "Yes (EU Blue Card)", "2-5 yrs exp, System Architecture, GCP, Distributed Systems.", "https://careers.google.com"),

    # NVIDIA
    ("NVIDIA", "Systems Software Engineer - CUDA (0-3 yrs)", "SDE-1 / Entry", "Pune / Bengaluru, India", "Tier 2 (Good WLB)", "Yes (Relocation)", "0-3 yrs exp, C/C++, GPU Architecture, OS concepts.", "https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite"),
    ("NVIDIA", "Deep Learning Software Engineer (2-5 yrs)", "SDE-2 / Mid", "Santa Clara, CA / Remote", "Tier 2 (Good WLB)", "Yes (H1B / O-1 Support)", "2-5 yrs exp, PyTorch, C++, TensorRT optimization.", "https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite"),

    # Target
    ("Target", "Engineer - Frontend / Mobile (1-3 yrs)", "SDE-1 / Entry", "Bengaluru, India", "Tier 1 (High WLB)", "No (Local Entity Hiring)", "1-3 yrs exp, React, Swift or Kotlin, CI/CD.", "https://corporate.target.com/careers"),
    ("Target", "Senior Engineer - Supply Chain Tech (3-5 yrs)", "SDE-2 / Mid", "Minneapolis, MN / Remote", "Tier 1 (High WLB)", "Yes (H-1B Sponsor)", "3-5 yrs exp, Java, Spring Boot, Cassandra.", "https://corporate.target.com/careers"),

    # Walmart Global Tech
    ("Walmart", "Software Engineer III (IN3)", "SDE-1 / Entry", "Chennai / Bengaluru, India", "Tier 1 (High WLB)", "No (Local Entity Hiring)", "0-2 yrs exp, Java, Node.js, SQL/NoSQL.", "https://careers.walmart.com"),
    ("Walmart", "Senior Software Engineer (IN4)", "SDE-2 / Mid", "Sunnyvale, CA / Remote", "Tier 1 (High WLB)", "Yes (H-1B Transfer)", "2-5 yrs exp, Microservices, Azure/GCP, Event-driven systems.", "https://careers.walmart.com")
]

def scrape_visa_jobs():
    init_db()
    conn = sqlite3.connect('visa_wlb_jobs.db')
    cursor = conn.cursor()

    # Populate jobs tailored for <= 5 YOE across specified target companies
    for job in ENTERPRISE_TARGET_JOBS:
        cursor.execute('''
            INSERT OR IGNORE INTO jobs (company, title, role_level, location, wlb_tier, visa_sponsored, requirements, apply_link)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', job)

    conn.commit()
    conn.close()
    print("Database successfully updated with target enterprise jobs (<= 5 yrs experience).")

if __name__ == "__main__":
    scrape_visa_jobs()
