from flask import Flask, app, render_template, request, redirect, url_for
from database import database, Ticket, Comment
import os

# Application factory pattern, we wrap our application setup in 
# a function so we can easily create multiple instances of our app if needed.
def create_app():
    app = Flask(__name__)

    # Stores our database in a file called helpdesk.db in the same directory as our app.py file.
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///helpdesk.db" 


    # Turn off backround features that we don't really need for this project.
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False  

    # 'database' is an instance of SQLAlchemy we created in database.py
    # Through this linem we create a connection between our database and
    # our Flask application so the two can communicate.
    database.init_app(app)  

    # Think of this block of code as setting up our database. with app.app_context() creates 
    # a temporary enviroment where we can interact with our database. database.create_all() checks
    # if our database file (helpdesk.db, the place where our database information is stored) already
    # has the information required (so our tables), and if not, it creates the file and adds all 
    # necessary information. 
    
    with app.app_context(): # Creates the database enviornment for our application.
        # If the database information such as our tables are not already in our 
        # environemnt (helpdesk.db), create them using the defined tables in our database.py file.
        database.create_all()  

    # This is simple. Whenever we visit the root URL
    @app.route("/") 
    def dashboard():    # Run this function.
        return render_template("dashboard.html") # display dashboard.html.

    return app

if __name__ == "__main__":
    app = create_app() # Create an instance of our Flask application using the create_app function.
    app.run(debug = True)