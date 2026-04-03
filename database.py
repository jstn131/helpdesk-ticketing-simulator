# This file will define the database structure using
# SQLAlchemy. So instead of writing raw SQL, we define
# Python classes that SQLAlchemy will convert into database
# tables automatically!

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Create an instance of the database
database = SQLAlchemy()

# Create a Ticket model to represent support tickets in the system
class Ticket(database.Model):
    # This is the name of the table in the database
    __tablename__ = "tickets"

    # Define an Integer column named id and mark it as the primary key so each
    # record is automatically assigned a unique identifier.
    id = database.Column(database.Integer, primary_key = True) 

    # Define a String column named title (max length 100) and require it to be
    # non-null so every ticket has a title.
    title = database.Column(database.String(100), nullable = False)

    # Define a Text column named description and require it to be non-null since 
    # every ticket should be well described.
    description = database.Column(database.Text, nullable = False)

    # Define a String column named priority (max length 20) and require it to be non-null so every
    # ticket has a priority level.
    priority = database.Column(database.String(20), nullable = False)

    # Define a String column named status (max length 20) and set a default value of "Open" so 
    # new tickets are automatically marked as open. 
    status = database.Column(database.String(20), default = "Open")

    # Define a String column named assigned_to (max length 100) and set a defualt value
    # of "Unassigned" so new tickets are automatically marked as unassigned. This section
    # will be used to give tickets to "agents".
    assigned_to = database.Column(database.String(100), default = "Unassigned")

    # Define DateTime columns to track when the ticket is created and last updated.
    # "default" sets the initial timestamp, and "onupdate" refreshes it on updates.
    created_at = database.Column(database.DateTime, default = datetime.utcnow)
    updated_at = database.Column(database.DateTime, default = datetime.utcnow, onupdate = datetime.utcnow)


    # Define a relationship which gives python access to all comments related to a ticket.
    # 'Comment" tells SQLAlchemy the related model, "backref" automatically adds an attribute
    # on the Comment model called ticket. lazy = True means that the related comments will only be loaded
    # when we actually ask for them.
    comments = database.relationship("Comment", backref = "ticket", lazy = True)

    def __repr__(self):
        return f"<Ticket {self.id}: {self.title}>"


# Create a Comment model to represent comments on tickets.
class Comment(database.Model):
    __tablename__ = "comments"

    id = database.Column(database.Integer, primary_key = True)

    # Define an Integer column named ticket_id and mark it as a foreign key
    # referencing tickets.id. This links each comment to the ticket it belongs to.
    ticket_id = database.Column(database.Integer, database.ForeignKey("tickets.id"), nullable = False)

    note = database.Column(database.Text, nullable = False)

    # created_at tracks when the comment was made, giving it the current timestap by default.
    created_at = database.Column(database.DateTime, default = datetime.utcnow)
    def __repr__(self):
        return f"<Comment {self.id} on Ticket {self.ticket_id}>"
