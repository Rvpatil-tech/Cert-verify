import os
import csv
from io import StringIO
from functools import wraps
from flask import Flask, request, render_template, redirect, url_for, session, make_response, flash
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "tensor_talezz_secure_secret_key")

MONGO_URI = os.environ.get('MONGO_URI')

db_client = None
db = None

def get_db():
    global db_client, db
    if db is None:
        if not MONGO_URI:
            raise ValueError("MONGO_URI environment variable not set. Please set it in .env or your environment variables.")
        db_client = MongoClient(MONGO_URI)
        db = db_client['ttcert']
    return db

def init_db():
    database = get_db()
    # Check if admin exists
    admin = database.admins.find_one({"username": "TT-ADMIN"})
    if not admin:
        database.admins.insert_one({
            "username": "TT-ADMIN",
            "password_hash": generate_password_hash("Sakhii_Aarvi")
        })

@app.before_request
def initialize_database():
    if not hasattr(app, 'db_initialized'):
        if MONGO_URI:
            init_db()
        app.db_initialized = True

# Decorator for secure admin routes
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session:
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

def generate_cert_id(database):
    # Find the latest certificate by sorting by certificate_id descending
    latest_cert = database.certificates.find_one({}, sort=[("certificate_id", -1)])
    year = datetime.datetime.now().year
    prefix = f"TT-AI-{year}-"
    if latest_cert and latest_cert.get('certificate_id'):
        last_id = latest_cert['certificate_id']
        try:
            last_num = int(last_id.split('-')[-1])
            new_num = last_num + 1
        except ValueError:
            new_num = 1
    else:
        new_num = 1
    
    return f"{prefix}{new_num:03d}"

@app.route('/', methods=['GET'])
def index():
    cert_id = request.args.get('cert_id', '')
    return render_template('index.html', cert_id=cert_id)

@app.route('/api/verify', methods=['POST'])
def verify_cert():
    cert_id = request.form.get('certificate_id', '').strip()
    if not cert_id:
        return render_template('index.html', error="Please enter a Certificate ID.")
    
    try:
        database = get_db()
        cert = database.certificates.find_one({"certificate_id": cert_id})

        if cert:
            return render_template('index.html', cert=cert)
        else:
            return render_template('index.html', error="Certificate not found or invalid.")
    except Exception as e:
        return render_template('index.html', error="Database connection error. Please try again later.")

@app.route('/admin', methods=['GET'])
@login_required
def admin_dashboard():
    database = get_db()
    certificates = list(database.certificates.find().sort([("issue_date", -1), ("certificate_id", -1)]))
    return render_template('admin.html', certificates=certificates)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        try:
            database = get_db()
            admin = database.admins.find_one({"username": username})
            
            if admin and check_password_hash(admin['password_hash'], password):
                session['admin_logged_in'] = True
                return redirect(url_for('admin_dashboard'))
            else:
                flash("Invalid credentials.")
                return render_template('login.html', error="Invalid username or password.")
        except Exception as e:
            flash("Database connection error. Ensure MONGO_URI is set.")
            return render_template('login.html', error="Database connection error.")
            
    return render_template('login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('index'))

@app.route('/admin/add', methods=['POST'])
@login_required
def add_certificate():
    participant_name = request.form.get('participant_name')
    program_name = request.form.get('program_name')
    if program_name == 'Other':
        custom_program = request.form.get('custom_program_name')
        if custom_program:
            program_name = custom_program
    repo_link = request.form.get('repo_link', '')
    issue_date = request.form.get('issue_date')
    
    if not participant_name or not program_name or not issue_date:
        flash("Please fill in all required fields.")
        return redirect(url_for('admin_dashboard'))

    try:
        database = get_db()
        new_cert_id = generate_cert_id(database)
        database.certificates.insert_one({
            "certificate_id": new_cert_id,
            "participant_name": participant_name,
            "program_name": program_name,
            "repo_link": repo_link,
            "issue_date": issue_date,
            "status": "Verified"
        })
        flash(f"Certificate {new_cert_id} added successfully.")
    except Exception as e:
        flash(f"An error occurred: {str(e)}")
        
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/export')
@login_required
def export_csv():
    database = get_db()
    certificates = list(database.certificates.find().sort("certificate_id", 1))

    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(['Certificate ID', 'Participant Name', 'Program Name', 'Repo Link', 'Issue Date', 'Status'])
    for c in certificates:
        cw.writerow([
            c.get('certificate_id', ''), 
            c.get('participant_name', ''), 
            c.get('program_name', ''), 
            c.get('repo_link', ''), 
            c.get('issue_date', ''), 
            c.get('status', 'Verified')
        ])
    
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=certificates.csv"
    output.headers["Content-type"] = "text/csv"
    return output

if __name__ == '__main__':
    app.run(debug=True, port=5000)
