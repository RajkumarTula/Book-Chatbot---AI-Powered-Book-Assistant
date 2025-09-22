#!/usr/bin/env python3
"""
Setup script for the Book Chatbot project.
This script automates the installation and setup process.
"""

import os
import sys
import subprocess
import platform
import json
from pathlib import Path

def run_command(command, cwd=None, check=True):
    """Run a command and return the result."""
    print(f"Running: {command}")
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            cwd=cwd, 
            check=check,
            capture_output=True, 
            text=True
        )
        if result.stdout:
            print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        return e

def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ is required. Current version:", f"{version.major}.{version.minor}")
        return False
    print(f"✅ Python {version.major}.{version.minor} detected")
    return True

def check_node_version():
    """Check if Node.js is installed."""
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Node.js {result.stdout.strip()} detected")
            return True
    except FileNotFoundError:
        pass
    
    print("❌ Node.js not found. Please install Node.js 16+ from https://nodejs.org/")
    return False

def check_redis():
    """Check if Redis is available."""
    try:
        result = subprocess.run(["redis-cli", "ping"], capture_output=True, text=True)
        if result.returncode == 0 and "PONG" in result.stdout:
            print("✅ Redis is running")
            return True
    except FileNotFoundError:
        pass
    
    print("❌ Redis not found or not running")
    print("Please install and start Redis:")
    if platform.system() == "Windows":
        print("  - Download from: https://github.com/microsoftarchive/redis/releases")
        print("  - Or use Chocolatey: choco install redis-64")
    elif platform.system() == "Darwin":  # macOS
        print("  - brew install redis")
        print("  - brew services start redis")
    else:  # Linux
        print("  - sudo apt install redis-server")
        print("  - sudo systemctl start redis")
    return False

def create_virtual_environment():
    """Create Python virtual environment."""
    if os.path.exists("venv"):
        print("✅ Virtual environment already exists")
        return True
    
    print("Creating virtual environment...")
    result = run_command("python -m venv venv")
    if result.returncode == 0:
        print("✅ Virtual environment created")
        return True
    else:
        print("❌ Failed to create virtual environment")
        return False

def activate_virtual_environment():
    """Get the activation command for the virtual environment."""
    if platform.system() == "Windows":
        return "venv\\Scripts\\activate"
    else:
        return "source venv/bin/activate"

def install_python_dependencies():
    """Install Python dependencies."""
    print("Installing Python dependencies...")
    
    # Determine pip command based on platform
    if platform.system() == "Windows":
        pip_cmd = "venv\\Scripts\\pip"
    else:
        pip_cmd = "venv/bin/pip"
    
    # Upgrade pip first
    run_command(f"{pip_cmd} install --upgrade pip")
    
    # Install requirements
    result = run_command(f"{pip_cmd} install -r requirements.txt")
    if result.returncode == 0:
        print("✅ Python dependencies installed")
        return True
    else:
        print("❌ Failed to install Python dependencies")
        return False

def install_react_dependencies():
    """Install React dependencies."""
    if not os.path.exists("react-frontend"):
        print("❌ React frontend directory not found")
        return False
    
    print("Installing React dependencies...")
    result = run_command("npm install", cwd="react-frontend")
    if result.returncode == 0:
        print("✅ React dependencies installed")
        return True
    else:
        print("❌ Failed to install React dependencies")
        return False

def create_env_file():
    """Create .env file with default values."""
    env_file = Path(".env")
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    print("Creating .env file...")
    env_content = """# Google Books API (optional but recommended for higher rate limits)
GOOGLE_BOOKS_API_KEY=your_api_key_here

# OpenAI API (for LangChain RAG)
OPENAI_API_KEY=your_openai_api_key_here

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
"""
    
    with open(env_file, "w") as f:
        f.write(env_content)
    
    print("✅ .env file created")
    print("⚠️  Please edit .env file and add your API keys")
    return True

def train_rasa_model():
    """Train the Rasa model."""
    if not os.path.exists("Booky"):
        print("❌ Rasa directory not found")
        return False
    
    print("Training Rasa model...")
    result = run_command("rasa train", cwd="Booky")
    if result.returncode == 0:
        print("✅ Rasa model trained successfully")
        return True
    else:
        print("❌ Failed to train Rasa model")
        return False

