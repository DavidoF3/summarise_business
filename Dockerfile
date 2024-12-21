FROM python:3.11.11-slim-bookworm

WORKDIR /app

COPY requirements.txt ./
COPY pyproject.toml ./

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir .

COPY . .

EXPOSE 4000

CMD ["fastapi", "run", "app/main.py", "--port", "4000"]
