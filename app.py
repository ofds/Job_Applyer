# app.py

from flask import Flask
from database import create_db_and_tables  # <-- 1. ADD THIS IMPORT

# Create the Flask application instance
app = Flask(__name__)

# This will call the function from database.py to create the .db file and tables
create_db_and_tables()  # <-- 2. ADD THIS LINE

# Define a route for the home page
@app.route('/')
def hello_world():
    return 'Hello, World! Your Flask server is running.'

# This allows you to run the app directly from the command line
if __name__ == '__main__':
    app.run(debug=True)