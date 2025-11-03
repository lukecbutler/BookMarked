import os
from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import date,timedelta

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
#Created by Jake Rouse
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


#BERKER: calculates the rental period for a library item
def rental_days_for(item: LibraryItem) -> int:
    item_type = ItemType.query.get(item.ItemType) if item else None
    return int(item_type.RentalLength) if (item_type and item_type.RentalLength) else 0

#### --- Routes --- ####
MAX_ITEMS_PER_PATRON = 20

@app.route('/')
def home():
    return render_template('index.html')



#### API Endpoints for Dropdown Menu's on Front-end ####
@app.route('/patrons') #is this the api route for patrons
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

@app.route('/api/itemtypes') 
def api_item_types() -> jsonify:
    '''This api returns all item types from the database in JSON format'''
    
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
def api_items_by_type() -> jsonify:
    '''This api returns all library items[ID & Title] in JSON format'''
    type_id_from_url = request.args.get('type_id', '').strip() # check for query parameter in url

    query = LibraryItem.query
    if type_id_from_url.isdigit(): 
        query = query.filter(LibraryItem.ItemType == int(type_id_from_url))
#BERKER: filtering unavailable items from dropdown, will remove after changing dropdown structure.
    query = query.filter(LibraryItem.Availability == True)
    items_from_db = query.order_by(LibraryItem.ItemTitle).all()

    output_list = []
    for item in items_from_db:
        item_data = {
            "ItemID": item.ItemID,
            "ItemTitle": item.ItemTitle
        }

        output_list.append(item_data)
    return jsonify(output_list)

@app.route('/api/patrons-with-checkouts')
def api_patrons_with_checkouts() -> jsonify:
    '''
    This api returns JSON of all library items a patron has checked out 
    Item is 'CheckedOut' when Availability == False and no Return record
    '''
    active_checkout_patrons = (
        database.session.query(Patron) # create db query
        .join(Checkout, Patron.PatronID == Checkout.PatronID)
        .join(LibraryItem, Checkout.ItemID == LibraryItem.ItemID)
        .outerjoin(Return, Checkout.TransactionID == Return.TransactionID)
        .filter(
            LibraryItem.Availability == False, # Item is not on shelf
            Return.TransactionID.is_(None)     # and item is not yet returned
        )
        .distinct(Patron.PatronID) 
        .order_by(Patron.PatronLN, Patron.PatronFN)
        .all()
    )
    
    patron_list = [ # Create JSON of patrons that have items checked out
        {
            "PatronID": p.PatronID,
            "PatronName": f"{p.PatronLN}, {p.PatronFN}" 
        }
        for p in active_checkout_patrons
    ]
    return jsonify(patron_list)


@app.route('/api/checkedout')
def api_checked_out_items() -> jsonify:
    """
    API endpoint returns list of all items currently in the 'CheckedOut' state.
    """
    query = (
        LibraryItem.query
        .join(Checkout, LibraryItem.ItemID == Checkout.ItemID)
        .outerjoin(Return, Checkout.TransactionID == Return.TransactionID)
        .filter(
            LibraryItem.Availability == False, # Item is not on shelf
            Return.TransactionID.is_(None)     # AND not yet returned - this results in checked out state
        )
    )

    items_from_db = query.order_by(LibraryItem.ItemID).all() # Order by ItemID

    output_list = [] # Create JSON list of all items currently in checked out state
    for item in items_from_db: 
        item_data = {
            "ItemID": item.ItemID,
            "ItemTitle": item.ItemTitle
        }
        output_list.append(item_data)
    return jsonify(output_list)

@app.route('/api/branches')
def api_branches():
    '''API endpoint that returns all library branches'''
    all_branches = LibraryBranch.query.order_by(LibraryBranch.BranchName).all()
    branch_list = [ # create list for json to be returned
        {"BranchID": branch.BranchID, "BranchName": branch.BranchName}
        for branch in all_branches
    ]
    return jsonify(branch_list)

