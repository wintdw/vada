FROM python:3.11.11-alpine
WORKDIR /app
RUN pip install --no-cache-dir requests mysql-connector-python cryptography
COPY . .
CMD ["python", "datasync.py"]
