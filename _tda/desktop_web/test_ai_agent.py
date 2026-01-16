import time
import sentry_sdk
from selenium.webdriver.common.by import By


# Time to wait after conversation completes before closing the chat
# This allows for proper Sentry trace capture
WAIT_BEFORE_CLOSE_SECONDS = 80


def test_ai_agent(desktop_web_1browser_driver, endpoints):
    """
    Test the AI Agent Chat widget on the React homepage.
    
    This test:
    1. Opens the chat widget
    2. Waits for the welcome messages
    3. Answers "full sun" to the light question
    4. Answers "yes" to the maintenance question
    5. Waits for the API response
    6. Waits 80 seconds for trace data capture
    7. Closes the chat by clicking X
    """
    
    endpoint = endpoints.react_endpoint
    
    url = endpoint  # use default backend as it doesn't matter for this test
    
    try:
        # Navigate to the homepage
        desktop_web_1browser_driver.get(url)
        
        # Wait for page to load
        time.sleep(3)
        
        # Click the AI Agent button to open chat
        chat_button = desktop_web_1browser_driver.find_element(By.ID, 'chat-widget-button')
        chat_button.click()
        
        # Wait for the chat to open and show initial messages
        # The bot will show typing indicator, then welcome message, then typing, then first question
        time.sleep(5)
        
        # Find the input field (indicates first question is ready)
        chat_input = desktop_web_1browser_driver.find_element(By.ID, 'chat-message-input')
        
        # Answer the first question: "How much light does your room get?"
        chat_input.send_keys("full sun")
        
        # Click Send
        send_button = desktop_web_1browser_driver.find_element(By.ID, 'chat-send-button')
        send_button.click()
        
        # Wait for the second question to appear
        time.sleep(3)
        
        # Find the input field again
        chat_input = desktop_web_1browser_driver.find_element(By.ID, 'chat-message-input')
        
        # Answer the second question: "Are you only looking for low-maintenance plants?"
        chat_input.send_keys("yes")
        
        # Click Send
        send_button = desktop_web_1browser_driver.find_element(By.ID, 'chat-send-button')
        send_button.click()
        
        # Wait for the API response to appear
        # The bot will show typing indicator while waiting for the API, then show the response
        time.sleep(10)
        
        # Wait the specified time before closing to allow trace data to be captured
        print(f"Waiting {WAIT_BEFORE_CLOSE_SECONDS} seconds before closing chat...")
        time.sleep(WAIT_BEFORE_CLOSE_SECONDS)
        
        # Close the chat by clicking the chat button again (chat close button may not be visible)
        chat_button.click()
        
        # Small delay to ensure the close action completes
        time.sleep(2)
        
    except Exception as err:
        sentry_sdk.capture_exception(err)
        raise
