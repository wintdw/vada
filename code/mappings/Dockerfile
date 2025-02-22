FROM python
WORKDIR /app
COPY mappings/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY .. .
CMD uvicorn mappings.main:app --host 0.0.0.0 --port $PORT --workers 1