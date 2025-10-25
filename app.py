import os
from flask import Flask, request, jsonify, render_template_string
from flask_sqlalchemy import SQLAlchemy
from datetime import date
from flask import render_template_string 

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
@app.route('/')
def home():
    all_patrons = Patron.query.all()
    return jsonify([
        {"PatronID": p.PatronID, "FName": p.PatronFN, "LName": p.PatronLN}
        for p in all_patrons
    ])

@app.route('/api/itemtypes')
def api_item_types():
    types = ItemType.query.order_by(ItemType.TypeName).all()
    return jsonify([{"TypeID": t.TypeID, "TypeName": t.TypeName} for t in types])

@app.route('/api/items')
def api_items_by_type():
    type_id_raw = request.args.get('type_id', '').strip()

    q = LibraryItem.query
    if type_id_raw.isdigit():
        q = q.filter(LibraryItem.ItemType == int(type_id_raw))

    items = q.order_by(LibraryItem.ItemTitle).all()
    return jsonify([{"ItemID": i.ItemID, "ItemTitle": i.ItemTitle} for i in items])

# demo page code
_checkout_form_min = """
<!doctype html>
<title>Select an Item</title>
<h2>Select an Item (minimal demo)</h2>

<label>Item Type</label><br>
<select id="item_type">
  <option value="">-- select type --</option>
</select>
<br><br>

<label>Item</label><br>
<select id="item_id">
  <option value="">-- select item --</option>
</select>
<br><br>

<div id="picked" style="margin-top:10px; font-family: monospace;"></div>

<script>
// load item types
async function loadTypes() {
  const resp = await fetch('/api/itemtypes');
  const types = await resp.json();
  const sel = document.getElementById('item_type');
  sel.innerHTML = '<option value="">-- select type --</option>';
  types.forEach(t => {
    const opt = document.createElement('option');
    opt.value = t.TypeID;
    opt.textContent = t.TypeName;
    sel.appendChild(opt);
  });
}

// load items for a given type id (or all if empty)
async function loadItems(typeId) {
  const url = '/api/items' + (typeId ? ('?type_id=' + encodeURIComponent(typeId)) : '');
  const resp = await fetch(url);
  const items = await resp.json();
  const sel = document.getElementById('item_id');
  sel.innerHTML = '<option value="">-- select item --</option>';
  items.forEach(i => {
    const opt = document.createElement('option');
    opt.value = i.ItemID;
    opt.textContent = i.ItemTitle + ' (ID ' + i.ItemID + ')';
    sel.appendChild(opt);
  });
}

// wire up
document.addEventListener('DOMContentLoaded', () => {
  loadTypes();
  // when type changes, load items
  document.getElementById('item_type').addEventListener('change', (e) => {
    loadItems(e.target.value);
    document.getElementById('picked').textContent = '';
  });
  // show the chosen item (purely visual for now)
  document.getElementById('item_id').addEventListener('change', (e) => {
    const itemId = e.target.value || '';
    const itemText = e.target.options[e.target.selectedIndex]?.text || '';
    document.getElementById('picked').textContent =
      itemId ? ('Selected: ' + itemText) : '';
  });
});
</script>
"""

@app.route('/checkout', methods=['GET'])
def checkout_form_min():
    # DEmo page
    return render_template_string(_checkout_form_min)


# ---------- Utility ----------

@app.route('/dbinfo')
def dbinfo():
    return jsonify({"db_uri": app.config['SQLALCHEMY_DATABASE_URI']})

# --- Main execution block ---
if __name__ == '__main__':
    with app.app_context():
        database.create_all()

    #BERKER: Updated port to 5001, had problems with 80.
    app.run(debug=True, host='0.0.0.0', port=5001)
