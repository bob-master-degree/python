FROM python:3.12-slim AS builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --prefix=/install -r requirements.txt

FROM python:3.12-slim
WORKDIR /app

COPY --from=builder /install /usr/local
COPY backend /app/backend/

RUN useradd -m -u 10001 appuser \
    && chown -R appuser:appuser /app

USER appuser
EXPOSE 8000

CMD ["python", "-m", "backend.main"]
