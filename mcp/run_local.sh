#!/bin/bash

echo "ERROR: Local MCP server cannot be used with the Agent."
echo ""
echo "The OpenAI Agents SDK requires MCP servers to be publicly accessible."
echo "When your agent calls OpenAI's API, OpenAI's servers connect to the MCP URL -"
echo "they cannot reach localhost or host.docker.internal."
echo ""
echo "Options:"
echo "  1. Deploy MCP to staging first, then run agent locally (uses staging MCP)"
echo "  2. Use ngrok to expose local MCP: ngrok http 8094"
echo "  3. Test MCP in isolation: cd mcp && pnpm dev"
echo ""
exit 1

#set -e
#
#function cleanup {
#  stop.sh mcp $MCP_LOCAL_PORT
#}
#trap cleanup EXIT
#
## Ensure Docker (via Colima) is available - sources DOCKER_HOST
#source ensure_docker.sh
#
## Only PORT needs explicit export (not in .env, comes from MCP_LOCAL_PORT)
## Other vars are read from .env file by docker-compose (via env_file directive)
#export PORT=$MCP_LOCAL_PORT
#
#docker-compose up
