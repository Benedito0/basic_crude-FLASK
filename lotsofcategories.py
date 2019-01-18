from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import *

engine = create_engine('sqlite:///catalog.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
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

category = Category(category_name="Football")
session.add(category)
session.commit()

category = Category(category_name="American Football")
session.add(category)
session.commit()

category = Category(category_name="Basketball")
session.add(category)
session.commit()

category = Category(category_name="Softball")
session.add(category)
session.commit()

category = Category(category_name="Swimming")
session.add(category)
session.commit()

category = Category(category_name="Cycling")
session.add(category)
session.commit()

category = Category(category_name="Skating")
session.add(category)
session.commit()

print("Added to the db")
