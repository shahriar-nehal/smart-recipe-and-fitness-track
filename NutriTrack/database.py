from pprint import pprint
#import mongita
from bson.objectid import ObjectId

#from mongita import MongitaClientDisk
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
    for activity in activities:
        activity["id"] = str(activity["_id"])
        del activity["_id"]
        # pet["_id"] = ObjectId(pet["id"])
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

def create_activity_log(data):
    activities_collection = tracker_db.activities
    #data["_id"] = ObjectId(data["_id"])
    new_activity = data
    activities_collection.insert_one(new_activity)

def delete_activity_log(activity_id, user_id):
    activities_collection = tracker_db.activities
    # Ensure the user can only delete their own activities
    activities_collection.delete_one({"_id": ObjectId(activity_id), "user_id": user_id})

def get_activity_log_by_id(activity_id, user_id):
    activities_collection = tracker_db.activities
    return activities_collection.find_one({"_id": ObjectId(activity_id), "user_id": user_id})

def update_activity_log(activity_id, updated_data, user_id):
    activities_collection = tracker_db.activities
    activities_collection.update_one(
        {"_id": ObjectId(activity_id), "user_id": user_id},
        {"$set": updated_data}
    )

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

def retrieve_user_by_id(user_id):
    users_collection = tracker_db.users
    return users_collection.find_one({"_id": ObjectId(user_id)})

def update_user(user_id, updated_data):
    users_collection = tracker_db.users
    users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": updated_data}
    )