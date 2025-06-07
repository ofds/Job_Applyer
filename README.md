Project Title: Job_Applyer Automation & Management Dashboard

Document Version: 2.0
Last Updated: June 7, 2025

About This Document: This is the single source of truth for the Job_Applyer project. It is intended to be a comprehensive guide for human developers and a detailed context prompt for Large Language Model (LLM) assistants. It outlines the project's goals, architecture, technical specifications, and history of key decisions.
1. Project Status

    Current Phase: Phase 2: Database and Gupy Bot Development.
    Completed Milestones:
        Full project setup and environment configuration.
        Creation and customization of the frontend dashboard shell.
        Database schema definition and file creation.
        Initial implementation and debugging of the Gupy bot's login and search flow.
    Next Immediate Goal: Achieve a successful end-to-end run of the Gupy bot, from login to applying for the first new job found.

2. Project Overview & Objective

The primary objective is to develop a system that automates the repetitive tasks of job searching and applying on platforms like Gupy and LinkedIn. The system will find relevant job openings, apply to them where possible, and present all activities and their outcomes in a centralized, interactive web dashboard.

The end goal is a powerful, personal "control center" that handles high-volume, simple applications, allowing the user to focus their time and energy on applications that require manual, human intervention (e.g., custom cover letters, complex questions).
3. System Architecture & Data Flow

The system operates in a decoupled manner, especially during development:

    Manual Trigger: The user manually executes a bot script (e.g., python scripts/gupy_bot.py) from the command line.
    Configuration: The script starts by loading credentials and settings (keywords, file paths) from config.py.
    Automation: The script uses Selenium to open a browser, navigate to the target website (e.g., Gupy), and perform actions like logging in, searching, and filling forms.
    Data Persistence: As the bot operates, it reads from and writes to the central jobs.db SQLite database. It checks the database to avoid re-applying for jobs and saves new jobs and application statuses.
    Dashboard (Future): In a separate process, the user will run the Flask server (app.py). This server will have API endpoints that read data from jobs.db. The web dashboard, running in the browser, will call these APIs to fetch and display the application data. Eventually, the dashboard will have buttons to trigger the bot scripts.

4. Project File Structure

Job_Applyer/
├── .gitignore
├── dashboard/                <-- Frontend AdminLTE template files (HTML, CSS, JS)
├── scripts/                  <-- Selenium automation scripts
│   ├── gupy_bot.py
│   └── linkedin_bot.py       (To be created)
├── app.py                    <-- Main Flask application file (API & web server)
├── config.py                 <-- User credentials, keywords, file paths (SECRET)
├── database.py               <-- SQLAlchemy database models and setup
├── jobs.db                   <-- The SQLite database file
└── objective.txt             <-- This file

5. Technology Stack

    Automation/Backend: Python 3.x
    Browser Automation: Selenium
        Driver Management: webdriver-manager (with default caching)
    Web Framework (API): Flask
    Database: SQLite
    Database ORM: SQLAlchemy
    Frontend: Pre-built AdminLTE Dashboard Template (HTML, CSS, JavaScript)

6. Core Components & Functionality

A) Scraper & Operator Bots (The "Worker")

    Files: scripts/gupy_bot.py, scripts/linkedin_bot.py
    Role: Python scripts using Selenium to mimic human actions.
    Gupy Bot: Navigates Gupy portals, logs in, searches keywords, checks the database for existing applications, and applies to the first new job found.
    LinkedIn Bot: (Future) Will handle LinkedIn "Easy Apply" jobs.

B) Central Database (The "Brain")

    Files: database.py (definition), jobs.db (data file)
    Role: An SQLite database managed by SQLAlchemy, acting as the project's memory.
    Function: Stores job listings, application statuses, timestamps, and notes. Crucially used by bots to determine which jobs are "new" and avoid duplication.

C) Interactive Dashboard (The "Control Center")

    Files: app.py (backend server), dashboard/ (frontend files)
    Role: A web interface for monitoring and eventually controlling the bots.
    Function:
        Main View: Table of all applications.
        Control Panel: (Future) Buttons to trigger bot runs.
        Action Required Tab: Lists applications that failed or need manual completion.

7. Core Data Models (Database Schema)

Source: database.py
Python

class Job(Base):
    __tablename__ = 'jobs'
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    company = Column(String, nullable=False)
    url = Column(String, unique=True, nullable=False)
    platform = Column(String)
    applications = relationship("Application", back_populates="job")

class Application(Base):
    __tablename__ = 'applications'
    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey('jobs.id'), nullable=False)
    status = Column(String, default='Pending')
    application_date = Column(DateTime, default=datetime.utcnow)
    notes = Column(String)
    job = relationship("Job", back_populates="applications")

8. Key Challenges & Implemented Solutions

    ModuleNotFoundError: Encountered when running scripts from a subfolder.
        Solution: Added a code block at the top of bot scripts to dynamically add the project's root directory to Python's sys.path, ensuring modules like config and database are always found.
    Slow Bot Startup: The driver was being re-downloaded on every run.
        Solution: Corrected the Selenium setup to use the default caching mechanism of webdriver-manager, ensuring the driver is downloaded only once, providing near-instant startups on subsequent runs.
    Dynamic/Random CSS Classes: Job card elements had unstable class names.
        Solution: Refactored the bot to use more stable selectors, such as the <ul>/<li> HTML tag structure and data-testid attributes where available.
    Cookie Consent Banners: Pop-ups were blocking access to login forms.
        Solution: Implemented a try/except block in the login function that waits for a few seconds for the cookie banner to appear and clicks it if found, but continues safely if it doesn't appear.

9. MVP Success Criteria

