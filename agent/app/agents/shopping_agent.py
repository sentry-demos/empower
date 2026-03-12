"""Shopping Agent for Empower Plant store conversational commerce."""

import json
import logging
import os

from agents import Agent, HostedMCPTool, Runner, SQLiteSession

from config import settings

from ..api.models import ResponseItem
from ..question_store import question_store, SessionState, QuestionItem
from .question_generator import fetch_products_via_mcp, HARDCODED_QUESTIONS

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Database path for session storage
DB_PATH = "agent_sessions.db"

# Shopping agent configuration
SHOPPING_AGENT_NAME = "shopping_agent"
SHOPPING_AGENT_INSTRUCTIONS = """
You are a friendly shopping assistant for Empower Plant store.

CRITICAL: You can ONLY recommend products from the AVAILABLE PRODUCTS list provided in this conversation.
NEVER invent, make up, or reference products not in that list. If a product isn't listed, it doesn't exist.

You will be given:
1. AVAILABLE PRODUCTS with descriptions and customer reviews (provided once, refer to them throughout)
2. Previous customer Q&A (if any)
3. Instructions on what to do next (recommend or ask a specific question)
4. Customer's message

YOUR JOB:
- When told to ask a question, ask it naturally and conversationally
- When told to decide between recommending or asking the next question: carefully analyze the products,
  their descriptions, and customer reviews against ALL the customer's answers so far.
  Only recommend if the answers unambiguously narrow it down to a single product.
  When in doubt, ask the next question — more information leads to better recommendations.

WHEN RECOMMENDING - use EXACT format on its own line:
PRODUCT_CARD:{"id":X,"name":"Exact Product Name From List","price":XX,"description":"Brief description"}

The id, name, and price MUST EXACTLY match the AVAILABLE PRODUCTS list. Copy the name exactly.
Add a brief, friendly intro before the product card explaining why this product fits their needs.
Do NOT ask if they want to add to cart - they will click the button themselves.

CHECKOUT (when user says they want to check out):
Use the MCP 'checkout' tool with:
- email: "demo@empower-plant.com"
- name: "Demo Customer"  
- address: "123 Plant Street, Garden City, CA 94000"

Report as:
CHECKOUT_RESULT:{"success":true,"message":"Order confirmed!"}
or
CHECKOUT_RESULT:{"success":false,"error":"Error message"}

ERROR HANDLING: If checkout or any operation fails, display the error and stop. Do NOT offer to retry or troubleshoot.

STYLE: Concise, friendly, ONE question at a time.
"""

# Create the shopping agent
shopping_agent = Agent(
    name=SHOPPING_AGENT_NAME,
    instructions=SHOPPING_AGENT_INSTRUCTIONS,
    model=settings.agent_model,
    tools=[],
)

# Configure MCP tool for checkout
mcp_tool = HostedMCPTool(
    tool_config={
        "type": "mcp",
        "server_label": "empower-mcp",
        "server_url": os.environ["MCP_URL"] + "/mcp",
        "require_approval": "never",
    }
)

shopping_agent.tools.append(mcp_tool)


def parse_agent_output(output: str) -> list[ResponseItem]:
    """Parse agent output for structured markers."""
    items = []
    
    if not output:
        return items
    
    lines = output.split('\n')
    message_buffer = []
    
    for line in lines:
        stripped = line.strip()
        
        if stripped.startswith('PRODUCT_CARD:'):
            if message_buffer:
                text = '\n'.join(message_buffer).strip()
                if text:
                    items.append(ResponseItem(type="message", content={"text": text}))
                message_buffer = []
            
            try:
                json_str = stripped[13:]
                data = json.loads(json_str)
                items.append(ResponseItem(type="product_card", content=data))
            except json.JSONDecodeError as e:
                logging.warning(f"Failed to parse PRODUCT_CARD JSON: {e}")
                message_buffer.append(line)
                
        elif stripped.startswith('CHECKOUT_RESULT:'):
            if message_buffer:
                text = '\n'.join(message_buffer).strip()
                if text:
                    items.append(ResponseItem(type="message", content={"text": text}))
                message_buffer = []
            
            try:
                json_str = stripped[16:]
                data = json.loads(json_str)
                items.append(ResponseItem(type="checkout_result", content=data))
            except json.JSONDecodeError as e:
                logging.warning(f"Failed to parse CHECKOUT_RESULT JSON: {e}")
                message_buffer.append(line)
        else:
            if stripped:
                message_buffer.append(line)
    
    if message_buffer:
        text = '\n'.join(message_buffer).strip()
        if text:
            items.append(ResponseItem(type="message", content={"text": text}))
    
    return items


