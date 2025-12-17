# Multi-Agent System Project

This project implements a multi-agent system using the CrewAI framework, with a front-end developed in PHP, JavaScript, and HTML, and a back-end built in Python.

## Project Structure

The project is organized into two main directories: `backend` and `frontend`.

### Backend

- **crewai_app**: Contains the core application logic.
  - `__init__.py`: Initializes the CrewAI application package.
  - `agents.py`: Defines agent classes such as AudienceMarketAuditor, KeywordPlanner, ContentWriter, and ContentManager.
  - `main.py`: Entry point for the application, orchestrating agent execution.
  - `utils.py`: Contains utility functions for data processing and API calls.
- `requirements.txt`: Lists the dependencies required for the Python backend.
- `README.md`: Documentation for setting up and running the Python application.

### Frontend

- **public**: Contains static files for the front-end application.
  - `index.html`: Main HTML file for the web dashboard.
  - `styles.css`: CSS styles for the dashboard.
  - `app.js`: JavaScript code for handling user interactions and API requests.
- **src**: Contains server-side scripts.
  - `api.php`: Handles API requests from the front-end to the back-end.
- `README.md`: Documentation for setting up and running the PHP application.

## Setup Instructions

### Backend

1. Navigate to the `backend` directory.
2. Install the required dependencies using pip:
   ```
   pip install -r requirements.txt
   ```
3. Run the application:
   ```
   python -m crewai_app.main
   ```

### Frontend

1. Navigate to the `frontend` directory.
2. Ensure your PHP server is running.
3. Access the application via your web browser.

## Architecture

The system is designed to facilitate interaction between multiple agents, each responsible for specific tasks in the workflow. The front-end communicates with the back-end via API calls, allowing for real-time updates and user interactions.

## Workflow

1. Users interact with the front-end dashboard.
2. The front-end sends requests to the back-end via the API.
3. The back-end processes the requests using the defined agents.
4. Results are returned to the front-end for display.

This project aims to provide a robust framework for developing and managing multi-agent systems efficiently.