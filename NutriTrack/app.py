from flask import Flask, flash, jsonify, render_template, request, redirect, url_for
import database
#from bson.objectid import ObjectId
from bson import errors, ObjectId
import pymongo
from pymongo import MongoClient
from flask import session
from werkzeug.security import generate_password_hash
from pprint import pprint
from bson.errors import InvalidId
from datetime import datetime, timedelta

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
        gender = request.form['gender']
        dob = request.form['dob']
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
            'gender': gender,
            'dob': dob,
            'height': height,
            'weight': weight,
            'bmi': bmi,
            'target_weight': target_weight
        }

        # Insert the new user into the database
        database.create_user(new_user)        
        return redirect(url_for("get_index"))

    return render_template('register.html')

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
            'email': user['email'],
            'password': user['password'],
            'dob': user['dob'],
            'gender': user['gender'],
            'height': height,
            'weight': weight,
            'bmi': bmi,
            'target_weight': target_weight
        }
        database.update_user(user_id, updated_profile)
        return redirect(url_for('get_profile'))

    return render_template('update_profile.html', user=user)

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
    earned_badges = database.get_earned_badges(user_id)
    return render_template("activity_log.html", activity_logs=activity_logs, badges=earned_badges)


@app.route("/create_activity_log", methods=["GET", "POST"])
def get_post_create_activity_log():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("get_post_login_user"))

    if request.method == "POST":
        activity_id = request.form.get("activity_id")
        duration = request.form.get("duration")
        date = request.form.get("date")
        time = request.form.get("time")
        start_latitude = request.form.get("start_latitude")
        start_longitude = request.form.get("start_longitude")
        end_latitude = request.form.get("end_latitude")
        end_longitude = request.form.get("end_longitude")

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
            "date": date,
            "time":time,
            "start_latitude": float(start_latitude) if start_latitude else None,
            "start_longitude": float(start_longitude) if start_longitude else None,
            "end_latitude": float(end_latitude) if end_latitude else None,
            "end_longitude": float(end_longitude) if end_longitude else None,
            "activity_name": activity["name"],
            "bmi": bmi,
        }
        database.create_activity_log(new_activity_log)
        flash("Activity log created successfully!", "success")
        database.assign_badges(user_id)
        return redirect(url_for("get_activity_logs"))

    # Retrieve activities for the dropdown
    activities = database.retrieve_activities()
    return render_template("create_activity_log.html", activities=activities)

@app.route('/view_route/<log_id>')
def view_route(log_id):
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("get_post_login_user"))
    log = database.get_activity_log_by_id(log_id, user_id)
    if not log:
        flash("Activity log not found.", "error")
        return redirect(url_for('get_activity_logs'))
    
    start_coords = (log['start_latitude'], log['start_longitude']) if log['start_latitude'] and log['start_longitude'] else None
    end_coords = (log['end_latitude'], log['end_longitude']) if log['end_latitude'] and log['end_longitude'] else None
    
    return render_template('view_route.html', start_coords=start_coords, end_coords=end_coords)


