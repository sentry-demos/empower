import React from 'react';

// Suggestion chips. The agent derives these server-side from whichever tool ran
// last and sends them on the `pills` SSE event, so the ids below are stable and
// TDA can drive the demo path by id. They are pre-filled prompts, not the only
// way through the flow — the free-text input stays available at all times.
function ChatPills({ pills, onSelect, disabled }) {
  if (!pills || pills.length === 0) return null;

  return (
    <div className="chat-pills">
      {pills.map((pill) => (
        <button
          key={pill.id}
          id={pill.id}
          type="button"
          className="chat-pill sentry-unmask"
          disabled={disabled}
          onClick={() => onSelect(pill)}
        >
          {pill.label}
        </button>
      ))}
    </div>
  );
}

export default ChatPills;
