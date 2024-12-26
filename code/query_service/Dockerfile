FROM python:3.11.11-alpine
WORKDIR /app
RUN pip install --no-cache-dir asyncio uvicorn fastapi
COPY . .
EXPOSE 8003
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8003", "--reload"]
