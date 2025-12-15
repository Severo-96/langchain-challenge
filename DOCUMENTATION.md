# 📚 Technical Documentation

Complete documentation about the development process, technologies used, and main challenges faced in this project.


## 🎯 Project Overview

This project is an **intelligent assistant with Function Calling** that uses Large Language Models (LLMs) to answer questions about countries and exchange rates. The assistant maintains conversation history, allows interaction via command line, and uses external tools to fetch real-time information. The project is currently focused on single terminal use, but has space to develop and grow.

### Main Features

- **AI Conversation**: Natural interaction with GPT-4o-mini model via LangChain
- **Function Calling**: The model automatically decides when to use external tools
- **Information Search**: Integration with external APIs (REST Countries and ExchangeRate)
- **Persistence**: Conversation history managed via LangGraph Checkpoints (SQLite)
- **Streaming**: Real-time responses, token by token
- **CLI Interface**: Interactive menu to manage conversations
- **Conversation Summarization**: Automatic summarization when conversations exceed 100 messages
- **Testing**: Comprehensive test suite with pytest


## 🛠️ Technologies Used

### Core Technologies

#### 1. **Python 3.11+**
- **Why it was chosen**: Python is the standard language for AI application and agent development. It offers a vast library ecosystem, robust type support, and clear syntax.
- **How it is used**: The entire application is written in Python, from business logic to CLI interface.
- **Important concepts applied**:
  - **Type Hints**: Type annotations for better readability and error detection
  - **Pathlib**: Modern file path handling
  - **Context Managers**: Automatic resource management (like database connections)

#### 2. **LangChain 1.0+ & LangGraph**
- **What it is**: Specialized framework for building LLM applications. Simplifies agent creation, tool integration, and message handling.
- **Why it was chosen**: LangChain abstracts the complexity of working with LLMs, offering consistent and powerful APIs.
- **Main features used**:
  - `create_agent()`: Agent creation with function calling support
  - `StructuredTool`: Tool definition with automatic parameter validation
  - **Streaming**: Real-time responses using two stream modes (`updates` and `messages`)
  - **Message Types**: `HumanMessage`, `AIMessage`, `ToolMessage`, `AIMessageChunk`
  - **Checkpoints**: LangGraph checkpoint system for conversation state persistence
- **How it works in the project**: The agent receives user messages, decides when to call external tools, executes the calls, and returns formatted responses. Checkpoints automatically save and restore conversation state.

#### 3. **OpenAI API (GPT-4o-mini)**
- **What it is**: OpenAI API that provides access to large-scale language models.
- **Model chosen**: `gpt-4o-mini` - more economical version of GPT-4, maintaining good quality
- **Configuration**:
  - **Temperature**: 0.5 (balance between creativity and consistency)
  - **Function Calling**: Automatically enabled - the model decides when to use tools
- **Why this model**: Excellent cost-benefit for this type of application, with full function calling support and adequate speed.

#### 4. **SQLite & LangGraph Checkpoints**
- **What it is**: Embedded relational database, no separate server required.
- **Why it was chosen**: 
  - Simplicity: no server configuration required
  - Portability: database is a single file
  - Zero configuration: works immediately
- **How it is used**: 
  - **Checkpoints**: Full conversation state (messages, tool calls, metadata) is automatically saved by LangGraph's `SqliteSaver` in `checkpoints.db`
  - **Metadata**: Conversation metadata (ID, first message, timestamps) is stored in `conversations.db` for quick listing and selection
  - **Thread ID**: Each conversation has a unique `thread_id` that links metadata to checkpoint data

#### 5. **Pydantic**
- **What it is**: Library for data validation using Python type annotations.
- **Why it was chosen**: Perfect integration with LangChain (recommended by the framework), automatic validation, and clear error messages.
- **How it is used**: Schemas are defined to validate tool parameters before calling external APIs.

#### 6. **Requests**
- **What it is**: HTTP library for making calls to external APIs.
- **How it is used**: HTTP clients fetch country information and exchange rates.
- **Integrated APIs**:
  - **REST Countries API**: Free, no authentication required
  - **ExchangeRate-API**: Free with basic tier, no authentication required
- **Error handling**: 10-second timeout and network exception handling.

#### 7. **Questionary**
- **What it is**: Library for creating interactive terminal prompts.
- **Why it was chosen**: Better user experience and supports arrow key navigation.
- **How it is used**: Menu for selecting previous conversations on startup.

#### 8. **Python-dotenv**
- **What it is**: Library for loading environment variables from `.env` files.
- **Why it was chosen**: Security (prevents committing API keys) and easy configuration.
- **How it is used**: `OPENAI_API_KEY` and other settings are loaded from the `.env` file.

