from datetime import datetime, timedelta
from pprint import pprint
#import mongita
from bson.objectid import ObjectId

#from mongita import MongitaClientDisk
from flask import jsonify
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

uri = "mongodb+srv://srahmank:Mistcse55@pets.eec57.mongodb.net/?retryWrites=true&w=majority&appName=pets"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

#client = MongitaClientDisk()

tracker_db = client.tracker_db

def retrieve_activities():
    activities_collection = tracker_db.activities
    activities = list(activities_collection.find())
    return activities

def create_user(data):
    users_collection = tracker_db.users
    #data["_id"] = ObjectId(data["_id"])
    new_user = data
    users_collection.insert_one(new_user)

def login_user(email, password):
    users_collection = tracker_db.users
    user = users_collection.find_one({"email": email})
    
    if user and user["password"] == password:
        user["id"] = str(user["_id"])
        return user
    return None

def retrieve_activities_by_user_id(user_id):
    activities_collection = tracker_db.activities
    activities = list(activities_collection.find({"user_id": user_id}))
    return activities

def retrieve_activity_logs(user_id):
    activity_logs_collection = tracker_db.activity_log
    logs = list(activity_logs_collection.find({"user_id": user_id}))
    return logs


def create_activity_log(data):
    activity_logs_collection = tracker_db.activity_log
    activity_logs_collection.insert_one(data)


def get_activity_log_by_id(log_id, user_id):
    activity_logs_collection = tracker_db.activity_log
    log = activity_logs_collection.find_one({"_id": ObjectId(log_id), "user_id": user_id})
    return log


def update_activity_log(log_id, updated_data, user_id):
    activity_logs_collection = tracker_db.activity_log
    activity_logs_collection.update_one(
        {"_id": ObjectId(log_id), "user_id": user_id},
        {"$set": updated_data}
    )

def delete_activity_log(log_id, user_id):
    activity_logs_collection = tracker_db.activity_log
    activity_logs_collection.delete_one({"_id": ObjectId(log_id), "user_id": user_id})

def create_activity(data):
    activities_collection = tracker_db.activities
    #data["_id"] = ObjectId(data["_id"])
    new_activity = data
    activities_collection.insert_one(new_activity)

def delete_activity(activity_id):
    activities_collection = tracker_db.activities
    # Ensure the user can only delete their own activities
    activities_collection.delete_one({"_id": ObjectId(activity_id)})

def get_activity_by_id(activity_id):
    activities_collection = tracker_db.activities
    return activities_collection.find_one({"_id": ObjectId(activity_id)})

def update_activity(activity_id, updated_data):
    activities_collection = tracker_db.activities
    activities_collection.update_one(
        {"_id": ObjectId(activity_id)},
        {"$set": updated_data}
    )

def retrieve_ingredients():
    ingredients_collection = tracker_db.ingredients
    ingredients = list(ingredients_collection.find())
    return ingredients
def retrieve_ingredient_by_id(ingredient_id):
    ingredients_collection = tracker_db.ingredients
    return ingredients_collection.find_one({"_id": ObjectId(ingredient_id)})
def create_ingredient(data):
    ingredients_collection = tracker_db.ingredients
    #data["_id"] = ObjectId(data["_id"])
    new_ingredient = data
    ingredients_collection.insert_one(new_ingredient)
def delete_ingredient(ingredient_id):
    ingredients_collection = tracker_db.ingredients
    ingredients_collection.delete_one({"_id": ObjectId(ingredient_id)})
def update_ingredient(ingredient_id, updated_data):
    ingredients_collection = tracker_db.ingredients
    ingredients_collection.update_one(
        {"_id": ObjectId(ingredient_id)},
        {"$set": updated_data}  # Replace the existing data with the new data
    )

def retrieve_recipes():
    recipes_collection = tracker_db.recipes
    recipes = list(recipes_collection.find())
    return recipes
def retrieve_recipe_by_id(recipe_id):
    recipes_collection = tracker_db.recipes
    return recipes_collection.find_one({"_id": ObjectId(recipe_id)})
def create_recipe(data):
    recipes_collection = tracker_db.recipes
    #data["_id"] = ObjectId(data["_id"])
    new_recipe = data
    recipes_collection.insert_one(new_recipe)
