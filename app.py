from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_pymongo import PyMongo
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import os
import calendar
from bson import ObjectId

# Initialize Flask app
app = Flask(__name__, static_folder='static', static_url_path='/static')
app.secret_key = 'your_secret_key'

# Centralized workout program data
def get_workout_program(program_type=None):
    programs = {
        "pull_push_legs": {
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
            ],
            "Legs": [
                {"name": "Squats", "sets": 3, "reps": "5"},
                {"name": "Romanian Deadlift", "sets": 3, "reps": "8-12"},
                {"name": "Leg Press", "sets": 3, "reps": "8-12"},
                {"name": "Leg Curls", "sets": 3, "reps": "8-12"},
                {"name": "Calf Raises", "sets": 5, "reps": "8-12"},
            ],
        },
        "upper_lower": {
            "Upper Body": [
                {"name": "Bench Press", "sets": 4, "reps": "6-8"},
                {"name": "Row", "sets": 4, "reps": "6-8"},
                {"name": "Incline Dumbbell Press", "sets": 3, "reps": "10-12"},
                {"name": "Pulldowns", "sets": 3, "reps": "10-12"},
            ],
            "Lower Body": [
                {"name": "Squats", "sets": 4, "reps": "6-8"},
                {"name": "Deadlifts", "sets": 3, "reps": "6-8"},
                {"name": "Lunges", "sets": 3, "reps": "10-12"},
                {"name": "Leg Curls", "sets": 3, "reps": "10-12"},
            ],
        },
        "full_body": {
            "Workout A": [
                {"name": "Squats", "sets": 3, "reps": "6-8"},
                {"name": "Bench Press", "sets": 3, "reps": "6-8"},
                {"name": "Lat Pull-Downs", "sets": 3, "reps": "8-10"},
                {"name": "Shoulder Press", "sets": 3, "reps": "8-10"},
                {"name": "Leg Curls", "sets": 3, "reps": "8-10"},
                {"name": "Biceps Curls", "sets": 3, "reps": "10-15"},
                {"name": "Face Pulls", "sets": 3, "reps": "10-15"},
            ],
            "Workout B": [
                {"name": "Romanian Deadlift", "sets": 3, "reps": "6-8"},
                {"name": "Seated Cable Rows", "sets": 3, "reps": "6-8"},
                {"name": "Incline Dumbbell Press", "sets": 3, "reps": "8-10"},
                {"name": "Leg Press", "sets": 3, "reps": "10-12"},
                {"name": "Lateral Raises", "sets": 3, "reps": "10-15"},
                {"name": "Triceps Pushdowns", "sets": 3, "reps": "10-15"},
                {"name": "Standing Calf Raises", "sets": 4, "reps": "6-10"},
            ],
        }
    }
    return programs.get(program_type, {})

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.secret_key = 'your_secret_key'