#### 9. **LangGraph Checkpoint System**
- **What it is**: Built-in persistence system for LangGraph agents that saves and restores conversation state.
- **Why it was chosen**: Eliminates manual message serialization, provides automatic state management, and ensures full conversation history preservation.
- **How it is used**:
  - `SqliteSaver`: Stores full conversation state (messages, tool calls, metadata) in SQLite
  - `thread_id`: Unique identifier linking conversations to their checkpoint data
  - `RunnableConfig`: Passes `thread_id` and `checkpoint_ns` to agent for automatic state management
  - Automatic save/restore: Checkpoint system handles persistence without manual intervention
- **Benefits**:
  - No manual serialization needed
  - Full state preservation (all message types, tool calls, metadata) 
  - Automatic restoration when resuming conversations
  - Thread-based isolation (each conversation has its own state)

### Development Tools

- **Docker & Docker Compose**: Containerization for consistent environment, supports running tests
- **Type Hints**: Type annotations throughout the code
- **pytest**: Testing framework with fixtures and mocking support
- **pytest-cov**: Code coverage reporting
- **pytest-mock**: Mocking utilities for testing


## 🏗️ Architecture and Design

### Modular Structure

The project follows a clear modular architecture, separating responsibilities:

```
src/
├── core/          # Business logic and configuration
│   ├── agent.py   # LangChain agent creation and configuration
│   ├── config.py  # Configuration and environment variable management
│   ├── schemas.py # Pydantic schemas for validation
│   └── summarizer.py # Conversation summarization logic
├── api/           # External API integrations
│   └── clients/   # HTTP clients for each API
├── tools/         # LangChain tools (API wrappers)
├── database/      # Data persistence
│   └── repository.py  # SQLite CRUD operations for metadata
└── ui/            # User interface
    ├── cli.py            # Main CLI logic
    ├── menu.py           # Conversation selection menu
    └── stream_handler.py # Streaming processing
```

**Why this structure?**
- **Separation of concerns**: Each module has a clear function
- **Easier testing**: Each component can be tested in isolation
- **Scalability**: Easy to add new tools or features
- **Maintainability**: Organized code is easier to understand and modify

### Execution Flow

