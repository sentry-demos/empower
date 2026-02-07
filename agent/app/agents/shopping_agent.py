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
3. Current question to ask
4. Customer's message

YOUR JOB:
- First interaction: Greet warmly and ask the provided question
- After an answer: Either ask the next question OR recommend a product from AVAILABLE PRODUCTS

WHEN RECOMMENDING - use EXACT format on its own line:
PRODUCT_CARD:{"id":X,"name":"Exact Product Name From List","price":XX,"description":"Brief description"}

The id, name, and price MUST EXACTLY match the AVAILABLE PRODUCTS list. Copy the name exactly.

AFTER RECOMMENDATION:
Wait for user to add to cart, then ask if they'd like to check out.

CHECKOUT (when user confirms):
Use the MCP 'checkout' tool with:
- email: "demo@empower-plant.com"
- name: "Demo Customer"  
- address: "123 Plant Street, Garden City, CA 94000"

Report as:
CHECKOUT_RESULT:{"success":true,"message":"Order confirmed!"}
or
CHECKOUT_RESULT:{"success":false,"error":"Error message"}

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
    
    if current_q:
        prompt_parts.append(f"\nCURRENT QUESTION TO ASK:\n{current_q.question}")
        prompt_parts.append(f"\nHOW ANSWERS NARROW CHOICES:\n{current_q.answer_interpretation}")
    else:
        # No more questions - should recommend
        prompt_parts.append("\nNo more questions needed - make a product recommendation based on the customer's answers!")
    
    # Check if we should recommend early
    if len(state.user_answers) >= 2 and current_q:
        prompt_parts.append("\nYou have gathered enough information - if you can make a good recommendation now, do it!")
    
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
                next_question=q.get("next_question")
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
            
            # Move to next question
            current_q = state.questions[state.current_question_index]
            if current_q.next_question is not None and current_q.next_question < len(state.questions):
                state.current_question_index = current_q.next_question
            else:
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


# Keep legacy function for backward compatibility
async def process_user_request(light: str, maintenance: str) -> str:
    """Legacy function for plant purchase workflow."""
    logging.debug(
        f"Legacy process_user_request invoked with light: {light}, maintenance: {maintenance}"
    )
    message = f"I want to buy plants for {light} light and {maintenance} maintenance."

    # Run the agent with streaming to get recommendations
    result = Runner.run_streamed(shopping_agent, message)

    # Consume the stream
    async for _ in result.stream_events():
        pass

    logging.debug(f"shopping_agent completed purchase: {result.final_output}")
    print(result)
    return str(result.final_output)
