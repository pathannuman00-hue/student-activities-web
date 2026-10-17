from flask import Flask, render_template, request, redirect, url_for, Response
from pathlib import Path
import sqlite3
import csv
import io

app = Flask(__name__)
DB_PATH = Path(__file__).resolve().parent / "student_activities.db"

YEARS = {1: "1st Year", 2: "2nd Year", 3: "3rd Year", 4: "4th Year"}
CATEGORIES = [
    "Technical", "Cultural", "Sports", "Workshop", "Hackathon",
    "Project", "Internship", "Certification", "Research", "Other"
]
STATUSES = ["Registered", "Completed", "Cancelled"]

def db_connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def initialize_database():
    with db_connect() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            roll_no TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            department TEXT NOT NULL,
            year INTEGER NOT NULL CHECK(year BETWEEN 1 AND 4),
            email TEXT DEFAULT ''
        );
        CREATE TABLE IF NOT EXISTS activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            activity_date TEXT NOT NULL,
            venue TEXT DEFAULT '',
            description TEXT DEFAULT '',
            target_year INTEGER NOT NULL DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS participation (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            activity_id INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'Registered',
            achievement TEXT DEFAULT '',
            UNIQUE(student_id, activity_id),
            FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE,
            FOREIGN KEY(activity_id) REFERENCES activities(id) ON DELETE CASCADE
        );
        """)

# --- DASHBOARD ROUTE ---
@app.route('/')
def dashboard():
    with db_connect() as conn:
        student_count = conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]
        activity_count = conn.execute("SELECT COUNT(*) FROM activities").fetchone()[0]
        registration_count = conn.execute("SELECT COUNT(*) FROM participation").fetchone()[0]
        complete_count = conn.execute("SELECT COUNT(*) FROM participation WHERE status='Completed'").fetchone()[0]
        recent = conn.execute("SELECT * FROM activities ORDER BY activity_date DESC LIMIT 5").fetchall()
    
    return render_template('dashboard.html', 
                           student_count=student_count, 
                           activity_count=activity_count,
                           registration_count=registration_count,
                           complete_count=complete_count,
                           recent=recent, years=YEARS)

# --- STUDENTS ROUTES ---
@app.route('/students', methods=['GET', 'POST'])
def students():
    with db_connect() as conn:
        if request.method == 'POST':
            roll_no = request.form.get('roll_no')
            name = request.form.get('name')
            department = request.form.get('department')
            year = request.form.get('year')
            email = request.form.get('email')
            try:
                conn.execute("INSERT INTO students (roll_no, name, department, year, email) VALUES (?, ?, ?, ?, ?)",
                             (roll_no, name, department, year, email))
            except sqlite3.IntegrityError:
                pass 
            return redirect(url_for('students'))
        
        rows = conn.execute("SELECT * FROM students ORDER BY year, name").fetchall()
    return render_template('students.html', students=rows, years=YEARS)

@app.route('/students/delete/<int:id>')
def delete_student(id):
    with db_connect() as conn:
        conn.execute("DELETE FROM students WHERE id=?", (id,))
    return redirect(url_for('students'))

# --- ACTIVITIES ROUTES ---
@app.route('/activities', methods=['GET', 'POST'])
def activities():
    with db_connect() as conn:
        if request.method == 'POST':
            title = request.form.get('title')
            category = request.form.get('category')
            activity_date = request.form.get('activity_date')
            venue = request.form.get('venue')
            description = request.form.get('description', '')
            target_year = request.form.get('target_year', 0)
            
            conn.execute("INSERT INTO activities (title, category, activity_date, venue, description, target_year) VALUES (?, ?, ?, ?, ?, ?)",
                         (title, category, activity_date, venue, description, target_year))
            return redirect(url_for('activities'))
            
        rows = conn.execute("SELECT * FROM activities ORDER BY activity_date DESC").fetchall()
    return render_template('activities.html', activities=rows, categories=CATEGORIES, years=YEARS)

@app.route('/activities/delete/<int:id>')
def delete_activity(id):
    with db_connect() as conn:
        conn.execute("DELETE FROM activities WHERE id=?", (id,))
    return redirect(url_for('activities'))

# --- PARTICIPATION ROUTES ---
@app.route('/participation', methods=['GET', 'POST'])
def participation():
    with db_connect() as conn:
        if request.method == 'POST':
            student_id = request.form.get('student_id')
            activity_id = request.form.get('activity_id')
            status = request.form.get('status', 'Registered')
            achievement = request.form.get('achievement', '')
            try:
                conn.execute("INSERT INTO participation (student_id, activity_id, status, achievement) VALUES (?, ?, ?, ?)",
                             (student_id, activity_id, status, achievement))
            except sqlite3.IntegrityError:
                pass
            return redirect(url_for('participation'))
            
        records = conn.execute("""
            SELECT p.id, s.roll_no, s.name, s.year, a.title, a.activity_date, p.status, p.achievement
            FROM participation p 
            JOIN students s ON s.id = p.student_id
            JOIN activities a ON a.id = p.activity_id
            ORDER BY a.activity_date DESC
        """).fetchall()
        
        all_students = conn.execute("SELECT id, roll_no, name FROM students").fetchall()
        all_activities = conn.execute("SELECT id, title FROM activities").fetchall()
        
    return render_template('participation.html', records=records, students=all_students, activities=all_activities, years=YEARS, statuses=STATUSES)

@app.route('/participation/status/<int:id>/<status>')
def update_status(id, status):
    with db_connect() as conn:
        conn.execute("UPDATE participation SET status=? WHERE id=?", (status, id))
    return redirect(url_for('participation'))

@app.route('/participation/delete/<int:id>')
def delete_participation(id):
    with db_connect() as conn:
        conn.execute("DELETE FROM participation WHERE id=?", (id,))
    return redirect(url_for('participation'))

# --- REPORTS & EXPORT ROUTES ---
@app.route('/reports')
def reports():
    with db_connect() as conn:
        year_data = []
        for year, label in YEARS.items():
            scount = conn.execute("SELECT COUNT(*) FROM students WHERE year=?", (year,)).fetchone()[0]
            rcount = conn.execute("SELECT COUNT(*) FROM participation p JOIN students s ON s.id=p.student_id WHERE s.year=?", (year,)).fetchone()[0]
            ccount = conn.execute("SELECT COUNT(*) FROM participation p JOIN students s ON s.id=p.student_id WHERE s.year=? AND p.status='Completed'", (year,)).fetchone()[0]
            year_data.append({"label": label, "students": scount, "registrations": rcount, "completed": ccount})
            
        category_data = conn.execute("SELECT category, COUNT(*) AS total FROM activities GROUP BY category ORDER BY total DESC").fetchall()
    return render_template('reports.html', year_data=year_data, category_data=category_data)

@app.route('/export-csv')
def export_csv():
    with db_connect() as conn:
        records = conn.execute("""
            SELECT s.roll_no, s.name, s.year, a.title, a.category, a.activity_date, p.status, p.achievement
            FROM participation p 
            JOIN students s ON s.id = p.student_id
            JOIN activities a ON a.id = p.activity_id
        """).fetchall()
        
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Roll No", "Student Name", "Year", "Activity Title", "Category", "Date", "Status", "Achievement"])
    for r in records:
        writer.writerow([r["roll_no"], r["name"], YEARS[r["year"]], r["title"], r["category"], r["activity_date"], r["status"], r["achievement"]])
        
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=participation_report.csv"}
    )

if __name__ == '__main__':
    initialize_database()
    app.run(debug=True, port=5000)