# 📚 Documentation

Technical documentation about the development process, technologies used, and challenges faced in this project.

## 🛠️ Technologies Used

### Core Technologies

#### 1. **Python 3.11+**
- **Purpose**: Main programming language
- **Why**: Modern features, excellent library ecosystem, strong typing support, and mainly language used in IA agent coding
- **Usage**: All application code, CLI interface, data processing

#### 2. **LangChain 1.0+**
- **Purpose**: Framework for building LLM applications
- **Why**: Simplifies agent creation, tool integration, and message handling
- **Key Features Used**:
  - `create_agent()` - Agent creation with function calling
  - `StructuredTool` - Tool definition with Pydantic validation
  - Message streaming for real-time responses
  - Message types: `HumanMessage`, `AIMessage`, `ToolMessage`, `AIMessageChunk`

#### 3. **OpenAI API (GPT-4o-mini)**
- **Purpose**: Large Language Model for natural language understanding
- **Why**: Cost-effective model with function calling capabilities
- **Configuration**:
  - Model: `gpt-4o-mini` (default, configurable)
  - Temperature: `0.5` (balanced creativity)
  - Function Calling: Automatic tool selection

#### 4. **SQLite**
- **Purpose**: Local database for conversation persistence
- **Why**: Lightweight, no server required, perfect for local storage
- **Schema**: Simple table with JSON-serialized messages
- **Location**: `data/conversations.db` (fixed path)

#### 5. **Pydantic**
- **Purpose**: Data validation and schema definition
- **Why**: Type safety, automatic validation, excellent LangChain integration
- **Usage**: Tool parameter validation (`CountryInfoInput`, `ExchangeRateInput`)

#### 6. **Requests**
- **Purpose**: HTTP client for external API calls
- **APIs Used**:
  - REST Countries API (free, no authentication)
  - ExchangeRate-API (free tier)

#### 7. **Questionary**
- **Purpose**: Interactive CLI prompts
- **Why**: Better UX than raw `input()`, supports arrow keys navigation
- **Usage**: Conversation selection menu

#### 8. **Python-dotenv**
- **Purpose**: Environment variable management
- **Why**: Secure configuration, easy deployment
- **Usage**: Loading `OPENAI_API_KEY` and other settings

### Development Tools

- **Docker & Docker Compose**: Containerization and orchestration
- **Type Hints**: Full type annotation for better code quality
- **Dataclasses**: Clean configuration management

## 🏗️ Development Process

### Architecture Decisions

#### 1. **Modular Structure**
The project follows a clean architecture pattern:

```
src/
├── core/       # Business logic, configuration
├── api/        # External integrations
├── tools/      # LangChain tools
├── database/   # Data persistence
└── ui/         # User interface
```

**Rationale**: 
- Separation of concerns
- Easy to test and maintain
- Scalable for adding new features

#### 2. **Settings Management**
Using `@dataclass` with `@classmethod` factory pattern:

```python
@dataclass
class Settings:
    openai_api_key: str
    model_name: str = "gpt-4o-mini"
    temperature: float = 0.5
    
    @classmethod
    def from_env(cls) -> "Settings":
        # Loads from environment variables
```

**Benefits**:
- Type-safe configuration
- Default values
- Environment-based configuration
- Single source of truth

#### 3. **Tool Pattern**
Each tool follows a consistent pattern:

1. **API Client** (`src/api/clients/`) - Raw API calls
2. **Wrapper Function** (`src/tools/`) - Formats response for LLM
3. **StructuredTool** - LangChain integration with validation

**Example Flow**:
```
User Question → Agent → Tool → API Client → API → Response → Formatted → Agent → User
```

#### 4. **Streaming Implementation**
Real-time response streaming using LangChain's dual stream mode:

- `updates` mode: Captures tool calls and model messages
- `messages` mode: Streams token-by-token response

**Challenge**: Managing two stream modes simultaneously while avoiding duplication.

### Code Organization Principles

1. **Single Responsibility**: Each module has one clear purpose
2. **Dependency Injection**: Settings and database injected, not hardcoded
3. **Type Safety**: Full type hints throughout
4. **Error Handling**: Try/except blocks with meaningful messages
5. **Documentation**: All functions have docstrings

## 🎯 Main Challenges Faced

### 1. **Learning Python from Scratch**

**Challenge**: No prior knowledge of Python programming language before starting this project.

**Learning Journey**:
- Started with basic Python syntax and concepts
- Learned about Python's object-oriented programming
- Understood Python's type system and type hints
- Learning by doing: implementing features while learning

**Key Python Concepts Learned**:
- **Dataclasses**: Simplified class definition with automatic methods
- **Type Hints**: Improving code readability and IDE support
- **Pathlib**: Modern file path handling
- **Context Managers**: Resource management (database connections)
- **Decorators**: Understanding `@dataclass`, `@classmethod`
- **Module System**: Package structure and imports
- **Exception Handling**: Try/except blocks and error management

**Impact**: This learning curve added time to development but resulted in a solid foundation in Python, which is the primary language for AI agent development.

### 2. **Message Serialization/Deserialization**

**Challenge**: LangChain messages are complex objects that need to be stored in SQLite (text-only).

