"""
Entry point for the application.
Interface CLI (Command Line Interface) to interact with the assistant.
"""

from src.database.repository import ConversationDB
from src.ui.cli import run_cli


def main():
    """Main application entry point."""
    db = ConversationDB()
    run_cli(db)


if __name__ == "__main__":
    main()

