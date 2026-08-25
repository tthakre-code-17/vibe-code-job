import os
import sqlite3
from flask import Flask, jsonify, render_template, request
from scraper import scrape_visa_jobs

app = Flask(__name__, template_folder='.')


def init_db_if_needed():
    """Ensure database file and jobs table exist before querying."""
    db_path = 'visa_wlb_jobs.db'

    # Check if database or jobs table is missing
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='jobs'"
    )
    table_exists = cursor.fetchone()
    conn.close()

    if not table_exists:
        print("Database/Table missing. Running initial scraper...")
        scrape_visa_jobs()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/jobs', methods=['GET'])
def get_jobs():
    init_db_if_needed()

    region = request.args.get('region', 'all')
    level = request.args.get('level', 'all')
    visa_only = request.args.get('visa_only', 'false')

    conn = sqlite3.connect('visa_wlb_jobs.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = 'SELECT * FROM jobs WHERE 1=1'
    params = []

    if region == 'global':
        query += ' AND is_india = 0'
    elif region == 'india':
        query += ' AND is_india = 1'

    if level == 'sde1':
        query += " AND role_level = 'SDE-1 / Entry'"
    elif level == 'sde2':
        query += " AND role_level = 'SDE-2 / Mid'"

    if visa_only == 'true':
        query += " AND visa_sponsored LIKE 'Yes%'"

    cursor.execute(query, params)
    jobs = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return jsonify(jobs)


if __name__ == '__main__':
    init_db_if_needed()
    app.run(host='0.0.0.0', port=5000)
