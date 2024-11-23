import datetime
from flask import Flask, flash, render_template, request, redirect, url_for
import database
from bson.objectid import ObjectId
import pymongo
from pymongo import MongoClient
from flask import session
from werkzeug.security import generate_password_hash
from pprint import pprint
from bson.errors import InvalidId

app = Flask(__name__)
app.secret_key = "123456"  # Replace with a strong secret key


# List of pets, showing related kind information
@app.route("/")
@app.route("/index")
def get_index():
    return render_template("index.html")

# Get, Post, Register user
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        height = float(request.form['height'])
        weight = float(request.form['weight'])
        target_weight = float(request.form['target_weight'])

        # Calculate BMI
        bmi = weight / ((height / 100) ** 2)

        # Hash the password (you can use werkzeug.security for this)
        #hashed_password = generate_password_hash(password, method='sha256')

        # Create a new user document
        new_user = {
            'username': username,
            'email': email,
            'password': password,
            'height': height,
            'weight': weight,
            'bmi': bmi,
            'target_weight': target_weight
        }

        # Insert the new user into the database
        database.create_user(new_user)        
        return redirect(url_for("get_index"))

    return render_template('register.html')


# Get, Post, Login user
@app.route("/login", methods=["GET", "POST"])
def get_post_login_user():    
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        
        if not email or not password:
            error = "Email and password are required."
            return render_template("login.html", error=error)
        
        user = database.login_user(email, password)
        if user:
            session["user_id"] = str(user["_id"])  # Store user ID in session
            session["username"] = user["username"]  # Store username in session
            return redirect(url_for("get_index"))
        else:
            error = "Invalid email or password"
            return render_template("login.html", error=error)
    return render_template("login.html")
@app.route("/activities_log")
def get_activity_logs():
    user_id = session.get("user_id")  # Retrieve user ID from session
    if not user_id:
        return redirect(url_for("get_post_login_user"))
    
    # Retrieve activity logs for the logged-in user
    activity_logs = database.retrieve_activity_logs(user_id)
    return render_template("activity_log.html", activity_logs=activity_logs)


@app.route("/create_activity_log", methods=["GET", "POST"])
def get_post_create_activity_log():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("get_post_login_user"))

    if request.method == "POST":
        activity_id = request.form.get("activity_id")
        duration = request.form.get("duration")

        # Validate inputs
        if not activity_id or not duration:
            flash("Please fill all fields!", "error")
            return redirect(url_for("get_post_create_activity_log"))

        try:
            # Ensure the activity_id is a valid ObjectId
            activity_id = ObjectId(activity_id)
        except InvalidId:
            flash("Invalid activity selected. Please try again.", "error")
            return redirect(url_for("get_post_create_activity_log"))

        try:
            duration = float(duration)  # Convert duration to float
        except ValueError:
            flash("Invalid duration. Please enter a valid number.", "error")
            return redirect(url_for("get_post_create_activity_log"))

        # Get user information
        user = database.retrieve_user_by_id(user_id)
        weight_kg = user.get("weight")
        height_m = user.get("height") / 100  # Convert cm to meters
        bmi = weight_kg / (height_m ** 2)

        # Get activity MET value
        activity = database.get_activity_by_id(activity_id)
        if not activity:
            flash("Activity not found. Please try again.", "error")
            return redirect(url_for("get_post_create_activity_log"))

        met_value = activity["met_value"]

        # Calculate calories burned
        calories_burned = met_value * weight_kg * (duration / 60)

        # Create the activity log
        new_activity_log = {
            "user_id": user_id,
            "activity_id": str(activity_id),
            "duration": duration,
            "calories_burned": calories_burned,
            "activity_name": activity["name"],
        }
        database.create_activity_log(new_activity_log)
        flash("Activity log created successfully!", "success")
        return redirect(url_for("get_activity_logs"))

    # Retrieve activities for the dropdown
    activities = database.retrieve_activities()
    return render_template("create_activity_log.html", activities=activities)


@app.route("/update_activity_log/<log_id>", methods=["GET", "POST"])
def update_activity_log(log_id):
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("get_post_login_user"))

    if request.method == "POST":
        activity_id = request.form["activity_id"]
        duration = float(request.form["duration"])

        # Recalculate calories burned
        user = database.retrieve_user_by_id(user_id)
        weight_kg = user.get("weight")
        activity = database.get_activity_by_id(activity_id)
        met_value = activity["met_value"]
        calories_burned = met_value * weight_kg * (duration / 60)

        updated_activity_log = {
            "activity_id": activity_id,
            "duration": duration,
            "calories_burned": calories_burned,
        }
        database.update_activity_log(log_id, updated_activity_log, user_id)
        return redirect(url_for("get_activity_logs"))

    activity_log = database.get_activity_log_by_id(log_id, user_id)
    activities = database.retrieve_activities()
    return render_template("update_activities_log.html", activity_log=activity_log, activities=activities)

