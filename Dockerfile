FROM python:3.10-slim

WORKDIR /app

# System deps (Pillow, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY handler.py .

CMD ["python", "-m", "runpod.serverless.worker", "handler"]
