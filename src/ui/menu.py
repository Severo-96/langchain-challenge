"""
Conversation selection menu.
"""

from typing import List, Tuple

import questionary
from langchain_core.messages import BaseMessage

from src.database.repository import ConversationDB


def show_conversation_menu(
    db: ConversationDB
) -> Tuple[List[BaseMessage], int | None]:
    """
    Shows the initial conversation menu and returns the selected conversation.
    
    Args:
        db: Database instance
        
    Returns:
        Tuple of (conversation_history, conversation_id)
        conversation_id is None for new conversations
    """
    try:
        conversations = db.get_conversations_list()
        
        # Create formatted options list for questionary
        options = ["💬 Nova conversa"]
        
        if conversations:
            for conv in conversations:
                updated_at = conv.get('updated_at')

                # Get first message (truncate if too long)
                first_message = conv.get('first_message')
                if first_message and len(first_message) > 50:
                    first_message = first_message[:47] + "..."

                options.append(f"ID {conv.get('id')} - {first_message} - {updated_at}")
        
        # Use questionary for interactive selection
        choice = questionary.select(
            "Selecione uma conversa ou crie uma nova:",
            choices=options
        ).ask()
        
        if not choice or choice == "💬 Nova conversa":
            return [], None
        
        # Extract ID from choice and get conversation from database
        conv_id = int(choice.split()[1])
        conversation = db.get_conversation(conv_id)

        if conversation:
            return conversation['messages_history'], conv_id
        
        return [], None
        
    except Exception as e:
        print(f"\n❌ Erro ao carregar conversas: {e}")
        return [], None

