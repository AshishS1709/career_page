from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class UserProfile(Base):
    __tablename__ = 'user_profiles'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String(100), unique=True)
    interests = Column(Text)
    skills = Column(Text)
    goals = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

# Create engine (SQLite example)
engine = create_engine('sqlite:///career_system.db')
Base.metadata.create_all(engine)

# Create session
Session = sessionmaker(bind=engine)
session = Session()