The initial version is a success when the user can:

    Run the Gupy bot script from the command line.
    The bot successfully logs in, searches for a keyword, finds a job not already in the database, and performs the initial "apply" steps.
    The new job and application status are correctly saved in the jobs.db file.
    (Future) Launch the dashboard via app.py and see a table populated with the data from jobs.db.

(The original 50-step checklist is retained below for historical project planning purposes.)
Project Checklist: The 50 Steps to Completion
Phase 1: Project Setup & Dashboard Configuration (Steps 1-8)

    [ ] 1. Create the master project folder: Job_Applyer.
    [ ] 2. Create and populate the objective.txt file with the project overview.
    [ ] 3. Initialize and activate a Python virtual environment (venv) inside the project folder.
    [ ] 4. Install all core Python packages: pip install flask selenium webdriver-manager sqlalchemy.
    [ ] 5. Download the AdminLTE dashboard template and place it in a /dashboard subfolder.
    [ ] 6. Create the basic project file structure: app.py (main Flask app), /scripts (for bots), /database (for the db file).
    [ ] 7. Create a "Hello World" Flask route in app.py to confirm the server runs correctly.
    [ ] 8. Customize the AdminLTE dashboard: strip out all unnecessary pages and widgets, leaving a clean shell for our application table.

Phase 2: Database and Gupy Bot Development (Steps 9-21)

    [ ] 9. In a new database.py file, define the Job and Application database models using SQLAlchemy.
    [ ] 10. Write a script to create the initial jobs.db SQLite database file from the models.
    [ ] 11. Create a config.py file to store your keywords, Gupy login credentials, and resume file path.
    [ ] 12. Create the Gupy bot script: scripts/gupy_bot.py.
    [ ] 13. Implement the initial Selenium logic to open a browser and navigate to a target Gupy-powered career page.
    [ ] 14. Write the function to perform a job search using the keywords from config.py.
    [ ] 15. Develop the scraper function to extract job titles and application URLs from the search results page.
    [ ] 16. Write the logic to save new, unique jobs found by the scraper into the jobs.db database.
    [ ] 17. Develop the core application bot: navigate to a job link and identify the main application form.
    [ ] 18. Write the Selenium code to fill in basic form fields (name, email, etc.) by reading your info from the config file.
    [ ] 19. Implement the Selenium logic to handle the file input for uploading your resume.
    [ ] 20. Implement try...except error handling: if a step fails, log it.
    [x] 21. After an application attempt, update the application's status in the database to "Applied" or "Failed".

Phase 3: LinkedIn Bot Development (Steps 22-31)

    [ ] 22. Create the LinkedIn bot script: scripts/linkedin_bot.py.
    [ ] 23. Manually log into LinkedIn, export the session cookies, and save them to a file.
    [ ] 24. Write the Selenium logic to start a session by loading the saved cookies to bypass direct login.
    [ ] 25. Implement the LinkedIn job search function (navigate to /jobs, enter keywords, apply filters).
    [ ] 26. Write the scraper logic to specifically identify "Easy Apply" jobs and extract their data.
    [ ] 27. Save the scraped LinkedIn "Easy Apply" jobs to the database.
    [ ] 28. Develop the "Easy Apply" bot logic to click through the application modal.
    [ ] 29. Write Selenium code to fill out the standard fields within the "Easy Apply" form.
    [ ] 30. Implement basic logic to handle common conditional steps, like yes/no radio buttons.
    [ ] 31. Update the database with "Applied" or "Failed" status after each LinkedIn application attempt.

Phase 4: Backend API Development (Steps 32-39)

    [ ] 32. In app.py, set up the Flask application and connect it to the SQLite database.
    [ ] 33. Create the main API endpoint /api/applications to fetch and return all applications as JSON.
    [ ] 34. Create the "Action Required" API endpoint /api/applications/action-required to return only applications with a "Failed" or "Pending Action" status.
    [ ] 35. Create a trigger endpoint /api/run-gupy that, when called, will execute the gupy_bot.py script.
    [ ] 36. Create a similar trigger endpoint /api/run-linkedin to execute the linkedin_bot.py script.
    [ ] 37. Add Cross-Origin Resource Sharing (CORS) support to your Flask app to allow the dashboard to communicate with it.
    [ ] 38. Refine all API endpoints to ensure they handle requests correctly and return proper JSON responses and status codes.
    [ ] 39. Add logging to your Flask app to see incoming API requests in the terminal.

Phase 5: Dashboard Frontend Integration (Steps 40-46)

    [ ] 40. In your main dashboard/index.html file, create the final HTML table structure for displaying applications.
    [ ] 41. Write JavaScript to call your /api/applications endpoint using the fetch() API when the page loads.
    [ ] 42. Write the JavaScript function to dynamically create and populate the table rows with the data received from the API.
    [ ] 43. Create the "Action Required" tab in the dashboard and write the JavaScript to populate its table using the corresponding API endpoint.
    [ ] 44. Create the "Run Gupy Bot" and "Run LinkedIn Bot" buttons in the dashboard UI.
    [ ] 45. Hook up the UI buttons to the API trigger endpoints (/api/run-gupy, etc.) using JavaScript.
    [ ] 46. Add a simple loading indicator or message that appears when the bots are running.

Phase 6: Final Testing & Refinement (Steps 47-50)

    [ ] 47. Perform a full, end-to-end test: Use the dashboard UI to start a bot, watch it run, and see the application table populate automatically.
    [ ] 48. Refine the UI based on testing: improve auto-refresh, format dates nicely, make links clickable.
    [ ] 49. Review all your Python and JavaScript code, adding comments where necessary for future reference.
    [ ] 50. Create the final README.md file in your project's root directory, explaining what the project is and how to set it up and run it from scratch.