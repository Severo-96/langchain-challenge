"""
Main CLI interface logic.
"""

from typing import Optional, List
import sys
from langchain_core.messages import HumanMessage
from src.core.agent import create_agent_executor
from src.database.repository import ConversationDB
from src.ui.menu import show_conversation_menu
from src.ui.stream_handler import process_agent_stream


def run_cli():
    """
    Function that starts the CLI application.
    """
    print("=" * 60)
    print("🤖 Assistente IA com Function Calling")
    print("=" * 60)
    print("\nEste assistente pode ajudar você com:")
    print("  • Informações sobre países")
    print("  • Taxas de câmbio")
    print("=" * 60)
    print()
    
    # Cria o agente
    try:
        agent = create_agent_executor()
        print("✅ Assistente inicializado com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao inicializar assistente: {e}")
        sys.exit(1)
    
    # Inicializa o banco de dados
    db = ConversationDB()
    
    # Mostra menu de conversas no início
    conversation_history, current_conv_id = show_conversation_menu(db)
    
    if conversation_history:
        print(f"\n✅ Conversa carregada! ({len(conversation_history)} mensagem(ns) no histórico)")
    else:
        print("\n💬 Nova conversa iniciada!")
    
    print("\nDigite 'sair' ou 'quit' para encerrar.")
    print("Digite 'limpar' para limpar o histórico da conversa.")
    print("=" * 60)
    print()
    
    # Loop principal de interação
    while True:
        try:
            # Lê a pergunta do usuário
            user_input = input("\n\n👤 Você: ").strip()
            
            # Verifica se o usuário quer sair
            if user_input.lower() in ['sair', 'quit', 'exit', 'q']:
                print("\n👋 Até logo!")
                break
            
            # Verifica se o usuário quer limpar o histórico
            if user_input.lower() in ['limpar', 'clear', 'reset']:
                conversation_history = []
                # Remove apenas a conversa atual do banco de dados, se existir
                if current_conv_id is not None:
                    try:
                        db.delete_conversation(current_conv_id)
                        print("\n🧹 Histórico da conversa limpo!")
                    except Exception as e:
                        print(f"\n🧹 Histórico da conversa limpo localmente! (Aviso: não foi possível remover do banco: {e})")
                else:
                    print("\n🧹 Histórico da conversa limpo!")
                current_conv_id = None  # Reseta o ID para criar nova conversa
                continue
            
            # Ignora entradas vazias
            if not user_input:
                continue

            # Identifica como primeira mensagem do histórico, se ela não existir
            first_message = user_input if not conversation_history else None
            
            # Adiciona a mensagem do usuário ao histórico
            user_message = HumanMessage(content=user_input)
            conversation_history.append(user_message)
            
            # Processa o streaming do agente
            conversation_history = process_agent_stream(agent, conversation_history)

            # Salva ou atualiza o histórico no banco de dados
            if conversation_history:
                try:
                    if current_conv_id:
                        # Atualiza conversa existente
                        db.update_conversation(current_conv_id, conversation_history)
                    else:
                        # Cria nova conversa e salva o ID
                        current_conv_id = db.save_conversation(first_message, conversation_history)
                except Exception as e:
                    print(f"\n\n⚠️ Aviso: Não foi possível salvar no banco de dados: {e}")

        except KeyboardInterrupt:
            # Trata Ctrl+C graciosamente
            print("\n\n👋 Interrompido pelo usuário. Até logo!")
            break
        except Exception as e:
            print(f"\n❌ Erro: {e}")
            print("Tente novamente ou digite 'sair' para encerrar.")

