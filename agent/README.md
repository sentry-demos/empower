# Simple Plant Care AI Agent

A simple FastAPI-based plant care AI assistant powered by the OpenAI Agents SDK. Just provide a plant name and get personalized care advice!

## Features

- 🌱 **Simple Plant Care Agent**: Get care advice for any plant by name
- 🛠️ **One Tool**: Basic plant care database with common houseplants
- 🚀 **FastAPI Backend**: Modern, fast API with automatic docs
- 📚 **Interactive API Docs**: Built-in Swagger UI at `/docs`
- 🎯 **Minimal Dependencies**: Bare bones implementation following OpenAI Agents SDK

## Quick Start

### Prerequisites

- Python 3.11+
- OpenAI API key

### Installation

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd empower-plant-agent-demo
   ```

2. **Set up environment variables**

   ```bash
   export OPENAI_API_KEY=sk-your-api-key-here
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python main.py
   ```

The API will be available at `http://localhost:8000` with interactive docs at `http://localhost:8000/docs`.

## Usage

### API Endpoint

**POST** `/api/v1/plant-care`

Request body:

```json
{
  "plant_name": "pothos"
}
```

Response:

```json
{
  "response": "🌱 **Pothos Care Guide**\n\n**Watering**: Water when top inch of soil is dry (every 1-2 weeks)\n**Light**: Bright, indirect light\n**Pro Tip**: Very forgiving plant, great for beginners. Can tolerate low light.\n\n**General Care Reminders**:\n• Check soil moisture before watering\n• Ensure good drainage\n• Watch for signs of overwatering (yellow leaves)\n• Rotate plant occasionally for even growth",
  "agent_name": "PlantCareAgent"
}
```

### Direct Python Usage

```python
import asyncio
from app.agents.simple_plant_agent import process_plant_query

async def main():
    advice = await process_plant_query("snake plant")
    print(advice)

asyncio.run(main())
```

### Example with curl

```bash
curl -X POST "http://localhost:8000/api/v1/plant-care" \
     -H "Content-Type: application/json" \
     -d '{"plant_name": "monstera"}'
```

## Supported Plants

The agent has specific care information for:

- Pothos
- Snake Plant
- Monstera
- Fiddle Leaf Fig
- Peace Lily
- Rubber Plant
- Succulents

For other plants, it provides general care advice and suggests trying the supported plants.

## Project Structure

```
app/
├── agents/
│   └── simple_plant_agent.py    # Main agent with OpenAI Agents SDK
├── tools/
│   └── simple_plant_tool.py     # Plant care tool/function
└── api/
    ├── models.py                # Pydantic request/response models
    └── routes.py         # FastAPI routes

main.py                          # FastAPI application entry point
simple_example.py               # Direct usage example
config.py                       # Configuration management
```

## Configuration

Set these environment variables:

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `light_model`: Model for the agent (default: "gpt-4o-mini")
- `API_HOST`: API host (default: "0.0.0.0")
- `PORT`: API port (default: 8000)

## Development

Run the simple example:

```bash
python simple_example.py
```

Check the API docs:

```bash
python main.py
# Visit http://localhost:8000/docs
```

## OpenAI Agents SDK

This project follows the [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/) patterns:

- **Agent**: Simple plant care assistant with instructions
- **Tool**: Function tool for plant care advice
- **Runner**: Handles the agent execution loop

The implementation is minimal and focused, demonstrating the core concepts without complexity.
