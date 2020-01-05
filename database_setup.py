import datetime

from sqlalchemy import Column, Integer, Unicode, Date, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine


Base = declarative_base()


class Book(Base):
    '''
    Schema of books
    '''
    __tablename__ = 'Book'

    id = Column(Integer, primary_key=True)
    name = Column(Unicode(1000), nullable=False)
    author = Column(Unicode(250), nullable=False)
    updated_at = Column(DateTime,
        nullable=False,
        default=datetime.datetime.now())

    # Serialization function for JSON API requests
    @property
    def attribs(self):
        return {
            'name': self.name,
            'author': self.author,
        }


class Genre(Base):
    """
    Schema of genre
    """
    __tablename__ = 'Genre'

    id = Column(Integer, primary_key=True)
    name = Column(Unicode(200), nullable=False)
    updated_at = Column(DateTime,
        nullable=False,
        default=datetime.datetime.now())


class BookGenreXref(Base):
    """
    Foreign key table for books and their tagged genre
    """
    __tablename__ = 'BookGenreXref'

    id = Column(Integer, primary_key=True)
    bookid = Column(Integer, ForeignKey('Book.id'), nullable=False)
    genreid = Column(Integer, ForeignKey('Genre.id'), nullable=False)
    updated_at = Column(DateTime,
        nullable=False,
        default=datetime.datetime.now())


engine = create_engine('postgresql+psycopg2://libra:passw0rd@localhost/catalogue')
Base.metadata.create_all(engine)
