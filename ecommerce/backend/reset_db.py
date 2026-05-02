import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from app.database.database import engine, Base
from app.database.models import *

print("Dropping all tables...")
Base.metadata.drop_all(bind=engine)
print("Creating all tables...")
Base.metadata.create_all(bind=engine)
print("DB reset OK")