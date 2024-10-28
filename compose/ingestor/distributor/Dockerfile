FROM python
WORKDIR /app
RUN pip install --no-cache-dir confluent_kafka asyncio uvicorn fastapi
COPY app.py .
CMD ["uvicorn", "app:app", "--host", "0.0.0.0"]