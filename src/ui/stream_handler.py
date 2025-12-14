"""
Handler for processing agent message streaming.
"""

from typing import Any, Dict, List, Set

from langchain_core.messages import (
    AIMessage,
    AIMessageChunk,
    ToolMessage,
)
from langchain_core.runnables import RunnableConfig


def process_agent_stream(
    agent: Runnable,
    user_message: Any,
    thread_id: str
) -> None:
    """
    Processes agent streaming with checkpoint support.
    
    Args:
        agent: Configured LangChain agent with checkpointer
        user_message: User message to send to agent
        thread_id: Thread ID for checkpoint
    """
    # Execute agent and get complete response
    print("\n🤖 Assistente: Analisando...\n", end="", flush=True)

    tool_content_list: Set[str] = set()
    first_message_chunk = True
    
    # Stream with thread_id - checkpoint automatically loads/saves history
    for stream_mode, chunk in agent.stream(
        {"messages": [user_message]},
        stream_mode=["updates", "messages"],
        config=RunnableConfig(configurable={"thread_id": thread_id, "checkpoint_ns": ""})
    ):
        if stream_mode == "updates":
            _process_updates_chunk(chunk, tool_content_list)
        elif stream_mode == "messages":
            first_message_chunk = _process_messages_chunk(
                chunk, first_message_chunk
            )


def _process_updates_chunk(
    chunk: Dict[str, Any],
    tool_content_list: Set[str]
) -> None:
    """
    Processes 'updates' stream mode chunks.
    
    Args:
        chunk: Stream chunk from agent
        tool_content_list: Set of tool contents to track duplicates
    """
    if 'tools' in chunk:
        _handle_tool_message(chunk['tools'], tool_content_list)


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

