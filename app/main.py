from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def home() -> dict:
    """
    Home endpoint.
    """
    return {"message": "DevOps Practice Project"}