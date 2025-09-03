# PowerShell script to run tests locally before GitHub push
param(
    [switch]$SkipDocker,
    [switch]$SkipIntegration
)

Write-Host "🚀 Running local tests before GitHub push..." -ForegroundColor Green

# Change to project directory
$ProjectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectDir

# Set PYTHONPATH
$BackendPath = Join-Path $ProjectDir "backend"
$env:PYTHONPATH = $BackendPath

$TestsPassed = 0
$TotalTests = 0

# Function to run command and check result
function Run-TestCommand {
    param(
        [string]$Command,
        [string]$Description,
        [switch]$Optional
    )
    
    Write-Host "`n🔄 $Description..." -ForegroundColor Yellow
    Write-Host "Running: $Command" -ForegroundColor Cyan
    
    $Result = Invoke-Expression $Command
    $ExitCode = $LASTEXITCODE
    
    if ($ExitCode -eq 0) {
        Write-Host "✅ $Description - PASSED" -ForegroundColor Green
        return $true
    } else {
        if ($Optional) {
            Write-Host "⚠️  $Description - SKIPPED (Optional)" -ForegroundColor Yellow
        } else {
            Write-Host "❌ $Description - FAILED" -ForegroundColor Red
        }
        return $false
    }
}

# 1. Install dependencies
$TotalTests++
if (Run-TestCommand "pip install -r requirements.txt" "Installing dependencies") {
    $TestsPassed++
}

# 2. Run unit tests
$TotalTests++
if (Run-TestCommand "python -m pytest backend/test/unit/llms/test.py -v" "Unit tests") {
    $TestsPassed++
}

# 3. Check if Ollama is running (optional for integration tests)
if (-not $SkipIntegration) {
    Write-Host "`n🔍 Checking Ollama server..." -ForegroundColor Yellow
    $OllamaCommand = "python -c ""import requests; requests.get('http://localhost:11434/api/tags', timeout=3)"""
    $OllamaAvailable = Run-TestCommand $OllamaCommand "Ollama server check" -Optional
    
    if ($OllamaAvailable) {
        # 4. Run integration tests
        $TotalTests++
        if (Run-TestCommand "python -m pytest backend/test/integration/llms/test.py -v" "Integration tests") {
            $TestsPassed++
        }
    } else {
        Write-Host "⚠️  Ollama server not available. Skipping integration tests." -ForegroundColor Yellow
        Write-Host "   To run integration tests, start Ollama: ollama serve" -ForegroundColor Cyan
    }
}

# 5. Test Docker build (optional)
if (-not $SkipDocker) {
    Write-Host "`n🐳 Testing Docker build..." -ForegroundColor Yellow
    $TotalTests++
    
    # Check if Docker is running
    $DockerRunning = $false
    try {
        $null = docker version
        $DockerRunning = $true
    } catch {
        Write-Host "⚠️  Docker not running. Skipping Docker build test." -ForegroundColor Yellow
    }
    
    if ($DockerRunning) {
        if (Run-TestCommand "docker build -t ai-recruitment-test ." "Docker build test") {
            $TestsPassed++
            # Clean up test image
            docker rmi ai-recruitment-test 2>$null
        }
    }
}

# Summary
Write-Host "`n📊 Test Summary: $TestsPassed/$TotalTests passed" -ForegroundColor Cyan

if ($TestsPassed -eq $TotalTests) {
    Write-Host "🎉 All tests passed! Ready to push to GitHub." -ForegroundColor Green
    exit 0
} else {
    Write-Host "💥 Some tests failed. Please fix before pushing." -ForegroundColor Red
    exit 1
}
