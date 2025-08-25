FROM python

WORKDIR /app

# Install deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy code & config
COPY service.py config.yaml ./

# Expose FastAPI port
EXPOSE 8500

# Run with uvicorn
CMD ["uvicorn", "service:app", "--host", "0.0.0.0", "--port", "8500"]