from fastapi import FastAPI, Request ,Depends
from fastapi.security import OAuth2PasswordBearer
import os
from dotenv import load_dotenv
from starlette.responses import RedirectResponse
import httpx

load_dotenv()

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/github")
async def github_login(request: Request):
    return RedirectResponse(url=f"https://github.com/login/oauth/authorize?client_id={os.getenv('Client_ID')}&redirect_uri={request.base_url}callback&scope=read:user",status_code=302)

@app.get("/callback")
async def github_callback(code: str = None, error: str = None,error_description: str = None):
    if error:
        return {"message": f"Error: {error_description}"}
    url = f"https://github.com/login/oauth/access_token?client_id={os.getenv('Client_ID')}&client_secret={os.getenv('Client_secrets')}&code={code}"
    headers = {"Accept": "application/json"}
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code != 200:
            return {"message": "Failed to get access token", "code": response.status_code}
    return {"message": "GitHub token received", "code": response.text}


@app.get("/me")
async def me(token: Annotated[str, Depends(oauth2_scheme)]):
    url = "https://api.github.com/user"

    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2026-03-10"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
    if response.status_code != 200:
        return {"message": "Failed to get user data", "code": response.status_code}
    
    data = {
        "username": response.json()["login"],
        "name": response.json()["name"],
        "email": response.json()["email"],
        "repositories": response.json()["repos_url"],

    }
    return data