from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import os

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database connection function
def get_db_connection():
    db_path = os.path.join(os.path.dirname(__file__), 'workout.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

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
            {"name": "Pull-ups", "sets": 3},
            {"name": "Barbell Rows", "sets": 3},
            {"name": "Lat Pulldowns", "sets": 3}
        ],
        "Push": [
            {"name": "Bench Press", "sets": 3},
            {"name": "Overhead Press", "sets": 3},
            {"name": "Dips", "sets": 3}
        ],
        "Legs": [
            {"name": "Squats", "sets": 3},
            {"name": "Deadlifts", "sets": 3},
            {"name": "Lunges", "sets": 3}
        ]
    }
    return render_template('index.html', workout_program=workout_program)

@app.route('/workout_form/<workout_type>', methods=['GET', 'POST'])
def workout_form(workout_type):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    workout_program = {
        "Pull": [
            {"name": "Pull-ups", "sets": 3},
            {"name": "Barbell Rows", "sets": 3},
            {"name": "Lat Pulldowns", "sets": 3}
        ],
        "Push": [
            {"name": "Bench Press", "sets": 3},
            {"name": "Overhead Press", "sets": 3},
            {"name": "Dips", "sets": 3}
        ],
        "Legs": [
            {"name": "Squats", "sets": 3},
            {"name": "Deadlifts", "sets": 3},
            {"name": "Lunges", "sets": 3}
        ]
    }

    exercises = workout_program.get(workout_type, [])
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

if __name__ == '__main__':
    app.run(debug=True)
