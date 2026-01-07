# Number Converter MCP Server (FastAPI + Ollama)

* This project is a multi-tool MCP (Model Context Protocol) server built using FastAPI and Ollama.
* It converts numbers into:
* Words (e.g. 77 → seventy-seven)
* Roman numerals (e.g. 88 → LXXXVIII)

## It supports:

✅ Normal HTTP API
✅ Natural-language input using Ollama (woks, roks)
✅ Multi-tool MCP server (/mcp/tools, /mcp/invoke)
✅ Agent-friendly design (LibreChat, Cursor, custom agents)

##🧠 Key Concepts (Important)
```
What is MCP here?

MCP (Model Context Protocol) is a tool interface that allows AI agents to:

Discover tools (/mcp/tools)

Call tools deterministically (/mcp/invoke)

Avoid hallucination by always using tools

This project implements MCP over HTTP (most stable and widely used).

🏗 Architecture
Client / Agent
   |
   |  (MCP / HTTP)
   v
FastAPI Server
   |
   |  (intent extraction)
   v
Ollama (llama3)
   |
   v
Words / Roman result


Ollama is used only for intent extraction

Core logic is deterministic (no LLM for math)

MCP tools wrap the logic cleanly
``

##📁 Project Structure
```
run-mcp-server/
├── main.py            # Complete API + MCP server
├── requirements.txt   # Python dependencies
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## 📦 Requirements
```
Local (without Docker)

Python 3.10+

Ollama installed locally

Docker (recommended)

Docker

Docker Compose
```

## 🐳 Running WITH Docker (Recommended)
```
1️⃣ Build & start
docker compose up --build

2️⃣ Pull model (first time only)
docker compose exec ollama ollama pull qwen

3️⃣ Restart API (after model load)
docker compose restart api

⏹ Stop the Server
Docker
docker compose down

Local
CTRL + C
```

## 🔎 API Overview
|*Endpoint*|*Purpose|
|---|---|
|/	Health check||
|/convert-textr|	Natural language conversion|
|/mcp/tools|	MCP tool registry|
|/mcp/invoke|	MCP tool execution|

##🌐 Normal HTTP API
* Health check
* curl http://127.0.0.1:8000/|

**Response:
i```
{ "status": "ok" }
```

Natural-language conversion
curl -X POST http://127.0.0.1:8000/convert-text \
  -H "Content-Type: application/json" \
  -d '{"text":"woks this number 77"}'


Response:

{
  "input": "woks this number 77",
  "mode": "words",
  "number": 77,
  "result": "seventy-seven"
}

🧠 Supported Keywords
Keyword	Meaning
woks	Convert to words
roks	Convert to roman numerals

Examples:

woks 12

roks this number 88

please woks number 100

🛠 MCP (Multi-Tool Server)
List available tools
curl http://127.0.0.1:8000/mcp/tools


Tools exposed:

convert_number_from_text

number_to_words

number_to_roman

health_check

Invoke MCP tool (Natural language)
curl -X POST http://127.0.0.1:8000/mcp/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "convert_number_from_text",
    "arguments": {
      "text": "roks 88"
    }
  }'


Response:

{
  "mode": "roman",
  "number": 88,
  "result": "LXXXVIII"
}

Invoke MCP tool (Direct number → words)
curl -X POST http://127.0.0.1:8000/mcp/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "number_to_words",
    "arguments": { "number": 42 }
  }'

Invoke MCP tool (Direct number → roman)
curl -X POST http://127.0.0.1:8000/mcp/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "number_to_roman",
    "arguments": { "number": 99 }
  }'

🤖 Agent Prompt (Auto-Select Tools)

Use this system prompt in LibreChat / Cursor / custom agents:

You are an AI agent with access to MCP tools.

Rules:
- If input contains "woks" or "roks", call convert_number_from_text
- If input asks for words with a number, call number_to_words
- If input asks for roman numerals with a number, call number_to_roman
- Always use a tool when one applies
- Never answer directly
- Return ONLY the tool output


This ensures:

✅ Correct tool selection

✅ No hallucination

✅ Deterministic results

✅ Test Cases (Complete Matrix)
✅ Valid inputs
Input	Expected
woks 1	one
woks 77	seventy-seven
roks 9	IX
roks 3999	MMMCMXCIX
please woks number 100	one hundred
❌ Invalid inputs
Input	Result
words 10	error
roman 5	error
roks 0	error
roks 5000	error
convert apple	error
🧪 Ollama failure cases
Condition	Result
Ollama down	clear error
Model not pulled	timeout error
Slow model load	retry works

✔ A real MCP server

✔ Multiple deterministic tools

✔ Ollama-powered intent parsing

✔ Agent-ready design

✔ Docker-ready setup
