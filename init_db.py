import sqlite3

# Connect to the database (or create it if it doesn't exist)
conn = sqlite3.connect('workout.db')

# Create a cursor object
cursor = conn.cursor()

# Create the users table
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
)
''')

# Create the workouts table
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

# Commit changes and close the connection
conn.commit()
conn.close()

print("Database initialized and tables created successfully.")