# MongoDB Configuration
app.config["MONGO_URI"] = "mongodb+srv://Zulmei:OiQVj32iu0@workouttrackercluster.7m2oj.mongodb.net/workout_tracker?retryWrites=true&w=majority&appName=WorkoutTrackerCluster"
mongo = PyMongo(app)


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the username already exists
        if mongo.db.users.find_one({"username": username}):
            flash('Username already taken!', 'danger')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)

        # Add error handling for the insert operation
        try:
            mongo.db.users.insert_one({"username": username, "password": hashed_password})
            flash('Registration successful. Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash(f'An error occurred during registration: {e}', 'danger')
            return redirect(url_for('register'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = mongo.db.users.find_one({"username": username})

        if user and check_password_hash(user['password'], password):
            session['user_id'] = str(user['_id'])
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
    return render_template('index.html')


@app.route('/workout_form/<workout_type>', methods=['GET', 'POST'])
def workout_form(workout_type):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # Determine which program type the workout_type belongs to
    workout_program = {}
    if workout_type in get_workout_program("pull_push_legs"):
        workout_program = get_workout_program("pull_push_legs")
    elif workout_type in get_workout_program("upper_lower"):
        workout_program = get_workout_program("upper_lower")
    elif workout_type in get_workout_program("full_body"):
        workout_program = get_workout_program("full_body")

    # Fetch the exercises for the specific workout type
    exercises = workout_program.get(workout_type, [])

    # Render the workout_form.html template
    return render_template('workout_form.html', workout_type=workout_type, exercises=exercises)


@app.route('/submit', methods=['POST'])
def submit_workout():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    workout_type = request.form['workout_type']
    exercises = request.form.to_dict()

    try:
        for key, value in exercises.items():
            if key.endswith("_reps"):
                base_key = key.replace("_reps", "")
                exercise_name, set_number = base_key.rsplit("_set_", 1)
                reps = int(value)
                weight_key = f"{exercise_name}_set_{set_number}_weight"
                weight = float(exercises.get(weight_key, 0))

                mongo.db.workouts.insert_one({
                    "user_id": user_id,
                    "workout_type": workout_type,
                    "exercise_name": exercise_name,
                    "sets": int(set_number),
                    "reps": reps,
                    "weight": weight,
                    "date": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })

        flash('Workout submitted successfully!', 'success')
        return redirect(url_for('index'))

    except Exception as e:
        flash(f'An error occurred while submitting the workout: {e}', 'danger')
        return redirect(url_for('workout_form', workout_type=workout_type))

@app.route('/history')
def workout_history():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    workouts = mongo.db.workouts.find({"user_id": user_id}).sort("date", -1)

    # Convert MongoDB cursor to a list of dictionaries
    workout_data = [
        {
            "workout_type": workout["workout_type"],
            "exercise_name": workout["exercise_name"],
            "sets": workout["sets"],
            "reps": workout["reps"],
            "weight": workout["weight"],
            "date": workout["date"]
        }
        for workout in workouts
    ]

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

    user_id = session.get('user_id')
    workouts = mongo.db.workouts.find({
        "user_id": user_id,
        "date": {
            "$regex": f"^{year}-{month:02d}-"  # Matches dates starting with YYYY-MM-
        }
    })

    # Extract just the day numbers from the result
    workout_days = {int(workout['date'].split(' ')[0].split('-')[2]) for workout in workouts}

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
        workout_days=workout_days  # Days with workouts
    )


@app.route('/history/<int:year>/<int:month>/<int:day>')
def workout_history_day(year, month, day):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    date_str = f"{year}-{month:02d}-{day:02d}"

    # Fetch workouts for the given user and date
    workouts = mongo.db.workouts.find({
        "user_id": user_id,
        "date": {"$regex": f"^{date_str}"}
    })

    # Convert MongoDB cursor to a list of dictionaries
    workout_data = [
        {
            "workout_type": workout["workout_type"],
            "exercise_name": workout["exercise_name"],
            "sets": workout["sets"],
            "reps": workout["reps"],
            "weight": workout["weight"],
            "date": workout["date"]
        }
        for workout in workouts
    ]

    return render_template('history_day.html', workout_data=workout_data, date=date_str)

@app.route('/split/<split_type>')
def split_page(split_type):
    # Logic to load the appropriate page for the split type
    if split_type == 'pull_push_legs':
        return render_template('pull_push_legs.html', split_type='Pull/Push/Legs')
    elif split_type == 'upper_lower':
        workout_program = get_workout_program("upper_lower")
        return render_template('upper_lower.html', workout_program=workout_program)
    else:
        return "Invalid split type", 404

@app.route('/pull_push_legs')
def pull_push_legs():
    workout_program = get_workout_program("pull_push_legs")
    return render_template('pull_push_legs.html', workout_program=workout_program)

@app.route('/upper_lower')
def upper_lower():
    workout_program = get_workout_program("upper_lower")
    return render_template('upper_lower.html', workout_program=workout_program)

@app.route('/full_body')
def full_body():
    workout_program = get_workout_program("full_body")
    return render_template('full_body.html', workout_program=workout_program)


if __name__ == '__main__':
    app.run(debug=True)
