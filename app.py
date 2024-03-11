from flask import Flask, render_template, request, redirect, url_for, make_response
import csv
import pandas as pd
import os

app = Flask(__name__)

class FoodApplication:
    def __init__(self):
        self.users = {'user': 'password'}  # User credentials (username: password)
        self.recipes = {}  # Recipe data (name: details)
        self.reviews = {}  # Reviews data (recipe_id: [review1, review2, ...])
        self.folders = {}  # User folders (username: [folder1, folder2, ...])


    def preprocess_dataset(dataset_path):
        # Read the dataset into a Pandas DataFrame
        df = pd.read_csv(dataset_path)

        # Convert time durations to a consistent format (PTxxHxxM)
        time_columns = ['CookTime', 'PrepTime', 'TotalTime']
        for column in time_columns:
            df[column] = df[column].apply(lambda x: f'PT{x.upper()}' if pd.notnull(x) else x)

        # Convert DatePublished to a datetime object
        df['DatePublished'] = pd.to_datetime(df['DatePublished'])

        # Handle missing values
        df = df.fillna('NA')

        # Process Ingredients
        df['RecipeIngredientQuantities'] = df['RecipeIngredientQuantities'].apply(
        lambda x: [item.strip() for item in x.split(',')] if pd.notna(x) else []
    )
        df['RecipeIngredientParts'] = df['RecipeIngredientParts'].apply(
        lambda x: [item.strip() for item in x.split(',')] if pd.notna(x) else []
    )

        return df

    # Example usage:
    dataset_path = 'resource/recipes.csv'  # Replace with the actual path to your dataset
    preprocessed_df = preprocess_dataset(dataset_path)

    def read_recipes_from_csv(self, file_path):
        # Read recipes from CSV file and populate the recipes dictionary
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                self.recipes[row['RecipeId']] = {
                    'Name': row['Name'],
                    'Details': row['Description'],  # Using 'Description' as a substitute for 'Details'
                    'AuthorId': row['AuthorId'],
                    'CookTime': row['CookTime'],
                    'PrepTime': row['PrepTime'],
                    'TotalTime': row['TotalTime'],
                    'DatePublished': row['DatePublished'],
                    'Images': row['Images'],
                    'RecipeCategory': row['RecipeCategory'],
                    'Keywords': row['Keywords'],
                    'RecipeIngredientQuantities': row['RecipeIngredientQuantities'],
                    'RecipeIngredientParts': row['RecipeIngredientParts'],
                    'AggregatedRating': row['AggregatedRating'],
                    'ReviewCount': row['ReviewCount'],
                    'Calories': row['Calories'],
                    'FatContent': row['FatContent'],
                    'SaturatedFatContent': row['SaturatedFatContent'],
                    'CholesterolContent': row['CholesterolContent'],
                    'SodiumContent': row['SodiumContent'],
                    'CarbohydrateContent': row['CarbohydrateContent'],
                    'FiberContent': row['FiberContent'],
                    'SugarContent': row['SugarContent'],
                    'ProteinContent': row['ProteinContent'],
                    'RecipeServings': row['RecipeServings'],
                    'RecipeYield': row['RecipeYield'],
                    'RecipeInstructions': row['RecipeInstructions'],
            }   





    def read_reviews_from_csv(self, file_path):
    # Read reviews from CSV file and populate the reviews dictionary
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                recipe_id = row['RecipeId']
                if recipe_id not in self.reviews:
                    self.reviews[recipe_id] = []
                self.reviews[recipe_id].append({
                    'ReviewId': row['ReviewId'],
                    'AuthorId': row['AuthorId'],
                    'AuthorName': row['AuthorName'],
                    'Rating': row['Rating'],
                    'Review': row['Review'],
                    'DateSubmitted': row['DateSubmitted'],
                    'DateModified': row['DateModified'],
            })


    def user_authentication(self, username, password):
        # Check if the user is registered with the application
        if username in self.users and self.users[username] == password:
            return True
        else:
            return False

    def recipe_search(self, user, query):
        # Check if the user is logged in
        if user in self.users:
            # Perform recipe search based on the query
            search_results = []
            for recipe_id, recipe_data in self.recipes.items():
                if query.lower() in recipe_data['Name'].lower() or query.lower() in recipe_data['Details'].lower():
                    search_results.append((recipe_id, recipe_data))
            return search_results

    def get_reviews_for_recipe(self, recipe_id):
        # Get reviews for a specific recipe
        return self.reviews.get(recipe_id, [])

    def personalized_recommendations(self, user):
        # Display personalized recommendations on the landing page
        if user in self.users and user in self.folders:
            # You might want to implement recommendation logic based on user's folders and bookmarks
            # Display recommendations to the user
            return [f"Recommendation 1 for {user}", f"Recommendation 2 for {user}"]
        else:
            return []

food_app = FoodApplication()
food_app.read_recipes_from_csv('resource/recipes.csv')  # Assuming you have a method to read recipes from CSV
food_app.read_reviews_from_csv('resource/reviews.csv')  # Assuming you have a method to read reviews from CSV

@app.route('/')
def home():
    # Check if the user is authenticated, if not, redirect to the login page
    if 'user' not in request.cookies or not food_app.user_authentication(request.cookies['user'], request.cookies['password']):
        return redirect(url_for('login'))

    user = request.cookies['user']
    recommendations = food_app.personalized_recommendations(user)
    return render_template('home.html', user=user, recommendations=recommendations)

@app.route('/search', methods=['GET', 'POST'])
def search():
    # Check if the user is authenticated, if not, redirect to the login page
    if 'user' not in request.cookies or not food_app.user_authentication(request.cookies['user'], request.cookies['password']):
        return redirect(url_for('login'))

    if request.method == 'POST':
        query = request.form['query']
        search_results = food_app.recipe_search(request.cookies['user'], query)

        # Limit the search results to the top 5
        search_results = search_results[:5]

        # Ensure that search_results is a list of tuples with (recipe_id, recipe_data)
        return render_template('search_results.html', user=request.cookies['user'], search_results=search_results)

    return render_template('search.html', user=request.cookies['user'])

@app.route('/recipe/<recipe_id>')
def recipe(recipe_id):
    # Check if the user is authenticated, if not, redirect to the login page
    if 'user' not in request.cookies or not food_app.user_authentication(request.cookies['user'], request.cookies['password']):
        return redirect(url_for('login'))

    user = request.cookies['user']
    recipe_data = food_app.recipes.get(recipe_id)
    if recipe_data:
        reviews = food_app.get_reviews_for_recipe(recipe_id)
        return render_template('recipe_detail.html', user=user, recipe_data=recipe_data, reviews=reviews)

    return render_template('error.html', message="Recipe not found")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        print(f"Attempting login for user: {username}, password: {password}")
        if food_app.user_authentication(username, password):
            print(f"Login successful for user: {username}")
            response = make_response(redirect(url_for('home')))
            response.set_cookie('user', username)
            response.set_cookie('password', password)
            print("Cookies set:", request.cookies)
            return response
        else:
            print(f"Login failed for user: {username}")
            return render_template('login.html', error="Invalid username or password")

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        food_app.users[username] = password
        response = make_response(redirect(url_for('login')))
        response.set_cookie('user', username)
        response.set_cookie('password', password)
        return response

    return render_template('register.html')

if __name__ == '__main__':
    app.run(debug=True)
