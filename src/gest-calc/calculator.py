"""Lógica de cálculo independiente de la cámara y de la interfaz."""

import re
from decimal import Decimal, DecimalException, localcontext


def evaluate(expression):
    """Analiza números y + - * /, con precedencia y sin ejecutar código."""
    if not expression or len(expression) > 60:
        raise ValueError("Expresion vacia o demasiado larga")
    tokens = re.findall(r"\d+(?:\.\d*)?|\.\d+|[+*/-]", expression)
    if "".join(tokens) != expression:
        raise ValueError("Expresion no valida")
    position = 0

    def number():
        nonlocal position
        sign = 1
        if position < len(tokens) and tokens[position] in ("+", "-"):
            sign = -1 if tokens[position] == "-" else 1
            position += 1
        if position >= len(tokens) or tokens[position] in "+-*/":
            raise ValueError("Falta un numero")
        value = Decimal(tokens[position]) * sign
        position += 1
        return value

    def term():
        nonlocal position
        value = number()
        while position < len(tokens) and tokens[position] in ("*", "/"):
            operator = tokens[position]
            position += 1
            right = number()
            if operator == "/" and right == 0:
                raise ValueError("No se puede dividir entre cero")
            value = value * right if operator == "*" else value / right
        return value

    try:
        with localcontext() as context:
            context.prec = 16
            value = term()
            while position < len(tokens):
                operator = tokens[position]
                if operator not in ("+", "-"):
                    raise ValueError("Expresion no valida")
                position += 1
                right = term()
                value = value + right if operator == "+" else value - right
    except DecimalException as error:
        raise ValueError("Numero fuera de rango") from error
    result = format(value, "f")
    if "." in result:
        result = result.rstrip("0").rstrip(".")
    if len(result) > 60:
        raise ValueError("Resultado demasiado largo")
    return "0" if value == 0 else result


class Calculator:
    def __init__(self):
        self.expression = ""
        self.error = ""
        self.completed = False
        self.previous = ""

    def press(self, key):
        self.error = ""
        if key == "C":
            self.expression, self.previous, self.completed = "", "", False
        elif key == "<":
            self.expression = self.expression[:-1]
            self.completed = False
        elif key == "=":
            try:
                result = evaluate(self.expression)
            except ValueError as error:
                self.error = str(error)
            else:
                self.previous = self.expression + " ="
                self.expression = result
                self.completed = True
        elif key in "0123456789." and len(key) == 1:
            if self.completed:
                self.expression, self.completed = "", False
            if key == ".":
                current = re.split(r"[+*/-]", self.expression)[-1]
                if "." in current:
                    return
                key = "." if current else "0."
            if len(self.expression) + len(key) <= 60:
                self.expression += key
        elif key in ("+", "-", "*", "/"):
            self.completed = False
            if not self.expression:
                if key == "-":
                    self.expression = "-"
            elif self.expression[-1] in "+-*/":
                # Permite 5*-2, pero sustituye operadores repetidos.
                if key == "-" and self.expression[-1] in "*/":
                    self.expression += key
                elif len(self.expression) > 1 and self.expression[-2:] in ("*-", "/-"):
                    self.expression = self.expression[:-2] + key
                elif self.expression != "-":
                    self.expression = self.expression[:-1] + key
            elif len(self.expression) < 60:
                self.expression += key
