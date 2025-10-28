from flask import Blueprint, render_template, redirect, request, session
from backend.core.gpt_client import analyze_text_claims

bp = Blueprint("routes", __name__)

@bp.route("/")
def root():
    return redirect("/analyze", code=303)

@bp.route("/settings", methods=["GET"])
def settings_page():
    has_key = bool(session.get("openai_api_key"))
    return render_template("settings.html", has_key=has_key)

@bp.route("/settings", methods=["POST"])
def settings_submit():
    api_key = request.form.get("api_key")
    if api_key:
        session["openai_api_key"] = api_key
    return redirect("/settings", code=303)

@bp.route("/settings/delete", methods=["POST"])
def settings_delete():
    session.pop("openai_api_key", None)
    return redirect("/settings", code=303)

@bp.route("/analyze", methods=["GET"])
def analyze_page():
    has_key = bool(session.get("openai_api_key"))
    return render_template("analyze.html", has_key=has_key)

@bp.route("/analyze", methods=["POST"])
def analyze_submit():
    if not session.get("openai_api_key"):
        return render_template(
            "_error.html",
            message="Укажите OpenAI API Key на странице Настройки",
        ), 400

    text = request.form.get("text", "")
    result = analyze_text_claims(text)

    if isinstance(result, dict) and result.get("error"):
        return render_template(
            "_toast_error.html",
            message="Сервис OpenAI недоступен",
        ), 502

    return render_template("_analysis_result.html", result=result)
