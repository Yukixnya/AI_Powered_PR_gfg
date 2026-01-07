from fastapi import FastAPI, Request
from dotenv import load_dotenv
from app.github import github_webhook

load_dotenv()

app = FastAPI(title="Auto PR Writer")


@app.post("/webhook/github")
async def github_webhook_handler(request: Request):
    payload = await request.json()
    return github_webhook(payload)


# Optional: avoid 405 noise in logs
@app.get("/webhook/github")
def webhook_health():
    return {"status": "ok"}


@app.get("/")
def health_check():
    return {"status": "running"}
