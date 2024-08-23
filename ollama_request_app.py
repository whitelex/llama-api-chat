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

# In-memory storage for conversation histories
conversation_histories = {}

def get_conversation_history(session_id):
    return conversation_histories.get(session_id, [])

def update_conversation_history(session_id, role, content):
    if session_id not in conversation_histories:
        conversation_histories[session_id] = []
    conversation_histories[session_id].append({"role": role, "content": content})

@app.route('/api/chat', methods=['POST'])
def chat():
    # Get the data from the request and ensure it's parsed as JSON
    data = request.get_json()  # Use get_json() to ensure parsing
    model = data.get('model')
    prompt = data.get('prompt')
    session_id = data.get('session_id', str(uuid4()))  # Use existing or new session ID

    if not model or not prompt:
        return jsonify({"error": "Model and prompt are required"}), 400

    # Retrieve the conversation history
    conversation_history = get_conversation_history(session_id)

    # Update the conversation history with the new user input
    update_conversation_history(session_id, "user", prompt)

    # Prepare the payload for the external API request
    payload = {
        "model": model,
        "messages": conversation_history + [{"role": "user", "content": prompt}]
    }

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

        # Update the conversation history with the API's response
        update_conversation_history(session_id, "assistant", full_response)

    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

    # Return the session ID and the response
    return jsonify({"session_id": session_id, "response": full_response})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
