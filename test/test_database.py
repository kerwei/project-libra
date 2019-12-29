import csv
import random
import unittest

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, text

from database_setup import Book


class TestData(unittest.TestCase):
    def setUp(self):
        """
        Create a session to use for testing
        """
        engine = create_engine('postgresql+psycopg2://libra:passw0rd@localhost/catalogue')
        DBSession = sessionmaker(bind=engine)
        self.session = DBSession()

    def test_data_exist(self):
        """
        Checks that the Book table has been loaded
        """
        book = self.session.query(Book).first()
        self.assertIsNotNone(book)

    def test_column_iscorrect(self):
        """
        Checks that data is loaded into the correct columns
        """
        with open('sample.csv', 'r', encoding='utf-8') as f:
            rawdata = [r for r in csv.reader(f)]
            
        test_data = (random.choice(rawdata) for _ in range(10))
        rescount = [0] * 10

        for i, data in enumerate(test_data):
            res = self.session.query(Book).filter(Book.name == data[0], Book.author == data[1]).all()
            rescount[i] += len(res)

        self.assertTrue(all([i > 0 for i in rescount]))

    def test_data_encoding(self):
        """
        Checks that unicode characters are saved correctly
        """
        pass


