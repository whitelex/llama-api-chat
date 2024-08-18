# Flask Chat API with LLaMA Integration

This project is a Flask-based API that interacts with the LLaMA API to handle chat-based sessions. The API supports session management, allowing for follow-up questions to be answered in context by maintaining conversation history.

## Features

- **Session Handling**: Each session maintains the conversation history, allowing the LLaMA API to respond contextually to follow-up questions.
- **Configurable API Endpoint**: The external API URL can be configured via environment variables or a configuration file.
- **In-Memory Session Storage**: Conversation histories are stored in-memory using Python dictionaries.

## Requirements

- Python 3.7+
- Flask
- Requests
- A running instance of the LLaMA server

## Installation

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/your-username/your-repo-name.git
   cd your-repo-name
