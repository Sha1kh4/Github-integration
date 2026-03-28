from fastapi import FastAPI, Request ,Depends,HTTPException
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
    return RedirectResponse(url=f"https://github.com/login/oauth/authorize?client_id={os.getenv('Client_ID')}&redirect_uri={request.base_url}callback&scope=repo&state=123",status_code=302)

@app.get("/callback")
async def github_callback(code: str = None, error: str = None,error_description: str = None):
    if error:
        return {"message": f"Error: {error_description}"}
    url = f"https://github.com/login/oauth/access_token?client_id={os.getenv('Client_ID')}&client_secret={os.getenv('Client_secrets')}&code={code}"
    headers = {"Accept": "application/json"}
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail={
                    "message": "Failed to get access token",
                    "error": response.json()
                }
            )
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
        raise HTTPException(
            status_code=response.status_code,
            detail={
                "message": "Failed to get user data",
                "error": response.json()
            }
        )
    
    data = {
        "username": response.json()["login"],
        "name": response.json()["name"],
        "email": response.json()["email"],
        "repositories": response.json()["repos_url"],

    }
    return data

@app.get("/create-issue")
async def create_issue(token: Annotated[str, Depends(oauth2_scheme)], title: str, body: str,reponame: str,label : str = "bug"):
    url = f"https://api.github.com/repos/{reponame}/issues"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2026-03-10"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json={"title": title, "body": body, "labels": [label]})
    if response.status_code != 201:
        return {"message": "Failed to create issue", "code": response.json()}
    
    data = {
        "title": title,
        "body": body,
        "labels": label
    }
    return data,response.json()

@app.get("/get-issues")
async def get_issues(token: Annotated[str, Depends(oauth2_scheme)], reponame: str):
    url = f"https://api.github.com/repos/{reponame}/issues"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2026-03-10"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
    if response.status_code != 200:
        return {"message": "Failed to get issues", "code": response.json()}

    return response.json()

@app.get("/get-commits")
async def get_commits(token: Annotated[str, Depends(oauth2_scheme)], reponame: str):
    url = f"https://api.github.com/repos/{reponame}/commits"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2026-03-10"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
    if response.status_code != 200:
        return {"message": "Failed to get commits", "code": response.json()}
    
    return response.json()

@app.get("/crete-pull-request")
async def crete_pull_request(token: Annotated[str, Depends(oauth2_scheme)], title: str, body: str,reponame: str,branch : str ,base : str = "main"):
    url = f"https://api.github.com/repos/{reponame}/pulls"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2026-03-10"
    }
    print(f"https://api.github.com/repos/{reponame}/pulls")
    print(headers)
    print(title,body,branch,base)
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json={"title": title, "body": body, "head": f"{branch}", "base": base})
    if response.status_code != 201:
        raise HTTPException(
            status_code=response.status_code,
            detail={
                "message": "Failed to create pull request",
                "error": response.json()
            }
        )
    return response.json()