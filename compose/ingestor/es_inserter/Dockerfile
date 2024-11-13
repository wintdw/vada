FROM python
WORKDIR /app
RUN pip install --no-cache-dir confluent_kafka asyncio uvicorn fastapi aiohttp
COPY *.py .
EXPOSE 8002
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8002"]