def generate_test_data():
    """Generate test data."""
    if not os.path.exists("test_data/generate_test_data.py"):
        print("❌ Test data generator not found")
        return False
    
    print("Generating test data...")
    result = run_command("python test_data/generate_test_data.py")
    if result.returncode == 0:
        print("✅ Test data generated")
        return True
    else:
        print("❌ Failed to generate test data")
        return False

def create_start_scripts():
    """Create start scripts for different platforms."""
    print("Creating start scripts...")
    
    # Windows batch script
    windows_script = """@echo off
echo Starting Book Chatbot Services...

echo Starting Redis...
start "Redis" redis-server

echo Starting Rasa Action Server...
start "Rasa Actions" cmd /k "cd Booky && venv\\Scripts\\activate && rasa run actions"

echo Starting Rasa Server...
start "Rasa Server" cmd /k "cd Booky && venv\\Scripts\\activate && rasa run --enable-api --cors *"

echo Starting FastAPI Server...
start "FastAPI Server" cmd /k "venv\\Scripts\\activate && python api_server.py"

echo Starting React Frontend...
start "React Frontend" cmd /k "cd react-frontend && npm start"

echo All services started!
pause
"""
    
    with open("start_services.bat", "w") as f:
        f.write(windows_script)
    
    # Unix shell script
    unix_script = """#!/bin/bash
echo "Starting Book Chatbot Services..."

echo "Starting Redis..."
redis-server &
REDIS_PID=$!

echo "Starting Rasa Action Server..."
cd Booky
source ../venv/bin/activate
rasa run actions &
RASA_ACTIONS_PID=$!

echo "Starting Rasa Server..."
rasa run --enable-api --cors "*" &
RASA_SERVER_PID=$!

cd ..

echo "Starting FastAPI Server..."
source venv/bin/activate
python api_server.py &
API_PID=$!

echo "Starting React Frontend..."
cd react-frontend
npm start &
REACT_PID=$!

cd ..

echo "All services started!"
echo "Press Ctrl+C to stop all services"

# Function to cleanup on exit
cleanup() {
    echo "Stopping services..."
    kill $REDIS_PID $RASA_ACTIONS_PID $RASA_SERVER_PID $API_PID $REACT_PID 2>/dev/null
    exit
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Wait for all background processes
wait
"""
    
    with open("start_services.sh", "w") as f:
        f.write(unix_script)
    
    # Make shell script executable
    if platform.system() != "Windows":
        os.chmod("start_services.sh", 0o755)
    
    print("✅ Start scripts created")
    return True

def main():
    """Main setup function."""
    print("🚀 Book Chatbot Setup Script")
    print("=" * 50)
    
    # Check prerequisites
    if not check_python_version():
        sys.exit(1)
    
    if not check_node_version():
        print("⚠️  Node.js not found. React frontend will not be available.")
    
    # Create virtual environment
    if not create_virtual_environment():
        sys.exit(1)
    
    # Install Python dependencies
    if not install_python_dependencies():
        sys.exit(1)
    
    # Install React dependencies (optional)
    if check_node_version():
        install_react_dependencies()
    
    # Create .env file
    create_env_file()
    
    # Train Rasa model
    if not train_rasa_model():
        print("⚠️  Rasa model training failed. You may need to train it manually.")
    
    # Generate test data
    generate_test_data()
    
    # Create start scripts
    create_start_scripts()
    
    print("\n" + "=" * 50)
    print("✅ Setup completed successfully!")
    print("\nNext steps:")
    print("1. Edit .env file and add your API keys")
    print("2. Start Redis: redis-server")
    print("3. Run the application:")
    if platform.system() == "Windows":
        print("   - Double-click start_services.bat")
        print("   - Or run: start_services.bat")
    else:
        print("   - Run: ./start_services.sh")
    print("\n4. Access the application:")
    print("   - Vanilla frontend: http://localhost:8000")
    print("   - React frontend: http://localhost:3000")
    print("   - API documentation: http://localhost:8000/docs")

if __name__ == "__main__":
    main()



