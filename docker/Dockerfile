FROM python:3.12-slim
WORKDIR /app

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY docker/requirements.txt .

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \  
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --upgrade pip && pip3 install -r requirements.txt --no-cache-dir --no-compile

COPY ../assistant .

EXPOSE 8501

ENTRYPOINT ["streamlit", "run", "assistant.py", "--server.port=8501", "--server.address=0.0.0.0"]
