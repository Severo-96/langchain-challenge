"""
Entry point for the application.
Interface CLI (Command Line Interface) to interact with the assistant.
"""

from langchain_setup import create_agent_executor
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, AIMessageChunk
from database import ConversationDB
from typing import Optional, Tuple, List
import questionary
import sys


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

def main():
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
      
      # Executa o agente e obtém a resposta completa
      print("\n🤖 Assistente: Analisando...\n", end="", flush=True)

      # Lista de conteúdos das tools para evitar duplicação
      tool_content_list = set()
      # Flag para pular linha na primeira mensagem do stream mode "messages"
      first_message_chunk = True
      
      for stream_mode, chunk in agent.stream(
        {"messages": conversation_history},
        stream_mode=["updates", "messages"]
      ):
        if stream_mode == "updates":
          if 'tools' in chunk:
            tool_message = chunk['tools'].get('messages', [])[0]
            if isinstance(tool_message, ToolMessage):
              tool_content = tool_message.content.split(':')[0]
              # Verifica se o conteúdo da tool esta no set, evitando duplicação na tela
              if tool_content not in tool_content_list:
                print(f" - Buscando: {tool_content}")
                tool_content_list.add(tool_content)

          elif 'model' in chunk:
            model_message = chunk['model'].get('messages', [])[0]
            if isinstance(model_message, AIMessage):
              model_content = model_message.content
              # Verifica se content existe e não está vazio, para adicionar a lista de novas mensagens
              if model_content and str(model_content).strip():
                conversation_history.append(model_message)
        
        if stream_mode == "messages":
          message_chunk = chunk[0]
          # Verifica se é AIMessageChunk e tem conteúdo
          if isinstance(message_chunk, AIMessageChunk):
            if (content := message_chunk.content):
              # Pula linha na primeira interação
              if first_message_chunk:
                print("\n", end="", flush=True)
                first_message_chunk = False
              print(content, end="", flush=True)

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

if __name__ == "__main__":
  main()
