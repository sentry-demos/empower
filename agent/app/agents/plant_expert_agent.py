"""Plant Expert Agent to handle plant recommendation requests."""

import logging
import os

from agents import Agent, Runner

from config import settings

from ..tools.plant_base_info import plant_base_info_tool
from ..tools.plant_recommendations import plant_recommendation_tool

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Plant expert agent configuration
PLANT_EXPERT_AGENT_NAME = "plant_expert_agent"
PLANT_EXPERT_AGENT_INSTRUCTIONS = """You are the Plant Expert Agent.
Your role is to provide plant recommendations based on user criteria.

1. Use the get_plant_basic_info tool to gather basic information about plants.
2. Use the get_plant_recommendations tool to recommend plants based
on light and maintenance criteria.

Provide clear and concise recommendations. Always ensure the recommendations
match the user's criteria.
Once you have provided the recommendations, handoff the task
back to the Manager Agent."""

# Create the plant expert agent
plant_expert_agent = Agent(
    name=PLANT_EXPERT_AGENT_NAME,
    instructions=PLANT_EXPERT_AGENT_INSTRUCTIONS,
    model=settings.light_model,  # Use a cheaper model for simple recommendations
    tools=[plant_base_info_tool, plant_recommendation_tool],
)


async def get_recommendations(light: str, maintenance: str) -> str:
    """Get plant recommendations based on user criteria.

    Args:
        light: Light conditions
        maintenance: Maintenance level

    Returns:
        Recommended plants
    """

    logging.debug(
        f"PlantExpertAgent invoked with light: {light}, maintenance: {maintenance}"
    )
    # Create a message with user preferences
    msg = f"Reccomend plants for {light} light and {maintenance} maintenance."

    # Run the agent with streaming
    result = Runner.run_streamed(plant_expert_agent, msg)

    # Consume the stream
    async for _ in result.stream_events():
        pass

    logging.debug(f"PlantExpertAgent provided recommendations: {result.final_output}")
    return str(result.final_output)
