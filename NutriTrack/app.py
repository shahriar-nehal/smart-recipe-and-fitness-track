import datetime
from flask import Flask, flash, render_template, request, redirect, url_for
import database
from bson.objectid import ObjectId
import pymongo
from pymongo import MongoClient
from flask import session
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.secret_key = "123456"  # Replace with a strong secret key


# List of pets, showing related kind information
@app.route("/")
@app.route("/index")
def get_index():
    return render_template("index.html")


@app.route("/activities")
def get_activity_list():
    user_id = session.get("user_id")  # Retrieve user ID from session
    if not user_id:
        return redirect(url_for("get_index"))  # Redirect to login if not logged in
    
    # Fetch activities for the logged-in user
    activities = database.retrieve_activities_by_user_id(user_id)
    return render_template("activities.html", activities=activities)


# Get, Post, Create activity
@app.route("/create_activity", methods=["GET", "POST"])
def get_post_create_activity():
    if request.method == "POST":
        new_activity = {
            "user_id": session.get("user_id"),
            "type": request.form["type"],
            "duration": int(request.form["duration"]),
            "calories_burned": int(request.form["calories_burned"]),
            "date": request.form["date"]
        }
        database.create_activity(new_activity)
        return redirect(url_for("get_activity_list"))
    return render_template("create_activity.html")

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

@app.route("/delete_activity/<activity_id>", methods=["POST"])
def delete_activity(activity_id):
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("get_post_login_user"))
    
    database.delete_activity(activity_id, user_id)
    return redirect(url_for("get_activity_list"))

@app.route("/update_activity/<activity_id>", methods=["GET", "POST"])
def update_activity(activity_id):
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("get_post_login_user"))
    
    if request.method == "POST":
        updated_activity = {
            "type": request.form["type"],
            "duration": int(request.form["duration"]),
            "calories_burned": int(request.form["calories_burned"]),
            "date": request.form["date"]
        }
        database.update_activity(activity_id, updated_activity, user_id)
        return redirect(url_for("get_activity_list"))
    
    # Fetch the activity to pre-fill the form
    activity = database.get_activity_by_id(activity_id, user_id)
    if not activity:
        return redirect(url_for("get_activity_list"))  # Redirect if activity not found or not owned by user
    return render_template("update_activity.html", activity=activity)

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


