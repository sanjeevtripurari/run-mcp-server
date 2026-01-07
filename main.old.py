from fastapi import FastAPI, HTTPException, Query
from num2words import num2words

app = FastAPI(title="Number Converter API")


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


@app.get("/")
def health_check():
    return {"status": "ok"}


@app.get("/convert")
def convert_number(
    number: int = Query(..., description="Number to convert"),
    mode: str = Query(..., description="words or roman"),
):
    mode = mode.lower()

    try:
        if mode == "woks":
            return {
                "input": number,
                "mode": "words",
                "result": num2words(number),
            }

        if mode == "roks":
            return {
                "input": number,
                "mode": "roman",
                "result": to_roman(number),
            }

        raise HTTPException(
            status_code=400,
            detail="Invalid mode. Use 'words' or 'roman'",
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

