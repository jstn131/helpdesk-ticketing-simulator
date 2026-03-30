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

        # TODO: Remove this test code later.
        # TEST TO CHECK IF OUR TICKET IS CREATED PROPERLY
        tickets = Ticket.query.all()
        print(tickets)  


        return render_template("dashboard.html") # display dashboard.html.


    # If we visit the URL /tickets/new, run this function. 
    # POST will send data to requested body.
    # GET will just get the page without sending any data. 
    @app.route("/tickets/new", methods = ["GET", "POST"])
    def new_ticket():
        if request.method == "POST": # If we submit the form on the new ticket page
            title = request.form["title"] # Get the title from the form.
            description = request.form["description"] # Get the description from the form.
            priority = request.form["priority"] # Get the priority from the form.
            assigned_to = request.form["assigned_to"] # Get the assigned_to from the form.

        # Create a new Ticket object using our Ticket class in database.py
            ticket = Ticket(
                title = title,
                description = description,
                priority = priority,
                assigned_to = assigned_to
            )

            database.session.add(ticket) # Add the new ticket to our database session.
            database.session.commit() # Commit the session to save the ticket in our database.

            return redirect(url_for("dashboard")) # After saving, redirect us back to the dashboard.
        return render_template("new_ticket.html") # If we just visit the page, show the new_ticket.html form.

    return app

if __name__ == "__main__":
    app = create_app() # Create an instance of our Flask application using the create_app function.
    app.run(debug = True)