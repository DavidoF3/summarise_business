# FROM nvidia/cuda:11.7.1-runtime-ubuntu22.04
FROM python:3.11.11-slim-bookworm

# RUN apt-get update \
#     && apt-get install --yes --no-install-recommends vim

# ENV DEBIAN_FRONTEND=noninteractive
# RUN apt-get install -y python3.11 \
#     && apt install python3-pip -y \
#     && apt install python-is-python3

WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt ./
COPY pyproject.toml ./

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir .

COPY . .

EXPOSE 4000

CMD ["fastapi", "run", "app/main.py", "--port", "4000"]