@app.route("/update_activity_log/<log_id>", methods=["GET", "POST"])
def update_activity_log(log_id):
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("get_post_login_user"))

    log = database.get_activity_log_by_id(log_id,user_id)
    if not log:
        flash("Activity log not found.", "error")
        return redirect(url_for("get_activity_logs"))

    if request.method == "POST":
        activity_id = request.form.get("activity_id")
        duration = request.form.get("duration")
        date = request.form.get("date")
        time = request.form.get("time")
        start_latitude = request.form.get("start_latitude")
        start_longitude = request.form.get("start_longitude")
        end_latitude = request.form.get("end_latitude")
        end_longitude = request.form.get("end_longitude")

        # Validate inputs
        if not activity_id or not duration:
            flash("Please fill all fields!", "error")
            return redirect(url_for("update_activity_log", log_id=log_id))

        try:
            # Ensure the activity_id is a valid ObjectId
            activity_id = ObjectId(activity_id)
        except InvalidId:
            flash("Invalid activity selected. Please try again.", "error")
            return redirect(url_for("update_activity_log", log_id=log_id))

        try:
            duration = float(duration)  # Convert duration to float
        except ValueError:
            flash("Invalid duration. Please enter a valid number.", "error")
            return redirect(url_for("update_activity_log", log_id=log_id))

        # Get user information
        user = database.retrieve_user_by_id(user_id)
        weight_kg = user.get("weight")
        height_m = user.get("height") / 100  # Convert cm to meters
        bmi = weight_kg / (height_m ** 2)

        # Get activity MET value
        activity = database.get_activity_by_id(activity_id)
        if not activity:
            flash("Activity not found. Please try again.", "error")
            return redirect(url_for("update_activity_log", log_id=log_id))

        met_value = activity["met_value"]

        # Calculate calories burned
        calories_burned = met_value * weight_kg * (duration / 60)

        # Update the activity log
        updated_activity_log = {
            "user_id": user_id,
            "activity_id": str(activity_id),
            "duration": duration,
            "calories_burned": calories_burned,
            "date": date,
            "time": time,
            "start_latitude": float(start_latitude) if start_latitude else None,
            "start_longitude": float(start_longitude) if start_longitude else None,
            "end_latitude": float(end_latitude) if end_latitude else None,
            "end_longitude": float(end_longitude) if end_longitude else None,
            "activity_name": activity["name"],
            "bmi": bmi,
        }
        database.update_activity_log(log_id, updated_activity_log,user_id)
        flash("Activity log updated successfully!", "success")
        return redirect(url_for("get_activity_logs"))

    # Retrieve activities for the dropdown
    activities = database.retrieve_activities()
    return render_template("update_activity_log.html", log=log, activities=activities)



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

@app.route("/get_recipe/<recipe_id>", methods=["GET"])
def get_recipe(recipe_id):
    recipe = database.retrieve_recipe_by_id(recipe_id)
    if not recipe:
        return jsonify({"error": "Recipe not found"}), 404
    return jsonify({
        "calories": recipe["total_calories"]
    })


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

@app.route("/meal_log")
def get_meal_logs():
    user_id = session.get("user_id")  # Retrieve user ID from session
    if not user_id:
        return redirect(url_for("get_post_login_user"))
    
    # Retrieve activity logs for the logged-in user
    meal_logs = database.retrieve_meal_logs_by_user_id(user_id)
    return render_template("meal_log.html", meal_logs=meal_logs)

@app.route("/create_meal_log", methods=["GET", "POST"])
def create_meal_log():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("get_post_login_user"))

    if request.method == "POST":
        recipe_id = request.form["recipe_id"]

        # Fetch the recipe details
        recipe = database.retrieve_recipe_by_id(recipe_id)
        if not recipe:
            flash("Invalid recipe selection!", "error")
            return redirect(url_for("create_meal_log"))

        # Prepare the meal log
        meal_log = {
            "user_id": user_id,
            "recipe_id": recipe_id,
            "meal_name": recipe["name"],
            "calories_intake": recipe["total_calories"],
            "meal_type": request.form["meal_type"],
            "date": request.form["date"],
            "time": request.form["time"],
        }
        database.create_meal_log(meal_log)
        return redirect(url_for("get_meal_logs"))

    # Retrieve all recipes for the dropdown
    recipes = database.retrieve_recipes()
    return render_template("create_meal_log.html", recipes=recipes)

