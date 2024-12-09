from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import os
import calendar

# Initialize Flask app
app = Flask(__name__, static_folder='static', static_url_path='/static')
app.secret_key = 'your_secret_key'

# Database connection function
def get_db_connection():
    db_path = os.path.join(os.path.dirname(__file__), 'workout.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the database with required tables if not already created."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    )
    ''')

    # Create workouts table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS workouts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        workout_type TEXT NOT NULL,
        exercise_name TEXT NOT NULL,
        sets INTEGER NOT NULL,
        reps INTEGER NOT NULL,
        weight REAL NOT NULL,
        date TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')

    conn.commit()
    conn.close()
    print("Database initialized successfully.")


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        existing_user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        
        if existing_user:
            flash('Username already taken!', 'danger')
            conn.close()
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)
        conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
        conn.commit()
        conn.close()

        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

@app.route('/index')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    workout_program = {
        "Pull": [
            {"name": "Deadlift", "sets": 1, "reps": "5+"},
            {"name": "Pulldowns", "sets": 3, "reps": "8-12"},
            {"name": "Chest Supported Rows", "sets": 3, "reps": "8-12"},
            {"name": "Face Pulls", "sets": 5, "reps": "15-20"},
            {"name": "Hammer Curls", "sets": 4, "reps": "8-12"},
            {"name": "Dumbbell Curls", "sets": 4, "reps": "8-12"},
        ],
        "Push": [
            {"name": "Bench Press", "sets": 5, "reps": "5"},
            {"name": "Overhead Press", "sets": 3, "reps": "8-12"},
            {"name": "Incline Dumbbell Press", "sets": 3, "reps": "8-12"},
            {"name": "Triceps Pushdowns", "sets": 3, "reps": "8-12"},
            {"name": "Lat Raises", "sets": 3, "reps": "15-20"},
            {"name": "Overhead Tri Extensions", "sets": 3, "reps": "8-12"},
            {"name": "Lat Raises", "sets": 3, "reps": "15-20"},
        ],
        "Legs": [
            {"name": "Squats", "sets": 3, "reps": "5"},
            {"name": "Romanian Deadlift", "sets": 3, "reps": "8-12"},
            {"name": "Leg Press", "sets": 3, "reps": "8-12"},
            {"name": "Leg Curls", "sets": 3, "reps": "8-12"},
            {"name": "Calf Raises", "sets": 5, "reps": "8-12"},
        ]
    }
    return render_template('index.html', workout_program=workout_program)


@app.route('/workout_form/<workout_type>', methods=['GET', 'POST'])
def workout_form(workout_type):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # Define the updated workout program
    workout_program = {
        "Pull": [
            {"name": "Deadlift", "sets": 1, "reps": "5+"},
            {"name": "Pulldowns", "sets": 3, "reps": "8-12"},
            {"name": "Chest Supported Rows", "sets": 3, "reps": "8-12"},
            {"name": "Face Pulls", "sets": 5, "reps": "15-20"},
            {"name": "Hammer Curls", "sets": 4, "reps": "8-12"},
            {"name": "Dumbbell Curls", "sets": 4, "reps": "8-12"},
        ],
        "Push": [
            {"name": "Bench Press", "sets": 5, "reps": "5"},
            {"name": "Overhead Press", "sets": 3, "reps": "8-12"},
            {"name": "Incline Dumbbell Press", "sets": 3, "reps": "8-12"},
            {"name": "Triceps Pushdowns", "sets": 3, "reps": "8-12"},
            {"name": "Lat Raises", "sets": 3, "reps": "15-20"},
            {"name": "Overhead Tri Extensions", "sets": 3, "reps": "8-12"},
            {"name": "Lat Raises", "sets": 3, "reps": "15-20"},
        ],
        "Legs": [
            {"name": "Squats", "sets": 3, "reps": "5"},
            {"name": "Romanian Deadlift", "sets": 3, "reps": "8-12"},
            {"name": "Leg Press", "sets": 3, "reps": "8-12"},
            {"name": "Leg Curls", "sets": 3, "reps": "8-12"},
            {"name": "Calf Raises", "sets": 5, "reps": "8-12"},
        ]
    }

    # Get exercises for the selected workout type
    exercises = workout_program.get(workout_type, [])

    # Pass the selected workout type and exercises to the form
    return render_template('workout_form.html', workout_type=workout_type, exercises=exercises)


@app.route('/submit', methods=['POST'])
def submit_workout():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    workout_type = request.form['workout_type']
    exercises = request.form.to_dict()
    
    conn = get_db_connection()
    for key, value in exercises.items():
        if key.endswith("_reps"):
            # Extract exercise name and set number
            base_key = key.replace("_reps", "")
            exercise_name, set_number = base_key.rsplit("_set_", 1)  # Split at the last occurrence of "_set_"
            reps = value
            # Get the corresponding weight for this set
            weight_key = f"{exercise_name}_set_{set_number}_weight"
            weight = exercises.get(weight_key, 0)
            
            conn.execute(
                '''
                INSERT INTO workouts (user_id, workout_type, exercise_name, sets, reps, weight, date) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ''',
                (user_id, workout_type, exercise_name, int(set_number), int(reps), float(weight), datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            )
    conn.commit()
    conn.close()

    flash('Workout submitted successfully!', 'success')
    return redirect(url_for('index'))


@app.route('/history')
def workout_history():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = get_db_connection()
    workout_data = conn.execute(
        '''
        SELECT workout_type, exercise_name, sets, reps, weight, date 
        FROM workouts 
        WHERE user_id = ?
        ''',
        (user_id,)
    ).fetchall()
    conn.close()

    return render_template('trends.html', workout_data=workout_data)

@app.route('/calendar')
def workout_calendar():
    try:
        # Use defaults if parameters are missing or invalid
        year = int(request.args.get('year', datetime.now().year))
        month = int(request.args.get('month', datetime.now().month))
    except (ValueError, TypeError):
        year = datetime.now().year
        month = datetime.now().month

    # Ensure month is within valid range
    if month < 1:
        month = 12
        year -= 1
    elif month > 12:
        month = 1
        year += 1

    # Use both month name and numeric value
    month_name = calendar.month_name[month]

    # Generate the calendar for the given month, properly aligned
    cal = calendar.Calendar(firstweekday=6)  # Sunday as the first day of the week
    calendar_data = cal.monthdayscalendar(year, month)

    return render_template(
        'calendar.html',
        calendar=calendar_data,   # Aligned calendar data
        current_month=month_name,  # Full month name for display
        current_month_number=month,  # Numeric month value for URL generation
        current_year=year,
        prev_month=month - 1 if month > 1 else 12,
        prev_year=year if month > 1 else year - 1,
        next_month=month + 1 if month < 12 else 1,
        next_year=year if month < 12 else year + 1,
    )


@app.route('/history/<int:year>/<int:month>/<int:day>')
def workout_history_day(year, month, day):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    date_str = f"{year}-{month:02d}-{day:02d}"

    conn = get_db_connection()
    workout_data = conn.execute(
        '''
        SELECT workout_type, exercise_name, sets, reps, weight, date 
        FROM workouts 
        WHERE user_id = ? AND date(date) = ?
        ''',
        (user_id, date_str)
    ).fetchall()
    conn.close()

    return render_template('history_day.html', workout_data=workout_data, date=date_str)

@app.route('/split/<split_type>')
def split_page(split_type):
    # Logic to load the appropriate page for the split type
    if split_type == 'pull_push_legs':
        return render_template('pull_push_legs.html', split_type='Pull/Push/Legs')
    elif split_type == 'upper_lower':
        return render_template('upper_lower.html', split_type='Upper/Lower')
    else:
        return "Invalid split type", 404

@app.route('/pull_push_legs')
def pull_push_legs():
    workout_program = {
        "Pull": [
            {"name": "Deadlift", "sets": 1, "reps": "5+"},
            {"name": "Pulldowns", "sets": 3, "reps": "8-12"},
            {"name": "Chest Supported Rows", "sets": 3, "reps": "8-12"},
            {"name": "Face Pulls", "sets": 5, "reps": "15-20"},
            {"name": "Hammer Curls", "sets": 4, "reps": "8-12"},
            {"name": "Dumbbell Curls", "sets": 4, "reps": "8-12"},
        ],
        "Push": [
            {"name": "Bench Press", "sets": 5, "reps": "5"},
            {"name": "Overhead Press", "sets": 3, "reps": "8-12"},
            {"name": "Incline Dumbbell Press", "sets": 3, "reps": "8-12"},
            {"name": "Triceps Pushdowns", "sets": 3, "reps": "8-12"},
            {"name": "Lat Raises", "sets": 3, "reps": "15-20"},
            {"name": "Overhead Tri Extensions", "sets": 3, "reps": "8-12"},
            {"name": "Lat Raises", "sets": 3, "reps": "15-20"},
        ],
        "Legs": [
            {"name": "Squats", "sets": 3, "reps": "5"},
            {"name": "Romanian Deadlift", "sets": 3, "reps": "8-12"},
            {"name": "Leg Press", "sets": 3, "reps": "8-12"},
            {"name": "Leg Curls", "sets": 3, "reps": "8-12"},
            {"name": "Calf Raises", "sets": 5, "reps": "8-12"},
        ]
    }
    return render_template('pull_push_legs.html', workout_program=workout_program)




if __name__ == '__main__':
    init_db()  # Initialize the database before starting the app
    app.run(debug=True)

