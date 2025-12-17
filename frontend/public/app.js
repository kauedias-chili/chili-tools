// This file contains the JavaScript code for the front-end application, handling user interactions, API requests, and updating the dashboard in real-time.

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('agent-form');
    const resultDiv = document.getElementById('result');

    form.addEventListener('submit', function(event) {
        event.preventDefault();
        const formData = new FormData(form);
        fetch('src/api.php', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            resultDiv.innerHTML = JSON.stringify(data, null, 2);
        })
        .catch(error => {
            console.error('Error:', error);
            resultDiv.innerHTML = 'An error occurred. Please try again.';
        });
    });
});