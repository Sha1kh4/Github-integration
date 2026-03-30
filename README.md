# GitHub Integration API

A FastAPI application that integrates with GitHub's OAuth 2.0 flow, allowing users to authenticate and perform common GitHub operations — managing issues, browsing commits, and opening pull requests — on behalf of the logged-in user.

---

## Tech Stack

- **[FastAPI](https://fastapi.tiangolo.com/)** — Web framework
- **[uv](https://github.com/astral-sh/uv)** — Fast Python package manager
- **[httpx](https://www.python-httpx.org/)** — Async HTTP client
- **[Pydantic](https://docs.pydantic.dev/)** — Data validation and serialization
- **Python 3.14**


## Prerequisites

- Python 3.14+
- [uv](https://github.com/astral-sh/uv) installed
- A **GitHub OAuth App** — [create one here](https://github.com/settings/developers)
  - Set the **Authorization callback URL** to `http://localhost:8000/callback`

---

## Local Setup

**1. Clone the repository**

```bash
git clone https://github.com/Sha1kh4/Github-integration
cd Github-integration
```

**2. Install dependencies**

```bash
uv sync
```

**3. Configure environment variables**

Create a `.env` file in the project root:

```env
Client_ID=your_github_client_id
Client_secrets=your_github_client_secret
```

**4. Run the development server**

```bash
fastapi dev main.py
```

The API will be available at `http://localhost:8000`.

---

## Docker Setup

**Build the image**

```bash
docker build -t github-integration .
```

**Run the container**

```bash
docker run -p 8000:80 --env-file .env github-integration
```

The API will be available at `http://localhost:8000`.

---

## Authentication Flow

This app uses the **GitHub OAuth Authorization Code** flow.

```
User → GET /github → GitHub OAuth Page → Approve → GET /callback → Access Token
```

1. Visit `GET /github` — you'll be redirected to GitHub to authorize the app.
2. GitHub redirects back to `GET /callback?code=...`.
3. The server exchanges the code for an **access token** and returns it.
4. Use this token as a **Bearer token** in all subsequent requests:

```
Authorization: Bearer <your_access_token>
```

---

## API Reference

### `GET /`
Health check.

```json
{ "message": "Hello World" }
```

---

### `GET /github`
Redirects to GitHub's OAuth authorization page. Open this in a browser to begin the login flow.

---

### `GET /callback`
Handles the OAuth redirect from GitHub and returns an access token.

| Query Param         | Type   | Description                          |
|---------------------|--------|--------------------------------------|
| `code`              | string | Authorization code from GitHub       |
| `error`             | string | Error identifier (if auth failed)    |
| `error_description` | string | Human-readable error (if auth failed)|

**Response:**
```json
"gho_xxxxxxxxxxxxxxxxxxxx"
```

---

### `GET /me`
Returns the authenticated user's GitHub profile.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "username": "octocat",
  "name": "The Octocat",
  "email": "octocat@github.com",
  "repositories": "https://api.github.com/users/octocat/repos"
}
```

---

### `POST /create-issue`
Creates a new issue in a repository.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "reponame": "owner/repo",
  "title": "Bug: Something is broken",
  "body": "Steps to reproduce...",
  "label": "bug"
}
```

> `label` defaults to `"bug"` if not provided.

**Response:**
```json
{
  "title": "Bug: Something is broken",
  "body": "Steps to reproduce...",
  "labels": ["bug"]
}
```

---

### `GET /get-issues`
Lists all open issues for a repository.

**Headers:** `Authorization: Bearer <token>`

| Query Param | Type   | Description                            |
|-------------|--------|----------------------------------------|
| `reponame`  | string | Repository in `owner/repo` format      |

**Response:** Array of GitHub issue objects.

---

### `GET /get-commits`
Lists the commit history for a repository.

**Headers:** `Authorization: Bearer <token>`

| Query Param | Type   | Description                            |
|-------------|--------|----------------------------------------|
| `reponame`  | string | Repository in `owner/repo` format      |

**Response:** Array of GitHub commit objects.

---

### `POST /create-pull-request`
Opens a new pull request in a repository.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "reponame": "owner/repo",
  "title": "Feature: Add new endpoint",
  "body": "This PR adds...",
  "branch": "feature/my-branch",
  "base": "main"
}
```

> `base` defaults to `"main"` if not provided.

**Response:**
```json
{
  "id": 1234567890,
  "title": "Feature: Add new endpoint",
  "body": "This PR adds...",
  "state": "open",
  "html_url": "https://github.com/owner/repo/pull/42"
}
```

---

## Interactive Docs

FastAPI generates live API documentation automatically:

- **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## Notes

- All `reponame` fields expect the `owner/repo` format (e.g., `octocat/Hello-World`).
- The `repo` OAuth scope is requested, which grants read/write access to public and private repositories.
- The `httpx` and `python-dotenv` packages are used at runtime but are not listed in `pyproject.toml` — add them if needed:
  ```bash
  uv add httpx python-dotenv pydantic[email]
  ```