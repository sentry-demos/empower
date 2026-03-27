"""Tool to recommend plants based on light and maintenance criteria."""

import logging

from agents import FunctionTool

# Configure logging
logging.basicConfig(level=logging.DEBUG)


def get_plant_recommendations(light: str, maintenance: str) -> str:
    """Get plant recommendations based on criteria.

    Args:
        light: Light conditions (e.g., 'full sun', 'partial shade', 'low light')
        maintenance: Maintenance level (e.g., 'low', 'medium', 'high')

    Returns:
        Recommended plants to buy
    """
    # Simple plant recommendation database
    plant_recommendations = {
        "full sun": {
            "low": ["Cactus", "Lavender"],
            "medium": ["Rose", "Sunflower"],
            "high": ["Bougainvillea"],
        },
        "partial shade": {
            "low": ["Snake Plant", "ZZ Plant"],
            "medium": ["Peace Lily", "Fiddle Leaf Fig"],
            "high": ["Gardenia"],
        },
        "low light": {
            "low": ["Pothos", "Spider Plant"],
            "medium": ["Philodendron", "Dracaena"],
            "high": ["Orchid"],
        },
    }

    # Normalize input
    light_key = light.lower().strip()
    maintenance_key = maintenance.lower().strip()

    # Get recommendations
    recommendations = plant_recommendations.get(light_key, {}).get(maintenance_key, [])

    if recommendations:
        return (
            f"🌿 Recommended Plants for {light.title()} and "
            f"{maintenance.title()} Maintenance: {', '.join(recommendations)}"
        )
    else:
        return (
            "🌿 No specific recommendations available for the given criteria. "
            "Try different light or maintenance levels."
        )


# Create the function tool
plant_recommendation_tool = FunctionTool(
    name="get_plant_recommendations",
    description="Recommend plants to buy based on light and maintenance criteria",
    params_json_schema={
        "type": "object",
        "properties": {
            "light": {
                "type": "string",
                "description": (
                    "Light conditions (e.g., 'full sun', 'partial shade', "
                    "'low light')"
                ),
            },
            "maintenance": {
                "type": "string",
                "description": "Maintenance level (e.g., 'low', 'medium', 'high')",
            },
        },
        "required": ["light", "maintenance"],
    },
    on_invoke_tool=lambda context, input_json: _invoke_plant_recommendations(
        input_json
    ),
)


async def _invoke_plant_recommendations(input_json: str) -> str:
    """Invoke the plant recommendation tool."""
    import json

    try:
        logging.debug(f"Invoking get_plant_recommendations with input: {input_json}")
        params = json.loads(input_json)
        light = params.get("light", "")
        maintenance = params.get("maintenance", "")
        if not light or not maintenance:
            return (
                "Please provide both light and maintenance criteria to get "
                "recommendations."
            )
        return get_plant_recommendations(light, maintenance)
    except Exception as e:
        logging.error(f"Error in get_plant_recommendations: {str(e)}")
        return f"Error getting plant recommendations: {str(e)}"
