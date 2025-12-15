"""
Pytest configuration and shared fixtures.
"""
import sqlite3
import tempfile
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.sqlite import SqliteSaver

from src.core.config import Settings
from src.database.repository import ConversationDB


@pytest.fixture
def temp_db_path():
    """Creates a temporary database file for testing."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = Path(tmp.name)
    yield db_path
    # Cleanup
    if db_path.exists():
        db_path.unlink()


@pytest.fixture
def temp_checkpoint_db_path():
    """Creates a temporary checkpoint database file for testing."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = Path(tmp.name)
    yield db_path
    # Cleanup
    if db_path.exists():
        db_path.unlink()


@pytest.fixture
def test_settings(temp_db_path, temp_checkpoint_db_path):
    """Creates test settings with temporary database paths."""
    return Settings(
        openai_api_key="test-api-key",
        conversation_db_path=temp_db_path,
        checkpoint_db_path=temp_checkpoint_db_path,
        model_name="gpt-4o-mini",
        temperature=0.5
    )


@pytest.fixture
def conversation_db(temp_db_path, monkeypatch):
    """Creates a ConversationDB instance with temporary database."""
    # Mock settings to use temp database
    test_settings = Settings(
        openai_api_key="test-api-key",
        conversation_db_path=temp_db_path,
        checkpoint_db_path=Path("data/test_checkpoints.db"),
        model_name="gpt-4o-mini",
        temperature=0.5
    )
    monkeypatch.setattr("src.database.repository.settings", test_settings)
    return ConversationDB()


@pytest.fixture
def checkpointer(temp_checkpoint_db_path):
    """Creates a SqliteSaver instance with temporary database."""
    conn = sqlite3.connect(str(temp_checkpoint_db_path), check_same_thread=False)
    return SqliteSaver(conn)


@pytest.fixture
def mock_llm():
    """Creates a mock ChatOpenAI instance."""
    llm = MagicMock(spec=ChatOpenAI)
    llm.invoke.return_value = MagicMock(content="Test summary response")
    return llm


@pytest.fixture
def sample_messages():
    """Creates sample messages for testing."""
    return [
        HumanMessage(content="Hello"),
        AIMessage(content="Hi! How can I help?"),
        HumanMessage(content="What is the capital of Brazil?"),
        AIMessage(content="The capital of Brazil is Brasília."),
    ]


@pytest.fixture
def many_messages():
    """Creates 101 messages to trigger summarization."""
    messages = []
    for i in range(101):
        if i % 2 == 0:
            messages.append(HumanMessage(content=f"Question {i//2}"))
        else:
            messages.append(AIMessage(content=f"Answer {i//2}"))
    return messages

