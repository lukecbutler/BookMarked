from flask import Flask, request, jsonify, render_template_string
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

database = SQLAlchemy(app)

class LibraryBranch(database.Model):

    __tablename__ = 'LibraryBranch'

    BranchID = database.Column(database.Integer, primary_key=True, auto_increment=True)
    BranchName = database.Column(database.String(50))
    StreetNum = database.Column(database.Integer)
    StreetName = database.Column(database.String(30))
    City = database.Column(database.String(30))
    State = database.Column(database.String(30))
    Zip = database.Column(database.Integer)

class ItemType(database.Model):

    __tablename__ = 'ItemType'

    TypeID = database.Column(database.Integer, primary_key=True, auto_increment=True)
    TypeName = database.Column(database.String(30))
    RentalLength = database.Column(database.Integer)
    PerDayFine = database.Column(database.Numeric(10, 2))

class LibraryItem(database.Model):

    __tablename__ = 'LibraryItem'

    ItemID = database.Column(database.Integer, primary_key=True, auto_increment=True)
    ItemType = database.Column(database.Integer, database.ForeignKey('ItemType.TypeID'))
    BelongsTo = database.Column(database.Integer, database.ForeignKey('LibraryBranch.BranchID'))
    AquisitionDate = database.Column(database.Date)
    Cost = database.Column(database.Numeric(10, 2))
    ItemTitle = database.Column(database.String(50))
    Availability = database.Column(database.Boolean)
    ShelfCode = database.Column(database.String(5))
    DatePublished = database.Column(database.Date)

class ItemAuthor(database.Model):

    __tablename__ = 'ItemAuthor'

    ItemID = database.Column(database.Integer, database.ForeignKey('LibraryItem.ItemID'))
    AuthFN = database.Column(database.String(50))
    AuthLN = database.Column(database.String(50))

    __table_args__ = (
        database.PrimaryKeyConstraint('ItemID', 'AuthFN', 'AuthLN'),
    )

class Book(database.Model):

    __tablename__ = 'Book'

    ItemID = database.Column(database.Integer, database.ForeignKey('LibraryItem.ItemID'), primary_key=True)
    Publisher = database.Column(database.String(50))
    Genre = database.Column(database.String(50))
    Edition = database.Column(database.Integer)
    NumPages = database.Column(database.Integer)

class Periodical(database.Model):

    __tablename__ = 'Periodical'

    ItemID = database.Column(database.Integer, database.ForeignKey('LibraryItem.ItemID'), primary_key=True)
    Publisher = database.Column(database.String(50))
    Genre = database.Column(database.String(50))

class Recording(database.Model):

    __tablename__ = 'Recording'

    ItemID = database.Column(database.Integer, database.ForeignKey('LibraryItem.ItemID'), primary_key=True)
    FileType = database.Column(database.String(5))
    Length = database.Column(database.Time)
    Subject = database.Column(database.String(30))

class Video(database.Model):

    __tablename__ = 'Video'

    ItemID = database.Column(database.Integer, database.ForeignKey('LibraryItem.ItemID'), primary_key=True)
    FileType = database.Column(database.String(5))
    Length = database.Column(database.Time)
    Subject = database.Column(database.String(30))
    Quality = database.Column(database.String(10))

class Patron(database.Model):
    
    __tablename__ = 'Patron'

    PatronID = database.Column(database.Integer, primary_key=True, auto_increment=True)
    PatronFN = database.Column(database.String(50))
    PatronLN = database.Column(database.String(50))
    StreetNum = database.Column(database.Integer)
    StreetName = database.Column(database.String(30))
    City = database.Column(database.String(30))
    State = database.Column(database.String(30))
    Zip = database.Column(database.Integer)
    AccountExpDate = database.Column(database.Date)
    FeesOwed = database.Column(database.Numeric(10, 2))
    ItemsCheckedOut = database.Column(database.Integer)

class Checkout(database.Model):

    __tablename__ = 'Checkout'

    TransactionID = database.Column(database.Integer, primary_key=True, auto_increment=True)
    PatronID = database.Column(database.Integer, database.ForeignKey('Patron.PatronID'))
    ItemID = database.Column(database.Integer, database.ForeignKey('LibraryItem.ItemID'))
    CheckoutDate = database.Column(database.Date)

class Return(database.Model):

    __tablename__ = 'Return'

    TransactionID = database.Column(database.Integer, database.ForeignKey('Checkout.TransactionID'), primary_key=True)
    DateReturned = database.Column(database.Date)
    BranchReturnedTo = database.Column(database.Integer, database.ForeignKey('LibraryBranch.BranchID'))

with app.app_context():
    database.create_all()
