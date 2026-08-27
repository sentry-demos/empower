"""Manager Agent to handle user inputs and initiate handoffs."""

import logging
import os

from agents import Agent, ModelSettings, Runner
from agents.mcp import MCPServerStreamableHttp

from config import settings

from ..tools.buy_plants import buy_plants_tool
from .plant_expert_agent import plant_expert_agent

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Manager agent configuration
MANAGER_AGENT_NAME = "manager_agent"
MANAGER_AGENT_INSTRUCTIONS = """
You are the Manager Agent.
Your role is to interact with users, collect their preferences,
and manage the plant buying process.

1. Collect user inputs for light conditions and maintenance level.
2. Automatically handoff the task to the Plant Expert Agent to get
plant recommendations.

Once the Plant Expert Agent has provided the recommendations it will
handoff the task back to you.
You then need to buy the plants that were recommended.

3. Use the buy_plants tool to buy the plants that were recommended.
4. You MUST use the empower-mcp get_products to get the products that
would fit well with the plants that were ordered.

Keep interactions clear and concise. Do not ask for confirmation;
proceed directly with the workflow.
Report back to the user with the ordered plants and the products that
 would fit well with the plants."""

# OpenRouter's Responses API is stateless and rejects store=true.
_model_settings = ModelSettings(store=False)

# Create the manager agent
manager_agent = Agent(
    name=MANAGER_AGENT_NAME,
    instructions=MANAGER_AGENT_INSTRUCTIONS,
    model=settings.agent_model,  # Use a more expansive model for managing tasks
    model_settings=_model_settings,
    tools=[buy_plants_tool],
)

# Set up handoffs
manager_agent.handoffs = [
    plant_expert_agent
]  # Manager agent can handoff to plant expert agent
plant_expert_agent.handoffs = [
    manager_agent
]  # Plant expert agent can handoff back to manager agent


async def process_user_request(light: str, maintenance: str) -> str:
    """Process user request to buy plants based on criteria.

    Args:
        light: Light conditions
        maintenance: Maintenance level

    Returns:
        Confirmation of plant purchase
    """

    logging.debug(
        f"manager_agent invoked with light: {light}, maintenance: {maintenance}"
    )
    # Create a message with user preferences
    message = f"I want to buy plants for {light} light and {maintenance} maintenance."

    # Hosted MCP tools are OpenAI-only. Talk to empower-mcp from the app instead
    # so OpenRouter can still use the remote tools.
    async with MCPServerStreamableHttp(
        name="empower-mcp",
        params={"url": os.environ["MCP_URL"]},
        cache_tools_list=True,
    ) as mcp_server:
        manager_agent.mcp_servers = [mcp_server]
        try:
            result = await Runner.run(manager_agent, message)
        finally:
            manager_agent.mcp_servers = []

    logging.debug(f"manager_agent completed purchase: {result.final_output}")
    print(result)
    return str(result.final_output)
