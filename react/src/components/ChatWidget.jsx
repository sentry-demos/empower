import React, { useState, useEffect, useRef, useCallback } from 'react';
import * as Sentry from '@sentry/react';
import './chatWidget.css';
import agentIcon from '../assets/empower-agent.png';
import ChatPills from './ChatPills';
import ChatProductList from './ChatProductList';
import ChatCart from './ChatCart';
import ChatCheckout from './ChatCheckout';
import ChatConfirmation from './ChatConfirmation';
import ChatError from './ChatError';
import postEventStream from '../utils/sseStream';

// Was 15s, which is fine for a two-question form but not for a conversation —
// a user reading a product list and deciding what to add would blow through it
// and end the session span mid-chat. The timer is also suspended while a turn
// is in flight, since a slow product fetch is not user inactivity.
const CHAT_SESSION_INACTIVITY_TIMEOUT_MS = 120000;
const AGENT_URL = process.env.REACT_APP_BACKEND_URL_AGENT;

// Shown before the first turn. After that the agent sends pills itself.
const INITIAL_PILLS = [
  { id: 'chat-pill-show-products', label: 'Show me plants under $200' },
];

// Extra starters for the full view's empty state only, which has room for a row
// of tiles where the popup has room for one chip. Client-side and free-text on
// purpose: the agent's own pills drive the reproducible demo path and keep their
// chat-pill-* ids for TDA, so these use a chat-starter-* prefix and simply
// exercise the conversational routing (care questions reach the plant expert).
const FULL_VIEW_STARTERS = [
  { id: 'chat-starter-low-light', label: 'What does well in low light?' },
  { id: 'chat-starter-easy-care', label: 'Which plants are hardest to kill?' },
];

const GREETING =
  "Hi, I can help you find plants and get them into your cart. Ask me anything.";

