"""
Main CLI interface logic.
"""

import sys

from langchain_core.messages import HumanMessage
from langchain_core.runnables import Runnable

from src.core.agent import create_agent_executor
from src.database.repository import ConversationDB
from src.ui.menu import show_conversation_menu
from src.ui.stream_handler import process_agent_stream

# Command constants
EXIT_COMMANDS = ['sair', 'quit', 'exit', 'q']
CLEAR_COMMANDS = ['limpar', 'clear', 'reset']


def run_cli(db: ConversationDB | None = None, agent: Runnable | None = None) -> None:
    """
    Function that starts the CLI application.
    
    Args:
        db: Database instance. If None, a new instance will be created.
        agent: Agent instance. If None, a new instance will be created.
    """
    print("=" * 60)
    print("🤖 Assistente IA com Function Calling")
    print("=" * 60)
    print("\nEste assistente pode ajudar você com:")
    print("  • Informações sobre países")
    print("  • Taxas de câmbio")
    print("=" * 60)
    print()

    # Initialize database if not provided
    if db is None:
        db = ConversationDB()

    # Initialize agent if not provided
    try:
        if agent is None:
            agent = create_agent_executor()
        print("✅ Assistente inicializado com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao inicializar assistente: {e}")
        sys.exit(1)
    
    # Show conversation menu at startup
    conversation_history, current_conv_id = show_conversation_menu(db)
    
    if conversation_history:
        print(f"\n✅ Conversa carregada! ({len(conversation_history)} mensagem(ns) no histórico)")
    else:
        print("\n💬 Nova conversa iniciada!")
    
    print("\nDigite 'sair' ou 'quit' para encerrar.")
    print("Digite 'limpar' para limpar o histórico da conversa.")
    print("=" * 60)
    print()
    
    # Main interaction loop
    while True:
        try:
            # Read user input
            user_input = input("\n\n👤 Você: ").strip()
            
            # Check if user wants to exit
            if user_input.lower() in EXIT_COMMANDS:
                print("\n👋 Até logo!")
                break
            
            # Check if user wants to clear history
            if user_input.lower() in CLEAR_COMMANDS:
                conversation_history = []
                # Remove only current conversation from database, if it exists
                if current_conv_id is not None:
                    try:
                        db.delete_conversation(current_conv_id)
                        print("\n🧹 Histórico da conversa limpo!")
                    except Exception as e:
                        warning = (
                            f"\n🧹 Histórico da conversa limpo localmente! "
                            f"(Aviso: não foi possível remover do banco: {e})"
                        )
                        print(warning)
                else:
                    print("\n🧹 Histórico da conversa limpo!")
                current_conv_id = None  # Reset ID to create new conversation
                continue
            
            # Ignore empty inputs
            if not user_input:
                continue

            # Identify as first message in history, if it doesn't exist
            first_message = user_input if not conversation_history else None
            
            # Add user message to history
            user_message = HumanMessage(content=user_input)
            conversation_history.append(user_message)
            
            # Process agent streaming
            conversation_history = process_agent_stream(agent, conversation_history)

            # Save or update history in database
            if conversation_history:
                try:
                    if current_conv_id:
                        # Update existing conversation
                        db.update_conversation(current_conv_id, conversation_history)
                    else:
                        # Create new conversation and save ID
                        current_conv_id = db.save_conversation(first_message, conversation_history)
                except Exception as e:
                    print(f"\n\n⚠️ Aviso: Não foi possível salvar no banco de dados: {e}")

        except KeyboardInterrupt:
            # Handle Ctrl+C gracefully
            print("\n\n👋 Interrompido pelo usuário. Até logo!")
            break
        except Exception as e:
            print(f"\n❌ Erro: {e}")
            print("Tente novamente ou digite 'sair' para encerrar.")

