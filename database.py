# database.py

import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime

# This is the base class that our models will inherit from.
# SQLAlchemy uses this to connect our Python classes to database tables.
Base = declarative_base()

# --- Define the Database Tables as Python Classes ---

class Job(Base):
    """
    This class defines the 'jobs' table.
    It stores information about each unique job posting found.
    """
    __tablename__ = 'jobs'  # The actual name of the table in the database.

    id = Column(Integer, primary_key=True) # A unique ID for each job.
    title = Column(String, nullable=False) # The job title, e.g., "Software Engineer".
    company = Column(String, nullable=False) # The company name.
    url = Column(String, unique=True, nullable=False) # The URL to the job posting, must be unique.
    platform = Column(String) # Where we found the job, e.g., "LinkedIn" or "Gupy".

    # This creates a link to the Application model.
    # It says that one Job can have many Applications.
    applications = relationship("Application", back_populates="job")

    def __repr__(self):
        return f"<Job(id={self.id}, title='{self.title}', company='{self.company}')>"

class Application(Base):
    """
    This class defines the 'applications' table.
    It stores a record of every application attempt we make.
    """
    __tablename__ = 'applications'

    id = Column(Integer, primary_key=True) # A unique ID for each application attempt.
    job_id = Column(Integer, ForeignKey('jobs.id'), nullable=False) # A link to the specific job in the 'jobs' table.
    status = Column(String, default='Pending') # The status, e.g., "Applied", "Failed", "Pending Action".
    application_date = Column(DateTime, default=datetime.utcnow) # The date and time of the application attempt.
    notes = Column(String) # Optional notes, e.g., "Error during application", "Requires manual answer".

    # This links back to the Job model.
    job = relationship("Job", back_populates="applications")

    def __repr__(self):
        return f"<Application(id={self.id}, status='{self.status}', job_id='{self.job_id}')>"


# --- Setup to Connect to the Database ---

# Define the path to our database file.
# It will be created in the root of our project as 'jobs.db'.
DATABASE_URL = "sqlite:///jobs.db"

# The 'engine' is the entry point to our database.
engine = create_engine(DATABASE_URL)

# The 'SessionLocal' is what we'll use to actually talk to the database (add, query, etc.).
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_db_and_tables():
    """
    A function to create the database file and all defined tables.
    We will call this function once from our main app.py file.
    """
    Base.metadata.create_all(bind=engine)