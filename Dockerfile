FROM python:3.11-slim

LABEL maintainer="AquaVision AI"
LABEL description="Real-time water quality monitoring using computer vision"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/data

EXPOSE 8050

CMD ["python", "aquavision.py", "--config", "config.yaml"]
