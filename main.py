from datetime import datetime

from flask import Flask
from flask import request, render_template, redirect, url_for
from flask import session as login_session

from sqlalchemy import create_engine, desc, text
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Book


# DB
engine = create_engine('postgresql+psycopg2://libra:passw0rdg@localhost/catalogue')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()
# Starts the application and register the blueprints
app = Flask(__name__)


def parseUrlEntry(entry_string):
    if '|' in entry_string:
        name = entry_string.split('|')[0]
        dob = datetime.strptime(entry_string.split('|')[1], '%d-%m-%Y')
        return [name, dob]
    else:
        return []


# Adds a customer
@app.route('/book/add/<string:new_entry>', methods=['POST'])
def addBook(new_entry):
    data = parseUrlEntry(new_entry)
    # Creates the record and saves it to the database
    if data:
        new_item = Book(name=data[0], author=data[1])
        session.add(new_item)
        session.commit()

    return redirect(url_for('homePage'))


# Edits a customer
# @app.route('/book/edit/<string:item_id>/<string:new_entry>', methods=['POST'])
# def updateBook(item_id, new_entry):
#     if item_id.isdigit():
#         item_id = int(item_id)
#     else:
#         raise TypeError("Id must be integer")
    
#     data = parseUrlEntry(new_entry)
#     try:
#         item = session.query(Book).filter_by(id=item_id).one()
#         item.name = data[0]
#         item.dob = data[1]

#         session.add(item)
#         session.commit()
#     except:
#         pass

#     return redirect(url_for('homePage'))


# Deletes a customer
@app.route('/book/delete/<string:item_id>', methods=['DELETE'])
def deleteBook(item_id):
    if item_id.isdigit():
        item_id = int(item_id)
    else:
        raise TypeError("Id must be integer")

    try:
        item = session.query(Book).filter_by(id=item_id).one()
        session.delete(item)
        session.commit()
    except:
        pass

    return redirect(url_for('homePage'))


# Views a customer
# @app.route('/book/get/<string:item_id>', methods=['GET'])
# def viewBook(item_id):
#     if item_id.isdigit():
#         item_id = int(item_id)
#     else:
#         raise TypeError("Id must be integer")

#     book = session.query(Book).filter_by(id=item_id).one()
#     return render_template('view.html', book=book, text=None)


# Views youngest customer
# @app.route('/customer/youngest', methods=['GET'])
# def viewYoungest():
#     statement = 'SELECT name, dob FROM customer WHERE dob = (SELECT MAX(dob) FROM customer)'
#     sql = text(statement)
#     res = engine.execute(sql)
#     for row in res:
#         customer = row

#     return render_template('view.html', customer=customer, text=statement)


# Home
@app.route('/', methods=['GET'])
def homePage():
    books = session.query(Book).order_by(Book.updated_at.desc()).limit(10).all()
    return render_template('index.html', books=books)


if __name__ == '__main__':
    app.secret_key = 'my_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
