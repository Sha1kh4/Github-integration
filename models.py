from pydantic import BaseModel, EmailStr
from typing import Optional, List, Any


# ----------- AUTH / TOKEN -----------

class TokenResponse(BaseModel):
    access_token: str
    token_type: Optional[str] = "bearer"


# ----------- USER -----------

class UserResponse(BaseModel):
    username: str
    name: Optional[str]
    email: Optional[EmailStr]
    repositories: str


# ----------- ISSUE -----------

class CreateIssueRequest(BaseModel):
    title: str
    body: str
    reponame: str
    label: Optional[str] = "bug"


class IssueResponse(BaseModel):
    title: str
    body: str
    labels: List[str]


# ----------- COMMITS -----------

class CommitAuthor(BaseModel):
    name: str
    email: Optional[EmailStr]
    date: str


class CommitInfo(BaseModel):
    message: str
    author: CommitAuthor


class CommitResponse(BaseModel):
    sha: str
    commit: CommitInfo


# ----------- PULL REQUEST -----------

class CreatePullRequestRequest(BaseModel):
    title: str
    body: str
    reponame: str
    branch: str
    base: Optional[str] = "main"


class PullRequestResponse(BaseModel):
    id: int
    title: str
    body: Optional[str]
    state: str
    html_url: str


# ----------- GENERIC ERROR -----------

class ErrorResponse(BaseModel):
    message: str
    error: Optional[Any]