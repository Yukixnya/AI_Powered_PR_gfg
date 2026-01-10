from fastapi import FastAPI, Request
from app.pr_control import pr_controller

app = FastAPI(title="Auto PR Writer")


@app.post("/pr-gen")
def pr_gen_handler(payload: dict):
    return pr_controller(payload)

@app.get("/pr-gen")
def pr_gen_health():
    return {"status": "ok"}


@app.get("/")
def health_check():
    return {"status": "running"}
