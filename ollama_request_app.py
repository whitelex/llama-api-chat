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
    """Retrieve the conversation history for a given session ID, limited to the last 5 messages."""
    return conversation_histories.get(session_id, [])

def update_conversation_history(session_id, role, content):
    """Update the conversation history for a given session ID."""
    if session_id not in conversation_histories:
        conversation_histories[session_id] = []
    conversation_histories[session_id].append({"role": role, "content": content})

    # Limit the history to the last 5 messages
    if len(conversation_histories[session_id]) > 5:
        conversation_histories[session_id] = conversation_histories[session_id][-5:]

@app.route('/api/chat', methods=['POST'])
def chat():
    # Get the data from the request and ensure it's parsed as JSON
    data = request.get_json()
    model = data.get('model')
    session_id = data.get('session_id', str(uuid4()))  # Use existing session ID from Alexa or generate a new one

    if not model:
        return jsonify({"error": "Model is required"}), 400

    # Retrieve the conversation history based on the session ID
    conversation_history = get_conversation_history(session_id)

    # Extract the latest user input from the incoming messages
    messages = data.get('messages', [])
    if messages and isinstance(messages, list):
        latest_message = messages[-1]
        update_conversation_history(session_id, latest_message["role"], latest_message["content"])

    # Prepare the payload for the external API request
    payload = {
        "model": model,
        "messages": conversation_history
    }

    # Debug: Log the data being sent
    print(f"Sending to external API: {json.dumps(payload, indent=2)}")

    # Send the POST request to the external API
    try:
        response = requests.post(external_api_url, json=payload)
        response.raise_for_status()  # Raises an error for bad responses

        # Debug: Log the response data
        print(f"Received from external API: {response.text}")

        response_json = response.json()
        assistant_response = response_json.get('response', '')

        # Update the conversation history with the API's response
        update_conversation_history(session_id, "assistant", assistant_response)

    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

    # Return the session ID and the response
    return jsonify({"session_id": session_id, "response": assistant_response})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
