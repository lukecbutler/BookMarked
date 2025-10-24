from flask import Flask, request, jsonify, render_template_string
from flask_sqlalchemy import SQLAlchemy
from datetime import date # Import date for Date columns

app = Flask(__name__)

# Ensure this matches your database file name
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Sprint1db.db'

# Create the SQLAlchemy instance linked to the app
database = SQLAlchemy(app)

# --- Model Definitions (Copied Exactly) ---

class LibraryBranch(database.Model):

    __tablename__ = 'LibraryBranch'

    BranchID = database.Column(database.Integer, primary_key=True, autoincrement=True)
    BranchName = database.Column(database.String(50))

class ItemType(database.Model):

    __tablename__ = 'ItemType'

    TypeID = database.Column(database.Integer, primary_key=True, autoincrement=True)
    TypeName = database.Column(database.String(30))
    RentalLength = database.Column(database.Integer)
    PerDayFine = database.Column(database.Numeric(10, 2))

class LibraryItem(database.Model):

    __tablename__ = 'LibraryItem'

    ItemID = database.Column(database.Integer, primary_key=True, autoincrement=True)
    ItemType = database.Column(database.Integer, database.ForeignKey('ItemType.TypeID'))
    AquisitionDate = database.Column(database.Date)
    Cost = database.Column(database.Numeric(10, 2))
    ItemTitle = database.Column(database.String(50))
    Availability = database.Column(database.Boolean)
    ShelfCode = database.Column(database.String(5))

class Patron(database.Model):
    
    __tablename__ = 'Patron'

    PatronID = database.Column(database.Integer, primary_key=True, autoincrement=True)
    PatronFN = database.Column(database.String(50))
    PatronLN = database.Column(database.String(50))
    AccountExpDate = database.Column(database.Date)
    FeesOwed = database.Column(database.Numeric(10, 2))
    ItemsCheckedOut = database.Column(database.Integer)

class Checkout(database.Model):

    __tablename__ = 'Checkout'

    TransactionID = database.Column(database.Integer, primary_key=True, autoincrement=True)
    PatronID = database.Column(database.Integer, database.ForeignKey('Patron.PatronID'))
    ItemID = database.Column(database.Integer, database.ForeignKey('LibraryItem.ItemID'))
    CheckoutDate = database.Column(database.Date)

class Return(database.Model):

    __tablename__ = 'Return'

    TransactionID = database.Column(database.Integer, database.ForeignKey('Checkout.TransactionID'), primary_key=True)
    DateReturned = database.Column(database.Date)
    BranchReturnedTo = database.Column(database.Integer, database.ForeignKey('LibraryBranch.BranchID'))


# --- Routes ---
@app.route('/')
def home():
    """Returns a JSON list of all patrons."""
    try:
        # Use the exact model and column names provided
        all_patrons = Patron.query.all()
        patrons_list = [
            {"PatronID": p.PatronID, "FName": p.PatronFN, "LName": p.PatronLN}
            for p in all_patrons
        ]
        return jsonify(patrons_list)
    
    except Exception as e:
        app.logger.error(f"Error fetching patrons: {e}") # Log the error for debugging
        # Provide a more informative error response
        return jsonify({"error": "Could not fetch patrons", "details": str(e)}), 500

# --- Main execution block ---
if __name__ == '__main__':
    with app.app_context():
        # Create database tables if they don't exist based on the models defined above
        database.create_all()
    # Run the Flask development server
    # Port 5000 is standard for local Flask dev
    app.run(debug=True, host='0.0.0.0', port=80)
