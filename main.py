from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
from dotenv import load_dotenv
from starlette.responses import RedirectResponse
import httpx

from models import (
    TokenResponse,
    UserResponse,
    CreateIssueRequest,
    IssueResponse,
    CreatePullRequestRequest,
    PullRequestResponse
)

load_dotenv()

app = FastAPI()
security = HTTPBearer()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/github",tags=["Auth"])
async def github_login(request: Request):
    return RedirectResponse(url=f"https://github.com/login/oauth/authorize?client_id={os.getenv('Client_ID')}&redirect_uri={request.base_url}callback&scope=repo&state=123",status_code=302)

@app.get("/callback", response_model=TokenResponse,tags=["Auth"])
async def github_callback(code: str = None, error: str = None, error_description: str = None):
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
    response = response.json()
    if "error" in response:
        raise HTTPException(status_code=400, detail=response["error_description"])
    else:
        return response

@app.get("/me", response_model=UserResponse,tags=["Auth"])
async def me(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials

    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2026-03-10"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.github.com/user", headers=headers)
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

@app.post("/create-issue", response_model=IssueResponse,tags=["Issues"])
async def create_issue(
    payload: CreateIssueRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    url = f"https://api.github.com/repos/{payload.reponame}/issues"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2026-03-10"
    }

    body = {
        "title": payload.title,
        "body": payload.body,
        "labels": [payload.label]
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=body)
    if response.status_code != 201:
        raise HTTPException(status_code=response.status_code, detail=response.json())
    return {
        "title": payload.title,
        "body": payload.body,
        "labels": [payload.label]
    }

@app.get("/get-issues",tags=["Issues"])
async def get_issues(
    reponame: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    url = f"https://api.github.com/repos/{reponame}/issues"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2026-03-10"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.json())

    return response.json()

@app.get("/get-commits",tags=["Commits"])
async def get_commits(
    reponame: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials

    url = f"https://api.github.com/repos/{reponame}/commits"

    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2026-03-10"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.json())

    return response.json()

@app.post("/create-pull-request", response_model=PullRequestResponse,tags=["Pull Requests"])
async def create_pull_request(
    payload: CreatePullRequestRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials

    url = f"https://api.github.com/repos/{payload.reponame}/pulls"

    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2026-03-10"
    }

    body = {
        "title": payload.title,
        "body": payload.body,
        "head": payload.branch,
        "base": payload.base
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=body)

    if response.status_code != 201:
        raise HTTPException(status_code=response.status_code, detail=response.json())

    pr = response.json()

    return {
        "id": pr["id"],
        "title": pr["title"],
        "body": pr.get("body"),
        "state": pr["state"],
        "html_url": pr["html_url"]
    }
