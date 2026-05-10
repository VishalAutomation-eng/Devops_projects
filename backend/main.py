from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from calculator import calculate

app = FastAPI()

# Allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def home() -> dict:
    return {
        "message": "Calculator API Running"
    }


@app.get("/calculate")
async def calculate_result(a: float, b: float) -> dict:
    """
    API Endpoint for calculations.
    """

    result = calculate(a, b)

    return result