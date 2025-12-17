def process_data(data):
    # Function to process input data
    processed_data = data.strip().lower()
    return processed_data

def log_message(message):
    # Function to log messages to a file
    with open('app.log', 'a') as log_file:
        log_file.write(f"{message}\n")

def api_call(url, params=None):
    # Function to make an API call
    import requests
    response = requests.get(url, params=params)
    return response.json() if response.status_code == 200 else None