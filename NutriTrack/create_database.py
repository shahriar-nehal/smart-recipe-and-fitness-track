from pprint import pprint
import pymongo
from bson.objectid import ObjectId
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

uri = "mongodb+srv://srahmank:Mistcse55@pets.eec57.mongodb.net/?retryWrites=true&w=majority&appName=pets"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

# Database and collections
tracker_db = client.tracker_db

def create_database():
    # Drop collections if they exist
    tracker_db.drop_collection("users")
    tracker_db.drop_collection("recipes")
    tracker_db.drop_collection("ingredients")
    tracker_db.drop_collection("meals")
    tracker_db.drop_collection("activities")
    tracker_db.drop_collection("progress")

    # Users collection
    users_collection = tracker_db.users
    users_collection.insert_many([
        {"username": "user1", "email": "user1@example.com", "password": "pass123"},
        {"username": "user2", "email": "user2@example.com", "password": "pass123"},
        {"username": "user3", "email": "user3@example.com", "password": "pass123"},
        {"username": "user4", "email": "user4@example.com", "password": "pass123"},
        {"username": "user5", "email": "user5@example.com", "password": "pass123"},
        {"username": "user6", "email": "user6@example.com", "password": "pass123"},
        {"username": "user7", "email": "user7@example.com", "password": "pass123"},
        {"username": "user8", "email": "user8@example.com", "password": "pass123"},
        {"username": "user9", "email": "user9@example.com", "password": "pass123"},
        {"username": "user10", "email": "user10@example.com", "password": "pass123"}
    ])

    # Ingredients collection
    ingredients_collection = tracker_db.ingredients
    ingredients_collection.insert_many([
        {"name": "Tomato", "calories_per_gm": 0.18},
        {"name": "Lettuce", "calories_per_gm": 0.15},
        {"name": "Chicken", "calories_per_gm": 2.50},
        {"name": "Rice", "calories_per_gm": 1.30},
        {"name": "Olive Oil", "calories_per_gm": 8.84},
        {"name": "Potato", "calories_per_gm": 0.77},
        {"name": "Carrot", "calories_per_gm": 0.41},
        {"name": "Apple", "calories_per_gm": 0.52},
        {"name": "Egg", "calories_per_gm": 1.55},
        {"name": "Milk", "calories_per_gm": 0.64}
    ])

    # Recipes collection
    recipes_collection = tracker_db.recipes
    recipes_collection.insert_many([
        {"name": "Chicken Salad", "ingredients": [{"ingredient_id": 1, "quantity": 100}, {"ingredient_id": 3, "quantity": 150}, {"ingredient_id": 5, "quantity": 10}], "instructions": "Mix ingredients and serve.", "total_calories": 374.5, "created_by": 1},
        {"name": "Vegetable Soup", "ingredients": [{"ingredient_id": 2, "quantity": 50}, {"ingredient_id": 6, "quantity": 100}, {"ingredient_id": 7, "quantity": 50}], "instructions": "Cook vegetables in water.", "total_calories": 79.5, "created_by": 2},
        {"name": "Fruit Salad", "ingredients": [{"ingredient_id": 8, "quantity": 150}, {"ingredient_id": 9, "quantity": 50}], "instructions": "Mix fruits and serve.", "total_calories": 96.5, "created_by": 3},
        {"name": "Omelette", "ingredients": [{"ingredient_id": 9, "quantity": 2}, {"ingredient_id": 5, "quantity": 10}], "instructions": "Cook eggs in oil.", "total_calories": 175.8, "created_by": 4},
        {"name": "Pasta", "ingredients": [{"ingredient_id": 3, "quantity": 150}, {"ingredient_id": 10, "quantity": 200}], "instructions": "Cook pasta and chicken.", "total_calories": 450.0, "created_by": 5},
        {"name": "Smoothie", "ingredients": [{"ingredient_id": 8, "quantity": 100}, {"ingredient_id": 10, "quantity": 150}], "instructions": "Blend ingredients.", "total_calories": 196.0, "created_by": 6},
        {"name": "Grilled Chicken", "ingredients": [{"ingredient_id": 3, "quantity": 200}], "instructions": "Grill the chicken.", "total_calories": 500.0, "created_by": 7},
        {"name": "Baked Potato", "ingredients": [{"ingredient_id": 6, "quantity": 200}], "instructions": "Bake the potato.", "total_calories": 154.0, "created_by": 8},
        {"name": "Apple Pie", "ingredients": [{"ingredient_id": 8, "quantity": 200}], "instructions": "Bake the pie.", "total_calories": 104.0, "created_by": 9},
        {"name": "Scrambled Eggs", "ingredients": [{"ingredient_id": 9, "quantity": 3}], "instructions": "Scramble the eggs.", "total_calories": 155.0, "created_by": 10}
    ])

    # Meals collection
    meals_collection = tracker_db.meals
    meals_collection.insert_many([
        {"user_id": 1, "recipe_id": 1, "date": "2024-11-17", "meal_time": "Lunch", "quantity": 1},
        {"user_id": 2, "recipe_id": 2, "date": "2024-11-17", "meal_time": "Dinner", "quantity": 1},
        {"user_id": 3, "recipe_id": 3, "date": "2024-11-17", "meal_time": "Breakfast", "quantity": 1},
        {"user_id": 4, "recipe_id": 4, "date": "2024-11-17", "meal_time": "Lunch", "quantity": 1},
        {"user_id": 5, "recipe_id": 5, "date": "2024-11-17", "meal_time": "Dinner", "quantity": 1},
        {"user_id": 6, "recipe_id": 6, "date": "2024-11-17", "meal_time": "Breakfast", "quantity": 1},
        {"user_id": 7, "recipe_id": 7, "date": "2024-11-17", "meal_time": "Lunch", "quantity": 1},
        {"user_id": 8, "recipe_id": 8, "date": "2024-11-17", "meal_time": "Dinner", "quantity": 1},
        {"user_id": 9, "recipe_id": 9, "date": "2024-11-17", "meal_time": "Lunch", "quantity": 1},
        {"user_id": 10, "recipe_id": 10, "date": "2024-11-17", "meal_time": "Breakfast", "quantity": 1}
    ])

    # Activities collection
    activities_collection = tracker_db.activities
    # Continuation of activities collection insertion
    activities_collection.insert_many([
    {"user_id": 1, "type": "Running", "duration": 30, "calories_burned": 300, "date": "2024-11-17"},
    {"user_id": 2, "type": "Cycling", "duration": 45, "calories_burned": 400, "date": "2024-11-17"},
    {"user_id": 3, "type": "Swimming", "duration": 60, "calories_burned": 500, "date": "2024-11-17"},
    {"user_id": 4, "type": "Walking", "duration": 40, "calories_burned": 150, "date": "2024-11-17"},
    {"user_id": 5, "type": "Yoga", "duration": 50, "calories_burned": 200, "date": "2024-11-17"},
    {"user_id": 6, "type": "Weightlifting", "duration": 35, "calories_burned": 250, "date": "2024-11-17"},
    {"user_id": 7, "type": "Running", "duration": 20, "calories_burned": 180, "date": "2024-11-17"},
    {"user_id": 8, "type": "Cycling", "duration": 30, "calories_burned": 350, "date": "2024-11-17"},
    {"user_id": 9, "type": "Swimming", "duration": 45, "calories_burned": 480, "date": "2024-11-17"},
    {"user_id": 10, "type": "Walking", "duration": 60, "calories_burned": 170, "date": "2024-11-17"}
    ])

    # Progress collection
    progress_collection = tracker_db.progress
    progress_collection.insert_many([
    {"user_id": 1, "date": "2024-11-17", "weight": 150.0, "body_fat": 20.0, "notes": "Feeling great!"},
    {"user_id": 2, "date": "2024-11-17", "weight": 160.0, "body_fat": 18.0, "notes": "Good progress."},
    {"user_id": 3, "date": "2024-11-17", "weight": 140.0, "body_fat": 22.0, "notes": "Keep pushing."},
    {"user_id": 4, "date": "2024-11-17", "weight": 170.0, "body_fat": 15.0, "notes": "Doing well."},
    {"user_id": 5, "date": "2024-11-17", "weight": 155.0, "body_fat": 19.0, "notes": "Steady improvement."},
    {"user_id": 6, "date": "2024-11-17", "weight": 165.0, "body_fat": 17.0, "notes": "Feeling strong."},
    {"user_id": 7, "date": "2024-11-17", "weight": 150.0, "body_fat": 20.5, "notes": "Good workout."},
    {"user_id": 8, "date": "2024-11-17", "weight": 160.0, "body_fat": 16.0, "notes": "On track."},
    {"user_id": 9, "date": "2024-11-17", "weight": 145.0, "body_fat": 21.0, "notes": "Keep going."},
    {"user_id": 10, "date": "2024-11-17", "weight": 170.0, "body_fat": 18.5, "notes": "Nice progress."}
    ])

if __name__ == "__main__":
    create_database()
    print("done.")  