def build_context_prompt(state: SessionState, products: list[dict], user_message: str, is_first_interaction: bool = False) -> str:
    """Build a context-aware prompt for the agent."""
    
    prompt_parts = []
    
    num_answers = len(state.user_answers)
    
    if num_answers == 1:
        products_text = json.dumps(products, indent=2)
        prompt_parts.append(
            f"AVAILABLE PRODUCTS (analyze descriptions AND customer reviews):\n{products_text}\n"
        )
    elif num_answers > 1:
        prompt_parts.append(
            "Refer to the AVAILABLE PRODUCTS already listed earlier in this conversation.\n"
        )
    
    if state.user_answers:
        answers_summary = "Customer's answers so far:\n"
        for i, ans in enumerate(state.user_answers):
            if i < len(HARDCODED_QUESTIONS):
                answers_summary += f"- Q: {HARDCODED_QUESTIONS[i]}\n  A: {ans}\n"
        prompt_parts.append(answers_summary)
    
    if is_first_interaction:
        prompt_parts.append(
            f'Greet the customer warmly and ask: "{HARDCODED_QUESTIONS[0]}"'
        )
    elif state.current_question_index < len(HARDCODED_QUESTIONS):
        next_q = HARDCODED_QUESTIONS[state.current_question_index]
        prompt_parts.append(
            "Based on the customer's answers, analyze the products and their reviews."
            " If the answers unambiguously point to ONE best product, recommend it using the PRODUCT_CARD format."
            f' If multiple products could still be a good fit, ask this next question: "{next_q}"'
        )
    else:
        prompt_parts.append(
            "All questions have been asked. Based on ALL the customer's answers,"
            " analyze the products and their reviews and recommend the ONE best product."
        )
    
    prompt_parts.append(f"\nUSER'S MESSAGE: {user_message}")
    
    return "\n".join(prompt_parts)


async def process_chat_message(session_id: str, message: str) -> list[ResponseItem]:
    """Process a chat message with session context."""
    logging.debug(f"Processing chat message for session {session_id}: {message[:50]}...")
    
    # Get or create session state
    state = question_store.get_session(session_id)
    is_first_interaction = state is None
    
    if is_first_interaction:
        logging.debug("First interaction - creating session (products fetched lazily)...")
        
        state = SessionState(
            session_id=session_id,
            questions=[QuestionItem(question=q, answer_interpretation="") for q in HARDCODED_QUESTIONS],
            current_question_index=0,
        )
        
        question_store.save_session(state)
        logging.debug(f"Created session with {len(HARDCODED_QUESTIONS)} questions")
    else:
        logging.debug(f"Returning user. Current question index: {state.current_question_index}, answers so far: {len(state.user_answers)}")
        
        if state.recommended_product_id is None and state.current_question_index < len(HARDCODED_QUESTIONS):
            state.user_answers.append(message)
            state.current_question_index += 1
        
        # Fetch products on first answer if not yet cached
        if not state.products and state.user_answers:
            logging.debug("Fetching products for first time...")
            state.products = await fetch_products_via_mcp()
            state.remaining_product_ids = [p.get("id") for p in state.products if p.get("id")]
        
        question_store.save_session(state)
    
    # Use cached products from state
    products = state.products
    
    # Build context prompt
    context_prompt = build_context_prompt(state, products, message, is_first_interaction)
    
    # Create SQLite session for conversation history
    session = SQLiteSession(session_id, DB_PATH)
    
    # Run the agent
    result = await Runner.run(shopping_agent, context_prompt, session=session)
    
    logging.debug(f"Agent output: {result.final_output}")
    
    # Parse and return response
    items = parse_agent_output(str(result.final_output))
    
    # Track if a recommendation was made so we stop recording answers
    for item in items:
        if item.type == "product_card":
            state.recommended_product_id = item.content.get("id")
            question_store.save_session(state)
            break
    
    return items
