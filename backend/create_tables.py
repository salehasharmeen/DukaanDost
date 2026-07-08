from database.database import Base, engine
from models.transaction import Transaction

print("Creating tables...")

Base.metadata.create_all(bind=engine)

print("Tables created successfully!")