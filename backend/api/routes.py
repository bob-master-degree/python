from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import os

from backend.core.gpt_client import analyze_text_claims

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

@router.get("/", response_class=HTMLResponse)
async def root():
    return RedirectResponse(url="/analyze", status_code=303)

@router.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request):
    session = getattr(request, "session", {})
    has_key = bool(session.get("openai_api_key"))
    return templates.TemplateResponse("settings.html", {"request": request, "has_key": has_key})

@router.post("/settings", response_class=HTMLResponse)
async def settings_submit(request: Request, api_key: str = Form(...)):
    session = getattr(request, "session", {})
    session["openai_api_key"] = api_key
    return RedirectResponse(url="/settings", status_code=303)

@router.post("/settings/delete", response_class=HTMLResponse)
async def settings_delete(request: Request):
    session = getattr(request, "session", {})
    session.pop("openai_api_key", None)
    return RedirectResponse(url="/settings", status_code=303)

@router.get("/analyze", response_class=HTMLResponse)
async def analyze_page(request: Request):
    session = getattr(request, "session", {})
    has_key = bool(session.get("openai_api_key"))
    return templates.TemplateResponse("analyze.html", {"request": request, "has_key": has_key})

@router.post("/analyze", response_class=HTMLResponse)
async def analyze_submit(request: Request, text: str = Form(...)):
    session = getattr(request, "session", {})
    if not session.get("openai_api_key"):
        return templates.TemplateResponse(
            "_error.html",
            {"request": request, "message": "Укажите OpenAI API Key на странице Настройки"},
            status_code=400,
        )
    result = analyze_text_claims(text, request=request)
    if isinstance(result, dict) and result.get("error"):
        return templates.TemplateResponse(
            "_toast_error.html",
            {"request": request, "message": "Сервис OpenAI недоступен"},
            status_code=502,
        )
    return templates.TemplateResponse("_analysis_result.html", {"request": request, "result": result})
