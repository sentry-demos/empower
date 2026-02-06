import React, { useState, useEffect, useRef, useCallback } from 'react';
import * as Sentry from '@sentry/react';
import './chatWidget.css';
import agentIcon from '../assets/empower-agent.png';

const CHAT_SESSION_INACTIVITY_TIMEOUT_MS = 60000; // Increased for longer conversations
const AGENT_URL = process.env.REACT_APP_BACKEND_URL_AGENT;

let messageIdCounter = 0;
const generateMessageId = () => `msg-${Date.now()}-${++messageIdCounter}`;
const generateConversationId = () => `conv-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;

// Generate a UUID for session management
const generateSessionId = () => {
  if (typeof crypto !== 'undefined' && crypto.randomUUID) {
    return crypto.randomUUID();
  }
  // Fallback for older browsers
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
    const r = Math.random() * 16 | 0;
    const v = c === 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
};

const ChatWidget = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [userInput, setUserInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId] = useState(() => generateSessionId());
  const [hasStartedConversation, setHasStartedConversation] = useState(false);
  
  const messagesEndRef = useRef(null);
  const chatSpanRef = useRef(null);
  const conversationIdRef = useRef(null);
  const typingSpanRef = useRef(null);
  const typingTimeoutRef = useRef(null);
  const inactivityTimeoutRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const endChatSession = useCallback((reason = 'unknown') => {
    if (typingTimeoutRef.current) {
      clearTimeout(typingTimeoutRef.current);
      typingTimeoutRef.current = null;
    }
    if (typingSpanRef.current) {
      typingSpanRef.current.end();
      typingSpanRef.current = null;
    }
    if (inactivityTimeoutRef.current) {
      clearTimeout(inactivityTimeoutRef.current);
      inactivityTimeoutRef.current = null;
    }
    
    if (chatSpanRef.current) {
      const isTimeout = reason === 'inactivity_timeout';
      Sentry.withActiveSpan(chatSpanRef.current, () => {
        Sentry.startSpan(
          { 
            op: isTimeout ? 'mark' : 'ui.action',
            name: `Session End: ${reason}`
          },
          () => {}
        );
      });
      
      chatSpanRef.current.end();
      chatSpanRef.current = null;
    }
  }, []);

  const startInactivityTimeout = useCallback(() => {
    if (inactivityTimeoutRef.current) {
      clearTimeout(inactivityTimeoutRef.current);
    }
    
    if (chatSpanRef.current) {
      inactivityTimeoutRef.current = setTimeout(() => {
        endChatSession('inactivity_timeout');
      }, CHAT_SESSION_INACTIVITY_TIMEOUT_MS);
    }
  }, [endChatSession]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Send message to the agent API
  const sendMessage = useCallback(async (messageText) => {
    setIsLoading(true);
    
    // Show typing indicator
    setMessages(prev => [...prev, { type: 'typing', id: generateMessageId() }]);
    
    try {
      let response, data;
      
      const makeRequest = async () => {
        const res = await fetch(`${AGENT_URL}/api/v1/chat`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            session_id: sessionId,
            message: messageText
          })
        });
        return res;
      };
      
      if (chatSpanRef.current) {
        await Sentry.withActiveSpan(chatSpanRef.current, async () => {
          response = await makeRequest();
          data = await response.json();
        });
      } else {
        response = await makeRequest();
        data = await response.json();
      }
      
      if (!response.ok) {
        throw new Error(data.detail || 'Failed to get response');
      }
      
      // Process response items and add to messages
      setMessages(prev => {
        const withoutTyping = prev.filter(msg => msg.type !== 'typing');
        const newMessages = [];
        
        for (const item of data.items) {
          if (item.type === 'message') {
            newMessages.push({
              type: 'bot',
              text: item.content.text,
              id: generateMessageId()
            });
          } else if (item.type === 'product_card') {
            newMessages.push({
              type: 'product_card',
              content: item.content,
              id: generateMessageId()
            });
          } else if (item.type === 'checkout_result') {
            newMessages.push({
              type: 'checkout_result',
              content: item.content,
              id: generateMessageId()
            });
          }
        }
        
        return [...withoutTyping, ...newMessages];
      });
      
      startInactivityTimeout();
      
    } catch (error) {
      console.error('Chat error:', error);
      Sentry.captureException(error);
      
      setMessages(prev => [
        ...prev.filter(msg => msg.type !== 'typing'),
        {
          type: 'bot',
          text: 'Sorry, I encountered an error. Please try again.',
          id: generateMessageId()
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  }, [sessionId, startInactivityTimeout]);

  // Start conversation when chat opens
  useEffect(() => {
    if (isOpen && !hasStartedConversation) {
      setHasStartedConversation(true);
      // Send initial message to start the conversation
      sendMessage('Hi, I\'m looking for a plant recommendation.');
    }
  }, [isOpen, hasStartedConversation, sendMessage]);

  const handleInputFocus = () => {
    if (chatSpanRef.current) {
      Sentry.withActiveSpan(chatSpanRef.current, () => {
        Sentry.startSpan(
          { op: 'ui.action', name: 'Focus Chat Input' },
          () => {}
        );
      });
    }
  };

  const handleInputChange = (e) => {
    setUserInput(e.target.value);
    
    if (chatSpanRef.current && !typingSpanRef.current) {
      Sentry.withActiveSpan(chatSpanRef.current, () => {
        typingSpanRef.current = Sentry.startInactiveSpan({
          op: 'ui.action',
          name: 'User Typing'
        });
      });
    }
    
    if (typingTimeoutRef.current) {
      clearTimeout(typingTimeoutRef.current);
    }
    
    typingTimeoutRef.current = setTimeout(() => {
      if (typingSpanRef.current) {
        typingSpanRef.current.end();
        typingSpanRef.current = null;
      }
    }, 1000);
  };

  const handleSendClick = () => {
    if (typingSpanRef.current) {
      typingSpanRef.current.end();
      typingSpanRef.current = null;
    }
    if (typingTimeoutRef.current) {
      clearTimeout(typingTimeoutRef.current);
      typingTimeoutRef.current = null;
    }
    
    if (chatSpanRef.current) {
      Sentry.withActiveSpan(chatSpanRef.current, () => {
        Sentry.startSpan(
          { op: 'ui.action.click', name: 'Send Message' },
          () => {}
        );
      });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!userInput.trim() || isLoading) return;
    
    handleSendClick();

    const messageText = userInput;
    setUserInput('');
    
    // Add user message to chat
    setMessages(prev => [...prev, {
      type: 'user',
      text: messageText,
      id: generateMessageId()
    }]);
    
    // Send to agent
    await sendMessage(messageText);
  };

  const handleAddToCart = async (product) => {
    // Add user action message
    setMessages(prev => [...prev, {
      type: 'user',
      text: `Add "${product.name}" to cart`,
      id: generateMessageId()
    }]);
    
    // Send add to cart message to agent
    await sendMessage(`I'd like to add "${product.name}" (ID: ${product.id}) to my cart and checkout.`);
  };

  const openChat = () => {
    Sentry.startNewTrace(() => {
      const span = Sentry.startInactiveSpan({
        op: 'ui.interaction.chat',
        name: 'AI Agent Chat Session',
        forceTransaction: true,
      });
      chatSpanRef.current = span;
    });
    setIsOpen(true);
  };

  const closeChat = (reason) => {
    endChatSession(reason);
    setIsOpen(false);
  };

  const handleAgentButtonClick = () => {
    if (!isOpen) {
      openChat();
    } else {
      closeChat('click_agent_button');
    }
  };

  const handleCloseButtonClick = () => {
    closeChat('click_close_button');
  };
  
  useEffect(() => {
    return () => {
      endChatSession('navigation');
    };
  }, [endChatSession]);

  // Render a single message based on its type
  const renderMessage = (message) => {
    if (message.type === 'typing') {
      return (
        <div key={message.id} className="message bot-message">
          <div className="typing-indicator">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
      );
    }
    
    if (message.type === 'product_card') {
      const product = message.content;
      return (
        <div key={message.id} className="message bot-message">
          <div className="chat-product-card">
            <h4 className="product-name">{product.name}</h4>
            <p className="product-price">${product.price?.toFixed(2)}</p>
            {product.description && (
              <p className="product-description">{product.description}</p>
            )}
            <button 
              className="add-to-cart-button"
              onClick={() => handleAddToCart(product)}
              disabled={isLoading}
            >
              Add to Cart
            </button>
          </div>
        </div>
      );
    }
    
    if (message.type === 'checkout_result') {
      const result = message.content;
      return (
        <div key={message.id} className="message bot-message">
          <div className={`checkout-result ${result.success ? 'success' : 'error'}`}>
            {result.success ? (
              <>
                <span className="checkout-icon">&#10003;</span>
                <span>{result.message || 'Order placed successfully!'}</span>
              </>
            ) : (
              <>
                <span className="checkout-icon">&#10007;</span>
                <span>{result.error || 'Checkout failed. Please try again.'}</span>
              </>
            )}
          </div>
        </div>
      );
    }
    
    // Regular text message (bot or user)
    return (
      <div
        key={message.id}
        className={`message ${message.type === 'bot' ? 'bot-message' : 'user-message'}`}
      >
        <div className="message-bubble">
          {(message.text || '').split('\n').map((line, index, array) => (
            <React.Fragment key={index}>
              {line}
              {index < array.length - 1 && <br />}
            </React.Fragment>
          ))}
        </div>
      </div>
    );
  };

  return (
    <div className="chat-widget-container">
      {isOpen && (
        <div className="chat-window">
          <div className="chat-header">
            <div className="chat-header-content">
              <img src={agentIcon} alt="AI Agent" className="chat-header-icon" />
              <span className="chat-header-title">AI Shopping Assistant</span>
            </div>
            <button className="chat-close-button" onClick={handleCloseButtonClick}>×</button>
          </div>
          
          <div className="chat-messages">
            {messages.map(renderMessage)}
            <div ref={messagesEndRef} />
          </div>
          
          <form className="chat-input-form" onSubmit={handleSubmit}>
            <input
              id="chat-message-input"
              type="text"
              value={userInput}
              onChange={handleInputChange}
              onFocus={handleInputFocus}
              placeholder="Type your message..."
              className="chat-input"
              disabled={isLoading}
              autoFocus
            />
            <button 
              id="chat-send-button" 
              type="submit" 
              className="chat-send-button"
              disabled={isLoading || !userInput.trim()}
            >
              Send
            </button>
          </form>
        </div>
      )}
      
      <button id="chat-widget-button" className="chat-toggle-button" onClick={handleAgentButtonClick}>
        <img src={agentIcon} alt="Chat with AI Agent" />
      </button>
    </div>
  );
};

export default ChatWidget;
