import csv

from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Book


engine = create_engine('postgresql+psycopg2://libra:passw0rd@localhost/catalogue')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

# sample data
mockdata = {}
with open('sample.csv', 'r', encoding='utf-8') as f:
    rawdata = csv.reader(f)
    for i, row in enumerate(rawdata):
        mockdata[i] = {'name':row[0], 'author':row[1]}

def load_data(data):
    for book in add_entries(data):
        session.add(book)

def add_entries(data):
    for row in data.values():
        book = Book(name=row['name'], author=row['author'])
        yield book


if __name__ == '__main__':
    load_data(mockdata)
    session.commit()