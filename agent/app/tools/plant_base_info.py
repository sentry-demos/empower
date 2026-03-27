"""Simple plant care tool that provides basic advice for a given plant name."""

import logging
from typing import Any

from agents import FunctionTool

from ..utils import maybe_throw

# Configure logging
logging.basicConfig(level=logging.DEBUG)


def get_plant_basic_info(plant_names: list) -> str:
    """Get basic info for supported plants.

    Args:
        plant_names: List of plant names

    Returns:
        Basic info for each plant
    """
    plant_db = {
        "rose": {
            "water": "Water regularly, keep soil moist but not waterlogged",
            "light": "Full sun (6+ hours daily)",
            "tips": "Classic flowering plant. ",
        },
        "sunflower": {
            "water": "Water deeply but infrequently, drought tolerant once established",
            "light": "Full sun all day",
            "tips": "Fast-growing annual flower. Can grow very tall, may need staking.",
        },
        "tulip": {
            "water": "Water moderately during growing season, reduce after flowering",
            "light": "Full sun to partial shade",
            "tips": "Spring bulb flower. Plant bulbs in fall for spring blooms.",
        },
    }

    maybe_throw(0.1, Exception("Could not get plant basic info: Unknown plant"))

    # Collect info for each plant
    info_list = []
    for plant_name in plant_names:
        plant_key = plant_name.lower().strip()
        if plant_key in plant_db:
            plant_info = plant_db[plant_key]
            info_list.append(
                f"🌸 **{plant_name.title()} Basic Info**\n\n"
                f"**Watering**: {plant_info['water']}\n"
                f"**Light**: {plant_info['light']}\n"
                f"**Care Tip**: {plant_info['tips']}"
            )
        else:
            info_list.append(
                f"🌸 **{plant_name.title()}**\n\nNo specific information available."
            )

    return "\n\n".join(info_list)


async def _invoke_plant_advice(context: Any, input_json: str) -> str:
    """Invoke the plant advice tool."""
    import json

    maybe_throw(0.2, Exception("Could not get plant advice: File not found"))

    try:
        logging.debug(f"Invoking get_plant_basic_info with input: {input_json}")
        params = json.loads(input_json)
        plant_names = params.get("plant_names", [])
        if not plant_names:
            return "Please provide plant names to get care advice."
        return get_plant_basic_info(plant_names)
    except Exception as e:
        logging.error(f"Error in get_plant_basic_info: {str(e)}")
        return f"Error getting plant advice: {str(e)}"


# Create the function tool
plant_base_info_tool = FunctionTool(
    name="get_plant_basic_info",
    description="Get basic info for supported flowers (rose, sunflower, tulip)",
    params_json_schema={
        "type": "object",
        "properties": {
            "plant_names": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of plant names to get care advice for",
            }
        },
        "required": ["plant_names"],
    },
    on_invoke_tool=_invoke_plant_advice,
)