let messageIdCounter = 0;
const generateMessageId = () => `msg-${Date.now()}-${++messageIdCounter}`;
const generateConversationId = () =>
  `conv-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;

// Two shells around one conversation.
//
// `fullView` renders the page-sized view Home switches to when the customer
// picks the agent from the hero. Without it this is the original floating
// button and popup, which is left alone deliberately: _tda/test_ai_agent.py
// drives it by #chat-widget-button and re-clicks that same element to close, so
// removing or remounting it would break that test with a stale reference.
//
// Both shells share the session, SSE and span logic below; only the layout and
// the card sizing differ (the roomier styles are scoped under .chat-full).
const ChatWidget = ({ fullView = false, onExitFull }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [userInput, setUserInput] = useState('');
  const [pills, setPills] = useState(INITIAL_PILLS);
  const [isStreaming, setIsStreaming] = useState(false);

  const messagesEndRef = useRef(null);
  const messagesContainerRef = useRef(null);
  const chatSpanRef = useRef(null);
  const conversationIdRef = useRef(null);
  const typingSpanRef = useRef(null);
  const typingTimeoutRef = useRef(null);
  const inactivityTimeoutRef = useRef(null);
  const conversationStartedRef = useRef(false);
  const abortRef = useRef(null);
  const inputRef = useRef(null);

  // Scroll the transcript, not the document. scrollIntoView walks up and
  // scrolls every scrollable ancestor including the window, which in the full
  // view dragged the whole page down on each new message and left the header
  // sitting mid-screen. Setting scrollTop only ever moves this one element.
  const scrollToBottom = () => {
    const container = messagesContainerRef.current;
    if (container) {
      container.scrollTop = container.scrollHeight;
    }
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
    if (abortRef.current) {
      abortRef.current.abort();
      abortRef.current = null;
    }

    Sentry.setConversationId(null);
    // Record how the session ended
    if (chatSpanRef.current) {
      const isTimeout = reason === 'inactivity_timeout';
      Sentry.withActiveSpan(chatSpanRef.current, () => {
        Sentry.startSpan(
          {
            op: isTimeout ? 'mark' : 'ui.action',
            name: `Session End: ${reason}`,
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
      inactivityTimeoutRef.current = null;
    }

    if (chatSpanRef.current) {
      inactivityTimeoutRef.current = setTimeout(() => {
        endChatSession('inactivity_timeout');
      }, CHAT_SESSION_INACTIVITY_TIMEOUT_MS);
    }
  }, [endChatSession]);

  useEffect(() => {
    scrollToBottom();
    // The product and cart cards hold images with no intrinsic size, so the
    // transcript is still short when this effect runs and the scroll lands at
    // the top. A frame later the layout has settled.
    const frame = requestAnimationFrame(scrollToBottom);
    return () => cancelAnimationFrame(frame);
  }, [messages]);

  // Images finish loading well after their message is committed, each one
  // growing the transcript underneath a scroll that has already happened.
  // `load` does not bubble, hence the capture-phase listener.
  useEffect(() => {
    const container = messagesContainerRef.current;
    if (!container) return undefined;
    const onLoad = () => scrollToBottom();
    container.addEventListener('load', onLoad, true);
    return () => container.removeEventListener('load', onLoad, true);
  }, [isOpen, fullView]);

  // Focus the composer when either shell opens, but never scroll to do it.
  // Plain autoFocus scrolled the full view's page down by ~400px on open,
  // putting the greeting and the starter tiles above the viewport.
  useEffect(() => {
    if (!isOpen && !fullView) return;
    if (fullView) window.scrollTo(0, 0);
    inputRef.current?.focus({ preventScroll: true });
  }, [isOpen, fullView]);

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
          name: 'User Typing',
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

  const endTypingSpan = () => {
    if (typingSpanRef.current) {
      typingSpanRef.current.end();
      typingSpanRef.current = null;
    }
    if (typingTimeoutRef.current) {
      clearTimeout(typingTimeoutRef.current);
      typingTimeoutRef.current = null;
    }
  };

  // Map the operator-facing error flags on the page URL onto the agent's
  // domain-named params, so the demo triggers don't stand out in the agent's
  // span attributes.
  const chatUrl = () => {
    const pageParams = new URLSearchParams(window.location.search);
    const params = new URLSearchParams();
    const adviceError = pageParams.get('agent_advice_error');
    if (adviceError) params.set('validate_plant_advice', adviceError);
    const infoError = pageParams.get('agent_info_error');
    if (infoError) params.set('validate_plant_info', infoError);
    const query = params.toString();
    return `${AGENT_URL}/api/v1/chat${query ? `?${query}` : ''}`;
  };

  // Run one turn: post the message, then fold the SSE events into messages.
  const runTurn = useCallback(
    async (message) => {
      const controller = new AbortController();
      abortRef.current = controller;
      setIsStreaming(true);
      setPills([]);

      // Suspend the inactivity timer for the duration of the turn.
      if (inactivityTimeoutRef.current) {
        clearTimeout(inactivityTimeoutRef.current);
        inactivityTimeoutRef.current = null;
      }

      setMessages((prev) => [
        ...prev,
        { type: 'user', text: message, id: generateMessageId() },
        { type: 'typing', id: generateMessageId() },
      ]);

      // One chat.turn span per turn, under the session span.
      const turnSpan = chatSpanRef.current
        ? Sentry.withActiveSpan(chatSpanRef.current, () =>
            Sentry.startInactiveSpan({ op: 'chat.turn', name: 'Chat Turn' })
          )
        : null;
      turnSpan?.setAttribute('chat.message', message);

      // Assistant prose streams in as deltas; keep appending to one bubble.
      let botMessageId = null;
      const appendToken = (text) => {
        setMessages((prev) => {
          const next = prev.filter(
            (m) => m.type !== 'typing' && m.type !== 'status'
          );
          const existing = next.find((m) => m.id === botMessageId);
          if (existing) {
            return next.map((m) =>
              m.id === botMessageId ? { ...m, text: m.text + text } : m
            );
          }
          botMessageId = generateMessageId();
          return [...next, { type: 'bot', text, id: botMessageId }];
        });
      };

      const onEvent = ({ event, data }) => {
        if (event === 'status') {
          botMessageId = null;
          setMessages((prev) => [
            ...prev.filter((m) => m.type !== 'typing' && m.type !== 'status'),
            { type: 'status', text: data.label, id: generateMessageId() },
          ]);
          turnSpan?.setAttribute(`chat.tool.${data.tool}`, true);
        } else if (event === 'token') {
          appendToken(data.text);
        } else if (event === 'message_end') {
          // Close the current bubble so the next assistant message starts its
          // own, rather than running on from this one.
          botMessageId = null;
        } else if (event === 'widget') {
          botMessageId = null;
          setMessages((prev) => [
            ...prev.filter((m) => m.type !== 'typing' && m.type !== 'status'),
            {
              type: 'widget',
              widget: { type: data.type, data: data.data },
              id: generateMessageId(),
            },
          ]);
        } else if (event === 'pills') {
          setPills(data.pills || []);
        } else if (event === 'error') {
          turnSpan?.setAttribute('chat.turn.error', data.code || 'unknown');
          Sentry.captureMessage(`Chat turn failed: ${data.message}`, 'error');
        }
      };

      try {
        await postEventStream(chatUrl(), {
          headers: { 'x-conversation-id': conversationIdRef.current },
          body: { message },
          signal: controller.signal,
          onEvent,
        });
      } catch (error) {
        if (error.name !== 'AbortError') {
          Sentry.captureException(error);
          setMessages((prev) => [
            ...prev.filter((m) => m.type !== 'typing' && m.type !== 'status'),
            {
              type: 'widget',
              widget: { type: 'error', data: { message: error.message } },
              id: generateMessageId(),
            },
          ]);
          setPills(INITIAL_PILLS);
        }
      } finally {
        // Drop any leftover placeholder so a turn never ends mid-spinner.
        setMessages((prev) =>
          prev.filter((m) => m.type !== 'typing' && m.type !== 'status')
        );
        turnSpan?.end();
        abortRef.current = null;
        setIsStreaming(false);
        startInactivityTimeout();
      }
    },
    [startInactivityTimeout]
  );

  const sendMessage = useCallback(
    (message) => {
      if (!message.trim() || isStreaming) return;

      Sentry.withActiveSpan(chatSpanRef.current, () => {
        Sentry.logger.info('Chat message sent');
        Sentry.metrics.count('chat.message_sent', 1);
        if (!conversationStartedRef.current) {
          conversationStartedRef.current = true;
          Sentry.metrics.count('chat.conversation_started', 1);
        }
      });

      runTurn(message);
    },
    [isStreaming, runTurn]
  );

  const handleSubmit = (e) => {
    e.preventDefault();
    endTypingSpan();

    if (chatSpanRef.current) {
      Sentry.withActiveSpan(chatSpanRef.current, () => {
        Sentry.startSpan({ op: 'ui.action.click', name: 'Send Message' }, () => {
          // Span ends immediately after click
        });
      });
    }

    const message = userInput;
    setUserInput('');
    sendMessage(message);
  };

  const handlePillSelect = (pill) => {
    endTypingSpan();

    if (chatSpanRef.current) {
      Sentry.withActiveSpan(chatSpanRef.current, () => {
        Sentry.startSpan(
          { op: 'ui.action.click', name: `Chat Pill: ${pill.label}` },
          (span) => {
            span.setAttribute('chat.pill.id', pill.id);
          }
        );
      });
    }

    sendMessage(pill.label);
  };

  // Everything a new conversation needs, independent of which shell shows it.
  const startSession = useCallback(() => {
    conversationStartedRef.current = false;
    const conversationId = generateConversationId();
    conversationIdRef.current = conversationId;
    Sentry.setConversationId(conversationId);
    Sentry.startNewTrace(() => {
      const span = Sentry.startInactiveSpan({
        op: 'ui.interaction.chat',
        name: 'AI Agent Chat Session',
        forceTransaction: true,
      });
      chatSpanRef.current = span;
      Sentry.logger.info('Chat session started');
      Sentry.metrics.count('chat.open', 1);
    });
    setMessages([{ type: 'bot', text: GREETING, id: generateMessageId() }]);
    setPills(INITIAL_PILLS);
    startInactivityTimeout();
  }, [startInactivityTimeout]);

  const openChat = () => {
    startSession();
    setIsOpen(true);
  };

  const closeChat = (reason) => {
    endChatSession(reason);
    setIsOpen(false);
  };

  // The full view's session is tied to the prop rather than a click, so Home
  // stays the single owner of which view is on screen.
  useEffect(() => {
    if (!fullView) return undefined;
    startSession();
    return () => endChatSession('exit_full_view');
  }, [fullView, startSession, endChatSession]);

  // Hide the site footer while the conversation owns the page. The footer is
  // mounted in index.js outside the routed content, so Home cannot unmount it —
  // a body class is the only reach this component has. Its newsletter signup is
  // a second, unrelated call to action competing with the composer.
  useEffect(() => {
    if (!fullView) return undefined;
    document.body.classList.add('agent-full-view');
    return () => document.body.classList.remove('agent-full-view');
  }, [fullView]);

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

  const renderWidget = (message) => {
    const { type, data } = message.widget;
    if (type === 'products') {
      return (
        <ChatProductList
          products={data.products}
          disabled={isStreaming}
          onAddToCart={(product) =>
            sendMessage(`Add ${product.title} to my cart`)
          }
        />
      );
    }
    if (type === 'cart') {
      return <ChatCart cart={data.cart} promo={data.promo} />;
    }
    if (type === 'checkout') {
      if (data.error) return <ChatError message={data.error} />;
      return <ChatCheckout form={data.form} cart={data.cart} />;
    }
    if (type === 'promo') {
      // Applying a coupon is expected to fail in the demo (SAVE20 is seeded
      // expired, so Flask returns 410). Show the backend's own wording.
      if (data.ok) {
        return (
          <div className="chat-widget-card" id="chat-promo-applied">
            <span className="chat-confirmation-title sentry-unmask">
              Promo {data.code} applied
            </span>
            {data.promo && (
              <p className="chat-confirmation-body sentry-unmask">
                {data.promo.percent_discount}% off, up to $
                {data.promo.max_dollar_savings}
              </p>
            )}
          </div>
        );
      }
      return <ChatError message={data.message} code={data.error_code} />;
    }
    if (type === 'confirmation') {
      if (data.ok) {
        return (
          <ChatConfirmation
            orderTotal={data.order_total}
            itemCount={data.item_count}
          />
        );
      }
      return <ChatError message={data.message} code={String(data.status)} />;
    }
    if (type === 'error') {
      return <ChatError message={data.message} code={data.code} />;
    }
    return null;
  };

  const renderMessages = () => (
    <>
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

        if (message.type === 'status') {
          return (
            <div key={message.id} className="message bot-message">
              <div className="chat-status">
                <span className="chat-status-dot"></span>
                <span className="chat-status-label">{message.text}</span>
              </div>
            </div>
          );
        }

        if (message.type === 'widget') {
          return (
            <div key={message.id} className="message bot-message">
              {renderWidget(message)}
            </div>
          );
        }

        return (
          <div
            key={message.id}
            className={`message ${
              message.type === 'bot' ? 'bot-message' : 'user-message'
            }`}
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
    </>
  );

  // Always mounted, in both shells. The old widget unmounted the input after
  // the second answer, which is exactly the scripted experience this replaces.
  const renderComposer = () => (
    <form className="chat-input-form" onSubmit={handleSubmit}>
      <input
        id="chat-message-input"
        type="text"
        value={userInput}
        onChange={handleInputChange}
        onFocus={handleInputFocus}
        placeholder={isStreaming ? 'Thinking…' : 'Ask me anything...'}
        className="chat-input"
        ref={inputRef}
      />
      <button
        id="chat-send-button"
        type="submit"
        className="chat-send-button"
        disabled={isStreaming || !userInput.trim()}
      >
        Send
      </button>
    </form>
  );

  if (fullView) {
    // The greeting is seeded by startSession, so "has the customer said
    // anything yet" is what decides between the empty state and the transcript.
    const started = messages.some((message) => message.type === 'user');

    return (
      <div className="chat-full">
        <nav className="chat-rail" aria-label="Conversation">
          {/* Only controls that do something. The reference design has a row of
              icons, but dead buttons in a demo invite clicks that go nowhere. */}
          <button
            type="button"
            id="chat-exit-full"
            className="chat-rail-button sentry-unmask"
            onClick={() => onExitFull && onExitFull()}
            title="Back to Empower Plant"
          >
            <span aria-hidden="true">←</span>
            <span className="chat-rail-label">Store</span>
          </button>
          <button
            type="button"
            id="chat-new-conversation"
            className="chat-rail-button sentry-unmask"
            onClick={() => {
              endChatSession('new_conversation');
              startSession();
            }}
            title="Start a new conversation"
          >
            <span aria-hidden="true">+</span>
            <span className="chat-rail-label">New</span>
          </button>
        </nav>

        <div className="chat-full-main">
          {started ? (
            <div
              className="chat-messages chat-full-messages"
              ref={messagesContainerRef}
            >
              {renderMessages()}
            </div>
          ) : (
            <div className="chat-full-intro">
              <img
                src={agentIcon}
                alt=""
                className="chat-full-avatar sentry-block"
              />
              <p className="chat-full-eyebrow sentry-unmask">
                Empower Plant assistant
              </p>
              <h1 className="chat-full-heading sentry-unmask">
                Let&rsquo;s find your next plant
              </h1>
              <ChatPills
                pills={[...pills, ...FULL_VIEW_STARTERS]}
                onSelect={handlePillSelect}
                disabled={isStreaming}
                variant="cards"
              />
            </div>
          )}

          <div className="chat-full-composer">
            {started && (
              <ChatPills
                pills={pills}
                onSelect={handlePillSelect}
                disabled={isStreaming}
              />
            )}
            {/* Only the input gets a frame. The pills sit above it unboxed —
                they are already self-contained chips, so wrapping them in the
                same panel drew a container around containers. */}
            <div className="chat-full-composer-box">{renderComposer()}</div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="chat-widget-container">
      {isOpen && (
        <div className="chat-window">
          <div className="chat-header">
            <div className="chat-header-content">
              <img src={agentIcon} alt="AI Agent" className="chat-header-icon" />
              <span className="chat-header-title">AI Agent</span>
            </div>
            <button className="chat-close-button" onClick={handleCloseButtonClick}>
              ×
            </button>
          </div>

          <div className="chat-messages" ref={messagesContainerRef}>
            {renderMessages()}
          </div>

          <ChatPills
            pills={pills}
            onSelect={handlePillSelect}
            disabled={isStreaming}
          />

          {renderComposer()}
        </div>
      )}

      <button
        id="chat-widget-button"
        className="chat-toggle-button"
        onClick={handleAgentButtonClick}
      >
        <img src={agentIcon} alt="Chat with AI Agent" />
      </button>
    </div>
  );
};

export default ChatWidget;
