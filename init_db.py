from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["workout_tracker"]

# Create collections (MongoDB creates them automatically on first use)
users_collection = db["users"]
workouts_collection = db["workouts"]

# Define sample indexes to ensure unique usernames and efficient queries
users_collection.create_index("username", unique=True)

print("MongoDB initialized and collections created successfully.")
