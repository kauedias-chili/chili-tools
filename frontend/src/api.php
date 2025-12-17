<?php
// This file handles API requests from the front-end to the back-end, processing input from the user and returning data from the agents.

header("Content-Type: application/json");

// Include the necessary files for backend communication
require_once 'backend/crewai_app/main.php';

// Function to handle incoming API requests
function handleApiRequest($request) {
    // Process the request and interact with the backend
    // Example: Call the main function from the backend to execute agents
    $response = executeAgents($request);
    return $response;
}

// Get the request method and input data
$requestMethod = $_SERVER['REQUEST_METHOD'];
$requestData = json_decode(file_get_contents('php://input'), true);

if ($requestMethod === 'POST') {
    // Handle POST requests
    $response = handleApiRequest($requestData);
    echo json_encode($response);
} else {
    // Handle unsupported request methods
    http_response_code(405);
    echo json_encode(["error" => "Method not allowed"]);
}
?>