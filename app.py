from flask import Flask, render_template, request, redirect, url_for, session, flash
from argon2 import PasswordHasher
from functools import wraps
import json
import os

from utils import format_timestamp, format_timestamp_with_time, add_log, save_backup, load_backup
from encryption import encrypt_secret, decrypt_secret
from models import db, User, Secret, Log
from config import DB_PATH

app = Flask(__name__)
app.secret_key = os.urandom(32)

app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{DB_PATH}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
ph = PasswordHasher()

app.jinja_env.filters['format_timestamp'] = format_timestamp
app.jinja_env.filters['format_timestamp_with_time'] = format_timestamp_with_time


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in') or 'master_password' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def setup_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not User.query.first():
            return redirect(url_for('setup'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
def index():
    if not User.query.first():
        return redirect(url_for('setup'))
    return redirect(url_for('login'))

@app.route('/docs')
def docs():
    return render_template('docs.html')

@app.route('/setup', methods=['GET', 'POST'])
def setup():
    if User.query.first():
        return redirect(url_for('login'))
    if request.method == 'POST':
        password = request.form.get('password')
        if not password.strip():
            flash("Password is required", "error")
            return render_template('setup.html')
        password_hash = ph.hash(password)
        user = User(password_hash=password_hash)
        db.session.add(user)
        db.session.commit()
        flash("Password setup complete - Please login", "success")
        return redirect(url_for('login'))
    return render_template('setup.html')

@app.route('/login', methods=['GET', 'POST'])
@setup_required
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        user = User.query.first()
        try:
            ph.verify(user.password_hash, password)
            session['logged_in'] = True
            session['master_password'] = password
            flash("Login successful", "success")
            add_log("Login successful") 
            load_backup(password)
            return redirect(url_for('dashboard'))
        except:
            flash("Incorrect password", "error")
            add_log("Login failed: incorrect password")
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    session.pop('logged_in', None)
    session.pop('master_password', None)
    flash("Logged out successfully", "success")
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    category = request.args.get('category', 'All Categories')
    if category == 'All Categories':
        secrets = Secret.query.all()
    else:
        secrets = Secret.query.filter_by(category=category).all()
    categories = ["All Categories", "Seed", "Private Key", "Other"]
    
    return render_template('dashboard.html',
                           secrets=secrets,
                           current_category=category,
                           categories=categories
                           )

@app.route('/logs')
@login_required
def logs():
    all_logs = Log.query.order_by(Log.timestamp.desc()).all()
    return render_template('logs.html', logs=all_logs)

@app.route('/upload', methods=["GET", "POST"])
@login_required
def upload():
    if request.method == 'POST':
        category = request.form.get('category')
        label = request.form.get('label')
        data = request.form.get('data')
        tag = request.form.get('tag')
        master_pw = session.get('master_password')

        if not label.strip() or not data.strip():
            flash("All fields are required", "error")
            return redirect(url_for('upload'))

        cipher_blob = encrypt_secret(data, master_pw)
        new_upload = Secret(
            category=category,
            label=label,
            data=cipher_blob,
            tag=tag
        )
        db.session.add(new_upload)
        db.session.commit()
        save_backup()
        add_log(f"Secret uploaded", new_upload)
        flash("Secret encrypted successfully", "success")
        return redirect(url_for('dashboard'))
    return render_template('upload.html')

@app.route('/secret/<int:id>')
@login_required
def view_secret(id):
    secret = Secret.query.get_or_404(id)
    master_pw = session.get('master_password')

    if not master_pw:
        flash("Session expired. Please login again.", "error")
        return redirect(url_for('login'))

    try:
        plaintext = decrypt_secret(secret.data, master_pw)
        add_log("Secret viewed", secret)
        
    except Exception as e:
        print(f"Decryption error for secret {secret.id}: {str(e)}")
        import traceback
        traceback.print_exc()
        plaintext = "[Decryption failed - check console for details]"

    return render_template('secret.html', secret=secret, plaintext=plaintext)

@app.route('/secret/<int:id>/delete', methods=['POST'])
@login_required
def delete_secret(id):
    secret = Secret.query.get_or_404(id)
    db.session.delete(secret)
    db.session.commit()
    save_backup()
    add_log("Secret deleted", secret)
    flash("Secret deleted successfully", "success")
    return redirect(url_for('dashboard'))

@app.route('/import_backup', methods=['GET', 'POST'])
@login_required
def import_backup_route():
    if request.method == 'POST':
        master_pw = session.get('master_password')
        if not master_pw:
            flash("Session expired. Login again.", "error")
            return redirect(url_for('login'))

        file = request.files.get('backup_file')
        if not file or not file.filename.endswith('.json'):
            flash("Please upload a valid JSON file.", "error")
            return redirect(url_for('import_backup_route'))

        try:
            backup_data = json.load(file)
        except Exception:
            flash("Invalid JSON file.", "error")
            return redirect(url_for('import_backup_route'))

        imported = 0
        for item in backup_data:
            if Secret.query.filter_by(id=item.get("id")).first():
                continue

            try:
                decrypt_secret(item["data"], master_pw)
            except Exception:
                continue

            new_secret = Secret(
                id=item.get("id"),
                category=item.get("category", "Other"),
                label=item.get("label", "Unnamed"),
                tag=item.get("tag", ""),
                data=item["data"]
            )
            db.session.add(new_secret)
            imported += 1

        db.session.commit()
        add_log(f"Imported {imported} secrets from backup")
        flash(f"Imported {imported} secrets from uploaded backup.", "success")
        return redirect(url_for('dashboard'))

    return render_template('import_backup.html')

@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        old_pw = request.form.get('old_password')
        new_pw = request.form.get('new_password')
        confirm = request.form.get('confirm')
        user = User.query.first()

        if new_pw != confirm:
            flash("New passwords do not match", "error")
            return redirect(url_for('change_password'))

        try:
            ph.verify(user.password_hash, old_pw)
        except:
            flash("Old password incorrect", "error")
            return redirect(url_for('change_password'))

        session['master_password'] = new_pw
        user.password_hash = ph.hash(new_pw)
        db.session.commit()

        for s in Secret.query.all():
            plaintext = decrypt_secret(s.data, old_pw)
            s.data = encrypt_secret(plaintext, new_pw)
        db.session.commit()
        save_backup()
        add_log("Master password changed")
        flash("Password changed successfully", "success")
        return redirect(url_for('dashboard'))

    return render_template('change_password.html')


def init_db():
    with app.app_context():
        db.create_all()