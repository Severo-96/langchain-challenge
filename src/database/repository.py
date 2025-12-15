"""
Module for managing SQLite database.
Saves and retrieves conversation history.
"""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

from src.core.config import settings


class ConversationDB:
    """Manages the conversation database."""
    
    def __init__(self) -> None:
        """
        Initializes the database connection.
        """
        self.db_path: Path = settings.conversation_db_path
        # Ensure directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self) -> None:
        """Creates the conversations table and trigger if they don't exist."""
        with sqlite3.connect(str(self.db_path)) as connection:
            cursor = connection.cursor()
            
            # Create table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    thread_id TEXT UNIQUE,
                    first_message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create trigger to automatically set thread_id = 't' || id on insert
            cursor.execute('''
                CREATE TRIGGER IF NOT EXISTS set_thread_id_on_insert
                AFTER INSERT ON conversations
                WHEN NEW.thread_id IS NULL
                BEGIN
                    UPDATE conversations
                    SET thread_id = 't' || NEW.id
                    WHERE id = NEW.id;
                END
            ''')
            
            connection.commit()

    def get_conversations_list(self) -> list[dict[str, Any]]:
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
    
    def get_conversation(self, conversation_id: int) -> dict[str, Any] | None:
        """
        Retrieves conversation metadata by ID.
        
        Args:
            conversation_id: Record ID
            
        Returns:
            Dictionary with id and thread_id, or None
        """
        with sqlite3.connect(str(self.db_path)) as connection:
            connection.row_factory = sqlite3.Row
            cursor = connection.cursor()
            cursor.execute('''
                SELECT id, thread_id
                FROM conversations
                WHERE id = ?
            ''', (conversation_id,))
            row = cursor.fetchone()
            
            if row:
                return {
                    'id': row['id'],
                    'thread_id': row['thread_id'],
                }
            return None

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

    def save_conversation_metadata(self, first_message: str) -> tuple[int, str]:
        """
        Saves conversation metadata to the database.
        The trigger automatically sets thread_id = 't' || id.
        
        Args:
            first_message: First user message content (string)
            
        Returns:
            Tuple of (conversation_id, thread_id)
        """
        with sqlite3.connect(str(self.db_path)) as connection:
            cursor = connection.cursor()
            cursor.execute('''
                INSERT INTO conversations (first_message)
                VALUES (?)
            ''', (first_message,))
            connection.commit()
            return cursor.lastrowid, f"t{cursor.lastrowid}"
