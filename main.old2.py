from fastapi import FastAPI, HTTPException
from num2words import num2words
import requests
import re

app = FastAPI(title="Number Converter API with Ollama")

OLLAMA_URL = "http://ollama:11434/api/generate"
OLLAMA_MODEL = "llama3"


def to_roman(number: int) -> str:
    if number <= 0 or number > 3999:
        raise ValueError("Roman numerals support numbers from 1 to 3999")

    roman_map = [
        (1000, "M"),
        (900, "CM"),
        (500, "D"),
        (400, "CD"),
        (100, "C"),
        (90, "XC"),
        (50, "L"),
        (40, "XL"),
        (10, "X"),
        (9, "IX"),
        (5, "V"),
        (4, "IV"),
        (1, "I"),
    ]

    result = ""
    for value, symbol in roman_map:
        while number >= value:
            result += symbol
            number -= value

    return result


def parse_with_ollama(prompt: str) -> dict:
    system_prompt = """
Extract intent from the user input.

Rules:
- mode must be exactly "woks" or "roks"
- number must be an integer

Respond ONLY in JSON like:
{"mode":"woks","number":77}
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": OLLAMA_MODEL,
            "prompt": f"{system_prompt}\nUser input: {prompt}",
            "stream": False,
        },
        timeout=30,
    )

    text = response.json()["response"]

    # Fallback safety (in case model misbehaves)
    match = re.search(r'\{.*\}', text)
    if not match:
        raise ValueError("Could not parse intent")

    return eval(match.group())  # controlled input


@app.post("/convert-text")
def convert_from_text(text: str):
    try:
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

