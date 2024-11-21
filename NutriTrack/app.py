from flask import Flask, flash, render_template, request, redirect, url_for
import database
import pymongo
from pymongo import MongoClient
from flask import session
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
@app.route("/register", methods=["GET", "POST"])
def get_post_register_user():
    if request.method == "POST":
        new_user = {
            "username": request.form["username"],
            "email": request.form["email"],
            "password": request.form["password"]
        }
        database.create_user(new_user)        
        return redirect(url_for("get_index"))
    return render_template("register.html")

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
            session["user_id"] = user["id"]  # Store user ID in session
            return redirect(url_for("get_activity_list"))
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
def view_recipes():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("get_post_login_user"))
    recipes = database.retrieve_recipes()
    return render_template("recipes.html", recipes=recipes)

@app.route("/create_recipe", methods=["GET", "POST"])
def create_recipe():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("get_post_login_user"))
    
    if request.method == "POST":
        name = request.form["name"]
        instructions = request.form["instructions"]
        total_calories = float(request.form["total_calories"])
        ingredients = []
        for i in range(len(request.form.getlist("ingredient_id"))):
            ingredients.append({
                "ingredient_id": int(request.form.getlist("ingredient_id")[i]),
                "quantity": int(request.form.getlist("quantity")[i])
            })
        new_recipe = {
            "name": name,
            "ingredients": ingredients,
            "instructions": instructions,
            "total_calories": total_calories,
            "created_by": user_id
        }
        database.create_recipe(new_recipe)
        return redirect(url_for("view_recipes"))
    
    all_ingredients = database.retrieve_ingredients()
    return render_template("create_recipe.html", ingredients=all_ingredients)

@app.route("/update_recipe/<recipe_id>", methods=["GET", "POST"])
def update_recipe(recipe_id):
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("get_post_login_user"))
    
    if request.method == "POST":
        name = request.form["name"]
        instructions = request.form["instructions"]
        total_calories = float(request.form["total_calories"])
        ingredients = []
        for i in range(len(request.form.getlist("ingredient_id"))):
            ingredients.append({
                "ingredient_id": int(request.form.getlist("ingredient_id")[i]),
                "quantity": int(request.form.getlist("quantity")[i])
            })
        updated_recipe = {
            "name": name,
            "ingredients": ingredients,
            "instructions": instructions,
            "total_calories": total_calories,
        }
        database.update_recipe(recipe_id, updated_recipe)
        return redirect(url_for("view_recipes"))
    
    recipe = database.retrieve_recipe_by_id(recipe_id)
    if not recipe:
        return redirect(url_for("view_recipes"))
    all_ingredients = database.retrieve_ingredients()
    return render_template("update_recipe.html", recipe=recipe, ingredients=all_ingredients)

@app.route("/delete_recipe/<recipe_id>", methods=["POST"])
def delete_recipe(recipe_id):
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("get_post_login_user"))
    
    database.delete_recipe(recipe_id)
    return redirect(url_for("view_recipes"))

@app.route("/profile")
def get_profile():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("get_post_login_user"))
    
    user = database.get_user_by_id(user_id)
    return render_template("profile.html", user=user)

@app.route("/logout")
def logout():
    session.clear()  # Clear the session
    return redirect(url_for("get_index"))  # Redirect to login page