#BERKER: to get item details by ID (replaced dropdown approach)
@app.route('/api/item/<int:item_id>')
def api_get_item(item_id: int) -> jsonify:
    item = LibraryItem.query.get(item_id) 
    if not item:
        return jsonify({"ok": False, "error": "Item not found"}), 404  
    item_type = ItemType.query.get(item.ItemType)  
    item_data = {
        "ok": True,
        "ItemID": item.ItemID,
        "ItemTitle": item.ItemTitle,
        "ItemType": item_type.TypeName if item_type else "Unknown",
        "Availability": item.Availability,
        "ShelfCode": item.ShelfCode
    }
    
    return jsonify(item_data)


@app.route('/api/items-for-patron')
def api_items_for_patron() -> jsonify:
    '''
    Returns a JSON list of items in the 'CheckedOut' state for a specific patron.
    Accepts a URL query parameter: /api/items-for-patron?patron_id=patronid
    '''
    patron_id_str = request.args.get('patron_id', '').strip() # get query parameter

    if not patron_id_str.isdigit(): # check if query parameter is a digit
        return jsonify({"error": "Valid PatronID is required"}), 400

    patron_id = int(patron_id_str) # change string to an int

    items_for_patron = ( # Find items for this patron that are 'CheckedOut'
        database.session.query(LibraryItem)
        .join(Checkout, LibraryItem.ItemID == Checkout.ItemID)
        .outerjoin(Return, Checkout.TransactionID == Return.TransactionID)
        .filter(
            Checkout.PatronID == patron_id,
            LibraryItem.Availability == False, # Item is not on shelf
            Return.TransactionID.is_(None)     # AND not yet returned
        )
        .order_by(LibraryItem.ItemTitle)
        .all()
    )

    item_list = [ # Create the JSON list that is returned
        {
            "ItemID": item.ItemID,
            "ItemTitle": item.ItemTitle
        }
        for item in items_for_patron
    ]
    return jsonify(item_list)
# Extend Membership card
@app.route('/api/check_membership', methods=['GET'])
def check_membership():
    """Check if a patron's account is expired."""
    patron_id = request.args.get('patron_id', type=int)
    patron = Patron.query.get(patron_id)

    if not patron:
        return jsonify({"ok": False, "error": "Patron not found"}), 404

    expired = membership_expired(patron)
    return jsonify({
        "ok": True,
        "patron_id": patron.PatronID,
        "expired": expired,
        "expiration_date": str(patron.AccountExpDate)
    })


@app.route('/api/extend_membership', methods=['POST'])
def extend_membership():
    """Extend or set a patron's membership expiration."""
    payload = request.get_json(silent=True) or request.form
    patron_id = int(payload.get("patron_id", -1))

    patron = Patron.query.get(patron_id)
    if not patron:
        return jsonify({"ok": False, "error": "Patron not found"}), 404

    # Option 1: client sent a specific date
    exp_date_str = payload.get("expiration_date")
    if exp_date_str:
      try:
          # expected format: YYYY-MM-DD from <input type="date">
          year, month, day = map(int, exp_date_str.split('-'))
          patron.AccountExpDate = date(year, month, day)
          database.session.commit()
          return jsonify({
              "ok": True,
              "message": "Membership expiration updated.",
              "new_expiration": str(patron.AccountExpDate)
          })
      except Exception:
          return jsonify({"ok": False, "error": "Invalid expiration date format (expected YYYY-MM-DD)"}), 400

    # Option 2: fallback: extend by days (old behavior)
    days = int(payload.get("days", 365))
    current = patron.AccountExpDate
    base_date = date.today() if (current is None or current < date.today()) else current
    patron.AccountExpDate = base_date + timedelta(days=days)

    database.session.commit()

    return jsonify({
        "ok": True,
        "message": f"Membership extended by {days} days.",
        "new_expiration": str(patron.AccountExpDate)
    })

# --- Fines API ---

