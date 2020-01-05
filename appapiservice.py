import csv
import os

from datetime import datetime
from flask import Flask
from flask import request, jsonify, make_response
from sqlalchemy import create_engine, desc, text
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Book, Genre, BookGenreXref
import langtools


# DB
engine = create_engine('postgresql+psycopg2://libra:passw0rd@localhost/catalogue')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# Starts the application and register the blueprints
app = Flask(__name__)

# CONSTANTS
THRESHOLD = 0.3
# Creates a dictionary of genre with the respective db primary keys
db_genre = session.query(Genre).all()
GENRE = {i.name: i.id for i in db_genre}


class CSVFactory:
    """
    Produces a csv file from data
    """
    outdir = 'output'

    @classmethod
    def make_file(Class, data):
        return Class.File(data).fname

    class File:
        fname = None

        def __init__(self, data):
            sfx = datetime.now().strftime('%Y%m%d%H%M%S%f')
            fname = '_'.join(['title','author',sfx])
            self.fname = '.'.join([fname, 'csv'])

            with open(os.path.join(CSVFactory.outdir, self.fname), 'w') as f:
                fieldnames = data[0].keys()
                writer = csv.DictWriter(f, fieldnames=fieldnames)

                writer.writeheader()

                for dct in data:
                    writer.writerow(dct)


class XMLFactory(CSVFactory):
    """
    Produces an xml file from data
    """
    class File:
        def __init__(self, data):
            raise NotImplementedError


def quotewrap(target, char):
    """
    Wrap a string within a quote character
    """
    return ''.join([char, target, char])


# Creates a csv with all records
@app.route('/book/getall/<string:filetype>', methods=['GET'])
def getall(filetype):
    books = session.query(Book).order_by(Book.updated_at.asc()).all()
    data = [b.attribs for b in books]

    if filetype == 'csv':
        fname = CSVFactory.make_file(data)
    elif filetype == 'xml':
        fname = XMLFactory.make_file(data)

    return make_response((fname))


# Attempts to guess the genre of a book
@app.route('/book/genre/<int:bookid>/', methods=['GET'])
def genre(bookid):
    book = session.query(Book).filter(Book.id == bookid).one()

    features = langtools.extract_featureset(book.name)
    genre_scoreboard = langtools.assign_genre(features)
    print(genre_scoreboard)
    tags = (GENRE[k] for k, v in genre_scoreboard.items() if v >= THRESHOLD)

    for tag in tags:
        book_genre = BookGenreXref(bookid=book.id, genreid=tag)
        session.add(book_genre)

    session.commit()

    print(book_genre.id)
    return make_response()


if __name__ == '__main__':
    app.secret_key = 'my_secret_key'
    app.config['JSON_AS_ASCII'] = False
    app.debug = True
    app.run(host='127.0.0.1', port=2020)