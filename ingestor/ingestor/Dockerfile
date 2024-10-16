FROM python
WORKDIR /app
RUN pip install --no-cache-dir confluent_kafka asyncio uvicorn fastapi
COPY app.py .
EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
