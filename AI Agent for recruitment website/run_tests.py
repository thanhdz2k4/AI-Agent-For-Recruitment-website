#!/usr/bin/env python3
"""
Script để chạy test locally trước khi push lên GitHub
"""
import subprocess
import sys
import os


def run_command(command, description):
    """Chạy command và kiểm tra kết quả"""
    print(f"\n🔄 {description}...")
    print(f"Running: {command}")
    
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✅ {description} - PASSED")
        if result.stdout:
            print(result.stdout)
        return True
    else:
        print(f"❌ {description} - FAILED")
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        return False


def main():
    """Main function để chạy tất cả tests"""
    print("🚀 Running local tests before GitHub push...")
    
    # Change to project directory
    project_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_dir)
    
    # Set PYTHONPATH
    backend_path = os.path.join(project_dir, "backend")
    os.environ["PYTHONPATH"] = backend_path
    
    tests_passed = 0
    total_tests = 0
    
    # 1. Install dependencies
    total_tests += 1
    if run_command("pip install -r requirements.txt", "Installing dependencies"):
        tests_passed += 1
    
    # 2. Run unit tests
    total_tests += 1
    if run_command("python -m pytest backend/test/unit/ -v", "Unit tests"):
        tests_passed += 1
    
    # 3. Check if Ollama is running (optional for integration tests)
    print("\n🔍 Checking Ollama server...")
    ollama_available = run_command(
        "python -c \"import requests; requests.get('http://localhost:11434/api/tags', timeout=3)\"",
        "Ollama server check"
    )
    
    if ollama_available:
        # 4. Run integration tests
        total_tests += 1
        if run_command("python -m pytest backend/test/integration/ -v", "Integration tests"):
            tests_passed += 1
    else:
        print("⚠️  Ollama server not available. Skipping integration tests.")
        print("   To run integration tests, start Ollama: ollama serve")
    
    # 5. Test Docker build (optional)
    print("\n🐳 Testing Docker build...")
    total_tests += 1
    if run_command("docker build -t ai-recruitment-test .", "Docker build test"):
        tests_passed += 1
        # Clean up test image
        subprocess.run("docker rmi ai-recruitment-test", shell=True, capture_output=True)
    
    # Summary
    print(f"\n📊 Test Summary: {tests_passed}/{total_tests} passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! Ready to push to GitHub.")
        return 0
    else:
        print("💥 Some tests failed. Please fix before pushing.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
