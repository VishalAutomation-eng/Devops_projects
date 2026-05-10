from typing import Dict, Union

from operations import add, subtract, multiply

Number = Union[int, float]


def calculate(a: Number, b: Number) -> Dict[str, Number]:
    """
    Process all calculations.
    """

    return {
        "addition": add(a, b),
        "subtraction": subtract(a, b),
        "multiplication": multiply(a, b)
    }