def delete_recipe(recipe_id):
    recipes_collection = tracker_db.recipes
    recipes_collection.delete_one({"_id": ObjectId(recipe_id)})
def update_recipe(recipe_id, updated_data): 
    recipes_collection = tracker_db.recipes
    recipes_collection.update_one(
        {"_id": ObjectId(recipe_id)},
        {"$set": updated_data}  # Replace the existing data with the new data
    )

def retrieve_meals():
    meals_collection = tracker_db.meals
    meals = list(meals_collection.find())
    return meals
def retrieve_meal_logs_by_user_id(user_id):
    meal_logs_collection = tracker_db.meals
    logs = list(meal_logs_collection.find({"user_id": user_id}))
    return logs
def retrieve_meal_by_id(meal_id):
    meals_collection = tracker_db.meals
    return meals_collection.find_one({"_id": ObjectId(meal_id)})
def create_meal_log(data):
    meals_collection = tracker_db.meals
    #data["_id"] = ObjectId(data["_id"])
    new_meal = data
    meals_collection.insert_one(new_meal)
def delete_meal_log(meal_id, user_id):
    meals_collection = tracker_db.meals
    meals_collection.delete_one({"_id": ObjectId(meal_id), "user_id": user_id})
def update_meal_log(meal_id, updated_data):
    meals_collection = tracker_db.meals
    meals_collection.update_one(
        {"_id": ObjectId(meal_id)},
        {"$set": updated_data}  # Replace the existing data with the new data
    )

def get_total_calories_consumed(user_id, date):
    meals_collection = tracker_db.meals
    meal_logs = meals_collection.find({'user_id': user_id, 'date': date})
    total_calories = sum(log['calories_intake'] for log in meal_logs)
    return total_calories

def get_total_calories_burned(user_id, date):
    activity_logs_collection = tracker_db.activity_log
    activity_logs = activity_logs_collection.find({'user_id': user_id, 'date': date})
    total_calories_burned = sum(log['calories_burned'] for log in activity_logs)
    return total_calories_burned

def calculate_net_calories(user_id, date):
    total_calories_consumed = get_total_calories_consumed(user_id, date)
    total_calories_burned = get_total_calories_burned(user_id, date)
    net_calories = total_calories_consumed - total_calories_burned
    return {
        'total_calories_consumed': total_calories_consumed,
        'total_calories_burned': total_calories_burned,
        'net_calories': net_calories
    }

def get_weekly_calories_consumed(user_id, start_date, end_date):
    meals_collection = tracker_db.meals
    meal_logs = meals_collection.find({
        'user_id': user_id,
        'date': {'$gte': start_date, '$lte': end_date}
    })

    daily_calories = {date.strftime('%Y-%m-%d'): 0 for date in (start_date + timedelta(days=n) for n in range(7))}
    for log in meal_logs:
        date = log['date'].strftime('%Y-%m-%d')
        daily_calories[date] += log['calories_intake']

    return daily_calories


def get_weekly_calories_burned(user_id, start_date, end_date):
    activity_logs_collection = tracker_db.activity_log
    activity_logs = activity_logs_collection.find({
        'user_id': user_id,
        'date': {'$gte': start_date, '$lte': end_date}
    })

    daily_calories_burned = {date.strftime('%Y-%m-%d'): 0 for date in (start_date + timedelta(days=n) for n in range(7))}
    for log in activity_logs:
        date = log['date'].strftime('%Y-%m-%d')
        daily_calories_burned[date] += log['calories_burned']

    return daily_calories_burned

def calculate_weekly_net_calories(user_id, start_date, end_date):
    daily_calories_consumed = get_weekly_calories_consumed(user_id, start_date, end_date)
    daily_calories_burned = get_weekly_calories_burned(user_id, start_date, end_date)
    
    weekly_data = []
    total_net_calories = 0
    
    for single_date in (start_date + timedelta(days=n) for n in range((end_date - start_date).days + 1)):
        date_str = single_date.strftime('%Y-%m-%d')
        consumed = daily_calories_consumed.get(date_str, 0)
        burned = daily_calories_burned.get(date_str, 0)
        net_calories = consumed - burned
        total_net_calories += net_calories
        weekly_data.append({'date': date_str, 'consumed': consumed, 'burned': burned, 'net': net_calories})
    
    # Estimate weight change
    weight_change_kg = total_net_calories / 7000.0  # 7000 calories per kg
    return weekly_data, weight_change_kg

