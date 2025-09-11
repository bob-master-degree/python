import json
from typing import Dict, Any, Optional
from fastapi import Request
from openai import OpenAI

_client_cache: dict[str, OpenAI] = {}

def _get_api_key(request: Optional[Request]) -> str:
    if request is not None:
        session = getattr(request, "session", {})
        key = session.get("openai_api_key")
        if key:
            return str(key)
    raise RuntimeError("OpenAI API Key not set. Go to Settings and save your key.")

def _get_client(api_key: str) -> OpenAI:
    if api_key in _client_cache:
        return _client_cache[api_key]
    client = OpenAI(api_key=api_key)
    _client_cache[api_key] = client
    return client

def ask_question(question: str, request: Optional[Request] = None) -> str:
    api_key = _get_api_key(request)
    client = _get_client(api_key)
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Отвечай кратко и по делу."},
                {"role": "user", "content": question},
            ],
            temperature=0.2,
        )
        content = response.choices[0].message.content
        return content or ""
    except Exception as exc:
        return f"Ошибка при обращении к модели: {exc}"

def analyze_text_claims(text: str, request: Optional[Request] = None) -> Dict[str, Any]:
    prompt = f"""
    Ты — помощник по факт-проверке. Разбей текст на предложения. Для каждого предложения:
    1) Определи, является ли оно утверждением (констатацией факта), а не вопросом, не просьбой и не мнением.
    2) Если это утверждение, оцени его достоверность.

    Для каждого утверждения верни объект:
    - claim: краткая формулировка утверждения (1–2 предложения)
    - snippet: точный отрывок из исходного текста
    - verdict: одно из [true, likely_true, disputed, false, unverifiable]
    - reason: краткое обоснование (почему так считаешь; если ложь — что именно неверно)

    Верни строго JSON формата:
    {{
      "facts": [
        {{"claim": str, "snippet": str, "verdict": str, "reason": str}},
        ...
      ]
    }}

    Не включай в список не-утверждения. Если утверждений нет — верни {{"facts": []}}.

    Текст:
    ---
    {text}
    ---
    """
    try:
        api_key = _get_api_key(request)
        client = _get_client(api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
        content = response.choices[0].message.content or "{}"
        data = json.loads(content)
        if isinstance(data, dict) and "facts" in data and isinstance(data["facts"], list):
            return data
        return {"facts": []}
    except Exception as exc:
        return {"error": str(exc)}
