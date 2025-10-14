from flask import Flask, request, jsonify, render_template_string
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

database = SQLAlchemy(app)

class Patron(database.Model):
    PatronID = database.Column(database.Integer, primary_key = True)
    FName = database.Column(database.String(50))
    LName = database.Column(database.String(50))

class Book(database.Model):
    BookID = database.Column(database.Integer, primary_key = True)
    BookTitle = database.Column(database.String(100))
    AuthFName = database.Column(database.String(50))
    AuthLName = database.Column(database.String(50))

class BookCheckout(database.Model):
    PatronID = database.Column(database.Integer, database.ForeignKey('patron.PatronID'))
    BookID = database.Column(database.Integer, database.ForeignKey('book.BookID'))

    __table_args__ = (
        database.PrimaryKeyConstraint('PatronID', 'BookID'),
    )

with app.app_context():
    database.create_all()

@app.route('/')
def home():
    patrons = Patron.query.all()
    return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Library System</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }
                h1 { color: #333; }
                form { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); width: 300px; }
                input { margin-bottom: 10px; width: 100%; padding: 8px; border: 1px solid #ccc; border-radius: 5px; }
                button { background: #4CAF50; color: white; border: none; padding: 10px; border-radius: 5px; cursor: pointer; width: 100%; }
                button:hover { background: #45a049; }
                table { margin-top: 40px; border-collapse: collapse; width: 100%; background: white; }
                th, td { padding: 10px; border-bottom: 1px solid #ddd; text-align: left; }
                th { background-color: #4CAF50; color: white; }
            </style>
        </head>
        <body>
            <h1>Library Patron Management</h1>

            <form action="/add" method="POST">
                <h3>Add New Patron</h3>
                <input type="number" name="patronID" placeholder="Patron ID" required>
                <input type="text" name="fname" placeholder="First Name" required>
                <input type="text" name="lname" placeholder="Last Name" required>
                <button type="submit">Add Patron</button>
            </form>

            <h2>Current Patrons</h2>
            {% if patrons %}
            <table>
                <tr>
                    <th>ID</th>
                    <th>First Name</th>
                    <th>Last Name</th>
                </tr>
                {% for p in patrons %}
                <tr>
                    <td>{{ p.PatronID }}</td>
                    <td>{{ p.FName }}</td>
                    <td>{{ p.LName }}</td>
                </tr>
                {% endfor %}
            </table>
            {% else %}
            <p>No patrons found.</p>
            {% endif %}
        </body>
        </html>
    ''', patrons=patrons)

@app.route('/add', methods=['POST'])
def add_patron():
    # Works for both form submissions and JSON
    if request.is_json:
        data = request.get_json()
        patron_id = data.get('patronID')
        fname = data.get('fname')
        lname = data.get('lname')
    else:
        patron_id = request.form['patronID']
        fname = request.form['fname']
        lname = request.form['lname']

    new_patron = Patron(PatronID=patron_id, FName=fname, LName=lname)
    database.session.add(new_patron)
    database.session.commit()
    return ("<script>alert('Patron added successfully!'); window.location.href='/'</script>")

@app.route('/patrons', methods=['GET'])
def get_patrons():
    patrons = Patron.query.all()
    return jsonify([{"ID": p.PatronID, 'fname': p.FName, 'lname': p.LName} for p in patrons])

if __name__ == '__main__':
    app.run(debug=True)

