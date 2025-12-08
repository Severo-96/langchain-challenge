"""
Handler for processing agent message streaming.
"""

from typing import List

from langchain_core.messages import (
    AIMessage,
    AIMessageChunk,
    HumanMessage,
    ToolMessage,
)


def process_agent_stream(agent, conversation_history: List) -> List:
    """
    Processes agent streaming and updates conversation history.
    
    Args:
        agent: Configured LangChain agent
        conversation_history: Current conversation history
        
    Returns:
        Updated history with agent messages
    """
    # Execute agent and get complete response
    print("\n🤖 Assistente: Analisando...\n", end="", flush=True)

    # List of tool contents to avoid duplication
    tool_content_list = set()
    # Flag to skip line on first message of stream mode "messages"
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
                    # Check if tool content is in set, avoiding screen duplication
                    if tool_content not in tool_content_list:
                        print(f" - Buscando: {tool_content}")
                        tool_content_list.add(tool_content)

            elif 'model' in chunk:
                model_message = chunk['model'].get('messages', [])[0]
                if isinstance(model_message, AIMessage):
                    model_content = model_message.content
                    # Check if content exists and is not empty,
                    # to add to new messages list
                    if model_content and str(model_content).strip():
                        conversation_history.append(model_message)
        
        if stream_mode == "messages":
            message_chunk = chunk[0]
            # Check if it's AIMessageChunk and has content
            if isinstance(message_chunk, AIMessageChunk):
                if (content := message_chunk.content):
                    # Skip line on first interaction
                    if first_message_chunk:
                        print("\n", end="", flush=True)
                        first_message_chunk = False
                    print(content, end="", flush=True)

    return conversation_history

