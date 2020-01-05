import abc
import requests

from collections import namedtuple, defaultdict
from datetime import datetime
from flask import Flask
from flask import request, render_template, redirect, make_response, url_for, send_from_directory
from flask import session as login_session
from sqlalchemy import create_engine, desc, text
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Book, BookGenreXref, Genre


# DB
engine = create_engine('postgresql+psycopg2://libra:passw0rd@localhost/catalogue')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()
# Starts the application and register the blueprints
app = Flask(__name__)

# Composite book object
BookGenre = namedtuple('BookGenre', ['id', 'name', 'author', 'updated_at', 'genre'])

# Adds a book
@app.route('/book/add', methods=['POST'])
def addBook():
    # Creates the record and saves it to the database
    if request.form:
        new_item = Book(name=request.form['name'], author=request.form['author'])
        session.add(new_item)
        session.commit()

    requests.get(f'http://localhost:2020/book/genre/{new_item.id}')

    return redirect(url_for('homePage'))

# Deletes a book
@app.route('/book/delete/<string:item_id>', methods=['POST'])
def deleteBook(item_id):
    if item_id.isdigit():
        item_id = int(item_id)
    else:
        raise TypeError("Id must be integer")

    # Get all associative book-genre relationships
    xref = session.query(BookGenreXref).filter(BookGenreXref.bookid == item_id).all()
    if xref:
        for xr in xref:
            session.delete(xr)

    # Delete the book
    item = session.query(Book).filter(Book.id == item_id).one()
    if item:
        session.delete(item)

    if any([xref, item]):
        session.commit()

    return redirect(url_for('homePage'))

# Download all records as CSV
@app.route('/book/download/<string:filetype>', methods=['GET'])
def downloadCSV(filetype):
    response = requests.get(f'http://localhost:2020/book/getall/{filetype}')

    return send_from_directory(app.config['FILE_FOLDER'], response.text, as_attachment=True)

# Home
@app.route('/', methods=['GET'])
def homePage():
    statement = \
        '''
            SELECT
                b.id,
                b.name,
                b.author,
                b.updated_at,
                g.name
            FROM
                public."Book" b
            INNER JOIN public."BookGenreXref" bx ON b.id = bx.bookid
            INNER JOIN public."Genre" g ON bx.genreid = g.id
            ORDER BY b.updated_at DESC
            LIMIT 30;
        '''
    sql = text(statement)
    res = engine.execute(sql)

    # Collapse all genres of a title into a single row
    books = list()
    for r_id, r_name, r_author, r_updated_at, r_genre in res:
        for i, book in enumerate(books):
            # To ensure no duplicates in the list,
            # pop the BookGenre object if it's already created, update and then add it back
            if book.id == r_id:
                upd_book = books.pop(i)

                upd_genre = ', '.join([upd_book.genre, r_genre])
                upd_book = upd_book._replace(genre=upd_genre)
                books.append(upd_book)
                break
        else:
            # Append a new object if the title has not been created yet
            books.append(BookGenre(
                id = r_id,
                name = r_name,
                author = r_author,
                updated_at = r_updated_at,
                genre = r_genre
            ))

    # TODO: I intend to show only 10 titles in the table. 
    # This should be handled more elegantly from the top instead of slicing
    return render_template('index.html', books=books[:10])


if __name__ == '__main__':
    app.secret_key = 'my_secret_key'
    app.config['FILE_FOLDER'] = 'output/'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
