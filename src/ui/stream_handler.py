"""
Handler for processing agent message streaming.
"""

from typing import List
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, AIMessageChunk


def process_agent_stream(agent, conversation_history: List) -> List:
    """
    Processes agent streaming and updates conversation history.
    
    Args:
        agent: Configured LangChain agent
        conversation_history: Current conversation history
        
    Returns:
        Updated history with agent messages
    """
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

    return conversation_history

