# Frontend Multi-Agent System Documentation

## Overview
This directory contains the front-end components of the multi-agent system developed using the CrewAI framework. The front-end is built using PHP, JavaScript, and HTML, providing a user-friendly interface for interacting with the back-end agents.

## Structure
- **public/**: Contains the main HTML, CSS, and JavaScript files for the front-end application.
  - **index.html**: The entry point for the web dashboard.
  - **styles.css**: Styles for the dashboard layout and appearance.
  - **app.js**: JavaScript code for handling user interactions and API requests.

- **src/**: Contains server-side scripts.
  - **api.php**: Handles API requests from the front-end to the back-end.

## Setup Instructions
1. Ensure you have a web server capable of running PHP.
2. Place the contents of the `public` directory in your web server's root directory.
3. Configure the server to point to the `src/api.php` for handling API requests.
4. Open `index.html` in your web browser to access the dashboard.

## Usage
- The front-end allows users to interact with the multi-agent system, sending requests to the back-end and receiving responses from the agents.
- Users can perform various tasks as defined by the capabilities of the agents.

## Development
- For any changes in the front-end, update the respective files in the `public` and `src` directories.
- Ensure to test the application in a local environment before deploying changes to production.

## Contributing
Contributions to improve the front-end experience are welcome. Please follow the standard procedure for submitting pull requests and ensure to document any changes made.