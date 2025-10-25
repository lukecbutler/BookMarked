import os
from flask import Flask, request, jsonify, render_template_string
from flask_sqlalchemy import SQLAlchemy
from datetime import date
from flask import render_template

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



# --- Routes ---

MAX_ITEMS_PER_PATRON = 20

@app.route('/')
def home():
    #To return JSON
    all_patrons = Patron.query.all()
    patrons_list = [
        {"PatronID": p.PatronID, "FName": p.PatronFN, "LName": p.PatronLN}
        for p in all_patrons
    ]
    return jsonify(patrons_list)

@app.route('/api/itemtypes')
def api_item_types():
    """Return all item types."""
    types = ItemType.query.order_by(ItemType.TypeName).all()
    return jsonify([
        {"TypeID": t.TypeID, "TypeName": t.TypeName}
        for t in types
    ])

@app.route('/api/items')
def api_items_by_type():
    """Return items filtered by item type (no validation or availability filters yet)."""
    type_id_raw = request.args.get('type_id', '').strip()

    q = LibraryItem.query
    if type_id_raw.isdigit():
        q = q.filter(LibraryItem.ItemType == int(type_id_raw))

    items = q.order_by(LibraryItem.ItemTitle).all()
    return jsonify([
        {"ItemID": i.ItemID, "ItemTitle": i.ItemTitle}
        for i in items
    ])


# Checkout demo page + porst


@app.route('/checkout', methods=['GET'])
def checkout_form():
    return render_template('checkout.html')

@app.route('/checkout', methods=['POST'])


# ----------------------------
# Utility
# ----------------------------
@app.route('/dbinfo')
def checkout_basic():
    payload = request.get_json(silent=True) or request.form
    patron_id = int(payload.get('patron_id', -1))
    item_id = int(payload.get('item_id', -1))

    patron = Patron.query.get(patron_id)
    item = LibraryItem.query.get(item_id)

    if patron is None:
        return jsonify({"ok": False, "error": "Patron not found"})
    if item is None:
        return jsonify({"ok": False, "error": "Item not found"})

    # availability check
    if item.Availability is False:
        return jsonify({"ok": False, "error": "Item not avaliable"})

    #limit check
    current_count = patron.ItemsCheckedOut or 0
    if current_count >= MAX_ITEMS_PER_PATRON:
        return jsonify({"ok": False, "error": f"Individual checkout imit reached 20 items"})

    co = Checkout(PatronID=patron_id, ItemID=item_id, CheckoutDate=date.today())
    database.session.add(co)

    item.Availability = False
    patron.ItemsCheckedOut = current_count + 1

    database.session.commit()

    return jsonify({
        "ok": True,
        "message": "Checkout recorded.",
        "patron_id": patron_id,
        "item_id": item_id,
        "checkout_date": str(date.today())
    }), 201




# --- Main execution block ---
if __name__ == '__main__':
    with app.app_context():
        database.create_all()

    #BERKER: Updated port to 5001, had problems with 80.
    app.run(debug=True, host='0.0.0.0', port=5001)