@app.route('/api/check_fines', methods=['GET'])
def check_fines():
    patron_id = request.args.get('patron_id', type=int)
    patron = Patron.query.get(patron_id)
    if not patron:
        return jsonify({"ok": False, "error": "Patron not found"}), 404
    fines = float(patron.FeesOwed or 0)
    return jsonify({"ok": True, "patron_id": patron.PatronID, "fines_due": fines})


#BERKER returns patron details by patron id
@app.route('/api/patron/<int:patron_id>')
def api_get_patron(patron_id: int) -> jsonify:

    patron = Patron.query.get(patron_id)
    
    if not patron:
        return jsonify({"ok": False, "error": "Patron not found"}), 404
    
    patron_data = {
        "ok": True,
        "PatronID": patron.PatronID,
        "FirstName": patron.PatronFN,
        "LastName": patron.PatronLN,
        "FullName": f"{patron.PatronFN} {patron.PatronLN}",
        "AccountExpDate": str(patron.AccountExpDate),
        "FeesOwed": float(patron.FeesOwed or 0),
        "ItemsCheckedOut": patron.ItemsCheckedOut or 0
    }
    
    return jsonify(patron_data)

@app.route('/api/pay_fines', methods=['POST'])
def pay_fines():
    payload = request.get_json(silent=True) or request.form
    try:
        patron_id = int(payload.get("patron_id", -1))
    except (TypeError, ValueError):
        return jsonify({"ok": False, "error": "Invalid patron_id"}), 400

    patron = Patron.query.get(patron_id)
    if not patron:
        return jsonify({"ok": False, "error": "Patron not found"}), 404

    previous = float(patron.FeesOwed or 0)
    patron.FeesOwed = 0
    database.session.commit()

    return jsonify({
        "ok": True,
        "message": "Fines paid successfully.",
        "previous_fines": previous,
        "new_fines": float(patron.FeesOwed or 0),
        "patron_id": patron.PatronID
    })


# Checkin demo
#---------------------------
@app.route('/checkin', methods=['GET'])
def checkin_form():
    return render_template('checkin.html')

@app.route('/checkin', methods=['POST'])
def checkin_item() -> jsonify:
    '''
    This function processes a check-in transaction.
    Also moves an item from 'CheckedOut' to 'CheckedIn' state.
    It does NOT make the item 'Available' - that is the purpose of the 'reshelve' function
    '''
    payload = request.get_json(silent=True) or request.form # get json of form submision
    item_id_str = payload.get('item_id', '').strip() # get item_id & branch_id from form submission - clear any accidental whitespace
    branch_id_str = payload.get('branch_id', '').strip()

    if not item_id_str.isdigit() or not branch_id_str.isdigit(): # Raise error if item_id or branch_id is not a digit
        return jsonify({"ok": False, "error": "Invalid ItemID or BranchID"}), 400
    
    item_id = int(item_id_str) # Set item and branch id to integer for query
    branch_id = int(branch_id_str)

    branch = LibraryBranch.query.get(branch_id) # query for branch object
    if not branch: # raise error if the branch is not found
            return jsonify({"ok": False, "error": "Branch not found"}), 404

    # Find Active checkout - active checkout is one with this ItemID that has no corresponding return record (based on return id)
    active_checkout = (
        Checkout.query # Query checkout table
        .outerjoin(Return, Return.TransactionID == Checkout.TransactionID) 
        .filter(
            Checkout.ItemID == item_id,
            Return.TransactionID.is_(None) # No return record exists
        )
        .first()
    )

    # shouldn't need this but it's a double check on the js
    if not active_checkout: # If no active checkout is found, it's either already 'Available' or 'CheckedIn'
        item_check = LibraryItem.query.get(item_id)
        if item_check and item_check.Availability:
                return jsonify({"ok": False, "error": "This item is still Available."}), 400
        else:
                return jsonify({"ok": False, "error": "This item is already 'CheckedIn' and awaiting reshelving"}), 400

    item = LibraryItem.query.get(item_id) # Get the item object
    patron = Patron.query.get(active_checkout.PatronID) # Get the patron object

    if not item or not patron: #check against database error - if this hits check the db
            return jsonify({"ok": False, "error": "Internal Error: Item or Patron record missing"}), 500 

    try:
        # 1. Create the Return record
        new_return = Return(
            TransactionID=active_checkout.TransactionID,
            DateReturned=date.today(),
            BranchReturnedTo=branch_id
        )
        database.session.add(new_return) # add new return entry to the db - by adding return the item's logical state is changed from 'CheckedOut' to 'CheckedIn'

        # item.Availability stays 'False'.
        # To update Item Availability add to the 'Return' record, the item's state is now 'CheckIn'.

        # 3. Update Patron's item count - reduce it by 1
        current_count = patron.ItemsCheckedOut or 0
        if current_count > 0:
            patron.ItemsCheckedOut = current_count - 1

        database.session.commit() # commit changes to the db

        return jsonify({ # return messsage check in was successful
            "ok": True,
            "message": f"Item '{item.ItemTitle}' checked in successfully. Awaiting reshelving.",
            "item_id": item.ItemID,
            "patron_id": patron.PatronID,
            "patron_name": f"{patron.PatronFN} {patron.PatronLN}",
            "return_date": str(date.today())
        })

    except Exception as e:
        database.session.rollback()
        app.logger.error(f"Error during checkin: {e}")
        return jsonify({"ok": False, "error": f"A database error occurred: {e}"}), 500