def get_total_calories_consumed_for_week(user_id, start_date, end_date):
    meals_collection = tracker_db.meals
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')

    # Query the database
    meal_logs = meals_collection.find({
        'user_id': user_id,
        'date': {'$gte': start_date_str, '$lte': end_date_str}
    })
    
    daily_calories = {}
    for log in meal_logs:
        # Convert date string to datetime object
        log_date = datetime.strptime(log['date'], '%Y-%m-%d').date()
        daily_calories[log_date] = daily_calories.get(log_date, 0) + log.get('calories_intake', 0)
    
    print("Calories Consumed (Daily):", daily_calories)
    return daily_calories


def get_total_calories_burned_for_week(user_id, start_date, end_date):
    activity_logs_collection = tracker_db.activity_log
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')

    # Query the database
    activity_logs = activity_logs_collection.find({
        'user_id': user_id,
        'date': {'$gte': start_date_str, '$lte': end_date_str}
    })

    daily_calories_burned = {}
    for log in activity_logs:
        # Convert date string to datetime object
        log_date = datetime.strptime(log['date'], '%Y-%m-%d').date()
        daily_calories_burned[log_date] = daily_calories_burned.get(log_date, 0) + log.get('calories_burned', 0)

    print("Calories Burned (Daily):", daily_calories_burned)
    return daily_calories_burned


def calculate_weekly_net_calories(user_id, start_date, end_date):
    consumed = get_total_calories_consumed_for_week(user_id, start_date, end_date)
    burned = get_total_calories_burned_for_week(user_id, start_date, end_date)

    weekly_data = []
    total_net_calories = 0

    for single_date in (start_date + timedelta(days=n) for n in range((end_date - start_date).days + 1)):
        date = single_date.date()
        consumed_calories = consumed.get(date, 0)
        burned_calories = burned.get(date, 0)
        net_calories = consumed_calories - burned_calories
        total_net_calories += net_calories

        weekly_data.append({
            'date': single_date.strftime('%Y-%m-%d'),
            'consumed': consumed_calories,
            'burned': burned_calories,
            'net': net_calories
        })

    weight_change_kg = total_net_calories / 7000.0  # Approx. 1 kg per 7000 calories
    print("Weekly Data:", weekly_data)
    print("Total Weight Change (kg):", weight_change_kg)

    return weekly_data, weight_change_kg


def retrieve_user_by_id(user_id):
    users_collection = tracker_db.users
    return users_collection.find_one({"_id": ObjectId(user_id)})

def update_user(user_id, updated_data):
    users_collection = tracker_db.users
    users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": updated_data}
    )


def get_total_calories_burned1(user_id, date):
    activity_logs_collection = tracker_db.activity_log
    
    # Convert date to datetime string for comparison
    date_str = date.strftime('%Y-%m-%d')
    
    activity_logs = activity_logs_collection.find({
        'user_id': user_id,
        'date': date_str
    })

    total_calories_burned = sum(log['calories_burned'] for log in activity_logs)
    print(f"Total Calories Burned on {date_str}: {total_calories_burned}")
    return total_calories_burned






def check_consecutive_days(user_activities):
    # Extract dates and ensure they are datetime objects
    activity_dates = []
    for activity in user_activities:
        if 'date' in activity:
            # Convert string dates to datetime objects if necessary
            date_value = activity['date']
            if isinstance(date_value, str):
                date_value = datetime.strptime(date_value, '%Y-%m-%d')  # Adjust format if needed
            activity_dates.append(date_value.date())

    activity_dates = sorted(activity_dates)  # Sort dates

    if not activity_dates:
        return 0

    max_consecutive_days = 1
    current_streak = 1

    for i in range(1, len(activity_dates)):
        # Check if the current date is exactly one day after the previous date
        if activity_dates[i] == activity_dates[i - 1] + timedelta(days=1):
            current_streak += 1
        else:
            max_consecutive_days = max(max_consecutive_days, current_streak)
            current_streak = 1

    max_consecutive_days = max(max_consecutive_days, current_streak)

    return max_consecutive_days