**Solution**: Custom serialization to JSON:
```python
def _serialize_history(self, conversation_history: List[BaseMessage]) -> str:
    messages_dict = []
    for msg in conversation_history:
        msg_dict = {
            'type': type(msg).__name__,
            'content': getattr(msg, 'content', '')
        }
        messages_dict.append(msg_dict)
    return json.dumps(messages_dict, ensure_ascii=False)
```

**Limitation**: Only stores `HumanMessage` and `AIMessage`. `ToolMessage` is not persisted (recreated on demand).

### 3. **Streaming Duplication**

**Challenge**: The dual stream mode (`updates` and `messages`) can cause duplicate output.

**Solution**: 
- Use a `set()` to track displayed tool messages
- Flag system to handle first message chunk
- Separate handling for each stream mode

```python
tool_content_list = set()  # Prevents duplicate tool messages
first_message_chunk = True  # Handles first chunk formatting
```

### 4. **Function Calling Integration**

**Challenge**: Ensuring the LLM correctly identifies when to call tools and with what parameters.

**Solution**:
- Detailed tool descriptions
- Pydantic schemas for parameter validation
- Clear system prompt instructions
- Testing with various question formats

### 5. **Database Path Management**

**Challenge**: Ensuring database directory exists and handling path differences between environments.

**Solution**:
```python
self.db_path = Path(db_path)
self.db_path.parent.mkdir(parents=True, exist_ok=True)
```

### 6. **Docker Interactive Mode**

**Challenge**: CLI application needs interactive input/output in Docker.

**Solution**:
- `stdin_open: true` and `tty: true` in docker-compose
- Using `docker compose exec` for interactive sessions
- Keeping container running with `tail -f /dev/null`

### 7. **Error Handling in API Calls**

**Challenge**: External APIs can fail, timeout, or return unexpected data.

**Solution**:
- Try/except blocks around all API calls
- Consistent error response format: `{"success": False, "error": "..."}`
- Timeout configuration (10 seconds)
- Graceful degradation with error messages

### 8. **Type Safety with LangChain Messages**

**Challenge**: LangChain uses multiple message types that need type checking.

**Solution**:
- `isinstance()` checks for each message type
- Type hints: `List[BaseMessage]`
- Handling edge cases (empty content, None values)

### 9. **Environment Variable Management**

**Challenge**: Different environments (local, Docker) need consistent configuration.

**Solution**:
- `.env.example` as template
- `python-dotenv` for loading
- Settings class with defaults
- Clear documentation

## 🔄 Development Workflow

### Initial Setup
1. Created basic structure with single files
2. Implemented core functionality
3. Added database persistence
4. Integrated streaming

### Refactoring Phase
1. Reorganized into modular structure
2. Separated concerns (API clients, tools, UI)
3. Improved error handling
4. Added type hints throughout

### Docker Integration
1. Created Dockerfile
2. Added docker-compose.yml
3. Configured volumes for development
4. Set up environment variable mounting

## 📊 Technical Decisions

### Why GPT-4o-mini?
- **Cost**: More affordable than GPT-4
- **Performance**: Sufficient for this use case
- **Function Calling**: Full support
- **Speed**: Faster responses

### Why SQLite?
- **Simplicity**: No server setup required
- **Portability**: Single file database
- **Performance**: Fast for local use
- **Compatibility**: Works everywhere Python runs

### Why Modular Architecture?
- **Maintainability**: Easy to find and fix issues
- **Testability**: Each module can be tested independently
- **Scalability**: Easy to add new tools/features
- **Team Collaboration**: Clear boundaries

### Why Streaming?
- **UX**: Better user experience with real-time feedback
- **Perception**: Users see progress, not just waiting
- **Debugging**: Easier to see what's happening

## 🚀 Future Improvements

### Potential Enhancements

1. **Error Recovery**: Retry logic for failed API calls
2. **Caching**: Cache API responses to reduce calls
3. **Logging**: Structured logging system
4. **Testing**: Unit and integration tests
5. **More Tools**: Additional function calling capabilities
6. **Web Interface**: Optional web UI
7. **Multi-language**: Support for multiple languages
8. **Export Conversations**: Export chat history

### Technical Debt

1. **ToolMessage Persistence**: Currently not saved in database
2. **Error Messages**: Some error messages still in Portuguese
3. **Hardcoded Paths**: Database path is fixed (by design)
4. **No Connection Pooling**: SQLite connections created per operation
5. **Limited Validation**: API responses not fully validated

## 📝 Code Quality

### Standards Followed

- **PEP 8**: Python style guide compliance
- **Type Hints**: Full type annotation
- **Docstrings**: Google-style documentation
- **4 Spaces**: Standard indentation
- **English**: Code and documentation in English

### Best Practices Implemented

- ✅ Separation of concerns
- ✅ Dependency injection
- ✅ Error handling
- ✅ Type safety
- ✅ Configuration management
- ✅ Modular design
- ✅ Clean code principles

## 🔍 Key Learnings

1. **Function Calling**: Powerful pattern for extending LLM capabilities
2. **Streaming**: Complex but provides better UX
3. **Message Serialization**: Requires careful handling of complex objects
4. **Modular Architecture**: Pays off in maintainability
5. **Docker**: Essential for consistent environments
6. **Type Hints**: Catch errors early, improve IDE support

---

**This documentation reflects the current state of the project and the development journey.**

