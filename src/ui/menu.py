"""
Conversation selection menu.
"""

import questionary

from src.database.repository import ConversationDB


def show_conversation_menu(
    db: ConversationDB
) -> tuple[str | None, int | None]:
    """
    Shows the initial conversation menu and returns the selected conversation thread_id.
    
    Args:
        db: Database instance
        
    Returns:
        Tuple of (thread_id, conversation_id)
        Both are None for new conversations
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
            return None, None
        
        # Extract ID from choice and get thread_id from database
        conv_id = int(choice.split()[1])
        thread_id = db.get_conversation(conv_id)['thread_id']

        if thread_id:
            return thread_id, conv_id
        
        return None, None
        
    except Exception as e:
        print(f"\n❌ Erro ao carregar conversas: {e}")
        return None, None

