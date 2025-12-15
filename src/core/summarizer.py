"""
Module for summarizing conversation history when it gets too long.
"""

from textwrap import dedent

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.sqlite import SqliteSaver

from src.core.config import settings

MAX_MESSAGES_BEFORE_SUMMARIZE = 100
MAX_SUMMARY_TOKENS = 500  # Maximum tokens for summary response


def summarize_conversation(
    checkpointer: SqliteSaver,
    thread_id: str,
    llm: ChatOpenAI | None = None
) -> bool:
    """
    Summarizes all messages if conversation exceeds limit.
    All messages are summarized into a single summary message.
    
    Args:
        checkpointer: Checkpoint saver instance
        thread_id: Thread ID for checkpoint
        llm: Language model for summarization. If None, creates a new instance.
        
    Returns:
        True if summarization was performed, False otherwise
    """
    try:
        # Get current checkpoint
        # Ensure thread_id is string for checkpoint and include checkpoint_ns
        config = RunnableConfig(configurable={"thread_id": thread_id, "checkpoint_ns": ""})
        checkpoint = checkpointer.get(config)
        if not checkpoint:
            return False
        
        # Extract messages from checkpoint
        channel_values = checkpoint.get("channel_values", {})
        messages = channel_values.get("messages", [])

        # Check if summarization is needed
        if len(messages) <= MAX_MESSAGES_BEFORE_SUMMARIZE:
            return False
        
        print("\n\n📝 Resumindo mensagens antigas...", end="", flush=True)
        
        # Summarize all messages
        if llm is None:
            llm = ChatOpenAI(
                model=settings.model_name,
                temperature=0.3,  # Lower temperature for more consistent summaries
                api_key=settings.openai_api_key
            )
        
        summary_text = _create_summary(messages, llm)
        
        # Create summary message - this replaces all previous messages
        summary_message = AIMessage(
            content=dedent(f"""\
                [Resume of previous conversation - {len(messages)} messages summarized]
                
                {summary_text}
            """)
        )
        
        # Replace all messages with just the summary
        summarized_messages = [summary_message]
        
        # Update checkpoint with summarized messages
        checkpoint["channel_values"]["messages"] = summarized_messages
        
        # Prepare metadata and channel versions for put()
        metadata = {
            "source": "summarizer",
            "step": 1,
            "writes": {"messages": len(summarized_messages)}
        }
        # Extract channel_versions from checkpoint if available, otherwise use empty dict
        new_versions = checkpoint.get("channel_versions", {})
        
        # Save updated checkpoint with required parameters
        checkpointer.put(config, checkpoint, metadata, new_versions)
        
        print(f" ✅ ({len(messages)} mensagens resumidas)\n")
        return True
        
    except Exception as e:
        print(f"\n⚠️ Aviso: Erro ao resumir conversa: {e}\n")
        return False

def _create_summary(messages: list[BaseMessage], llm: ChatOpenAI) -> str:
    """
    Creates a summary of old messages using the LLM.
    
    Args:
        messages: List of messages to summarize
        llm: Language model to use for summarization
        
    Returns:
        Summary text
    """
    # Build conversation text with user and assistant messages
    conversation_parts = []
    for msg in messages:
        if isinstance(msg, HumanMessage):
            conversation_parts.append(f"User: {msg.content}")
        elif isinstance(msg, AIMessage):
            conversation_parts.append(f"Assistant: {msg.content}")
    
    conversation_text = "\n".join(conversation_parts)
    
    # Create summary prompt
    summary_prompt = dedent(f"""\
        You are a system that summarizes conversations for long-term memory.

        Summarize the conversation below in the primary language used by the user
        (ignore system or tool language).
        The summary will be used to maintain context across future interactions.
        This is a summary, not a transcript.

        IMPORTANT: Keep the summary within approximately {MAX_SUMMARY_TOKENS} tokens.
        Be concise and prioritize the most important information.

        Guidelines:
        - Be concise and objective
        - Preserve key decisions, facts, numbers, and constraints
        - Keep only information useful for future context
        - Do NOT include greetings, filler text, or redundant details
        - Do NOT invent information

        Output format (follow strictly):
        - Main topics:
        - Important facts:
        - Decisions or conclusions:
        - Open questions or pending actions (if any):

        Conversation:
        {conversation_text}
    """)

    # Get summary from LLM
    response = llm.invoke(summary_prompt)
    summary = response.content if hasattr(response, 'content') else str(response)
    
    return summary

