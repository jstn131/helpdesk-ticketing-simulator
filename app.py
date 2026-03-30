from flask import Flask, render_template, request, redirect, url_for
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
        total_tickets = Ticket.query.count() # Get the total number of tickets in our database.
        
        # Here we use the filter_by method to search for any tickets that have the open status.
        open_tickets = Ticket.query.filter_by(status = "Open").count() # Get the number of open tickets in our database.

        # Filter for tickets with the In Progress status.
        in_progress = Ticket.query.filter_by(status = "In Progress").count() # Get the number of in progress tickets in our database.

        # Filter for tickets with resolved status
        resolved_tickets = Ticket.query.filter_by(status = "Resolved").count() # Get the number of closed tickets in our database.

        # Filter for tickets with closed status
        closed_tickets = Ticket.query.filter_by(status = "Closed").count() # Get the number of closed tickets in our database.

        # We will use this following function to ensure that our dashboard will 
        # have a graph display the percentage of completed tickets that we have.

        completed = resolved_tickets + closed_tickets # Calculate number of tickets no longer in progress

        if total_tickets > 0: # If we have any tickets at all, then calculate the percentage of completed tickets.
            completion_percentage = round((completed / total_tickets) * 100) 
        else: 
            completion_percentage = 0 # If we have no tickets, then the percentage of completed tickets is 0.

        # order_by method used to order tickets in descending order based on their created_at timestamp.
        # We limit it to 10 most recent tickets only and print out all results that match our query.
        recent_tickets = Ticket.query.order_by(Ticket.created_at.desc()).limit(10).all()

        # Updated return: Return all types of tickets and completed percentage alongside our dashboard.html display.
        return render_template("dashboard.html", 
                               total_tickets=total_tickets,
                               open_tickets=open_tickets, 
                               in_progress=in_progress, 
                               resolved_tickets=resolved_tickets, 
                               closed_tickets=closed_tickets, 
                               completed = completed,
                               completion_percentage=completion_percentage,
                               recent_tickets=recent_tickets)
    
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
    
    @app.route("/tickets/<int:ticket_id>")
    def ticket_detail(ticket_id):
        # Get ticket with specified ID or return 404 if not found.
        ticket = Ticket.query.get_or_404(ticket_id)

        # filter our comments to only show those that match the ticket_id of the ticket
        # we are viewing. We also order the comments in ascending order based on their created
        # time so that older tickets are shown first.
        comments = Comment.query.filter_by(ticket_id=ticket_id)\
                  .order_by(Comment.created_at.asc()).all()
        
        return render_template("view_ticket.html", ticket=ticket, comments=comments)
    
    @app.route("/tickets/<int:ticket_id>/comment", methods=["POST"])
    def add_comment(ticket_id):
        # Ensure that the ticket exists before creating a comment for it.
        ticket = Ticket.query.get_or_404(ticket_id)

        note = request.form["note"] # Get the comment note from the form.
        # Create a new Comment object using our Comment class in database.
        comment = Comment(note = note, ticket_id = ticket_id)

        database.session.add(comment)
        database.session.commit()

        # Return the user back to the ticket detail page after they have added a comment.
        return redirect(url_for("ticket_detail", ticket_id=ticket_id))

    @app.route("/tickets/<int:ticket_id>/edit", methods=["GET", "POST"])
    def edit_ticket(ticket_id):
        ticket = Ticket.query.get_or_404(ticket_id)

        if request.method == "POST":
            ticket.status = request.form["status"] # Update the ticket's status with the new value from the form.
            ticket.priority = request.form["priority"] # Update the ticket's priority with the new value from the form.
            ticket.assigned_to = request.form["assigned_to"] # Update the ticket's assigned_to with the new value from the form.

            database.session.commit()

            return redirect(url_for("ticket_detail", ticket_id=ticket.id))

        # If the user is just visiting the edit page, show the edit_ticket.html file.
        return render_template("edit_ticket.html", ticket=ticket)
    

    # AI Implementation: This route will allow us to view all tickets.
    @app.route("/tickets")
    def all_tickets():
        # Get search and filter values from URL parameters
        search   = request.args.get("search", "")
        priority = request.args.get("priority", "")
        status   = request.args.get("status", "")

        # Start with all tickets
        query = Ticket.query

        # Apply search filter if user typed something
        if search:
            query = query.filter(Ticket.title.like(f"%{search}%"))

        # Apply priority filter if selected
        if priority:
            query = query.filter_by(priority=priority)

        # Apply status filter if selected
        if status:
            query = query.filter_by(status=status)

        # Execute query ordered by newest first
        tickets = query.order_by(Ticket.created_at.desc()).all()

        return render_template("tickets.html",
                            tickets=tickets,
                            search=search,
                            priority=priority,
                            status=status)

    return app

if __name__ == "__main__":
    app = create_app() # Create an instance of our Flask application using the create_app function.
    app.run(debug = True)