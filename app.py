import os
from flask import Flask, request, jsonify, render_template_string
from flask_sqlalchemy import SQLAlchemy
from datetime import date, timedelta
from flask import render_template

#added time delta for due date calculations

app = Flask(__name__)

db_dir = app.instance_path
os.makedirs(db_dir, exist_ok=True)
db_path = os.path.join(db_dir, 'sprint1db.db') 


app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

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


# should we have account expiration date or calculate expiration on account creation dates?? - we can check the account expiration date in the patron table. That's how I populated the db. Your function below looks good. Also berker this is fire nice fing job. ~ Luke
# def membership_expired(patron) -> bool:
#     if not patron or not patron.AccountCreatedDate:
#         return False
#     days_since_account_created = (date.today() - patron.AccountCreatedDate).days
#     return days_since_account_created >= 365

def membership_expired(patron) -> bool:
    return bool(patron and patron.AccountExpDate and patron.AccountExpDate < date.today())

def rental_days_for(item: LibraryItem) -> int:
    item_type = ItemType.query.get(item.ItemType) if item else None
    return int(item_type.RentalLength) if (item_type and item_type.RentalLength) else 0


# --- Routes ---
MAX_ITEMS_PER_PATRON = 20

@app.route('/')
def home():
    #to return json
    all_patrons = Patron.query.all()
    patrons_list = [
        {"PatronID": p.PatronID, "FName": p.PatronFN, "LName": p.PatronLN}
        for p in all_patrons
    ]
    return jsonify(patrons_list)

###api endpoints for dropdowns

@app.route('/api/itemtypes')
def api_item_types():
    ##return all items
    types = ItemType.query.order_by(ItemType.TypeName).all()
    return jsonify([{"TypeID": t.TypeID, "TypeName": t.TypeName} for t in types])

@app.route('/api/items')
def api_items_by_type():
   #returning filtered items
    type_id_raw = request.args.get('type_id', '').strip()

#filtering types
    available_items_query = LibraryItem.query
    if type_id_raw.isdigit():
        available_items_query = available_items_query.filter(
            LibraryItem.ItemType == int(type_id_raw)
        )
    
    available_items_query = available_items_query.filter(
        LibraryItem.Availability == True
    ) #available items show up onlu

    available_items = available_items_query.order_by(LibraryItem.ItemTitle).all()

    items_response = [
        {"ItemID": item.ItemID, "ItemTitle": item.ItemTitle} 
        for item in available_items
    ]

    return jsonify(items_response)


# Checkout demo page + post
#---------------------------

@app.route('/checkout', methods=['GET'])
def checkout_form():
    # loading demo page for now
    return render_template('checkout.html')

@app.route('/checkout', methods=['POST'])
def checkout_basic():
    payload = request.get_json(silent=True) or request.form
    patron_id = int(payload.get('patron_id', -1))
    item_id = int(payload.get('item_id', -1))
    # item_ids = payload.get('item_ids', [])  # listing items in the basket

    patron = Patron.query.get(patron_id)
    item = LibraryItem.query.get(item_id)

    # if patron exists
    if patron is None:
        return jsonify({"ok": False, "error": "Patron not found"})
    # if item exists
    if item is None:
        return jsonify({"ok": False, "error": "Item not found"})

    # if item is None:
    #     return jsonify({"ok": False, "error": "Item not found"})

    # check for expired membership
    if membership_expired(patron):
        return jsonify({
            "ok": False,
            "message": "RENEW MEMBERSHIP NOW!!",
            "expired_on": str(patron.AccountExpDate)
        })
    
    # checking if patron owes fees
    if patron.FeesOwed and patron.FeesOwed > 0:
        return jsonify({
        "ok": False,
        "error": f"fine balance of ${float(patron.FeesOwed):.2f}. clear fines first!!."
    })

    # basket related testing code
    # current_count = patron.ItemsCheckedOut or 0
    # if current_count + len(item_ids) > MAX_ITEMS_PER_PATRON:
    #     return jsonify({
    #         "ok": False, 
    #         "error": f"Basket checkout would exceed limit. You have {current_count} items, limit is {MAX_ITEMS_PER_PATRON}"
    #     })
    # items_to_checkout = []
    # for single_item_id in item_ids:
    #     item = LibraryItem.query.get(single_item_id)
    #     # if item exists
    #     if item is None:
    #         return jsonify({"ok": False, "error": f"Item ID {single_item_id} not found"})
        
        
    #to prevent duplicate checkouts(will test)
    active_checkout = (
        Checkout.query
        .outerjoin(Return, Return.TransactionID == Checkout.TransactionID)
        .filter(
            Checkout.ItemID == item_id,
            Return.TransactionID.is_(None)
        )
        .first()
    )
    if active_checkout:
        return jsonify({
            "ok": False, 
            "error": f"Item '{item.ItemTitle}' is already checked out."
            }) #should we show the librarian who the item checked out to?
    
    # check availability
    if item.Availability is False:
        return jsonify({
            "ok": False, 
            "error": f"fine balance of ${float(patron.FeesOwed):.2f}. clear fines first!!."
            })

        # items_to_checkout.append(item)


    # check if patron at 20 items
    current_count = patron.ItemsCheckedOut or 0
    if current_count >= MAX_ITEMS_PER_PATRON:
        return jsonify({
            "ok": False, 
            "error": "Individual checkout limit reached (20 items)"
            })
    
    #calculating due dates
    days = rental_days_for(item)
    due_date = date.today() + timedelta(days=days)


    # create checkout record
    new_checkout = Checkout(
        PatronID=patron_id, 
        ItemID=item.ItemID,
        CheckoutDate=date.today()
    )
    database.session.add(new_checkout)

    # update item and patron info
    item.Availability = False     
    # Update patron count once for all items
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

    checked_out_list = []
    for checkout_record, library_item, patron_record in active_checkouts:
        rental_days = rental_days_for(library_item)
        due_date = (checkout_record.CheckoutDate or date.today()) + timedelta(days=rental_days)
        checked_out_list.append({
            "TransactionID": checkout_record.TransactionID,
            "PatronID": patron_record.PatronID,
            "PatronName": f"{patron_record.PatronFN} {patron_record.PatronLN}",
            "ItemID": library_item.ItemID,
            "ItemTitle": library_item.ItemTitle,
            "CheckoutDate": str(checkout_record.CheckoutDate),
            "due_date": str(due_date)
        })

    return jsonify({
        "ok": True,
        "message": "Checkout recorded.",
        "patron_id": patron_id,
        "item_id": item_id,
        "checkout_date": str(date.today()),
        "due_date": str(due_date),
        "checked_out": checked_out_list
        # "items_checked_out": len(items_to_checkout)  # (Added count of items processed, may delete(if unnecessary)
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
