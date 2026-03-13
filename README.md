# LLM-Powered Prompt Router for Intent Classification

This is a Python-based service that intelligently routes user requests to specialized AI personas based on intent classification. It uses OpenAI's GPT models to classify user messages and generate responses from expert personas.

## Architecture

The system implements a two-step process:
1. **Classification**: A lightweight LLM call classifies the user's intent into categories (code, data, writing, career, unclear) with a confidence score.
2. **Routing and Response**: Based on the classified intent, routes to a specialized expert persona for generating the final response.

## Features

- Intent classification with confidence scoring
- Four specialized expert personas: Code Expert, Data Analyst, Writing Coach, Career Advisor
- Graceful handling of unclear intents with clarifying questions
- Comprehensive logging of all interactions to `route_log.jsonl`
- RESTful API endpoint for routing requests
- Containerized with Docker for easy deployment

## Setup Instructions

### Prerequisites
- Docker and Docker Compose
- OpenAI API key

### Installation

1. Clone this repository:
   ```bash
   git clone <repository-url>
   cd prompt-router
   ```

2. Copy the environment file and add your OpenAI API key:
   ```bash
   cp .env.example .env
   # Edit .env and replace 'your_openai_api_key_here' with your actual OpenAI API key
   ```

3. Build and run the application using Docker Compose:
   ```bash
   docker-compose up --build
   ```

The service will be available at `http://localhost:5000`.

## API Usage

### POST /route

Route a user message to the appropriate expert persona.

**Request Body:**
```json
{
  "message": "how do I sort a list in python?"
}
```

**Response:**
```json
{
  "response": "Here's production-quality code: ...",
  "intent": {
    "intent": "code",
    "confidence": 0.92
  }
}
```

**Example using curl:**
```bash
curl -X POST http://localhost:5000/route \
  -H "Content-Type: application/json" \
  -d '{"message": "how do I sort a list in python?"}'
```

## Expert Personas

### Code Expert
Provides production-quality code with robust error handling and idiomatic style.

### Data Analyst
Interprets data patterns using statistical concepts and suggests visualizations.

### Writing Coach
Offers feedback on clarity, structure, and tone without rewriting the text.

### Career Advisor
Gives concrete, actionable career advice after asking clarifying questions.

### Unclear Intent
When intent cannot be determined, asks for clarification.

## Logging

All routing decisions and responses are logged to `route_log.jsonl` in JSON Lines format. Each entry contains:
- `intent`: Classified intent label
- `confidence`: Confidence score
- `user_message`: Original user message
- `final_response`: Generated response

## Testing

The application has been tested with various sample messages covering different intents. The log file `route_log.jsonl` contains examples from testing.

## Design Decisions

- **Python/Flask**: Chosen for simplicity and ease of API development.
- **OpenAI GPT-3.5-turbo for classification**: Cost-effective and fast for intent classification.
- **OpenAI GPT-4 for responses**: Higher quality responses from expert personas.
- **JSON Lines logging**: Easy to append and parse log entries.
- **Docker containerization**: Ensures consistent deployment environment.

## Error Handling

- Invalid JSON responses from LLM are handled gracefully by defaulting to "unclear" intent.
- API errors are caught and logged, with fallback error messages.
- Missing API keys or network issues are handled with appropriate error responses.