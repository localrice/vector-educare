from flask import Flask, request, redirect, render_template
import os
import sqlite3
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

DB = 'data.db'

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
        conn.commit()

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
    return render_template('index.html', events=event_list)

@app.route('/admin')
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
    return render_template('admin.html', events=event_list)


@app.route('/admin/event', methods=['POST'])
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

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
