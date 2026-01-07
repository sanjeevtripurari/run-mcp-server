from fastapi import FastAPI, HTTPException, Body
from num2words import num2words
import requests
import json

app = FastAPI(title="Number Converter API with Ollama")

OLLAMA_URL = "http://ollama:11434/api/generate"
OLLAMA_MODEL = "qwen"


def to_roman(number: int) -> str:
    if number <= 0 or number > 3999:
        raise ValueError("Roman numerals support numbers from 1 to 3999")

    roman_map = [
        (1000, "M"), (900, "CM"), (500, "D"), (400, "CD"),
        (100, "C"), (90, "XC"), (50, "L"), (40, "XL"),
        (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I"),
    ]

    result = ""
    for value, symbol in roman_map:
        while number >= value:
            result += symbol
            number -= value
    return result


def parse_with_ollama(text: str) -> dict:
    prompt = f"""
Extract intent from the text.

Rules:
- mode must be exactly "woks" or "roks"
- number can be an integer or in words

Return ONLY valid JSON like:
{{"mode":"woks","number":77}}

Text: {text}
"""

    try:
        r = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
            },
            timeout=120,  # ⬅ increase timeout
        )
    except requests.exceptions.Timeout:
        raise ValueError("Ollama timed out. Is the model loaded?")

    except requests.exceptions.ConnectionError:
        raise ValueError("Cannot connect to Ollama. Is it running?")

    data = r.json()

    if "response" not in data:
        raise ValueError(f"Invalid Ollama response: {data}")

    return json.loads(data["response"])




@app.post("/convert-text")
def convert_from_text(payload: dict = Body(...)):
    try:
        text = payload["text"]
        parsed = parse_with_ollama(text)

        mode = parsed["mode"]
        number = int(parsed["number"])

        if mode == "woks":
            return {
                "input": text,
                "mode": "words",
                "number": number,
                "result": num2words(number),
            }

        if mode == "roks":
            return {
                "input": text,
                "mode": "roman",
                "number": number,
                "result": to_roman(number),
            }

        raise HTTPException(status_code=400, detail="Invalid mode")

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/mcp/tools")
def mcp_tools():
    return {
        "convert_number_from_text": {
            "description": "Convert a number using natural language. Use 'woks' for words and 'roks' for roman numerals.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Example: 'woks this number 77' or 'roks 88'",
                    }
                },
                "required": ["text"],
            },
        }
    }


@app.post("/mcp/invoke")
def mcp_invoke(payload: dict):
    tool = payload.get("tool")
    arguments = payload.get("arguments", {})

    if tool != "convert_number_from_text":
        raise HTTPException(status_code=404, detail="Unknown tool")

    return convert_from_text({"text": arguments.get("text")})


@app.get("/mcp/tools")
def mcp_tools():
    return {
        "convert_number_from_text": {
            "description": "Convert a number from natural language text. Use 'woks' for words and 'roks' for roman numerals.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Example: 'woks this number 77' or 'roks 88'",
                    }
                },
                "required": ["text"],
            },
        },
        "number_to_words": {
            "description": "Convert a number directly to words.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "number": {
                        "type": "integer",
                        "description": "Number to convert",
                    }
                },
                "required": ["number"],
            },
        },
        "number_to_roman": {
            "description": "Convert a number directly to roman numerals.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "number": {
                        "type": "integer",
                        "description": "Number to convert (1–3999)",
                    }
                },
                "required": ["number"],
            },
        },
        "health_check": {
            "description": "Check if the server and Ollama are healthy.",
            "input_schema": {
                "type": "object",
                "properties": {},
            },
        },
    }

