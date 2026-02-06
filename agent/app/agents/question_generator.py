"""Question Generator - fetches products and generates optimal question flow."""

import json
import logging
import os

import httpx
from agents import Agent, Runner

from config import settings

logging.basicConfig(level=logging.DEBUG)

# API URL for fetching products directly
FLASK_API_URL = os.environ.get("FLASK_API_URL", "http://localhost:8081")

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


async def fetch_products_from_api() -> list[dict]:
    """Fetch products directly from the Flask API (bypassing LLM).
    
    This ensures we get the actual product data without any hallucination.
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{FLASK_API_URL}/products",
                headers={
                    "Content-Type": "application/json",
                    "se": "agent-direct",
                }
            )
            response.raise_for_status()
            raw_products = response.json()
            
            # Transform to simplified structure matching MCP resource format
            products = []
            for p in raw_products:
                products.append({
                    "id": p.get("id"),
                    "name": p.get("title"),
                    "price": p.get("price"),
                    "description": p.get("description"),
                    "reviews": [r.get("description", "") for r in p.get("reviews", []) if r.get("description")]
                })
            
            logging.debug(f"Fetched {len(products)} products from API: {[p['name'] for p in products]}")
            return products
            
    except Exception as e:
        logging.error(f"Failed to fetch products from API: {e}")
        return []


# Create the question generator agent (no MCP tool - we pass products directly)
question_generator_agent = Agent(
    name=QUESTION_GENERATOR_NAME,
    instructions=QUESTION_GENERATOR_INSTRUCTIONS,
    model=settings.agent_model,
    tools=[],
)


async def generate_questions() -> tuple[list[dict], list[dict]]:
    """Generate optimal questions based on actual product data.
    
    Returns:
        Tuple of (questions_list, products_list)
        - questions_list: List of question dicts with question, answer_interpretation, next_question
        - products_list: List of product dicts from the API
    """
    logging.debug("Generating questions based on product analysis...")
    
    # Step 1: Fetch actual products from API (deterministic, no hallucination)
    products = await fetch_products_from_api()
    
    if not products:
        logging.error("No products fetched - returning fallback questions")
        return _get_fallback_questions(), []
    
    # Step 2: Format products for LLM context
    products_text = "ACTUAL PRODUCTS IN THE STORE:\n"
    for p in products:
        reviews_summary = f" ({len(p.get('reviews', []))} reviews)" if p.get('reviews') else ""
        products_text += f"- {p['name']} (id: {p['id']}, ${p['price']}): {p['description']}{reviews_summary}\n"
    
    # Step 3: Ask LLM to generate questions based on actual products
    prompt = f"""{products_text}

Based on ONLY these products, generate 2-3 questions to help a customer choose.
Remember: ONLY reference the product names listed above. Output ONLY a JSON array."""
    
    result = Runner.run_streamed(question_generator_agent, prompt)

    # Consume the stream
    async for _ in result.stream_events():
        pass

    output = str(result.final_output)
    
    logging.debug(f"Question generator output: {output}")
    
    # Step 4: Parse questions from LLM output
    questions = _parse_questions_json(output, products)
    
    logging.debug(f"Generated {len(questions)} questions for {len(products)} products")
    return questions, products


def _parse_questions_json(output: str, products: list[dict]) -> list[dict]:
    """Parse questions JSON from LLM output with validation."""
    try:
        start_idx = output.find('[')
        end_idx = output.rfind(']') + 1
        if start_idx != -1 and end_idx > start_idx:
            json_str = output[start_idx:end_idx]
            questions = json.loads(json_str)
            
            # Validate that questions reference actual products
            product_names = {p['name'].lower() for p in products}
            for q in questions:
                interpretation = q.get('answer_interpretation', '').lower()
                # Check if at least one product name is mentioned
                if not any(name in interpretation for name in product_names):
                    logging.warning(f"Question may not reference actual products: {q}")
            
            return questions
    except json.JSONDecodeError as e:
        logging.error(f"Failed to parse questions JSON: {e}")
        logging.error(f"Raw output was: {output}")
    
    return _get_fallback_questions()


def _get_fallback_questions() -> list[dict]:
    """Return safe fallback questions that don't assume specific products."""
    return [
        {
            "question": "What's your budget: under $50, $50-200, or over $200?",
            "answer_interpretation": "Budget determines which products to show - lower budget items vs premium options.",
            "next_question": 1
        },
        {
            "question": "Is this for yourself or as a gift?",
            "answer_interpretation": "Gifts may prefer unique/fun items; personal use focuses on functionality.",
            "next_question": None
        }
    ]
