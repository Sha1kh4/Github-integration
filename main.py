from fastapi import FastAPI, Request
import os
from dotenv import load_dotenv
from starlette.responses import RedirectResponse

load_dotenv()

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/github")
async def github_login(request: Request):
    return RedirectResponse(url=f"https://github.com/login/oauth/authorize?client_id={os.getenv('Client_ID')}&redirect_uri={request.base_url}callback",status_code=302)

@app.get("/callback")
async def github_callback(code: str):
    return {"message": "GitHub token received", "code": code}
    