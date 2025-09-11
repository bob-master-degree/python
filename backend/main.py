from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
import os
from backend.api.routes import router

app = FastAPI(title="FactCheck GPT Analyzer")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("APP_SESSION_SECRET"),
    session_cookie="factcheck_session",
    same_site="lax",
    https_only=False,
)

app.include_router(router)
