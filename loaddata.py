import csv
import string

from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Book, Genre, BookGenreXref

import langtools
from langtools import CATEGORIES


engine = create_engine('postgresql+psycopg2://libra:passw0rd@localhost/catalogue')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

ALPHANUM = set(string.ascii_letters).union(set([str(i) for i in range(10)]))
THRESHOLD = 0.3

# sample data
mockdata = {}
with open('sample.csv', 'r', encoding='utf-8') as f:
    rawdata = csv.reader(f)
    for i, row in enumerate(rawdata):
        mockdata[i] = {'name':row[0], 'author':row[1]}

def load_data(data):
    """
    Persist into postgresql
    """
    for book in add_entries(data):
        session.add(book)

def add_entries(data):
    """
    Create book objects for each title - author
    """
    for row in data.values():
        if is_alphanum(row['name']):
            book = Book(name=row['name'], author=row['author'])
            yield book

def is_alphanum(sentence):
    """
    Attempts to filter out only English title by checking for alphanum characters
    """
    return all([c in ALPHANUM for word in sentence.split() for c in word])


def load_genre():
    """
    Adds all genre to postgre table
    """
    for cat in CATEGORIES:
        session.add(Genre(name=cat))


if __name__ == '__main__':
    # Load mock data to base tables
    load_genre()
    load_data(mockdata)

    # Persist all mock data
    session.commit()

    # Creates a dictionary of genre with the respective db primary keys
    db_genre = session.query(Genre).all()
    GENRE = {i.name: i.id for i in db_genre}

    # Create foreign key relationship between book and genre
    for k in mockdata.values():
        book = session.query(Book).filter(Book.name == k['name'], Book.author == k['author']).limit(1).one_or_none()

        if not book:
            continue

        features = langtools.extract_featureset(book.name)
        genre_scoreboard = langtools.assign_genre(features)

        tags = (GENRE[k] for k, v in genre_scoreboard.items() if v >= THRESHOLD)

        for tag in tags:
            book_genre = BookGenreXref(bookid=book.id, genreid=tag)
            session.add(book_genre)

    session.commit()

