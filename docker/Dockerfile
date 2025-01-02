FROM python:3.12-slim

WORKDIR /app

COPY docker/requirements.txt .
COPY ../assistant .

RUN pip3 install --upgrade pip && pip3 install -r requirements.txt --no-cache-dir

EXPOSE 8501

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
