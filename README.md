# 🤖 LangChain Assistant

Intelligent assistant with Function Calling that searches for information about countries and exchange rates.

## 🚀 How to Run

### Option 1: Docker (Recommended)

1. **Create the `.env` file based on `.env.example`:**
   ```bash
   cp .env.example .env
   ```
   Edit the `.env` file and add your OpenAI API key.

2. **Run with Docker:**
   ```bash
   docker compose up -d
   ```
   
   Then execute using one of these options:
   ```bash
   # Option A: Using agent.py
   docker compose exec langchain-assistant python agent.py
   
   # Option B: Using src/main.py
   docker compose exec langchain-assistant python -m src.main
   ```

### Option 2: Local

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Create the `.env` file based on `.env.example`:**
   ```bash
   cp .env.example .env
   ```
   Edit the `.env` file and add your `OPENAI_API_KEY`.

3. **Run:**
   ```bash
   # Option A: Using agent.py
   python agent.py
   
   # Option B: Using src/main.py
   python -m src.main
   ```

## 📖 How to Use

### On startup

1. You will see a menu to select a previous conversation or create a new one
2. Use arrow keys to navigate and Enter to select

### During conversation

**Ask questions about:**
- Countries: "What is the capital of Brazil?", "How many inhabitants does Japan have?"
- Exchange rates: "What is the dollar to real exchange rate?", "How much is 1 euro in dollars?"

### Available commands

- **Exit**: Type `sair`, `quit`, `exit` or `q`
- **Clear history**: Type `limpar`, `clear` or `reset`

### Example

```
👤 You: What is the capital of Brazil?

🤖 Assistant: The capital of Brazil is Brasília.

👤 You: And how many inhabitants does it have?

🤖 Assistant: Brazil has approximately 212,559,417 inhabitants.
```

## 🔑 Get OpenAI API Key

1. Visit [https://platform.openai.com/](https://platform.openai.com/)
2. Log in and go to **API Keys**
3. Click **Create new secret key**
4. Copy the key and add it to the `.env` file

## 🧪 Running Tests

### Option 1: Docker

```bash
# Run all tests
docker compose exec langchain-assistant python -m pytest

# Run specific test file
docker compose exec langchain-assistant python -m pytest tests/test_repository.py
```

### Option 2: Local

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_repository.py
```

## 🐳 Useful Docker Commands

```bash
# Stop container
docker compose down

# View logs
docker compose logs -f

# Rebuild
docker compose build

# Run tests
docker compose exec langchain-assistant python -m pytest
```

---

**Ready!** Now you can use the assistant. 🎉
