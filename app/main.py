from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()


@app.get("/")
async def home():
    return {"message": "DevOps Practice Project"}


Instrumentator().instrument(app).expose(app)