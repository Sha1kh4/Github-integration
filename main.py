from fastapi import FastAPI, Request
import os
from dotenv import load_dotenv
from starlette.responses import RedirectResponse
import httpx

load_dotenv()

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/github")
async def github_login(request: Request):
    return RedirectResponse(url=f"https://github.com/login/oauth/authorize?client_id={os.getenv('Client_ID')}&redirect_uri={request.base_url}callback&scope=read:user",status_code=302)

@app.get("/callback")
async def github_callback(code: str):
    url = f"https://github.com/login/oauth/access_token?client_id={os.getenv('Client_ID')}&client_secret={os.getenv('Client_secrets')}&code={code}"
    headers = {"Accept": "application/json"}
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
    return {"message": "GitHub token received", "code": response.text}