@app.route("/update_meal_log/<log_id>", methods=["GET", "POST"])
def update_meal_log(log_id):
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("get_post_login_user"))

    if request.method == "POST":
        recipe_id = request.form["recipe_id"]

        # Fetch the recipe details
        recipe = database.retrieve_recipe_by_id(recipe_id)
        if not recipe:
            flash("Invalid recipe selection!", "error")
            return redirect(url_for("update_meal_log", log_id=log_id))

        # Prepare the meal log
        meal_log = {
            "user_id": user_id,
            "recipe_id": recipe_id,
            "meal_name": recipe["name"],
            "calories_intake": recipe["total_calories"],
            "meal_type": request.form["meal_type"],
            "date": request.form["date"],
            "time": request.form["time"],
        }
        database.update_meal_log(log_id, meal_log)
        return redirect(url_for("get_meal_logs"))

    # Retrieve the meal log to be updated    
    meal_log = database.retrieve_meal_by_id(log_id)
    if not meal_log:    
        return redirect(url_for("get_meal_logs"))  # Redirect if meal log not found

    # Retrieve all recipes for the dropdown
    recipes = database.retrieve_recipes()

    return render_template("update_meal_log.html", meal_log=meal_log, recipes=recipes)

@app.route("/delete_meal_log/<log_id>", methods=["POST"])
def delete_meal_log(log_id):
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("get_post_login_user"))

    database.delete_meal_log(log_id, user_id)
    return redirect(url_for("get_meal_logs"))
        
@app.route('/progress_report', methods=['GET'])
def daily_progress():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('get_post_login_user'))

    date = request.args.get('date', datetime.today().strftime('%Y-%m-%d'))
    progress_data = database.calculate_net_calories(user_id, date)
    
    return render_template('progress.html', progress_data=progress_data, date=date)

from datetime import datetime, timedelta

@app.route('/weekly_progress', methods=['GET'])
def weekly_progress():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('get_post_login_user'))

    end_date = datetime.today()
    start_date = end_date - timedelta(days=6)

    # Calculate net calories and weight change
    weekly_data, weight_change_kg = database.calculate_weekly_net_calories(user_id, start_date, end_date)

    # Retrieve and update user data
    user = database.retrieve_user_by_id(user_id)
    if user:
        current_weight = user.get('weight', 0)
        height_m = user.get('height', 0) / 100.0

        new_weight = current_weight + weight_change_kg
        new_bmi = new_weight / (height_m ** 2) if height_m > 0 else None

        database.update_user(user_id, {"weight": new_weight, "bmi": new_bmi})
    
    return render_template('weekly_progress.html', weekly_data=weekly_data, weight_change_kg=weight_change_kg)

@app.route("/badges")
def get_badges():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("get_post_login_user"))

    badges = database.retrieve_badges()
    return render_template("badges.html", badges=badges)

@app.route("/create_badge", methods=["GET", "POST"])
def get_post_create_badge():
    if request.method == "POST":
        # Collect form data
        badge_name = request.form.get("badge_name")
        badge_description = request.form.get("badge_description")
        badge_criteria = request.form.get("badge_criteria")

        # Validate inputs
        if not badge_name or not badge_description or not badge_criteria:
            flash("All fields are required to create a badge!", "error")
            return redirect(url_for("get_post_create_badge"))

        # Insert badge into the database
        new_badge = {
            "name": badge_name,
            "description": badge_description,
            "type": "criteria",  # Assuming all badges are criteria-based
            "criteria": badge_criteria
        }
        database.create_badge(new_badge)  # Custom function to insert into badges collection
        flash("Badge created successfully!", "success")
        return redirect(url_for("get_badges"))

    return render_template("create_badge.html")

@app.route('/badges/<user_id>')
def show_badges(user_id):
    # Fetch earned badges for the user
    earned_badges = database.get_earned_badges(user_id)

    # Pass earned badges to the HTML template
    return render_template('badge_earned.html', badges=earned_badges)


@app.route('/dashboard')
def dashboard():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('get_post_login_user'))

    user = database.retrieve_user_by_id(user_id)
    if not user:
        return redirect(url_for('get_post_login_user'))

    return render_template('dashboard.html', user=user)

@app.route('/about')
def about():
    current_date = datetime.now().strftime("%B %d, %Y")
    return render_template('about.html', date=current_date)


@app.route("/logout")
def logout():
    session.clear()  # Clear the session
    return redirect(url_for("get_index"))  # Redirect to login page

if __name__ == "__main__":
    app.run(debug=True)


