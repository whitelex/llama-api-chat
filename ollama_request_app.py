import json
from flask import Flask, request, jsonify
import requests
from uuid import uuid4

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for session handling

# Load configuration from a JSON file
with open('config.json') as config_file:
    config = json.load(config_file)

external_api_url = config.get('EXTERNAL_API_URL', 'https://default-url.example.com/api/chat')

# Flag to control debug logging
debug_logging = config.get('DEBUG_LOGGING', False)

@app.route('/api/chat', methods=['POST'])
def chat():
    # Get the data from the request and ensure it's parsed as JSON
    data = request.get_json()
    model = data.get('model')
    prompt = data.get('prompt')
    session_id = data.get('session_id', str(uuid4()))  # Use existing session ID or generate a new one

    if not model or not prompt:
        return jsonify({"error": "Model and prompt are required"}), 400

    # Prepare the payload for the external API request
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "session_id": session_id  # Pass the session_id to the external API
    }

    # Debug: Log the data being sent if debug_logging is enabled
    if debug_logging:
        print(f"DEBUG: Sending to external API: {json.dumps(payload, indent=2)}")

    # Send the POST request to the external API
    try:
        response = requests.post(external_api_url, json=payload, stream=True)
        response.raise_for_status()  # Raises an error for bad responses

        # Initialize an empty string to hold the full response
        full_response = ""

        # Read the response line by line
        for line in response.iter_lines():
            if line:
                # Decode and parse each line as JSON
                line_data = json.loads(line.decode('utf-8'))
                content = line_data['message']['content']
                full_response += content

        # Debug: Log the received data if debug_logging is enabled
        if debug_logging:
            print(f"DEBUG: Received from external API: {full_response}")

    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

    # Return the session ID and the response
    return jsonify({"session_id": session_id, "response": full_response})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
