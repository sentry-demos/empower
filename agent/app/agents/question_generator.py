"""Question Generator - fetches products via MCP and provides hardcoded question flow."""

import json
import logging
import os

from agents import Agent, HostedMCPTool, Runner

from config import settings

logging.basicConfig(level=logging.DEBUG)

# MCP URL for product data
MCP_URL = os.environ["MCP_URL"] + "/mcp"

HARDCODED_QUESTIONS = [
    "Are you looking for a fun novelty item or something to monitor a large number of plants?",
    "Is your main goal to never forget to water your plants?",
    "Do you have any pets or children?",
]

# Agent that fetches products from MCP
PRODUCT_FETCHER_NAME = "product_fetcher"
PRODUCT_FETCHER_INSTRUCTIONS = """
You are a product data fetcher. Your ONLY job is to:
1. Call the MCP "get-products" tool to fetch all available products
2. Output the product data as a JSON array, nothing else - do not add any explanation or commentary
"""

# Create the product fetcher agent with MCP tool
product_fetcher_agent = Agent(
    name=PRODUCT_FETCHER_NAME,
    instructions=PRODUCT_FETCHER_INSTRUCTIONS,
    model=settings.agent_model,
    tools=[
        HostedMCPTool(
            tool_config={
                "type": "mcp",
                "server_label": "empower-mcp",
                "server_url": MCP_URL,
                "require_approval": "never",
            }
        )
    ],
)


class MCPProductFetchError(Exception):
    """Raised when fetching products from MCP fails."""
    pass


async def fetch_products_via_mcp() -> list[dict]:
    """Fetch products using MCP via the product fetcher agent.
    
    Returns:
        List of product dicts from MCP.
        
    Raises:
        MCPProductFetchError: If MCP call fails or returns invalid data.
    """
    logging.debug("Fetching products via MCP...")
    
    result = await Runner.run(
        product_fetcher_agent,
        "Call the 'get-products' tool and output the JSON array of products."
    )
    output = str(result.final_output)
    logging.debug(f"Product fetcher output: {output[:500]}...")
    
    # Parse JSON from output
    start_idx = output.find('[')
    end_idx = output.rfind(']') + 1
    if start_idx == -1 or end_idx <= start_idx:
        raise MCPProductFetchError(f"No JSON array found in MCP output: {output}")
    
    json_str = output[start_idx:end_idx]
    try:
        products = json.loads(json_str)
    except json.JSONDecodeError as e:
        raise MCPProductFetchError(f"Invalid JSON from MCP: {e}. Raw: {json_str}")
    
    if not products:
        raise MCPProductFetchError("MCP returned empty product list")
    
    logging.debug(f"Parsed {len(products)} products from MCP")
    return products
