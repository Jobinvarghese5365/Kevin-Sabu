from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
from dotenv import load_dotenv

from backend.llm import research_brand
from backend.models import ResearchRequest, ResearchResult

load_dotenv()

app = FastAPI(title="Brand Research Desktop Pro API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}

@app.get("/", response_class=HTMLResponse)
def index(request: Request) -> HTMLResponse:
    regions = ["India", "USA", "Indonesia", "Malaysia"]
    return templates.TemplateResponse(
        request=request, name="index.html", context={"regions": regions}
    )


@app.post("/research", response_model=ResearchResult)
def research(payload: ResearchRequest) -> ResearchResult:
    try:
        return research_brand(payload.brand_name, payload.region)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

