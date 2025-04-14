FROM python:3.8-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "mcp_app:app", "--host", "0.0.0.0", "--port", "8001", "--workers", "4"]