1. **Initialization**:
   - Loads configuration from `.env`
   - Initializes databases (creates tables if they don't exist)
   - Creates SqliteSaver for checkpoint persistence
   - Shows menu to select or create conversation

2. **Agent Creation**:
   - Configures OpenAI model
   - Creates tools (country_tool, exchange_tool)
   - Defines system prompt with instructions
   - Attaches checkpointer to agent for state persistence

3. **Message Processing**:
   ```
   User → CLI → LangChain Agent (with checkpointer) → [Decision: use tool?]
                                                              ↓ Yes
                                                        Tool → External API → Response
                                                              ↓ No
                                                        Direct model response
   ```
   - Checkpoint automatically loads previous conversation state via `thread_id`
   - New messages are added to conversation state
   - Checkpoint automatically saves state after processing

4. **Streaming**:
   - `updates` mode: Captures tool calls and model messages
   - `messages` mode: Streams token-by-token final response
   - Both processed simultaneously for better UX
   - Uses `RunnableConfig` with `thread_id` for checkpoint integration

5. **Persistence**:
   - **Checkpoints**: LangGraph automatically saves full conversation state (messages, tool calls, metadata) after each interaction
   - **Metadata**: Conversation metadata (ID, first message, timestamps) saved separately for quick access
   - **Thread ID**: Links metadata to checkpoint data, automatically generated via SQLite trigger
   - **No manual serialization**: Checkpoint system handles all message persistence automatically

6. **Summarization** (when needed):
   - After each interaction, checks if conversation exceeds 100 messages
   - If exceeded, summarizes all messages into single summary message
   - Updates checkpoint with summarized version
   - Maintains conversation continuity while reducing token usage


## 🎯 Main Challenges Faced

### 1. **Learning Python from Scratch**

**Context**: This project was developed during the Python learning process.

**Specific challenges**:
- Language syntax and structure
- Type system and type hints
- Module and package management

**Solutions and learnings**:
- **Practical learning**: Implementing features while studying
- **Official documentation**: Constant consultation of Python documentation
- **Type hints**: Forced understanding of types
- **Code review**: Reviewing and refactoring code iteratively

**Impact on project**: Added development time, but resulted in better understanding of the language.

### 2. **LangChain Message Persistence - Checkpoint System**

**Problem**: LangChain messages are complex objects that need to be stored persistently across application restarts.

**Solution - LangGraph Checkpoints**:
- **SqliteSaver**: Uses LangGraph's built-in checkpoint system to automatically persist conversation state
- **Full state preservation**: Saves all messages, tool calls, and metadata automatically
- **Thread-based**: Each conversation has a unique `thread_id` that links metadata to checkpoint data
- **Automatic restoration**: When resuming a conversation, checkpoint system automatically loads previous state

**Implementation details**:
- Two databases: `conversations.db` (metadata) and `checkpoints.db` (full state)
- `thread_id` automatically generated via SQLite trigger: `'t' || conversation_id`
- `RunnableConfig` with `thread_id` and `checkpoint_ns` passed to agent.stream()
- No manual serialization needed - checkpoint system handles everything

**Why this solution**: Leverages LangGraph's built-in persistence, eliminating manual serialization complexity and ensuring full state preservation.

### 3. **Duplicate Streaming (Dual Stream Mode)**

**Problem**: LangChain offers two stream modes that can cause output duplication:
- `updates`: Captures everything (tool calls, model messages)
- `messages`: Streams token-by-token final response

**Challenge**: Process both simultaneously without showing duplicate information to the user.

**Strategy**:
- `updates`: Shows only when tools are called ("Searching: ..."), and to select which data to be saved
- `messages`: Shows response token by token
- Set to avoid duplicate tool messages

**Why both modes**: `updates` provides control over tool calls, as well as control on which data to save on database, 
`messages` enables smooth response streaming.

### 4. **Function Calling - Model Decision**

**Challenge**: Ensure the LLM correctly identifies when to use tools and with what parameters.

**Strategy**:

1. **Detailed tool descriptions**: Comprehensive descriptions explain what each tool does, when to use it, and what it returns, helping the LLM understand when to call each tool.

2. **Pydantic schemas for validation**: Pydantic models (`CountryInfoInput`, `ExchangeRateInput`) validate parameters and provide field descriptions that guide the LLM on expected parameter formats.

3. **Clear system prompt**: The system prompt lists available capabilities and instructs the model to use tools when necessary, providing context for decision-making.

**Learning**: Function calling is powerful, but requires clear descriptions and examples to work well.

### 5. **Database Path Management**

**Problem**: Ensure the database directory exists in different environments (local, Docker).

**Solution**:
```python
self.db_path = Path(db_path)
self.db_path.parent.mkdir(parents=True, exist_ok=True)
```

**Why it works**:
- `Path` is cross-platform (works on Windows, Linux, Mac)
- `mkdir(parents=True, exist_ok=True)` creates the entire necessary hierarchy
- Does not fail if the directory already exists

**Learning**: Directories should always be checked/created before creating files.

### 6. **Docker with Interactive Application**

**Challenge**: CLI needs interactive input/output in Docker, which is not trivial.

**Solutions**:

1. **Docker Compose configuration**: The `docker-compose.yml` file includes `stdin_open: true` to keep standard input open and `tty: true` to allocate a pseudo-TTY. These settings are essential for enabling interactive terminal input and formatted output within the container.

2. **Execution method**: The application is executed using `docker compose exec`, which allows running commands in an already running container. This approach maintains the interactive session and enables proper input/output handling.

3. **Container lifecycle**: The container is configured to stay running using a command that keeps it alive (like `tail -f /dev/null`). This allows multiple interactive sessions without restarting the container each time.

**Why necessary**: Docker by default is not interactive. These configurations enable user input and formatted output in the container, making it possible to use CLI applications that require real-time interaction.

### 7. **Error Handling in External APIs**

**Challenge**: External APIs can fail, timeout, or return unexpected data.

**Error handling strategy**:

1. **Try/except in all calls**: All API calls are wrapped in try/except blocks to catch network exceptions and timeouts.

2. **Consistent response format**: All API responses follow a consistent format with a `success` boolean and either `data` or `error` fields.

3. **Configured timeout**: 10-second timeout is configured to avoid infinite wait times.

4. **HTTP status validation**: HTTP status codes are validated before processing responses.

**Why important**: External APIs are failure points. Robust error handling improves the user experience.

### 8. **Type Safety with LangChain Messages**

**Challenge**: LangChain uses multiple message types that need to be handled differently.

**Why necessary**: Each type has a different structure. Type checking ensures each case is handled correctly.

**Learning**: Type hints and `isinstance()` are essential for robust code with complex libraries.

### 9. **Environment Variable Management**

**Challenge**: Different environments (local, Docker) need consistent configuration.

**Implemented solution**:

1. **`.env.example`**: Template with all necessary variables
2. **`python-dotenv`**: Automatically loads from `.env`
3. **Settings class**: Validation and default values
4. **Clear documentation**: README explains how to configure

**Benefits**:
- Security: keys are not committed to code
- Flexibility: easy to change configurations
- Validation: clear errors if something is missing

### 10. **Conversation Summarization**

**Challenge**: Long conversations can exceed LLM context window limits, causing errors or increased costs.

**Solution**:
- **Automatic detection**: When conversation reaches 100 messages, summarization is triggered
- **Full summarization**: All messages are summarized into a single `AIMessage` with key information
- **Checkpoint update**: Summarized conversation replaces all previous messages in checkpoint
- **Token limit**: Summary is limited to 500 tokens via `max_tokens` parameter
- **LLM reuse**: Uses the same LLM instance as the agent for consistency

**Implementation**:
- `summarize_conversation()` function checks message count after each interaction
- Uses structured prompt to create concise summary preserving important information
- Updates checkpoint with summarized version, maintaining conversation continuity

**Why important**: Prevents context window overflow, reduces token usage, and maintains conversation quality in long-running sessions.

### 11. **Testing Infrastructure**

**Challenge**: Ensure code quality and prevent regressions as the project grows.

**Solution**:
- **pytest framework**: Comprehensive test suite covering all major components
- **Fixtures**: Shared test setup via `conftest.py` (temporary databases, mocks)
- **Dependency Injection**: Tests use dependency injection for easy mocking
- **Coverage reporting**: `pytest-cov` tracks code coverage (currently ~44%)
- **CI/CD ready**: GitHub Actions workflow for automated testing

**Test coverage**:
- Repository operations (CRUD, thread_id generation)
- Agent creation and configuration
- API clients (with mocked HTTP calls)
- Tools and schemas
- CLI interface and menu
- Stream handler
- Summarization logic
- Configuration management

**Benefits**:
- Catches bugs early
- Enables confident refactoring
- Documents expected behavior
- Improves code quality

## 🔄 Development Process

### Phase 1: Initial Prototyping
- Created basic structure with single files
- Implemented core functionality (agent + one tool)
- Tested basic integration with OpenAI

### Phase 2: Feature Expansion
- Added second tool (exchange rates)
- Implemented conversation persistence
- Added conversation selection menu

### Phase 3: UX Improvements
- Implemented response streaming
- Improved error handling
- Added special commands (exit, clear)

### Phase 4: Refactoring and Organization
- Reorganized into modular structure
- Separated responsibilities (API clients, tools, UI)
- Added type hints throughout the code
- Improved documentation and docstrings

### Phase 5: Containerization
- Created Dockerfile
- Configured docker-compose
- Tested in isolated environment

### Phase 6: Checkpoint Integration
- Integrated LangGraph checkpoint system
- Replaced manual message serialization with SqliteSaver
- Implemented thread_id management with SQLite triggers
- Separated metadata and checkpoint storage

### Phase 7: Summarization
- Implemented automatic conversation summarization
- Added message count monitoring
- Created summarization prompt with token limits
- Integrated with checkpoint system

### Phase 8: Testing
- Created comprehensive test suite with pytest
- Implemented fixtures and mocks
- Added code coverage reporting
- Updated Docker setup to support test execution

## 🚀 Future Improvements

### Potential Enhancements

1. **Retry System**: Retry logic for failed API calls
2. **Cache**: API response cache to reduce calls
3. **Structured Logging**: Logging system for debugging
4. **More Tools**: Add more function calling capabilities
5. **Multi-language**: Support for multiple languages
6. **Export**: Export conversation history
7. **Better Error Messages**: Translate remaining Portuguese messages to English
8. **Connection Pooling**: SQLite connection pooling for better performance (if needed)

## 📝 Code Quality

### Standards Followed

- **PEP 8**: Python style guide
- **Type Hints**: Type annotations in all functions
- **Docstrings**: Google-style documentation
- **4 Spaces**: Standard indentation
- **English**: Code and documentation in English (except some error messages)

### Best Practices Implemented

- ✅ Separation of concerns
- ✅ Dependency injection
- ✅ Type safety
- ✅ Configuration management
- ✅ Modular design
- ✅ Clean code principles

## 🔍 Key Learnings

1. **Function Calling**: Powerful pattern for extending LLM capabilities
2. **Streaming**: Complex but significantly improves UX
3. **Checkpoint System**: LangGraph's checkpoint system eliminates manual serialization complexity
4. **Summarization**: Essential for managing long conversations and context window limits
5. **Modular Architecture**: Pays off in maintainability and testability
6. **Docker**: Essential for consistent environments and testing
7. **Type Hints**: Catches errors early and improves IDE support
8. **Error Handling**: External APIs can always fail - be prepared
9. **Testing**: Comprehensive tests enable confident refactoring and catch bugs early
10. **Dependency Injection**: Makes code more testable and flexible
11. **Documentation**: Documenting while developing saves time later

## 📚 Resources and References

### Documentation Consulted

- [LangChain Documentation](https://python.langchain.com/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)
- [pytest Documentation](https://docs.pytest.org/)

### APIs Used

- [REST Countries API](https://restcountries.com/)
- [ExchangeRate-API](https://www.exchangerate-api.com/)

---

**This documentation reflects the current state of the project and the development journey, including the challenges faced and solutions found.**
