"""
Handler for processing agent message streaming.
"""

from typing import Any, Dict, List, Set

from langchain_core.messages import (
    AIMessage,
    AIMessageChunk,
    BaseMessage,
    ToolMessage,
)


def process_agent_stream(
    agent: Any, conversation_history: List[BaseMessage]
) -> List[BaseMessage]:
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

    tool_content_list: Set[str] = set()
    first_message_chunk = True
    
    for stream_mode, chunk in agent.stream(
        {"messages": conversation_history},
        stream_mode=["updates", "messages"]
    ):
        if stream_mode == "updates":
            _process_updates_chunk(chunk, conversation_history, tool_content_list)
        elif stream_mode == "messages":
            first_message_chunk = _process_messages_chunk(
                chunk, first_message_chunk
            )

    return conversation_history


def _process_updates_chunk(
    chunk: Dict[str, Any],
    conversation_history: List[BaseMessage],
    tool_content_list: Set[str]
) -> None:
    """
    Processes 'updates' stream mode chunks.
    
    Args:
        chunk: Stream chunk from agent
        conversation_history: Current conversation history to update
        tool_content_list: Set of tool contents to track duplicates
    """
    if 'tools' in chunk:
        _handle_tool_message(chunk['tools'], tool_content_list)
    elif 'model' in chunk:
        _handle_model_message(chunk['model'], conversation_history)


def _process_messages_chunk(
    chunk: List[AIMessageChunk],
    first_message_chunk: bool
) -> bool:
    """
    Processes 'messages' stream mode chunks.
    
    Args:
        chunk: Message chunk from agent
        first_message_chunk: Flag indicating if this is the first chunk
        
    Returns:
        Updated first_message_chunk flag
    """
    message_chunk = chunk[0]
    
    if isinstance(message_chunk, AIMessageChunk):
        if (content := message_chunk.content):
            if first_message_chunk:
                print("\n", end="", flush=True)
                first_message_chunk = False
            print(content, end="", flush=True)
    
    return first_message_chunk


def _handle_tool_message(
    tools_chunk: Dict[str, Any], tool_content_list: Set[str]
) -> None:
    """
    Handles tool messages from stream updates.
    
    Args:
        tools_chunk: Tools chunk from stream
        tool_content_list: Set to track and prevent duplicate tool prints
    """
    messages = tools_chunk.get('messages', [])
    if not messages:
        return
    
    tool_message = messages[0]
    if not isinstance(tool_message, ToolMessage):
        return
    
    tool_content = tool_message.content.split(':')[0]
    if tool_content not in tool_content_list:
        print(f" - Buscando: {tool_content}")
        tool_content_list.add(tool_content)


def _handle_model_message(
    model_chunk: Dict[str, Any], conversation_history: List[BaseMessage]
) -> None:
    """
    Handles model messages from stream updates.
    
    Args:
        model_chunk: Model chunk from stream
        conversation_history: Conversation history to update
    """
    messages = model_chunk.get('messages', [])
    if not messages:
        return
    
    model_message = messages[0]
    if not isinstance(model_message, AIMessage):
        return
    
    model_content = model_message.content
    if model_content and str(model_content).strip():
        conversation_history.append(model_message)

