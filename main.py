"""
Entry point for the application.
Interface CLI (Command Line Interface) to interact with the assistant.
"""

from langchain_setup import create_agent_executor
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
import sys


def main():
    """
    Função principal que inicia a aplicação CLI.
    """
    print("=" * 60)
    print("🤖 Assistente IA com Function Calling")
    print("=" * 60)
    print("\nEste assistente pode ajudar você com:")
    print("  • Informações sobre países")
    print("  • Taxas de câmbio")
    print("\nDigite 'sair' ou 'quit' para encerrar.")
    print("Digite 'limpar' para limpar o histórico da conversa.")
    print("=" * 60)
    print()
    
    # Cria o agente
    try:
        agent = create_agent_executor()
        print("✅ Assistente inicializado com sucesso!\n")
    except Exception as e:
        print(f"❌ Erro ao inicializar assistente: {e}")
        print("\nVerifique se:")
        print("  1. O arquivo .env existe e contém OPENAI_API_KEY")
        print("  2. A chave da OpenAI é válida")
        print("  3. As dependências estão atualizadas (pip install -r requirements.txt)")
        sys.exit(1)
    
    # Histórico de mensagens - mantém o contexto da conversa
    conversation_history = []
    
    # Loop principal de interação
    while True:
        try:
            # Lê a pergunta do usuário
            user_input = input("\n👤 Você: ").strip()
            
            # Verifica se o usuário quer sair
            if user_input.lower() in ['sair', 'quit', 'exit', 'q']:
                print("\n👋 Até logo!")
                break
            
            # Verifica se o usuário quer limpar o histórico
            if user_input.lower() in ['limpar', 'clear', 'reset']:
                conversation_history = []
                print("\n🧹 Histórico da conversa limpo!")
                continue
            
            # Ignora entradas vazias
            if not user_input:
                continue
            
            # Adiciona a mensagem do usuário ao histórico
            user_message = HumanMessage(content=user_input)
            conversation_history.append(user_message)
            
            # Executa o agente e obtém a resposta completa
            print("\n🤖 Assistente: Analisando...\n", end="", flush=True)

            # Lista de conteúdos das tools para evitar duplicação na tela
            tool_content_list = set()
            for chunk in agent.stream(
                {"messages": conversation_history},
                stream_mode="updates"
            ):
                if 'tools' in chunk:
                    tool_message = chunk['tools']['messages'][0]
                    if isinstance(tool_message, ToolMessage):
                        tool_content = tool_message.content.split(':')[0]
                        # Verifica se o conteúdo da tool já foi impresso, evitando duplicação na tela
                        if tool_content not in tool_content_list:
                            print(f" - Buscando: {tool_content}")
                            tool_content_list.add(tool_content)

                elif 'model' in chunk:
                    model_message = chunk['model']['messages'][0]
                    if isinstance(model_message, AIMessage):
                        model_content = model_message.content
                        # Verifica se content existe e não está vazio, e então adiciona a mensagem ao histórico
                        if model_content and str(model_content).strip():
                            print(f"\n{model_content}")
                            conversation_history.append(model_message)

                else:
                    print(f"\nDesculpe, não consegui processar sua pergunta.\n")
                    print(f"\n\n{chunk}\n\n")
            
        except KeyboardInterrupt:
            # Trata Ctrl+C graciosamente
            print("\n\n👋 Interrompido pelo usuário. Até logo!")
            break
        except Exception as e:
            print(f"\n❌ Erro: {e}")
            print("Tente novamente ou digite 'sair' para encerrar.")


if __name__ == "__main__":
    main()
