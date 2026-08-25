import sqlite3
from flask import Flask, jsonify, render_template, request
from scraper import scrape_visa_jobs, init_db

# Support index.html either in root ('.') or in 'templates/'
app = Flask(__name__, template_folder='.')

def get_db_connection():
    conn = sqlite3.connect('visa_wlb_jobs.db')
    conn.row_factory = sqlite3.Row
    return conn

# Ensure DB table exists and is populated when Gunicorn initializes the worker
def initialize_app():
    init_db()
    try:
        conn = get_db_connection()
        count = conn.execute('SELECT COUNT(*) FROM jobs').fetchone()[0]
        conn.close()
        # If DB is empty, run scraper on startup
        if count == 0:
            scrape_visa_jobs()
    except Exception as e:
        print(f"Startup DB init warning: {e}")
        scrape_visa_jobs()

# Run initialization immediately on script load
initialize_app()

@app.route('/')
def home():
    try:
        return render_template('index.html')
    except Exception:
        return render_template('templates/index.html')

@app.route('/api/jobs', methods=['GET'])
def get_jobs():
    level_filter = request.args.get('level', '')
    conn = get_db_connection()
    try:
        if level_filter:
            jobs = conn.execute('SELECT * FROM jobs WHERE role_level LIKE ?', (f'%{level_filter}%',)).fetchall()
        else:
            jobs = conn.execute('SELECT * FROM jobs').fetchall()
        return jsonify([dict(job) for job in jobs])
    finally:
        conn.close()

if __name__ == '__main__':
    app.run()
