"""
Conversation selection menu.
"""

from typing import Optional, Tuple, List
import questionary
from src.database.repository import ConversationDB


def show_conversation_menu(db: ConversationDB) -> Tuple[List, Optional[int]]:
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
        
        # Cria lista de opções formatadas para o questionary
        options = ["💬 Nova conversa"]
        
        if conversations:
            for conv in conversations:
                updated_at = conv.get('updated_at')

                # Pega a primeira mensagem (trunca se muito longa)
                first_message = conv.get('first_message')
                if first_message and len(first_message) > 50:
                    first_message = first_message[:47] + "..."

                options.append(f"ID {conv.get('id')} - {first_message} - {updated_at}")
        
        # Usa questionary para seleção interativa
        choice = questionary.select(
            "Selecione uma conversa ou crie uma nova:",
            choices=options
        ).ask()
        
        if not choice or choice == "💬 Nova conversa":
            return [], None
        
        # Extrai o ID da escolha e pega a conversa no banco
        conv_id = int(choice.split()[1])
        conversation = db.get_conversation(conv_id)

        if conversation:
            return conversation['messages_history'], conv_id
        
        return [], None
        
    except Exception as e:
        print(f"\n❌ Erro ao carregar conversas: {e}")
        return [], None

