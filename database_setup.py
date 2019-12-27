import datetime

from sqlalchemy import Column, Integer, String, Date, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine


Base = declarative_base()


class Book(Base):
    '''
    Schema of books
    '''
    __tablename__ = 'books'

    id = Column(Integer, primary_key=True)
    name = Column(String(1000), nullable=False)
    author = Column(String(250), nullable=False)
    updated_at = Column(DateTime,
        nullable=False,
        default=datetime.datetime.now())

    # Serialization function for JSON API requests
    @property
    def serialize(self):
        return {
            'name': self.name,
            'author': self.author,
        }

engine = create_engine('postgresql+psycopg2://libra:passw0rd@localhost/catalogue')
Base.metadata.create_all(engine)
