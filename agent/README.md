# Empower Plant Shopping Agent

A FastAPI-based AI shopping assistant for plant care gadgets and accessories, powered by the OpenAI Agents SDK and MCP (Model Context Protocol).

## Features

- 🛒 **Conversational Shopping**: Interactive chat-based product recommendations
- 🔌 **MCP Integration**: Fetches real product data via MCP server
- 💬 **Session Management**: Maintains conversation history across messages
- 🎯 **Smart Questioning**: Dynamically generates relevant questions based on actual product differences
- 🛍️ **Checkout Flow**: Complete purchase flow with structured responses

## Quick Start

### Prerequisites

- Python 3.11+
- OpenAI API key
- Running MCP server (see `/mcp` directory)

### Installation

1. **Set up environment variables**

   The deploy script handles this, but key variables include:
   - `OPENAI_API_KEY` or `AGENT_OPENAI_API_KEY`
   - `MCP_URL` - URL to the MCP server

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python main.py
   ```

The API will be available at `http://localhost:8093` with interactive docs at `/docs`.

## API Endpoints

### Health Check

**GET** `/api/v1/health`

Returns service health status.

### Chat

**POST** `/api/v1/chat`

Conversational endpoint with session support.

Request body:
```json
{
  "session_id": "unique-session-id",
  "message": "I'm looking for a gift for a plant lover"
}
```

Response:
```json
{
  "session_id": "unique-session-id",
  "items": [
    {"type": "message", "content": {"text": "Great! What's your budget?"}},
    {"type": "product_card", "content": {"id": 3, "name": "Plant Mood", "price": 155, "description": "..."}},
    {"type": "checkout_result", "content": {"success": true, "message": "Order confirmed!"}}
  ]
}
```

Response item types:
- `message` - Text response from the agent
- `product_card` - Product recommendation (rendered as card in UI)
- `checkout_result` - Checkout success/failure

## Architecture

```
agent/
├── app/
│   ├── agents/
│   │   ├── shopping_agent.py      # Main shopping agent
│   │   └── question_generator.py  # Generates questions via MCP
│   ├── api/
│   │   ├── models.py              # Pydantic models
│   │   └── routes.py              # FastAPI routes
│   └── question_store.py          # Session state management
├── main.py                        # FastAPI entry point
└── config.py                      # Configuration
```

## How It Works

1. **First Message**: Agent fetches products from MCP, generates targeted questions
2. **Conversation**: Agent asks questions one at a time, narrows down choices
3. **Recommendation**: Once enough info gathered, recommends specific product
4. **Checkout**: User confirms, agent calls MCP checkout tool

## Configuration

Environment variables:
- `AGENT_DSN`: Sentry DSN for error tracking
- `AGENT_SENTRY_ENVIRONMENT`: Environment name
- `MCP_URL`: MCP server URL (e.g., `https://staging-mcp.example.com`)
- `OPENAI_API_KEY`: OpenAI API key

## Development

Run locally with the deploy script:
```bash
./deploy --env=local agent
```

Or with MCP via ngrok:
```bash
# Terminal 1: Start MCP with ngrok
cd mcp && ./run_local.sh

# Terminal 2: Start agent
cd agent && ./run_local.sh
```
