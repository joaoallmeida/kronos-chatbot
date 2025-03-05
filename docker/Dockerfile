FROM python:3.12-slim AS builder
WORKDIR /app

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY docker/requirements.txt .
RUN pip3 install --upgrade pip && pip3 install -r requirements.txt --no-cache-dir --no-compile


FROM python:3.12-slim
WORKDIR /app

COPY --from=builder /opt/venv /opt/venv
COPY ../assistant .

ENV PATH=/opt/venv/bin:$PATH
EXPOSE 8501

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
