"""
Configuration file for the project.
Manages the loading of environment variables.
"""

import os
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()

# Configuração da API OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Validação básica
if not OPENAI_API_KEY:
  raise ValueError(
    "OPENAI_API_KEY not found."
  )