# Checkout demo
#---------------------------
@app.route('/checkout', methods=['GET'])
def checkout_form():
    return render_template('checkout.html')

@app.route('/checkout', methods=['POST'])
def checkout_basic() -> jsonify:
    payload = request.get_json(silent=True) or request.form
    patron_id = int(payload.get('patron_id', -1))
    item_ids = payload.get('item_ids', [])  #BERKER: getting a list of items for the basket

#BERKER: helps convert to list if it s a string
    if isinstance(item_ids, str):
        item_ids = [int(x.strip()) for x in item_ids.split(',') if x.strip().isdigit()]

    patron = Patron.query.get(patron_id)

    if patron is None:
        return jsonify({"ok": False, "error": "Patron not found"})

    if membership_expired(patron):
        return jsonify({
            "ok": False,
            "error": "RENEW MEMBERSHIP NOW!!",
            "expired_on": str(patron.AccountExpDate)
        })
    
#BERKER: checking if patron has fines
    if patron.FeesOwed and patron.FeesOwed > 0:
        return jsonify({
            "ok": False,
            "error": f"Patron has fine balance of ${float(patron.FeesOwed):.2f}. Please clear fines before checkout."
        })

#Berker: checks if basket exceeds item limit (as in patron items + basket items)
    current_count = patron.ItemsCheckedOut or 0
    if current_count + len(item_ids) > MAX_ITEMS_PER_PATRON:
        return jsonify({
            "ok": False, 
            "error": f"Cannot checkout {len(item_ids)} items. Patron has {current_count} items checked out. Limit is {MAX_ITEMS_PER_PATRON}."
        })
    
#BERKER: validate all items before checking out any
    errors = []
    items_to_checkout = []
    
    for item_id in item_ids:
        item = LibraryItem.query.get(item_id)
        
        if item is None:
            errors.append(f"Item ID {item_id} not found")
            continue

#BERKER: Checks if specific item already has active checkout(to prevent duplicates)
        active_checkout = (
            Checkout.query
            .outerjoin(Return, Return.TransactionID == Checkout.TransactionID)
            .filter(
                Checkout.ItemID == item_id,
                Return.TransactionID.is_(None)
            )
            .first()
        )

#BERKER: If an active checkout exists, item is already checked out
        if active_checkout:
            errors.append(f"Item '{item.ItemTitle}' (ID {item_id}) is already checked out")
            continue

        if item.Availability is not True:
            errors.append(f"Item '{item.ItemTitle}' (ID {item_id}) is not available")
            continue
        
        items_to_checkout.append(item)

