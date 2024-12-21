# Workout Tracker App

The **Workout Tracker App** helps users log, track, and visualize their fitness journey. 
It allows users to choose workout plans, record workout details, view history, and monitor progress.

## Features
- User authentication with secure login and registration.
- Choose from workout plans like Pull/Push/Legs, Upper/Lower, or Full Body.
- Log sets, reps, and weights during workouts.
- View workout history on a calendar and detailed tables.
- Monitor progress trends over time.

## Setup Instructions

### Prerequisites
- Python 3.11 or higher
- pip (Python package manager)
- Google Cloud SDK (optional, for deployment)

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/Zulmei/workout-app.git
   cd workout-app
2. (Optional) Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
4. Initialize the database:
   ```bash
   python init_db.py
### Running Locally
Start the app with:
```bash
python app.py
```
Access the app at http://127.0.0.1:5000.


## Technologies Used
- **Frontend**: HTML, CSS, Bootstrap 5
- **Backend**: Flask, Flask-PyMongo
- **Database**: MongoDB
- **Deployment**: Google App Engine

## File Structure
- `app.py`: Main application logic and route handlers.
- `init_db.py`: Script to initialize the database.
- `templates/`: Contains all HTML templates for the app.
- `static/`: Static assets like images and stylesheets.
- `app.yaml`: Configuration for Google App Engine deployment.
- `requirements.txt`: Python dependencies.
- `.gitignore`: Specifies files and directories to be ignored by Git (e.g., virtual environment files, logs, credentials).
- `.gcloudignore`: Specifies files and directories to exclude during deployment to Google Cloud.