def assign_badges(user_id):
    """
    Assign badges to a user based on activity logs and criteria.
    """
    activity_log_collection = tracker_db.activity_log
    badges_collection = tracker_db.badges
    badges_log_collection = tracker_db.badges_log

    # Fetch user activities
    user_activities = list(activity_log_collection.find({"user_id": user_id}))
    consecutive_days = check_consecutive_days(user_activities)
    print(f"Consecutive Days: {consecutive_days}")

    # Fetch today's date and calculate daily calories burned
    current_date = datetime.today().date()
    print(f"Current Date: {current_date}")
    daily_calories_burned = get_total_calories_burned1(user_id, current_date)
    print(f"Daily Calories Burned: {daily_calories_burned}")

    # Add a helper to calculate total calories across all activities
    total_calories_burned = sum(activity.get("calories_burned", 0) for activity in user_activities)
    print(f"Total Calories Burned: {total_calories_burned}")

    # Iterate through badges with criteria
    for badge in badges_collection.find({"type": "criteria"}):  # Only evaluate criteria badges
        criteria = badge["criteria"]

        # Replace placeholders with actual values
        criteria = criteria.replace("activities_completed", str(len(user_activities)))
        criteria = criteria.replace("consecutive_days", str(consecutive_days))
        criteria = criteria.replace("daily_calories_burned", str(daily_calories_burned))
        criteria = criteria.replace(
            "sum(activity['calories_burned'] for activity in user_activities)",
            str(total_calories_burned)
        )

        try:
            # Evaluate the criteria safely with allowed built-ins
            if eval(criteria, {"__builtins__": None}, {"sum": sum, "user_activities": user_activities}):
                # Check if the badge has already been assigned
                existing_badge = badges_log_collection.find_one({
                    "user_id": user_id,
                    "badge_id": badge["_id"]
                })

                if not existing_badge:
                    # Assign the badge and log the assignment
                    badges_log_collection.insert_one({
                        "user_id": user_id,
                        "badge_id": badge["_id"],
                        "assigned_on": datetime.now()
                    })
                    print(f"Badge '{badge['name']}' assigned to user {user_id}.")
                else:
                    print(f"Badge '{badge['name']}' already assigned.")
        except Exception as e:
            print(f"Error evaluating badge criteria for '{badge['name']}': {e}")



def create_badge(badge_data):
    badges_collection = tracker_db.badges
    badges_collection.insert_one(badge_data)

def retrieve_badges():
    badges_collection = tracker_db.badges
    badges = list(badges_collection.find())
    return badges

def retrieve_badges_by_user_id(user_id):
    badges_log_collection = tracker_db.badges_log
    badges = list(badges_log_collection.find({'user_id': user_id}))
    return badges

from bson import ObjectId

def get_earned_badges(user_id):
    """
    Fetch all badges earned by a user.
    """
    badges_log_collection = tracker_db.badges_log
    badges_collection = tracker_db.badges

    # Fetch earned badge IDs for the user
    earned_badges = list(badges_log_collection.find({"user_id": user_id}))

    # Map to full badge details
    badge_ids = [badge_log['badge_id'] for badge_log in earned_badges]
    badges = list(badges_collection.find({"_id": {"$in": badge_ids}}))

    # Format the response
    response = []
    for badge in badges:
        response.append({
            "name": badge.get("name"),
            "description": badge.get("description"),
            "assigned_on": next((log["assigned_on"] for log in earned_badges if log["badge_id"] == badge["_id"]), None)
        })

    return list(response)

def retrieve_questions():
    questions_collection = tracker_db.questions
    questions = list(questions_collection.find().sort("timestamp", -1))
    return questions

def create_question(data):
    questions_collection = tracker_db.questions
    questions_collection.insert_one(data)

def retrieve_question_by_id(question_id):
    questions_collection = tracker_db.questions
    question = questions_collection.find_one({"_id": ObjectId(question_id)})
    return question

def delete_question(question_id):
    questions_collection = tracker_db.questions
    questions_collection.delete_one({"_id": ObjectId(question_id)})

def update_question(question_id, updated_data):
    questions_collection = tracker_db.questions
    questions_collection.update_one({"_id": ObjectId(question_id)}, {"$set": updated_data})

def retrieve_answers_by_question_id(question_id):
    answers_collection = tracker_db.answers
    answers = list(answers_collection.find({"question_id": ObjectId(question_id)}).sort("timestamp", -1))
    return answers

def create_answer(data):
    answers_collection = tracker_db.answers
    answers_collection.insert_one(data)

