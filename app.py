import sqlite3
from flask import Flask, jsonify, render_template, request
from scraper import scrape_visa_jobs

# Tell Flask to look in the current root directory ('.') for templates
app = Flask(__name__, template_folder='.')

def get_db_connection():
    conn = sqlite3.connect('visa_wlb_jobs.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/jobs', methods=['GET'])
def get_jobs():
    level_filter = request.args.get('level', '')
    conn = get_db_connection()
    if level_filter:
        jobs = conn.execute('SELECT * FROM jobs WHERE role_level LIKE ?', (f'%{level_filter}%',)).fetchall()
    else:
        jobs = conn.execute('SELECT * FROM jobs').fetchall()
    conn.close()
    return jsonify([dict(job) for job in jobs])

if __name__ == '__main__':
    scrape_visa_jobs()
    app.run()
