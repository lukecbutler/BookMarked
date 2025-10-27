import os
from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import date

app = Flask(__name__)

# Create db route
db_dir = app.instance_path
os.makedirs(db_dir, exist_ok=True)
db_path = os.path.join(db_dir, 'sprint1db.db') 

# Configure database
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Create the SQLAlchemy instance linked to the app
database = SQLAlchemy(app)

#### --- Database Models --- ####
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


# should we have account expiration date or calculate expiration on account creation dates?? - we can check the account expiration date in the patron table. That's how I populated the db. Your function below looks good. Also berker this is fire nice fing job. ~ Luke
# def membership_expired(patron) -> bool:
#     if not patron or not patron.AccountCreatedDate:
#         return False
#     days_since_account_created = (date.today() - patron.AccountCreatedDate).days
#     return days_since_account_created >= 365

#### --- Core Logic --- ####
def membership_expired(patron: Patron) -> bool:
    '''
    This function checks if a patron's account is expired
    Returns TRUE if expired
    Returns FALSE if not expired
    '''
    return bool(patron and patron.AccountExpDate and patron.AccountExpDate < date.today())

#### --- Routes --- ####
MAX_ITEMS_PER_PATRON = 20

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/patrons')
def patrons() -> jsonify:
    '''This route returns JSON data of all patrons in the database'''
    all_patrons = Patron.query.all()
    patrons_list = []

    for p in all_patrons:
        patron_data = {
            "PatronID": p.PatronID,
            "FName": p.PatronFN,
            "LName": p.PatronLN,
            "Fees": p.FeesOwed
        }
        patrons_list.append(patron_data)

    return jsonify(patrons_list)


#### API Endpoints for Dropdown Menu's on Front-end ####
@app.route('/api/itemtypes')
def api_item_types() -> jsonify:
    '''This function returns all item types from the database in JSON format'''
    
    all_types = ItemType.query.order_by(ItemType.TypeName).all() # Query all ItemType objects from the db
    types_list = [] # Init empty list to store JSON dicts

    # Loop through all types in db, create new dict for each TypeID & TypeName, add to JSON list of dicts
    for t in all_types:
        type_data = {
            "TypeID": t.TypeID,
            "TypeName": t.TypeName
        }
        types_list.append(type_data)

    return jsonify(types_list) # Convert the list of dictionaries to a JSON response

@app.route('/api/items')
def api_items_by_type():
    '''This function returns list all library items (ID & Title) in JSON format'''
    type_id_from_url = request.args.get('type_id', '').strip() # check for query parameter in url

    query = LibraryItem.query
    if type_id_from_url.isdigit(): 
        query = query.filter(LibraryItem.ItemType == int(type_id_from_url))

    items_from_db = query.order_by(LibraryItem.ItemTitle).all()

    output_list = []
    for item in items_from_db:
        item_data = {
            "ItemID": item.ItemID,
            "ItemTitle": item.ItemTitle
        }

        output_list.append(item_data)
    return jsonify(output_list)



# Checkout demo page + post
#---------------------------

@app.route('/checkout', methods=['GET'])
def checkout_form():
    return render_template('checkout.html') # loading demo page for now

@app.route('/checkout', methods=['POST'])
def checkout_basic() -> jsonify:
    payload = request.get_json(silent=True) or request.form
    patron_id = int(payload.get('patron_id', -1))
    item_id = int(payload.get('item_id', -1))

    patron = Patron.query.get(patron_id)
    item = LibraryItem.query.get(item_id)

    # if patron exists
    if patron is None:
        return jsonify({"ok": False, "error": "Patron not found"})
    # if item exists
    if item is None:
        return jsonify({"ok": False, "error": "Item not found"})

    # check for expired membership
    if membership_expired(patron):
        return jsonify({
            "ok": False,
            "message": "RENEW MEMBERSHIP NOW!!",
            "expired_on": str(patron.AccountExpDate)
        })

    # check availability
    if item.Availability is False:
        return jsonify({"ok": False, "error": "Item not available"})

    # check if patron at 20 items
    current_count = patron.ItemsCheckedOut or 0
    if current_count >= MAX_ITEMS_PER_PATRON:
        return jsonify({"ok": False, "error": "Individual checkout limit reached (20 items)"})
    
    # create checkout record
    new_checkout = Checkout(
        PatronID=patron_id, 
        ItemID=item_id, 
        CheckoutDate=date.today()
    )
    database.session.add(new_checkout)
    # update item and patron info
    item.Availability = False
    patron.ItemsCheckedOut = current_count + 1
    database.session.commit()

    #showing currently checkedout items for patron
    active_checkouts = (
        database.session.query(Checkout, LibraryItem, Patron)
        .join(LibraryItem, Checkout.ItemID == LibraryItem.ItemID)
        .join(Patron, Checkout.PatronID == Patron.PatronID)
        .outerjoin(Return, Return.TransactionID == Checkout.TransactionID)
        .filter(
            Return.TransactionID.is_(None),
            Checkout.PatronID == patron_id
        )
        .order_by(Checkout.CheckoutDate.desc(), Checkout.TransactionID.desc())
        .all()
    )

    checked_out_list = [
        {
            "TransactionID": checkout.TransactionID,
            "PatronID": patron.PatronID,
            "PatronName": f"{patron.PatronFN} {patron.PatronLN}",
            "ItemID": item.ItemID,
            "ItemTitle": item.ItemTitle,
            "CheckoutDate": str(checkout.CheckoutDate)
        }
        for checkout, item, patron in active_checkouts
    ]

    return jsonify({
        "ok": True,
        "message": "Checkout recorded.",
        "patron_id": patron_id,
        "item_id": item_id,
        "checkout_date": str(date.today()),
        "checked_out": checked_out_list
    })



# Utility
# ----------------------------
@app.route('/dbinfo', methods=['GET'])
def dbinfo():
    return jsonify({"db_uri":app.config['SQLALCHEMY_DATABASE_URI']})




# --- Main execution block ---
if __name__ == '__main__':

    with app.app_context():
        database.create_all()

    #BERKER: Updated port to 5001, had problems with 80.
    app.run(debug=True, host='0.0.0.0', port=5001)
