def calculate(expression: str) -> str:
    try:
        result = eval(expression, {"__builtins__": {}})
        return f"The result is {result}"
    except Exception:
        return "Sorry, I couldn't calculate that."