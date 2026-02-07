"""Session-based storage for generated questions and conversation state."""

import json
import logging
import os
import sqlite3
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

logging.basicConfig(level=logging.DEBUG)

# Database path for question storage
DB_PATH = "agent_sessions.db"


@dataclass
class QuestionItem:
    """A single question in the decision tree."""
    question: str
    answer_interpretation: str
    next_question: Optional[int] = None  # Index of next question, None if terminal
    
    def to_dict(self) -> dict:
        return {
            "question": self.question,
            "answer_interpretation": self.answer_interpretation,
            "next_question": self.next_question
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "QuestionItem":
        return cls(
            question=data["question"],
            answer_interpretation=data["answer_interpretation"],
            next_question=data.get("next_question")
        )


@dataclass 
class SessionState:
    """Conversation state for a session."""
    session_id: str
    questions: list[QuestionItem] = field(default_factory=list)
    products: list[dict] = field(default_factory=list)  # Cached products from MCP
    current_question_index: int = 0
    user_answers: list[str] = field(default_factory=list)
    remaining_product_ids: list[int] = field(default_factory=list)
    recommended_product_id: Optional[int] = None
    
    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "questions": [q.to_dict() for q in self.questions],
            "products": self.products,
            "current_question_index": self.current_question_index,
            "user_answers": self.user_answers,
            "remaining_product_ids": self.remaining_product_ids,
            "recommended_product_id": self.recommended_product_id
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "SessionState":
        return cls(
            session_id=data["session_id"],
            questions=[QuestionItem.from_dict(q) for q in data.get("questions", [])],
            products=data.get("products", []),
            current_question_index=data.get("current_question_index", 0),
            user_answers=data.get("user_answers", []),
            remaining_product_ids=data.get("remaining_product_ids", []),
            recommended_product_id=data.get("recommended_product_id")
        )


class QuestionStore:
    """SQLite-based storage for session question state."""
    
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize the database table."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS question_sessions (
                    session_id TEXT PRIMARY KEY,
                    state_json TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
    
    def get_session(self, session_id: str) -> Optional[SessionState]:
        """Get session state by ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT state_json FROM question_sessions WHERE session_id = ?",
                (session_id,)
            )
            row = cursor.fetchone()
            if row:
                data = json.loads(row[0])
                return SessionState.from_dict(data)
        return None
    
    def save_session(self, state: SessionState):
        """Save or update session state."""
        state_json = json.dumps(state.to_dict())
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO question_sessions (session_id, state_json, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(session_id) DO UPDATE SET
                    state_json = excluded.state_json,
                    updated_at = CURRENT_TIMESTAMP
            """, (state.session_id, state_json))
            conn.commit()
    
    def delete_session(self, session_id: str):
        """Delete a session."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "DELETE FROM question_sessions WHERE session_id = ?",
                (session_id,)
            )
            conn.commit()


# Global store instance
question_store = QuestionStore()
