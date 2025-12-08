"""
Module for managing SQLite database.
Saves and retrieves conversation history.
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage


class ConversationDB:
    """Manages the conversation database."""
    
    def __init__(self, db_path: str = 'data/conversations.db'):
        """
        Initializes the database connection.
        
        Args:
            db_path: Path to the database file
        """
        self.db_path = Path(db_path)
        # Ensure directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Creates the conversations table if it doesn't exist."""
        with sqlite3.connect(str(self.db_path)) as connection:
            cursor = connection.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    messages_history TEXT NOT NULL,
                    first_message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            connection.commit()

    def get_conversations_list(self) -> List[Dict[str, Any]]:
        """
        Retrieves the list of conversations.
        
        Returns:
            List of dictionaries with id, first_message and updated_at (formatted)
        """
        with sqlite3.connect(str(self.db_path)) as connection:
            connection.row_factory = sqlite3.Row
            cursor = connection.cursor()
            
            cursor.execute('''
                SELECT id, first_message, updated_at
                FROM conversations
                ORDER BY updated_at DESC
            ''')
            
            rows = cursor.fetchall()
            return [
                {
                    'id': row['id'],
                    'first_message': row['first_message'],
                    'updated_at': datetime.fromisoformat(row['updated_at']).strftime('%d-%m-%Y')
                }
                for row in rows
            ]
    
    def get_conversation(self, conversation_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieves a conversation history by ID.
        
        Args:
            conversation_id: Record ID
            
        Returns:
            Dictionary with id, messages_history (deserialized), or None
        """
        with sqlite3.connect(str(self.db_path)) as connection:
            connection.row_factory = sqlite3.Row
            cursor = connection.cursor()
            cursor.execute('''
                SELECT id, messages_history, first_message
                FROM conversations
                WHERE id = ?
            ''', (conversation_id,))
            row = cursor.fetchone()
            
            if row:
                return {
                    'id': row['id'],
                    'messages_history': self._deserialize_history(row['messages_history']),
                }
            return None

    def _deserialize_history(self, messages_history: str) -> List[BaseMessage]:
        """
        Deserializes conversation history from JSON.
        
        Args:
            messages_history: Serialized JSON string
            
        Returns:
            List of LangChain messages
        """
        # Convert messages to dictionaries
        messages_history_dict = json.loads(messages_history)
        messages_history = []

        for msg_dict in messages_history_dict:
            msg_type = msg_dict.get('type', '')
            content = msg_dict.get('content', '')
            
            if msg_type == 'HumanMessage':
                msg = HumanMessage(content=content)
            elif msg_type == 'AIMessage':
                msg = AIMessage(content=content)

            messages_history.append(msg)

        return messages_history

    def delete_conversation(self, conversation_id: int) -> bool:
        """
        Deletes a conversation history.
        
        Args:
            conversation_id: ID of the record to delete
            
        Returns:
            True if deleted successfully, False otherwise
        """
        with sqlite3.connect(str(self.db_path)) as connection:
            cursor = connection.cursor()
            cursor.execute('DELETE FROM conversations WHERE id = ?', (conversation_id,))
            connection.commit()
            return cursor.rowcount > 0

    def update_conversation(self, conversation_id: int, conversation_history: List[BaseMessage]):
        """
        Updates an existing conversation history.
        
        Args:
            conversation_id: ID of the record to update
            conversation_history: List of LangChain messages
        """
        messages_history_json = self._serialize_history(conversation_history)
        
        with sqlite3.connect(str(self.db_path)) as connection:
            cursor = connection.cursor()
            cursor.execute('''
                UPDATE conversations
                SET messages_history = ?, updated_at = ?
                WHERE id = ?
            ''', (messages_history_json, datetime.now().isoformat(), conversation_id))
            connection.commit()
    
    def _serialize_history(self, conversation_history: List[BaseMessage]) -> str:
        """
        Serializes conversation history to JSON.
        
        Args:
            conversation_history: List of LangChain messages
            
        Returns:
            Serialized JSON string
        """
        # Convert messages to dictionaries
        messages_dict = []
        for msg in conversation_history:
            msg_dict = {
                'type': type(msg).__name__,
                'content': getattr(msg, 'content', '')
            }
            messages_dict.append(msg_dict)

        return json.dumps(messages_dict, ensure_ascii=False)
    
    def save_conversation(self, first_message: str, conversation_history: List[BaseMessage]) -> int:
        """
        Saves conversation history to the database.
        
        Args:
            first_message: First user message content (string)
            conversation_history: List of LangChain messages
            
        Returns:
            ID of the inserted record
        """
        messages_history_json = self._serialize_history(conversation_history)
        
        with sqlite3.connect(str(self.db_path)) as connection:
            cursor = connection.cursor()
            cursor.execute('''
                INSERT INTO conversations (messages_history, first_message, updated_at)
                VALUES (?, ?, ?)
            ''', (messages_history_json, first_message, datetime.now().isoformat()))
            connection.commit()
            return cursor.lastrowid

