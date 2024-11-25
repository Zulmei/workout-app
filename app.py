from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a secure random key in production
CORS(app)

# Define exercises for each workout type with a fixed number of sets
workout_program = {
    "Push": [
        {"name": "Bench Press", "sets": 3},
        {"name": "Overhead Press", "sets": 3},
        {"name": "Tricep Extension", "sets": 3}
    ],
    "Pull": [
        {"name": "Pull-Ups", "sets": 3},
        {"name": "Barbell Row", "sets": 3},
        {"name": "Bicep Curl", "sets": 3}
    ],
    "Legs": [
        {"name": "Squats", "sets": 4},
        {"name": "Lunges", "sets": 4},
        {"name": "Leg Press", "sets": 3}
    ]
}

# Initialize the database
def init_db():
    conn = sqlite3.connect('workouts.db')
    cursor = conn.cursor()
    # Create user table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    # Create workout entries table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS workout_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            workout_type TEXT NOT NULL,
            exercise_name TEXT NOT NULL,
            set_number INTEGER NOT NULL,
            completed_reps INTEGER NOT NULL,
            completed_weight REAL NOT NULL,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Call to set up database
init_db()

# Home route (login/register page)
@app.route('/')
def home():
    return render_template('home.html')

# Register route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='sha256')

        conn = sqlite3.connect('workouts.db')
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
            conn.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username taken. Try again.', 'danger')
        finally:
            conn.close()
    return render_template('register.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('workouts.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[2], password):
            session['username'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Incorrect login. Try again.', 'danger')
    return render_template('login.html')

# Logout route
@app.route('/logout')
def logout():
    session.clear()  # Clears all session data
    flash("You have been logged out.", "info")
    return redirect(url_for('home'))

# Index route (workout selection) - requires login
@app.route('/index')
def index():
    if 'username' not in session:
        flash('Please log in to access the app.', 'warning')
        return redirect(url_for('login'))
    return render_template('index.html', workout_program=workout_program)

# Route to show exercises based on selected workout type - requires login
@app.route('/workout/<workout_type>')
def workout_form(workout_type):
    if 'username' not in session:
        flash('Please log in to access the app.', 'warning')
        return redirect(url_for('login'))
    exercises = workout_program.get(workout_type, [])
    return render_template('workout_form.html', workout_type=workout_type, exercises=exercises)

# Submit workout entry - requires login
@app.route('/submit', methods=['POST'])
def submit():
    if 'username' not in session:
        flash('Please log in to submit your workout.', 'warning')
        return redirect(url_for('login'))
    
    workout_type = request.form.get('workout_type')
    entries = []

    # Collect data for each exercise and each set
    for exercise in workout_program[workout_type]:
        exercise_name = exercise["name"]
        sets = exercise["sets"]
        for set_number in range(1, sets + 1):
            reps = int(request.form.get(f"{exercise_name}_set_{set_number}_reps", 0))
            weight = float(request.form.get(f"{exercise_name}_set_{set_number}_weight", 0))
            entries.append((workout_type, exercise_name, set_number, reps, weight))

    # Insert data into database
    conn = sqlite3.connect('workouts.db')
    cursor = conn.cursor()
    for entry in entries:
        cursor.execute('''
            INSERT INTO workout_entries (workout_type, exercise_name, set_number, completed_reps, completed_weight)
            VALUES (?, ?, ?, ?, ?)
        ''', entry)
    conn.commit()
    conn.close()

    flash('Workout logged successfully!', 'success')
    return redirect(url_for('index'))

# Route to show workout history - requires login
@app.route('/trends')
def trends():
    if 'username' not in session:
        flash('Please log in to view workout history.', 'warning')
        return redirect(url_for('login'))

    return render_template('trends.html')

# API endpoint: Workouts by date
@app.route('/workout_by_date', methods=['GET'])
def workout_by_date():
    date = request.args.get('date')
    conn = sqlite3.connect('workouts.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT workout_type, exercise_name, set_number, completed_reps, completed_weight
        FROM workout_entries
        WHERE DATE(date) = ?
    ''', (date,))
    rows = cursor.fetchall()
    conn.close()

    # Structure the data into JSON
    data = [
        {
            'workout_type': row[0],
            'exercise': row[1],
            'set_number': row[2],
            'completed_reps': row[3],
            'completed_weight': row[4]
        }
        for row in rows
    ]
    return jsonify(data)

# API endpoint: Workout dates
@app.route('/workout_dates', methods=['GET'])
def workout_dates():
    conn = sqlite3.connect('workouts.db')
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT DATE(date) FROM workout_entries")
    dates = [row[0] for row in cursor.fetchall()]
    conn.close()
    return jsonify(dates)

if __name__ == '__main__':
    app.run(debug=True)
