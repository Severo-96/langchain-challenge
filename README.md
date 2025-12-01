# 🤖 Assistente IA com Function Calling

Um assistente inteligente construído com LangChain e OpenAI que pode buscar informações em tempo real sobre países e taxas de câmbio usando Function Calling.

## 📋 Sobre o Projeto

Este projeto demonstra como usar **Function Calling** do OpenAI através do framework **LangChain** para criar um assistente que pode executar funções externas automaticamente. O assistente pode:

- Buscar informações sobre países (capital, população, região, moeda, idiomas)
- Consultar taxas de câmbio entre moedas
- Manter contexto da conversa (histórico)
- Responder perguntas de forma natural e contextual

## 🚀 Funcionalidades

### 1. Informações sobre Países
O assistente pode buscar informações detalhadas sobre qualquer país usando a [REST Countries API](https://restcountries.com/).

**Exemplos de perguntas:**
- "Qual é a capital do Brasil?"
- "Quantos habitantes tem o Japão?"
- "Quais são os idiomas falados na França?"
- "Qual é a moeda da Argentina?"

### 2. Taxas de Câmbio
O assistente pode consultar taxas de câmbio atualizadas entre diferentes moedas usando a [ExchangeRate-API](https://www.exchangerate-api.com/).

**Exemplos de perguntas:**
- "Qual é a cotação do dólar para o real?"
- "Quanto vale 1 euro em dólares?"
- "Qual a taxa de câmbio entre libra e iene?"

### 3. Histórico de Conversa
O assistente mantém o contexto da conversa, permitindo referências a mensagens anteriores.

**Exemplo:**
```
Você: Qual é a capital do Brasil?
Assistente: A capital do Brasil é Brasília.

Você: E do Japão?
Assistente: A capital do Japão é Tóquio.
```

## 📦 Pré-requisitos

- Python 3.10 ou superior
- Chave da API OpenAI ([como obter](#-como-obter-a-chave-da-openai))
- Conexão com a internet (para chamadas às APIs externas)

## 🔧 Instalação

### 1. Clone ou baixe o projeto

```bash
git clone <url-do-repositorio>
cd 001
```

### 2. Crie um ambiente virtual (recomendado)

```bash
python3 -m venv venv

# No Linux/Mac:
source venv/bin/activate

# No Windows:
venv\Scripts\activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto:

```bash
cp .env.example .env
```

Edite o arquivo `.env` e adicione sua chave da OpenAI:

```env
OPENAI_API_KEY=sk-sua-chave-aqui
```

## 🎯 Como Usar

### Executar o assistente

```bash
python main.py
```

### Comandos disponíveis

- **Sair**: Digite `sair`, `quit`, `exit` ou `q` para encerrar
- **Limpar histórico**: Digite `limpar`, `clear` ou `reset` para limpar o histórico da conversa

### Exemplo de uso

```
============================================================
🤖 Assistente IA com Function Calling
============================================================

Este assistente pode ajudar você com:
  • Informações sobre países
  • Taxas de câmbio

Digite 'sair' ou 'quit' para encerrar.
Digite 'limpar' para limpar o histórico da conversa.
============================================================

✅ Assistente inicializado com sucesso!

👤 Você: Qual é a capital do Brasil?

🤖 Assistente: A capital do Brasil é Brasília.

👤 Você: E quantos habitantes tem?

🤖 Assistente: O Brasil tem aproximadamente 212.559.417 habitantes.

👤 Você: Qual a cotação do dólar para o real?

🤖 Assistente: Taxa de câmbio:
- USD → BRL
- Taxa: 1 USD = 5.2341 BRL
- Data: 2024-01-15
```

## 📁 Estrutura do Projeto

```
001/
├── main.py              # Ponto de entrada, interface CLI
├── langchain_setup.py   # Configuração do LangChain e agente
├── api_client.py        # Funções para chamadas às APIs externas
├── config.py            # Configuração e carregamento de variáveis
├── requirements.txt     # Dependências do projeto
├── .env                 # Variáveis de ambiente (não commitado)
├── .env.example         # Exemplo de arquivo .env
└── README.md            # Este arquivo
```

### Descrição dos arquivos

- **`main.py`**: Interface de linha de comando que gerencia a interação com o usuário, histórico de conversa e exibição de respostas.

- **`langchain_setup.py`**: Configura o agente LangChain, define as tools (ferramentas) disponíveis e cria o sistema de Function Calling.

- **`api_client.py`**: Contém as funções que fazem chamadas às APIs externas (REST Countries e ExchangeRate-API).

- **`config.py`**: Carrega variáveis de ambiente do arquivo `.env` e valida configurações necessárias.

## 🔍 Como Funciona

### 1. Function Calling

O assistente usa **Function Calling** do OpenAI, que permite que o modelo de linguagem decida quando e quais funções externas chamar.

**Fluxo:**
1. Usuário faz uma pergunta
2. O modelo analisa a pergunta
3. Se necessário, o modelo decide chamar uma função (tool)
4. A função é executada e retorna dados
5. O modelo usa os dados para gerar uma resposta completa

### 2. Tools (Ferramentas)

As tools são funções que o assistente pode chamar automaticamente:

- **`get_country_info`**: Busca informações sobre países
- **`get_exchange_rate`**: Consulta taxas de câmbio

Cada tool é definida com:
- Nome da função
- Descrição (usada pelo modelo para decidir quando usar)
- Schema de parâmetros (validação com Pydantic)

### 3. Histórico de Conversa

O histórico é mantido como uma lista de mensagens (`HumanMessage` e `AIMessage`) que é passada para o agente a cada interação, permitindo que o assistente mantenha contexto.

### 4. APIs Externas

- **REST Countries API**: Gratuita, sem necessidade de autenticação
- **ExchangeRate-API**: Gratuita, sem necessidade de autenticação

## 🔑 Como Obter a Chave da OpenAI

1. Acesse [https://platform.openai.com/](https://platform.openai.com/)
2. Crie uma conta ou faça login
3. Vá em **API Keys** no menu
4. Clique em **Create new secret key**
5. Copie a chave e adicione no arquivo `.env`

**Importante**: A chave começa com `sk-` e é sensível. Nunca compartilhe ou commite no Git!

## 🛠️ Tecnologias Utilizadas

- **LangChain**: Framework para construção de aplicações com LLMs
- **OpenAI API**: Modelo de linguagem GPT-3.5-turbo
- **Pydantic**: Validação de dados e schemas
- **python-dotenv**: Gerenciamento de variáveis de ambiente
- **requests**: Cliente HTTP para chamadas às APIs

## 📝 Exemplos de Perguntas

### Sobre Países
- "Me fale sobre o Brasil"
- "Qual é a população da China?"
- "Quais idiomas são falados na Índia?"
- "Qual a moeda da Suíça?"

### Sobre Câmbio
- "Quanto vale 1 dólar em reais?"
- "Qual a cotação do euro?"
- "Converta 100 dólares para euros"
- "Taxa de câmbio entre libra e iene"

### Combinadas
- "Qual é a capital do Brasil e quantos habitantes tem?"
- "Me dê informações sobre o Japão e a cotação do iene para o real"

## ⚠️ Troubleshooting

### Erro: "OPENAI_API_KEY not found"
- Verifique se o arquivo `.env` existe
- Confirme que a chave está correta no arquivo
- Certifique-se de que o arquivo está na raiz do projeto

### Erro: "You exceeded your current quota"
- Verifique seu plano e créditos na OpenAI
- Confirme que sua chave está ativa

### Erro ao buscar informações
- Verifique sua conexão com a internet
- As APIs externas podem estar temporariamente indisponíveis

## 📄 Licença

Este projeto é um exemplo educacional e pode ser usado livremente.

## 🤝 Contribuindo

Sinta-se à vontade para fazer fork, melhorar e sugerir mudanças!

---

**Desenvolvido com ❤️ usando LangChain e OpenAI**

