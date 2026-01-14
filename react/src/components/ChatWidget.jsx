import React, { useState, useEffect, useRef, useCallback } from 'react';
import * as Sentry from '@sentry/react';
import './chatWidget.css';
import agentIcon from '../assets/empower-agent.png';

const CHAT_SESSION_INACTIVITY_TIMEOUT_MS = 15000;

let messageIdCounter = 0;
const generateMessageId = () => `msg-${Date.now()}-${++messageIdCounter}`;

const ChatWidget = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [userInput, setUserInput] = useState('');
  const [conversationState, setConversationState] = useState('initial');
  const [userResponses, setUserResponses] = useState({
    light: '',
    maintenance: ''
  });
  const messagesEndRef = useRef(null);
  const chatSpanRef = useRef(null);
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
    
    // Record how the session ended
    if (chatSpanRef.current) {
      const isTimeout = reason === 'inactivity_timeout';
      Sentry.withActiveSpan(chatSpanRef.current, () => {
        Sentry.startSpan(
          { 
            op: isTimeout ? 'mark' : 'ui.action',
            name: `Session End: ${reason}`
          },
          () => {
            // Span ends immediately
          }
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

  const addBotMessage = useCallback((text, updateFn) => {
    if (chatSpanRef.current) {
      Sentry.withActiveSpan(chatSpanRef.current, () => {
        Sentry.startSpan(
          { op: 'ui.render', name: 'Render Bot Message' },
          () => {
            if (updateFn) {
              updateFn();
            } else {
              setMessages(prev => [
                ...prev.filter(msg => msg.type !== 'typing'),
                {
                  type: 'bot',
                  text,
                  id: generateMessageId()
                }
              ]);
            }
          }
        );
      });
    } else {
      if (updateFn) {
        updateFn();
      } else {
        setMessages(prev => [
          ...prev.filter(msg => msg.type !== 'typing'),
          {
            type: 'bot',
            text,
            id: generateMessageId()
          }
        ]);
      }
    }
  }, []);

  useEffect(() => {
    if (isOpen && conversationState === 'initial') {
      // Show typing indicator
      setMessages([{ type: 'typing', id: generateMessageId() }]);
      
      setTimeout(() => {
        // Remove typing indicator and show welcome message
        addBotMessage("Hi, I can help you pick the right plants for your home", () => {
          setMessages([
            {
              type: 'bot',
              text: "Hi, I can help you pick the right plants for your home",
              id: generateMessageId()
            }
          ]);
        });
        
        // Show second message after a brief pause
        setTimeout(() => {
          // Show typing indicator
          setMessages(prev => [...prev, { type: 'typing', id: generateMessageId() }]);
          
          setTimeout(() => {
            addBotMessage('How much light does your room get?');
            setConversationState('awaiting_light');
          }, 1000);
        }, 500);
      }, 1000);
    }
  }, [isOpen, conversationState, addBotMessage]);

  const handleInputFocus = () => {
    if (chatSpanRef.current) {
      Sentry.withActiveSpan(chatSpanRef.current, () => {
        Sentry.startSpan(
          { op: 'ui.action', name: 'Focus Chat Input' },
          () => {
            // Span ends immediately after focus
          }
        );
      });
    }
  };

  const handleInputChange = (e) => {
    setUserInput(e.target.value);
    
    // Start typing span if not already started
    if (chatSpanRef.current && !typingSpanRef.current) {
      Sentry.withActiveSpan(chatSpanRef.current, () => {
        typingSpanRef.current = Sentry.startInactiveSpan({
          op: 'ui.action',
          name: 'User Typing'
        });
      });
    }
    
    // Clear existing timeout
    if (typingTimeoutRef.current) {
      clearTimeout(typingTimeoutRef.current);
    }
    
    // Set new timeout to end typing span after 1 second of inactivity
    typingTimeoutRef.current = setTimeout(() => {
      if (typingSpanRef.current) {
        typingSpanRef.current.end();
        typingSpanRef.current = null;
      }
    }, 1000);
  };

  const handleSendClick = () => {
    // End any active typing span
    if (typingSpanRef.current) {
      typingSpanRef.current.end();
      typingSpanRef.current = null;
    }
    if (typingTimeoutRef.current) {
      clearTimeout(typingTimeoutRef.current);
      typingTimeoutRef.current = null;
    }
    
    // Create send button click span
    if (chatSpanRef.current) {
      Sentry.withActiveSpan(chatSpanRef.current, () => {
        Sentry.startSpan(
          { op: 'ui.action.click', name: 'Send Message' },
          () => {
            // Span ends immediately after click
          }
        );
      });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!userInput.trim()) return;
    
    // Track the send click
    handleSendClick();

    // Add user message to chat
    const userMessage = {
      type: 'user',
      text: userInput,
      id: generateMessageId()
    };
    setMessages(prev => [...prev, userMessage]);
    
    if (conversationState === 'awaiting_light') {
      // Store light response
      setUserResponses(prev => ({ ...prev, light: userInput }));
      setUserInput('');
      
      // Show typing indicator
      setMessages(prev => [...prev, { type: 'typing', id: generateMessageId() }]);
      
      // Ask next question
      setTimeout(() => {
        addBotMessage('Are you only looking for low-maintenance plants?');
        setConversationState('awaiting_maintenance');
      }, 1000);
    } else if (conversationState === 'awaiting_maintenance') {
      // Store maintenance response
      const maintenanceAnswer = userInput;
      setUserInput('');
      
      // Show typing indicator
      setMessages(prev => [...prev, { type: 'typing', id: generateMessageId() }]);
      
      // Make API call within the active span context
      try {
        let response, data;
        
        if (chatSpanRef.current) {
          await Sentry.withActiveSpan(chatSpanRef.current, async () => {
            response = await fetch('https://empower-agent.sentry.gg/api/v1/buy-plants', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({
                light: userResponses.light,
                maintenance: `Are you only looking for low-maintenance plants? Answer: ${maintenanceAnswer}`
              })
            });
            data = await response.json();
          });
        } else {
          response = await fetch('https://empower-agent.sentry.gg/api/v1/buy-plants', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              light: userResponses.light,
              maintenance: `Are you only looking for low-maintenance plants? Answer: ${maintenanceAnswer}`
            })
          });
          data = await response.json();
        }
        
        // Remove typing indicator and show response
        addBotMessage(data.response, () => {
          setMessages(prev => [
            ...prev.filter(msg => msg.type !== 'typing'),
            {
              type: 'bot',
              text: data.response,
              agentName: data.agent_name,
              id: generateMessageId()
            }
          ]);
        });
        setConversationState('completed');
        
        // Start inactivity timeout after final bot response is rendered
        startInactivityTimeout();
      } catch (error) {
        // Handle error
        addBotMessage('Sorry, I encountered an error. Please try again later.');
        setConversationState('error');
        
        // Start inactivity timeout after error response is rendered
        startInactivityTimeout();
      }
    }
  };

  const openChat = () => {
    // Opening the chat - start a new trace
    Sentry.startNewTrace(() => {
      const span = Sentry.startInactiveSpan({ 
        op: 'ui.interaction.chat',
        name: 'AI Agent Chat Session',
        forceTransaction: true
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
  
  // Clean up spans on unmount or navigation
  useEffect(() => {
    return () => {
      endChatSession('navigation');
    };
  }, [endChatSession]);

  return (
    <div className="chat-widget-container">
      {isOpen && (
        <div className="chat-window">
          <div className="chat-header">
            <div className="chat-header-content">
              <img src={agentIcon} alt="AI Agent" className="chat-header-icon" />
              <span className="chat-header-title">AI Agent</span>
            </div>
            <button className="chat-close-button" onClick={handleCloseButtonClick}>×</button>
          </div>
          
          <div className="chat-messages">
            {messages.map((message) => {
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
            })}
            <div ref={messagesEndRef} />
          </div>
          
          {(conversationState === 'awaiting_light' || conversationState === 'awaiting_maintenance') && (
            <form className="chat-input-form" onSubmit={handleSubmit}>
              <input
                id="chat-message-input"
                type="text"
                value={userInput}
                onChange={handleInputChange}
                onFocus={handleInputFocus}
                placeholder="Type your answer..."
                className="chat-input"
                autoFocus
              />
              <button id="chat-send-button" type="submit" className="chat-send-button">Send</button>
            </form>
          )}
        </div>
      )}
      
      <button id="chat-widget-button" className="chat-toggle-button" onClick={handleAgentButtonClick}>
        <img src={agentIcon} alt="Chat with AI Agent" />
      </button>
    </div>
  );
};

export default ChatWidget;
