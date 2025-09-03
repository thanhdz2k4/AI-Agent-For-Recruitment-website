# AI Agent for Recruitment Website

## 🚀 CI/CD Pipeline

Project này sử dụng GitHub Actions để tự động chạy tests và build Docker image.

### Pipeline Flow:

1. **Unit Tests** - Chạy tất cả unit tests
2. **Integration Tests** - Chạy integration tests với Ollama
3. **Docker Build** - Build và push Docker image lên GitHub Container Registry (chỉ khi push vào main branch)

### 📋 Requirements

- Python 3.11+
- Docker
- Ollama (cho integration tests)

### 🧪 Running Tests Locally

#### Cách 1: Chạy script tự động
```bash
cd "AI Agent for recruitment website"
python run_tests.py
```

#### Cách 2: Chạy từng loại test
```bash
cd "AI Agent for recruitment website"

# Install dependencies
pip install -r requirements.txt

# Set PYTHONPATH
export PYTHONPATH=$(pwd)/backend  # Linux/Mac
# or
$env:PYTHONPATH="$(pwd)/backend"  # PowerShell

# Run unit tests
python -m pytest backend/test/unit/ -v

# Run integration tests (cần Ollama chạy)
python -m pytest backend/test/integration/ -v

# Run all tests
python -m pytest backend/test/ -v
```

### 🐳 Docker

#### Build locally:
```bash
cd "AI Agent for recruitment website"
docker build -t ai-recruitment .
```

#### Run container:
```bash
docker run -p 5000:5000 ai-recruitment
```

### 🔧 Setup Ollama cho Integration Tests

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama
ollama serve

# Pull model (trong terminal khác)
ollama pull tinyllama:latest
# hoặc
ollama pull llama2
```

### 📦 GitHub Container Registry

Sau khi push vào main branch, Docker image sẽ được build và push tự động tới:
```
ghcr.io/thanhdz2k4/ai-agent-for-recruitment-website:latest
```

### 🏗️ Project Structure

```
AI Agent for recruitment website/
├── .github/workflows/ci-cd.yml    # GitHub Actions pipeline
├── backend/
│   ├── llms/                      # LLM implementations
│   ├── test/
│   │   ├── unit/                  # Unit tests
│   │   └── integration/           # Integration tests
│   └── app/                       # Main application
├── requirements.txt               # Python dependencies
├── Dockerfile                     # Docker configuration
├── pytest.ini                    # Pytest configuration
└── run_tests.py                   # Local test runner
```

### 🔍 Test Guidelines

#### Unit Tests:
- Test individual functions/methods
- Use mocking cho external dependencies
- Fast execution

#### Integration Tests:
- Test với real services (Ollama)
- Test end-to-end workflows
- Có thể chậm hơn

### 🚨 Troubleshooting

#### Tests fail locally:
1. Kiểm tra PYTHONPATH đã set đúng chưa
2. Kiểm tra dependencies đã install đủ chưa
3. Cho integration tests, kiểm tra Ollama có chạy không

#### CI/CD fails:
1. Kiểm tra GitHub Actions logs
2. Đảm bảo tests pass locally trước
3. Kiểm tra dependencies trong requirements.txt

### 📝 Contributing

1. Tạo feature branch từ `main`
2. Viết tests cho code mới
3. Chạy `python run_tests.py` để kiểm tra
4. Tạo Pull Request
5. CI/CD sẽ tự động chạy tests
6. Merge vào `main` sau khi tests pass
