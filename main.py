import abc
import requests

from datetime import datetime
from flask import Flask
from flask import request, render_template, redirect, make_response, url_for, send_from_directory
from flask import session as login_session
from sqlalchemy import create_engine, desc, text
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Book


# DB
engine = create_engine('postgresql+psycopg2://libra:passw0rd@localhost/catalogue')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()
# Starts the application and register the blueprints
app = Flask(__name__)


# Adds a customer
@app.route('/book/add', methods=['POST'])
def addBook():
    # Creates the record and saves it to the database
    if request.form:
        new_item = Book(name=request.form['name'], author=request.form['author'])
        session.add(new_item)
        session.commit()

    return redirect(url_for('homePage'))

# Deletes a customer
@app.route('/book/delete/<string:item_id>', methods=['POST'])
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

# Download CSV
@app.route('/book/download/<string:filetype>', methods=['GET'])
def downloadCSV(filetype):
    response = requests.get(f'http://localhost:2020/book/getall/{filetype}')

    return send_from_directory(app.config['FILE_FOLDER'], response.text, as_attachment=True)

# Home
@app.route('/', methods=['GET'])
def homePage():
    books = session.query(Book).order_by(Book.updated_at.desc()).limit(10).all()
    return render_template('index.html', books=books)


if __name__ == '__main__':
    app.secret_key = 'my_secret_key'
    app.config['FILE_FOLDER'] = 'output/'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
