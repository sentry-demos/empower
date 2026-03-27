"""Stub tool for simulating plant purchase."""

import logging

from agents import FunctionTool

# Configure logging
logging.basicConfig(level=logging.DEBUG)


def buy_plants(plants: list) -> str:
    """Simulate buying plants.

    Args:
        plants: List of plants to buy

    Returns:
        Confirmation message
    """
    if not plants:
        return "No plants selected for purchase."

    return f"Successfully purchased: {', '.join(plants)}"


# Create the function tool
buy_plants_tool = FunctionTool(
    name="buy_plants",
    description="Simulate the purchase of selected plants",
    params_json_schema={
        "type": "object",
        "properties": {
            "plants": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of plants to buy",
            }
        },
        "required": ["plants"],
    },
    on_invoke_tool=lambda context, input_json: _invoke_buy_plants(input_json),
)


async def _invoke_buy_plants(input_json: str) -> str:
    """Invoke the buy plants tool."""
    import json

    try:
        logging.debug(f"Invoking buyPlants with input: {input_json}")
        params = json.loads(input_json)
        plants = params.get("plants", [])
        return buy_plants(plants)
    except Exception as e:
        logging.error(f"Error in buyPlants: {str(e)}")
        return f"Error processing purchase: {str(e)}"