@app.route("/delete_activity_log/<log_id>", methods=["POST"])
def delete_activity_log(log_id):
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("get_post_login_user"))

    database.delete_activity_log(log_id, user_id)
    return redirect(url_for("get_activity_logs"))

@app.route("/activities")
def get_activity_list():
    user_id = session.get("user_id")  # Retrieve user ID from session
    if not user_id:
        return redirect(url_for("get_index"))  # Redirect to login if not logged in
    
    # Fetch activities for the logged-in user
    activities = database.retrieve_activities()
    return render_template("activities.html", activities=activities)
@app.route("/create_activity", methods=["GET", "POST"])
def get_post_create_activity():
    if request.method == "POST":
        new_activity = {
            "name": request.form["name"],
            "met_value": float(request.form["met_value"]),
        }
        database.create_activity(new_activity)
        return redirect(url_for("get_activity_list"))
    return render_template("create_activity.html")

@app.route("/update_activity/<activity_id>", methods=["GET", "POST"])
def update_activity(activity_id):
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("get_post_login_user"))
    
    if request.method == "POST":
        updated_activity = {
            "name": request.form["name"],  # Ensure this matches the form field name
            "met_value": float(request.form["met_value"]),
        }
        database.update_activity(activity_id, updated_activity)
        return redirect(url_for("get_activity_list"))
    
    # Fetch the activity to pre-fill the form
    activity = database.get_activity_by_id(activity_id)
    pprint(activity)
    if not activity:
        return redirect(url_for("get_activity_list"))  # Redirect if activity not found
    return render_template("update_activity.html", activity=activity)

@app.route("/delete_activity/<activity_id>", methods=["POST"])
def delete_activity(activity_id):
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("get_post_login_user"))
    
    database.delete_activity(activity_id)
    return redirect(url_for("get_activity_list"))

@app.route("/ingredients")
def get_ingredients():
    user_id = session.get("user_id")  # Retrieve user ID from session
    if not user_id:
        return redirect(url_for("get_index"))  # Redirect to login if not logged in
    
    # Fetch activities for the logged-in user
    ingredients = database.retrieve_ingredients()
    return render_template("ingredients.html", ingredients=ingredients)

@app.route("/create_ingredient", methods=["GET", "POST"])
def get_post_create_ingredient():
    if request.method == "POST":
        new_ingredient = {
            "name": request.form["name"],
            "calories_per_gm": float(request.form["calories_per_gm"]),
        }
        database.create_ingredient(new_ingredient)
        return redirect(url_for("get_ingredients"))
    return render_template("create_ingredient.html")

@app.route("/update_ingredient/<ingredient_id>", methods=["GET", "POST"])
def update_ingredient(ingredient_id):
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("get_post_login_user"))
    
    if request.method == "POST":
        updated_ingredient = {
            "name": request.form["name"],
            "calories_per_gm": float(request.form["calories_per_gm"]),
        }
        database.update_ingredient(ingredient_id, updated_ingredient)    
        return redirect(url_for("get_ingredients"))
    
    # Fetch the activity to pre-fill the form
    ingredient = database.retrieve_ingredient_by_id(ingredient_id)
    if not ingredient:
        return redirect(url_for("get_ingredients"))  # Redirect if activity not found or not owned by user
    return render_template("update_ingredient.html", ingredient=ingredient)


@app.route("/delete_ingredient/<ingredient_id>", methods=["POST"])
def delete_ingredient(ingredient_id):
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("get_post_login_user"))
    
    database.delete_ingredient(ingredient_id)
    return redirect(url_for("get_ingredients"))

@app.route("/recipes")
def get_recipes():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("get_post_login_user"))
    
    recipes = database.retrieve_recipes()
    ingredients = database.retrieve_ingredients()

    # Convert _id to string for Jinja2 compatibility
    ingredient_lookup = {str(ingredient["_id"]): ingredient["name"] for ingredient in ingredients}
    for recipe in recipes:
        for ingredient in recipe.get("ingredients", []):
            ingredient_obj_id = str(ingredient["ingredient_id"])
            ingredient["name"] = ingredient_lookup.get(ingredient_obj_id, "Unknown Ingredient")
    
    return render_template("recipes.html", recipes=recipes)

