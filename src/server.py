from dotenv import load_dotenv

# load the environment variables
load_dotenv(".env")

from fastapi import FastAPI
import uvicorn
import os
from gpt import medha
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.mount("/static", StaticFiles(directory="www"), name="static")
app.include_router(router=medha.router)


if __name__ == "__main__":
    uvicorn.run(app, host=os.environ.get("HOST"), port=int(os.environ.get("PORT")))
