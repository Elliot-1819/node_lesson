FROM python:3.11-slim

WORKDIR /app

# System deps (kept minimal for scaffold)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . ./

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

CMD ["pytest", "-q"]