#BERKER: will return home If there are any errors
    if errors:
        return jsonify({"ok": False, "error": " | ".join(errors)})
    
    # All items are valid, proceed with checkout
    checked_out_list = []

    for item in items_to_checkout:
        rental_days = rental_days_for(item)
        due_date = date.today() + timedelta(days=rental_days)
        
#BERKER for checkout records
        new_checkout = Checkout(
            PatronID=patron_id,
            ItemID=item.ItemID,
            CheckoutDate=date.today()
        )
        database.session.add(new_checkout)
        
#BERKER: Updates item availability
        item.Availability = False
        
#BERKER: Adds to response list
        checked_out_list.append({
            "ItemID": item.ItemID,
            "ItemTitle": item.ItemTitle,
            "CheckoutDate": str(date.today()),
            "DueDate": str(due_date)
        })

#BERKER: Update patron s item count (outside the loop
    patron.ItemsCheckedOut = current_count + len(items_to_checkout)
    database.session.commit()

    return jsonify({
        "ok": True,
        "message": f"Successfully checked out {len(items_to_checkout)} item(s).",
        "patron_id": patron_id,
        "items_checked_out": checked_out_list
    })


@app.route('/api/items-to-reshelve', methods=['GET'])
def get_items_to_reshelve():
    '''
    Identifies and returns a list of all items that have been returned, 
    but not yet marked as available
    '''
    try:
    # This query finds items that are 
    # 1. In library item table
    # 2. Marked as unavailable (Availability == False)
    # 3. Have a corresponding return record
        items_awaiting_reshelve = (
            database.session.query(LibraryItem)
            .join(Checkout, LibraryItem.ItemID == Checkout.ItemID)
            .join(Return, Checkout.TransactionID == Return.TransactionID)
            .filter(LibraryItem.Availability == False)
            .distinct(LibraryItem.ItemID)
            .order_by(LibraryItem.ItemTitle)
            .all()         # Item is not yet available
        )

        #format list for front end
        output_list = [
            {
                "ItemID": item.ItemID,
                "ItemTitle": item.ItemTitle,
                "ShelfCode": item.ShelfCode
            }
            for item in items_awaiting_reshelve
        ]
        
        return jsonify(output_list)
    
    except Exception as e:
        return jsonify({"ok": False, "error": f"Database error: {str(e)}"}), 500
    
@app.route('/api/reshelve', methods=['POST'])
def reshelve_items():
    '''
    Handles the reshelveing of a single item, making 
    it available and logging the reshelve date.
    '''
    payload = request.get_json(silent=True) or request.form
    item_id = int(payload.get('item_id', -1))
                  
    if item_id == -1:
        return jsonify({"ok": False, "error": "ItemID is required"}), 400
    
    # Use database.session.get() which is the modern way
    item = database.session.get(LibraryItem, item_id)

    if item is None:
        return jsonify({"ok": False, "error": f"Item with ID {item_id} not found"}), 404
    
    #update items vailability and reshelve date
    try:
        item.Availability = True
        item.DateReshelved = date.today()
        database.session.commit()

        return jsonify({
            "ok": True,
            "message": f"Item '{item.ItemTitle}' (ID: {item.ItemID}) reshelved successfully.",
        })
    
    except Exception as e:
        database.session.rollback()
        return jsonify({"ok": False, "error": f"Database error: {str(e)}"}), 500

@app.route('/reshelve', methods=['GET'])
def reshelve_form():
    '''Serves the HTML page for reshelving items.'''
    return render_template('reshelve.html')


# Utility
# ----------------------------
@app.route('/dbinfo', methods=['GET'])
def dbinfo():
    return jsonify({"db_uri":app.config['SQLALCHEMY_DATABASE_URI']})


# --- Main execution block ---
if __name__ == '__main__':

    with app.app_context():
        database.create_all()

    app.run(debug=True, host='0.0.0.0', port=5001)
