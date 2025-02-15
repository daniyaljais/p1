# Use the official Python image
FROM python:3.11

# Set working directory
WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir uv fastapi uvicorn pandas numpy requests beautifulsoup4

# Copy all scripts
COPY . /app

# Expose the FastAPI server port
EXPOSE 8000

# Run FastAPI
CMD ["uvicorn", "pp2:app", "--host", "0.0.0.0", "--port", "8000"]
