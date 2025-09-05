# Mastra Setup

This directory contains a complete Mastra AI agent framework setup with example implementations.

## What's Included

- **Weather Agent** (`src/mastra/agents/weather-agent.ts`) - An AI agent that provides weather information and activity suggestions
- **Weather Tool** (`src/mastra/tools/weather-tool.ts`) - A tool that fetches real weather data from Open-Meteo API
- **Weather Workflow** (`src/mastra/workflows/weather-workflow.ts`) - A multi-step workflow that combines weather fetching with activity planning

## Quick Start

1. **Start the development server:**

   ```bash
   npm run dev
   ```

2. **Access the playground:**
   - API: http://localhost:4111/api
   - Playground: http://localhost:4111

## Key Features Demonstrated

- **Agent Memory** - The weather agent uses LibSQL for persistent memory storage
- **Tool Calling** - Agent can call the weather tool to get real-time data
- **Workflows** - Multi-step process combining weather data with AI-generated activity suggestions
- **Real API Integration** - Uses Open-Meteo API for accurate weather data

## Environment

The project is configured with:

- OpenAI GPT-4o-mini model
- LibSQL for storage
- Pino logger for structured logging
- Real weather data from Open-Meteo

## Try It Out

Ask the weather agent questions like:

- "What's the weather like in San Francisco?"
- "Plan activities for tomorrow in New York"
- "Should I go hiking in Seattle this weekend?"

The agent will fetch real weather data and provide intelligent suggestions based on current conditions.
