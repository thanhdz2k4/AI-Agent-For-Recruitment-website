# Sử dụng Python 3.11 slim image
FROM python:3.11-slim

# Thiết lập working directory
WORKDIR /app

# Copy requirements và install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code and frontend templates
COPY backend/ ./backend/
COPY frontend/ ./frontend/

# Set PYTHONPATH để có thể import modules
ENV PYTHONPATH=/app/backend

# Set Docker environment flag and Ollama URL for container
ENV DOCKER_ENV=true
ENV OLLAMA_URL=http://host.docker.internal:11434
ENV OLLAMA_MODEL=hf.co/Cactus-Compute/Qwen3-1.7B-Instruct-GGUF:Q4_K_M

# Expose port
EXPOSE 5000

# Command to run the application
CMD ["python", "backend/app/main.py"]
