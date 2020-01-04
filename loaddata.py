import csv
import string

from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Book


engine = create_engine('postgresql+psycopg2://libra:passw0rd@localhost/catalogue')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

ALPHANUM = set(string.ascii_letters).union(set([str(i) for i in range(10)]))

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
        print(row['name'].split())
        if is_alphanum(row['name']):
            book = Book(name=row['name'], author=row['author'])
            yield book

def is_alphanum(sentence):
    """
    Attempts to filter out only English title by checking for alphanum characters
    """
    return all([c in ALPHANUM for word in sentence.split() for c in word])


if __name__ == '__main__':
    load_data(mockdata)
    session.commit()