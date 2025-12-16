"""
Main CLI interface logic.
"""

import sqlite3
import sys

from langchain_core.messages import HumanMessage
from langchain_core.runnables import Runnable, RunnableConfig
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_openai import ChatOpenAI

from src.core.agent import create_agent_executor
from src.core.config import settings
from src.core.summarizer import summarize_conversation
from src.database.repository import ConversationDB
from src.ui.menu import show_conversation_menu
from src.ui.stream_handler import process_agent_stream

# Command constants
EXIT_COMMANDS = ['sair', 'quit', 'exit', 'q']
CLEAR_COMMANDS = ['limpar', 'clear', 'reset']


def run_cli(
    db: ConversationDB | None = None,
    agent: Runnable | None = None,
    checkpointer: SqliteSaver | None = None
) -> None:
    """
    Function that starts the CLI application.
    
    Args:
        db: Database instance. If None, a new instance will be created.
        agent: Agent instance. If None, a new instance will be created.
        checkpointer: Checkpoint saver instance. If None and agent is provided,
            a new instance will be created. If None and agent is None, will be
            created along with the agent.
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

    # Initialize agent and checkpointer if not provided
    try:
        if agent is None:
            agent, checkpointer = create_agent_executor()
        elif checkpointer is None:
            # If agent is provided but checkpointer is not, create a new one
            # This ensures we always have a checkpointer for summarization
            checkpoint_path = settings.checkpoint_db_path
            checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect(str(checkpoint_path), check_same_thread=False)
            checkpointer = SqliteSaver(conn)
        print("✅ Assistente inicializado com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao inicializar assistente: {e}")
        sys.exit(1)
    
    # Show conversation menu at startup
    thread_id, current_conv_id = show_conversation_menu(db)
    
    if current_conv_id is None:
        print("\n💬 Nova conversa iniciada!")
        # thread_id will be set when first message is saved
    else:
        print(f"\n✅ Conversa carregada do checkpoint! (ID: {current_conv_id})")
    
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
                # Delete checkpoint and conversation
                try:
                    # Delete from metadata database if exists
                    if current_conv_id is not None:
                        db.delete_conversation(current_conv_id)
                    
                    # Reset to create new conversation
                    thread_id = None
                    current_conv_id = None
                    config = None
                    
                    print("\n🧹 Histórico da conversa limpo!")
                except Exception as e:
                    print(f"\n🧹 Histórico da conversa limpo! (Aviso: {e})")
                
                continue
            
            # Ignore empty inputs
            if not user_input:
                continue

            # Create user message
            user_message = HumanMessage(content=user_input)
            
            # Check if this is the first message (for metadata saving)
            is_first_message = (current_conv_id is None)
            
            # For new conversations, save metadata first to get conversation_id and thread_id
            if is_first_message:
                try:
                    current_conv_id, thread_id = db.save_conversation_metadata(user_input)
                except Exception as e:
                    print(f"\n\n⚠️ Aviso: Não foi possível salvar metadados no banco: {e}")
                    continue
            
            # Process agent streaming with checkpoint
            # Checkpoint automatically loads previous history and saves after
            if thread_id is not None:
                process_agent_stream(agent, user_message, thread_id)
            
            # Check if summarization is needed (after new message was added)
            summarize_conversation(checkpointer, thread_id)
        except KeyboardInterrupt:
            # Handle Ctrl+C gracefully
            print("\n\n👋 Interrompido pelo usuário. Até logo!")
            break
        except Exception as e:
            print(f"\n❌ Erro: {e}")
            print("Tente novamente ou digite 'sair' para encerrar.")

