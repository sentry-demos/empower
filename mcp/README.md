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

# Development with caller script
pnpm dev:caller

# Production
pnpm build
pnpm start

# Production with caller script
pnpm start:caller
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

## Caller Script

The caller script automatically calls MCP tools at configurable intervals with callerful output.

### Usage

```bash
# Run with server (enabled via flag or env var)
pnpm start:with-caller
pnpm start:with-caller

# Run standalone
pnpm caller-script

# Run with custom options
pnpm caller-script -- --interval 30 --tool get-plant-care-guide
```

### Available Tools

- `get-products` - Fetch plant products
- `get-plant-care-guide` - Get plant care information
- `checkout` - Process checkout (requires parameters)

## Environment

Set `PORT` environment variable (default: 3000).
