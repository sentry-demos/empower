"""Shopping Agent for Empower Plant store conversational commerce."""

import json
import logging
import os

from agents import Agent, HostedMCPTool, Runner, SQLiteSession

from config import settings

from ..api.models import ResponseItem
from ..question_store import question_store, SessionState, QuestionItem
from .question_generator import generate_questions

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Database path for session storage
DB_PATH = "agent_sessions.db"

# Shopping agent configuration
SHOPPING_AGENT_NAME = "shopping_agent"
SHOPPING_AGENT_INSTRUCTIONS = """
You are a friendly shopping assistant for Empower Plant store.

CRITICAL: You can ONLY recommend products from the AVAILABLE PRODUCTS list provided below.
NEVER invent, make up, or reference products not in that list. If a product isn't listed, it doesn't exist.

You will be given:
1. AVAILABLE PRODUCTS - the ONLY products you can recommend (with exact names, IDs, prices)
2. Previous customer answers (if any)
3. Current question to ask (if still narrowing down)
4. Customer's message

YOUR JOB:
- First interaction: Greet warmly and ask the provided question
- After an answer: Check if you can narrow down to a SINGLE best product
  - If YES: Recommend it immediately (don't ask more questions)
  - If NO: Ask the next question to narrow down further

RECOMMEND AS SOON AS POSSIBLE - once you have enough info to pick ONE product, do it!

WHEN RECOMMENDING - use EXACT format on its own line:
PRODUCT_CARD:{"id":X,"name":"Exact Product Name From List","price":XX,"description":"Brief description"}

The id, name, and price MUST EXACTLY match the AVAILABLE PRODUCTS list. Copy the name exactly.
Add a brief, friendly intro before the product card (e.g., "Based on what you've told me, I'd recommend:").
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

STYLE: Concise, friendly, ONE question at a time. Recommend early when possible.
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
    
    # Format products for context
    products_text = json.dumps(products, indent=2) if products else "No products loaded"
    
    # Get current question info
    current_q = None
    if state.questions and state.current_question_index < len(state.questions):
        current_q = state.questions[state.current_question_index]
    
    # Build conversation summary
    answers_summary = ""
    if state.user_answers:
        answers_summary = "Previous answers from this customer:\n"
        for i, ans in enumerate(state.user_answers):
            if i < len(state.questions):
                answers_summary += f"- Q: {state.questions[i].question}\n  A: {ans}\n"
    
    # Build prompt
    prompt_parts = [
        f"AVAILABLE PRODUCTS:\n{products_text}\n",
    ]
    
    if answers_summary:
        prompt_parts.append(answers_summary)
    
    if is_first_interaction:
        prompt_parts.append("\nThis is the FIRST interaction. Greet the customer warmly and ask the first question.")
    
    # Check if we have enough info to recommend
    has_answers = len(state.user_answers) >= 1
    
    if current_q and not has_answers:
        # First question - must ask it
        prompt_parts.append(f"\nCURRENT QUESTION TO ASK:\n{current_q.question}")
        prompt_parts.append(f"\nHOW ANSWERS NARROW CHOICES:\n{current_q.answer_interpretation}")
    elif current_q and has_answers:
        # Have some answers - prioritize recommendation if possible
        prompt_parts.append(f"\nNEXT QUESTION (only if needed):\n{current_q.question}")
        prompt_parts.append(f"\nHOW IT NARROWS CHOICES:\n{current_q.answer_interpretation}")
        prompt_parts.append("\n** IMPORTANT: If the customer's answers so far point clearly to ONE product, recommend it NOW. Only ask the next question if you genuinely can't decide between products. **")
    else:
        # No more questions - must recommend
        prompt_parts.append("\nNo more questions - make a product recommendation based on the customer's answers!")
    
    prompt_parts.append(f"\nUSER'S MESSAGE: {user_message}")
    
    return "\n".join(prompt_parts)


async def process_chat_message(session_id: str, message: str) -> list[ResponseItem]:
    """Process a chat message with session context."""
    logging.debug(f"Processing chat message for session {session_id}: {message[:50]}...")
    
    # Get or create session state
    state = question_store.get_session(session_id)
    is_first_interaction = state is None
    
    if is_first_interaction:
        # First interaction - generate questions and fetch products
        logging.debug("First interaction - generating questions...")
        questions_list, products = await generate_questions()
        
        state = SessionState(
            session_id=session_id,
            questions=[QuestionItem(
                question=q.get("question", ""),
                answer_interpretation=q.get("answer_interpretation", ""),
            ) for q in questions_list],
            products=products,  # Cache products
            current_question_index=0,
            remaining_product_ids=[p.get("id") for p in products if p.get("id")]
        )
        
        question_store.save_session(state)
        logging.debug(f"Created session with {len(state.questions)} questions and {len(products)} products")
    else:
        # Returning user - record their answer and advance
        logging.debug(f"Returning user. Current question index: {state.current_question_index}, answers so far: {len(state.user_answers)}")
        
        if state.current_question_index < len(state.questions):
            state.user_answers.append(message)
            state.current_question_index += 1
        
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
    
    return items
