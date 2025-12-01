"""
Ponto de entrada principal da aplicação.
Interface CLI (Command Line Interface) simples para interagir com o assistente.
"""

from langchain_setup import create_agent_executor
from langchain_core.messages import HumanMessage, AIMessage
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
            print("\n🤖 Assistente: ", end="", flush=True)
            response = agent.invoke({"messages": conversation_history})
            
            # Processa a resposta do agente
            if isinstance(response, dict) and "messages" in response:
                messages = response["messages"]
                if messages and len(messages) > 0:
                    # Atualiza o histórico com todas as mensagens
                    conversation_history = messages
                    
                    # Encontra a última mensagem do assistente
                    last_message = None
                    for msg in reversed(messages):
                        if isinstance(msg, AIMessage):
                            last_message = msg
                            break
                    
                    # Exibe a resposta
                    if last_message:
                        if hasattr(last_message, "content"):
                            content = last_message.content
                            if content:
                                print(content)

            else:
                output = str(response) if response else "Desculpe, não consegui processar sua pergunta."
                print(output)
                conversation_history.append(AIMessage(content=output))
            
        except KeyboardInterrupt:
            # Trata Ctrl+C graciosamente
            print("\n\n👋 Interrompido pelo usuário. Até logo!")
            break
        except Exception as e:
            print(f"\n❌ Erro: {e}")
            print("Tente novamente ou digite 'sair' para encerrar.")


if __name__ == "__main__":
    main()
