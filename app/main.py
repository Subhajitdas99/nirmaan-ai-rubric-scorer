# app/main.py

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .models import ScoreRequest, ScoreResponse
from .rubric_scoring import score_transcript_full

app = FastAPI(title="Nirmaan AI – Communication Rubric Scorer")

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/score", response_model=ScoreResponse)
async def score(req: ScoreRequest):
    result = score_transcript_full(req.transcript, req.duration_sec)
    return result
