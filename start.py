"""
Startup script for the Agentic Query System.
Run this to start both the backend and frontend.
"""
import subprocess
import sys
import time
import webbrowser
from pathlib import Path


def check_requirements():
    """Check if required packages are installed."""
    try:
        import fastapi
        import streamlit
        import pandas
        import openai
        import jsonschema
        print("✅ All required packages are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        print("Please run: pip install -r requirements.txt")
        return False


def check_openai_key():
    """Check if OpenAI API key is set."""
    import os
    if os.getenv("OPENAI_API_KEY"):
        print("✅ OpenAI API key is set")
        return True
    else:
        print("❌ OpenAI API key not found")
        print("Please set your OpenAI API key:")
        print("Windows: set OPENAI_API_KEY=your_key_here")
        print("Linux/Mac: export OPENAI_API_KEY=your_key_here")
        return False


def start_backend():
    """Start the FastAPI backend."""
    print("🚀 Starting FastAPI backend...")
    backend_process = subprocess.Popen([
        sys.executable, "main.py"
    ], cwd=Path.cwd())
    
    # Give the backend time to start
    time.sleep(3)
    return backend_process


def start_frontend():
    """Start the Streamlit frontend."""
    print("🚀 Starting Streamlit frontend...")
    frontend_process = subprocess.Popen([
        sys.executable, "-m", "streamlit", "run", "streamlit_app.py"
    ], cwd=Path.cwd())
    
    # Open browser to the Streamlit app
    time.sleep(3)
    webbrowser.open("http://localhost:8501")
    
    return frontend_process


def main():
    """Main startup function."""
    print("🎥 Agentic Query System - Startup Script")
    print("=" * 50)
    
    # Check prerequisites
    if not check_requirements():
        return 1
    
    if not check_openai_key():
        return 1
    
    print("\n📊 Testing data loading...")
    try:
        from data_loader import data_loader
        data_loader.load_all_data()
        print("✅ Data loaded successfully!")
    except Exception as e:
        print(f"❌ Data loading failed: {e}")
        return 1
    
    print("\n🚀 Starting services...")
    
    try:
        # Start backend
        backend = start_backend()
        
        # Start frontend
        frontend = start_frontend()
        
        print("\n✅ Services started successfully!")
        print("🌐 Backend API: http://localhost:8000")
        print("🌐 Frontend UI: http://localhost:8501")
        print("\nPress Ctrl+C to stop both services...")
        
        # Wait for user interrupt
        try:
            backend.wait()
        except KeyboardInterrupt:
            print("\n🛑 Shutting down services...")
            backend.terminate()
            frontend.terminate()
            
    except Exception as e:
        print(f"❌ Error starting services: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
