# Backend README

# Multi-Agent System Backend

This document provides instructions for setting up and running the backend of the Multi-Agent System developed using the CrewAI framework.

## Project Structure

The backend consists of the following files:

- **crewai_app/**: Contains the main application code.
  - **\_\_init\_\_.py**: Initializes the CrewAI application package.
  - **agents.py**: Defines the agent classes including AudienceMarketAuditor, KeywordPlanner, ContentWriter, and ContentManager.
  - **main.py**: Entry point for the application, orchestrating the execution of agents.
  - **utils.py**: Contains utility functions for data processing, API calls, and logging.
  
- **requirements.txt**: Lists the dependencies required for the Python backend.

## Setup Instructions

1. **Clone the Repository**
   ```
   git clone <repository-url>
   cd multi-agent-system/backend
   ```

2. **Create a Virtual Environment**
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install Dependencies**
   ```
   pip install -r requirements.txt
   ```

## Running the Application

To run the application, execute the following command:
```
python crewai_app/main.py
```

## API Endpoints

The backend exposes several API endpoints that can be accessed by the front-end application. Refer to the front-end documentation for details on how to interact with these endpoints.

## Contributing

Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.