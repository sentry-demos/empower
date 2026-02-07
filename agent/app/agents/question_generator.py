"""Question Generator - fetches products via MCP and generates optimal question flow."""

import json
import logging
import os

from agents import Agent, HostedMCPTool, Runner

from config import settings

logging.basicConfig(level=logging.DEBUG)

# MCP URL for product data
MCP_URL = os.environ["MCP_URL"] + "/mcp"

# Agent that fetches products from MCP
PRODUCT_FETCHER_NAME = "product_fetcher"
PRODUCT_FETCHER_INSTRUCTIONS = """
You are a product data fetcher. Your ONLY job is to:
1. Call the MCP "get-products" tool to fetch all available products
2. Output the product data as a JSON array, nothing else - do not add any explanation or commentary
"""

# Agent that generates questions based on products
QUESTION_GENERATOR_NAME = "question_generator"
QUESTION_GENERATOR_INSTRUCTIONS = """
You are a product analysis specialist. You will be given a list of ACTUAL products from the Empower Plant store.

YOUR TASK:
1. Analyze the products provided below
2. Identify KEY DIFFERENCES: price ranges, features, use cases
3. Generate 2-3 questions that efficiently narrow down the choice

CRITICAL RULES:
- ONLY reference products from the list provided - NEVER make up product names
- Every answer_interpretation MUST name actual products from the list
- Questions should help differentiate between the ACTUAL products

OUTPUT FORMAT - JSON ARRAY ONLY:
[
  {
    "question": "Question text referencing actual products",
    "answer_interpretation": "If X -> recommend [actual product names]. If Y -> recommend [other actual products].",
    "next_question": 1
  }
]

RULES:
1. Max 3 questions
2. next_question = index of next question (0-indexed), or null if last
3. Output ONLY the JSON array, nothing else
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

# Create the question generator agent (no tools - just analyzes provided data)
question_generator_agent = Agent(
    name=QUESTION_GENERATOR_NAME,
    instructions=QUESTION_GENERATOR_INSTRUCTIONS,
    model=settings.agent_model,
    tools=[],
)


class MCPProductFetchError(Exception):
    """Raised when fetching products from MCP fails."""
    pass


class QuestionGenerationError(Exception):
    """Raised when generating questions fails."""
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


async def generate_questions() -> tuple[list[dict], list[dict]]:
    """Generate optimal questions based on product data from MCP.
    
    Returns:
        Tuple of (questions_list, products_list)
        - questions_list: List of question dicts with question, answer_interpretation, next_question
        - products_list: List of product dicts from MCP
        
    Raises:
        MCPProductFetchError: If fetching products fails.
        QuestionGenerationError: If generating questions fails.
    """
    logging.debug("Generating questions based on product analysis...")
    
    # Step 1: Fetch products via MCP
    products = await fetch_products_via_mcp()
    
    # Step 2: Format products for question generator context
    products_text = "ACTUAL PRODUCTS IN THE STORE:\n"
    for p in products:
        name = p.get('name') or p.get('title', 'Unknown')
        price = p.get('price', 0)
        description = p.get('description', '')
        reviews = p.get('reviews', [])
        reviews_summary = f" ({len(reviews)} reviews)" if reviews else ""
        products_text += f"- {name} (id: {p.get('id')}, ${price}): {description}{reviews_summary}\n"
    
    # Step 3: Generate questions using the question generator agent
    prompt = f"""{products_text}

Based on ONLY these products, generate 2-3 questions to help a customer choose.
Remember: ONLY reference the product names listed above. Output ONLY a JSON array."""
    
    result = await Runner.run(question_generator_agent, prompt)
    output = str(result.final_output)
    
    logging.debug(f"Question generator output: {output}")
    
    # Step 4: Parse questions from LLM output
    questions = _parse_questions_json(output, products)
    
    logging.debug(f"Generated {len(questions)} questions for {len(products)} products")
    return questions, products


def _parse_questions_json(output: str, products: list[dict]) -> list[dict]:
    """Parse questions JSON from LLM output with validation.
    
    Raises:
        QuestionGenerationError: If parsing fails or output is invalid.
    """
    start_idx = output.find('[')
    end_idx = output.rfind(']') + 1
    if start_idx == -1 or end_idx <= start_idx:
        raise QuestionGenerationError(f"No JSON array found in question generator output: {output}")
    
    json_str = output[start_idx:end_idx]
    try:
        questions = json.loads(json_str)
    except json.JSONDecodeError as e:
        raise QuestionGenerationError(f"Invalid JSON from question generator: {e}. Raw: {output}")
    
    if not questions:
        raise QuestionGenerationError("Question generator returned empty list")
    
    # Validate that questions reference actual products
    product_names = {(p.get('name') or p.get('title', '')).lower() for p in products}
    for q in questions:
        interpretation = q.get('answer_interpretation', '').lower()
        # Check if at least one product name is mentioned
        if not any(name in interpretation for name in product_names if name):
            logging.warning(f"Question may not reference actual products: {q}")
    
    return questions
