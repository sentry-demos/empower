# Empower MCP Plant Care Server

A Model Context Protocol (MCP) server providing plant care tools, resources, and prompts.

## Features

- **Tools**: Get products, plant care guides, checkout
- **Resources**: Plant care database, seasonal calendars, problem diagnostics
- **Prompts**: Plant care assistant, problem diagnosis, shopping help
- **SSE Support**: Real-time server-sent events

## Quick Start

```bash
# Install dependencies
pnpm install

# Development
pnpm dev

# Production
pnpm build
pnpm start
```

## Endpoints

- `/mcp` - MCP protocol endpoint
- `/sse` - Server-sent events
- `/` - Health check

## Usage

Connect your MCP client to `http://localhost:3000/mcp` to access:

You can use MCP inspector by running `npx @modelcontextprotocol/inspector`

- Plant product catalog and checkout
- Comprehensive plant care guides
- Seasonal care calendars
- Plant problem diagnostics
- Interactive care prompts

## Environment

Set `PORT` environment variable (default: 3000).
