from flask import Flask, request, redirect, render_template, url_for, session, flash
import os
import sqlite3
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

DB = '/litefs/data.db'

def check_env_vars(var_list):
    missing = [var for var in var_list if var not in os.environ]
    if missing:
        raise EnvironmentError(f"Missing environment variables: {', '.join(missing)}")
    return True

# Check required environment variables at startup
check_env_vars(['APP_SECRET_KEY', 'ADMIN_USERNAME', 'ADMIN_PASSWORD'])

# environment variables for security
app.secret_key = os.environ.get('APP_SECRET_KEY')
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD')

def init_db():
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            description TEXT,
            date TEXT,
            image_url TEXT
        )''')
        # Add teachers table if not exists
        c.execute('''CREATE TABLE IF NOT EXISTS teachers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            subject TEXT,
            faculties TEXT,
            experience TEXT,
            image_url TEXT
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS contact_info (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            phone1 TEXT,
            phone2 TEXT,
            whatsapp TEXT
        )''')
        # Ensure a default row exists
        c.execute('INSERT OR IGNORE INTO contact_info (id, phone1, phone2, whatsapp) VALUES (1, "", "", "")')
        conn.commit()

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('admin_page'))
        else:
            flash('Invalid credentials', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/')
def index():
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        events = c.execute("SELECT * FROM events ORDER BY id DESC").fetchall()
        event_list = [
            {
                'id': row[0],
                'title': row[1],
                'description': row[2],
                'date': row[3],
                'image_url': row[4]
            } for row in events
        ]
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        teachers = c.execute("SELECT * FROM teachers ORDER BY id DESC").fetchall()
        teacher_list = [
            {
                'id': row[0],
                'name': row[1],
                'subject': row[2],
                'faculties': row[3],
                'experience': row[4],
                'image_url': row[5]
            } for row in teachers
        ]
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        c.execute("SELECT phone1, phone2, whatsapp FROM contact_info WHERE id=1")
        contact = c.fetchone()
        contact_info = {
            'phone1': contact[0] if contact else '',
            'phone2': contact[1] if contact else '',
            'whatsapp': contact[2] if contact else ''
        }
    return render_template('index.html', events=event_list, teachers=teacher_list, contact_info=contact_info)

@app.route('/admin')
@login_required
def admin_page():
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        events = c.execute("SELECT * FROM events ORDER BY id DESC").fetchall()
        event_list = [
            {
                'id': row[0],
                'title': row[1],
                'description': row[2],
                'date': row[3],
                'image_url': row[4]
            } for row in events
        ]
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        teachers = c.execute("SELECT * FROM teachers ORDER BY id DESC").fetchall()
        teacher_list = [
            {
                'id': row[0],
                'name': row[1],
                'subject': row[2],
                'faculties': row[3],
                'experience': row[4],
                'image_url': row[5]
            } for row in teachers
        ]
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        c.execute("SELECT phone1, phone2, whatsapp FROM contact_info WHERE id=1")
        contact = c.fetchone()
        contact_info = {
            'phone1': contact[0] if contact else '',
            'phone2': contact[1] if contact else '',
            'whatsapp': contact[2] if contact else ''
        }
    return render_template('admin.html', events=event_list, teachers=teacher_list, contact_info=contact_info)

@app.route('/admin/event', methods=['POST'])
@login_required
def save_event():
    title = request.form['title']
    description = request.form['description']
    date = request.form['date']
    image = request.files['image']

    if image:
        filename = secure_filename(image.filename)
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image.save(image_path)
        image_url = f'/static/uploads/{filename}'
    else:
        image_url = ''

    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        c.execute('INSERT INTO events (title, description, date, image_url) VALUES (?, ?, ?, ?)',
                  (title, description, date, image_url))
        conn.commit()

    return redirect('/admin')

@app.route('/admin/event/delete/<int:event_id>', methods=['POST'])
@login_required
def delete_event(event_id):
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        # Get image_url before deleting
        c.execute('SELECT image_url FROM events WHERE id = ?', (event_id,))
        row = c.fetchone()
        if row and row[0]:
            image_url = row[0]
            # Remove leading slash if present
            if image_url.startswith('/'):
                image_url = image_url[1:]
            image_path = os.path.join(os.getcwd(), image_url)
            if os.path.exists(image_path):
                try:
                    os.remove(image_path)
                except Exception:
                    pass
        # Delete event from DB
        c.execute('DELETE FROM events WHERE id = ?', (event_id,))
        conn.commit()
    return redirect(url_for('admin_page'))


@app.route("/admin/teacher", methods=["POST"])
@login_required
def add_teacher():
    name = request.form['name']
    subject = request.form['subject']
    faculties = request.form['faculties']
    experience = request.form['experience']
    image = request.files['image']
    if image:
        filename = secure_filename(image.filename)
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image.save(image_path)
        image_url = f'/static/uploads/{filename}'
    else:
        image_url = ''
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        c.execute('INSERT INTO teachers (name, subject, faculties, experience, image_url) VALUES (?, ?, ?, ?, ?)',
                  (name, subject, faculties, experience, image_url))
        conn.commit()
    return redirect(url_for('admin_page'))

@app.route("/admin/delete_teacher/<int:teacher_id>", methods=["POST"])
@login_required
def delete_teacher(teacher_id):
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        # Get image_url before deleting
        c.execute('SELECT image_url FROM teachers WHERE id = ?', (teacher_id,))
        row = c.fetchone()
        if row and row[0]:
            image_url = row[0]
            if image_url.startswith('/'):
                image_url = image_url[1:]
            image_path = os.path.join(os.getcwd(), image_url)
            if os.path.exists(image_path):
                try:
                    os.remove(image_path)
                except Exception:
                    pass
        c.execute('DELETE FROM teachers WHERE id = ?', (teacher_id,))
        conn.commit()
    return redirect(url_for('admin_page'))

@app.route("/admin/edit_teacher/<int:teacher_id>", methods=["GET", "POST"])
@login_required
def edit_teacher(teacher_id):
    if request.method == "POST":
        name = request.form['name']
        subject = request.form['subject']
        faculties = request.form['faculties']
        experience = request.form['experience']
        image = request.files.get('image')
        with sqlite3.connect(DB) as conn:
            c = conn.cursor()
            if image and image.filename:
                filename = secure_filename(image.filename)
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                image.save(image_path)
                image_url = f'/static/uploads/{filename}'
                c.execute('UPDATE teachers SET name=?, subject=?, faculties=?, experience=?, image_url=? WHERE id=?',
                          (name, subject, faculties, experience, image_url, teacher_id))
            else:
                c.execute('UPDATE teachers SET name=?, subject=?, faculties=?, experience=? WHERE id=?',
                          (name, subject, faculties, experience, teacher_id))
            conn.commit()
        return redirect(url_for('admin_page'))
    else:
        with sqlite3.connect(DB) as conn:
            c = conn.cursor()
            c.execute('SELECT * FROM teachers WHERE id=?', (teacher_id,))
            row = c.fetchone()
            if not row:
                return redirect(url_for('admin_page'))
            teacher = {
                'id': row[0],
                'name': row[1],
                'subject': row[2],
                'faculties': row[3],
                'experience': row[4],
                'image_url': row[5]
            }
        return render_template('edit_teacher.html', teacher=teacher)

@app.route('/admin/contact', methods=['POST'])
@login_required
def update_contact():
    phone1 = request.form.get('phone1', '')
    phone2 = request.form.get('phone2', '')
    whatsapp = request.form.get('whatsapp', '')
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        c.execute('UPDATE contact_info SET phone1=?, phone2=?, whatsapp=? WHERE id=1', (phone1, phone2, whatsapp))
        conn.commit()
    flash('Contact info updated!', 'success')
    return redirect(url_for('admin_page'))

if __name__ == '__main__':
    init_db()
    app.run(host="0.0.0.0",port=8080)
