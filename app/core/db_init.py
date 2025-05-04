"""
Database initialization script.
This script should be run once before starting the application to create tables
and populate initial data. It's separate from the main app to avoid multiple
workers trying to initialize the database simultaneously.
"""

import datetime
import logging
import pathlib
import random

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.database import Base

# Import all models so Base.metadata.create_all works
from app.domains.department.department_model import Department
from app.domains.location.location_model import Location
from app.domains.process.process_model import Process
from app.domains.resource.resource_model import Resource
from app.domains.role.role_model import Role
from app.domains.user.user_model import User


def create_db_and_tables(engine):
    """Create all database tables."""
    try:
        Base.metadata.create_all(bind=engine, checkfirst=True)
    except Exception as e:
        print(f"Error creating database tables: {str(e)}")
        raise


def create_initial_data(session):
    """Insert initial data into the database."""
    try:
        # create 100 users
        users = []
        for i in range(100):
            user = User(title=f"user{i}", created_at=datetime.datetime.now())
            session.add(user)
            users.append(user)
        session.flush()

        # create 100 departments
        departments = []
        for i in range(100):
            department = Department(
                title=f"department{i}",
                created_at=datetime.datetime.now(),
                created_by_id=users[0].id,
            )
            session.add(department)
            departments.append(department)

        # create 100 locations
        locations = []
        for i in range(100):
            location = Location(
                title=f"location{i}", created_at=datetime.datetime.now(), created_by_id=users[0].id
            )
            session.add(location)
            locations.append(location)

        # create 100 resources
        resources = []
        for i in range(100):
            resource = Resource(
                title=f"resource{i}", created_at=datetime.datetime.now(), created_by_id=users[0].id
            )
            session.add(resource)
            resources.append(resource)

        # create 100 roles
        roles = []
        for i in range(100):
            role = Role(
                title=f"role{i}", created_at=datetime.datetime.now(), created_by_id=users[0].id
            )
            session.add(role)
            roles.append(role)

        # create 100 processes
        processes = []
        for i in range(100):
            process = Process(
                title=f"process{i}",
                created_at=datetime.datetime.now(),
                created_by_id=users[0].id,
                departments=random.sample(departments, 5),  # random 5 departments
                locations=random.sample(locations, 5),  # random 5 locations
                resources=random.sample(resources, 5),  # random 5 resources
                roles=random.sample(roles, 5),  # random 5 roles
            )
            session.add(process)
            processes.append(process)
        session.flush()
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"Error inserting initial data: {str(e)}")
        raise


def execute_sql_scripts(engine):
    """Execute all SQL scripts from app/sql-scripts directory."""
    try:
        # Get the base directory of the application
        base_dir = pathlib.Path(__file__).parent.parent
        sql_scripts_dir = base_dir / "sql-scripts"

        # Check if the directory exists
        if not sql_scripts_dir.exists():
            print(f"SQL scripts directory not found: {sql_scripts_dir}")
            return

        # Get all SQL files in the directory, sorted by name
        sql_files = sorted([f for f in sql_scripts_dir.glob("*.sql")])

        if not sql_files:
            print("No SQL scripts found in the directory.")
            return

        # Execute each SQL file
        with engine.connect() as connection:
            for sql_file in sql_files:
                print(f"Executing SQL script: {sql_file.name}")
                sql_content = sql_file.read_text()

                # Execute the SQL script
                connection.execute(text(sql_content))
                connection.commit()

                print(f"Successfully executed SQL script: {sql_file.name}")

        print(f"Successfully executed {len(sql_files)} SQL scripts.")

    except Exception as e:
        print(f"Error executing SQL scripts: {str(e)}")
        raise


def init_database():
    """Initialize the database with tables and initial data."""
    try:
        # Suppress SQLAlchemy engine logging
        logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

        db_url = settings.SQLALCHEMY_SYNCDATABASE_URI
        engine = create_engine(db_url, echo=False)
        Session = sessionmaker(bind=engine)

        # Create tables
        create_db_and_tables(engine)

        # Execute SQL scripts to create functions, procedures, and views
        execute_sql_scripts(engine)

        # Insert initial data and closes the session
        with Session() as session:
            create_initial_data(session)

        print("Database successfully initialized with tables and initial data.")

    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        raise


if __name__ == "__main__":
    """
    Run this script directly to initialize the database:
    python -m app.core.db_init
    """
    init_database()