# Route: Create Recipe
@app.route("/create_recipe", methods=["GET", "POST"])
def create_recipe():
    if request.method == "POST":
        name = request.form["name"]
        instructions = request.form["instructions"]
        ingredient_ids = request.form.getlist("ingredient_ids[]")
        ingredient_quantities = request.form.getlist("ingredient_quantities[]")

        total_calories = float(request.form["total_calories"])

        # Prepare ingredients list
        formatted_ingredients = [
            {
                "ingredient_id": ObjectId(ingredient_id),
                "quantity": float(quantity),
            }
            for ingredient_id, quantity in zip(ingredient_ids, ingredient_quantities)
        ]

        recipe = {
            "name": name,
            "instructions": instructions,
            "ingredients": formatted_ingredients,
            "total_calories": total_calories,
            "created_by": session["user_id"],
        }
        database.create_recipe(recipe)
        return redirect(url_for("get_recipes"))

    # Convert _id to string for Jinja2
    ingredients = database.retrieve_ingredients()
    for ingredient in ingredients:
        ingredient["_id"] = str(ingredient["_id"])

    return render_template("create_recipe.html", ingredients=ingredients)


# Route: Update Recipe
@app.route("/update_recipe/<recipe_id>", methods=["GET", "POST"])
def update_recipe(recipe_id):
    if request.method == "POST":
        name = request.form["name"]
        instructions = request.form["instructions"]
        ingredient_ids = request.form.getlist("ingredient_ids[]")
        ingredient_quantities = request.form.getlist("ingredient_quantities[]")

        total_calories = float(request.form["total_calories"])

        # Prepare ingredients list
        formatted_ingredients = [
            {
                "ingredient_id": ObjectId(ingredient_id),
                "quantity": float(quantity),
            }
            for ingredient_id, quantity in zip(ingredient_ids, ingredient_quantities)
        ]

        # Update the recipe
        updated_recipe = {
            "name": name,
            "instructions": instructions,
            "ingredients": formatted_ingredients,
            "total_calories": total_calories,
            "created_by": session["user_id"],
        }

        database.update_recipe(recipe_id, updated_recipe)
        return redirect(url_for("get_recipes"))

    # Get the recipe and ingredients from the database
    recipe = database.retrieve_recipe_by_id(ObjectId(recipe_id))
    ingredients = database.retrieve_ingredients()

    # Convert ObjectId to string for JSON serialization
    recipe["_id"] = str(recipe["_id"])
    for ingredient in recipe["ingredients"]:
        ingredient["ingredient_id"] = str(ingredient["ingredient_id"])
    for ingredient in ingredients:
        ingredient["_id"] = str(ingredient["_id"])

    return render_template("update_recipe.html", recipe=recipe, ingredients=ingredients)

# Route: Delete Recipe
@app.route("/delete_recipe/<recipe_id>")
def delete_recipe(recipe_id):
    database.delete_recipe(recipe_id)
    return redirect(url_for("get_recipes"))

@app.route("/profile")
def get_profile():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("get_post_login_user"))
    
    user = database.retrieve_user_by_id(user_id)
    return render_template("profile.html", user=user)
@app.route('/update_profile', methods=['GET', 'POST'])
def update_profile():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('get_post_login_user'))

    user = database.retrieve_user_by_id(user_id)
    if not user:
        return redirect(url_for('get_post_login_user'))

    if request.method == 'POST':
        height = float(request.form['height'])
        weight = float(request.form['weight'])
        target_weight = float(request.form['target_weight'])

        # Calculate BMI
        bmi = weight / ((height / 100) ** 2)

        # Update user profile
        updated_profile = {
            'height': height,
            'weight': weight,
            'bmi': bmi,
            'target_weight': target_weight
        }
        database.update_user(user_id, updated_profile)
        return redirect(url_for('get_profile'))

    return render_template('update_profile.html', user=user)


@app.route('/dashboard')
def dashboard():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('get_post_login_user'))

    user = database.retrieve_user_by_id(user_id)
    if not user:
        return redirect(url_for('get_post_login_user'))

    return render_template('dashboard.html', user=user)

@app.route("/logout")
def logout():
    session.clear()  # Clear the session
    return redirect(url_for("get_index"))  # Redirect to login page


