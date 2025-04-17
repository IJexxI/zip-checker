FROM python:alpine@sha256:18159b2be11db91f84b8f8f655cd860f805dbd9e49a583ddaac8ab39bf4fe1a7
RUN apk add --no-cache gcc musl-dev postgresql-dev
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app/ app/
COPY migrations/ migrations/
COPY tests/ tests/
COPY alembic.ini .
RUN ls -R /app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]