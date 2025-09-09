"""
Quick setup verification script for the Agentic Query System.
Run this to check if everything is ready before starting the application.
"""
import os
import sys
from pathlib import Path


def check_files():
    """Check if all required files exist."""
    required_files = [
        "main.py",
        "streamlit_app.py", 
        "data_loader.py",
        "tools_runtime.py",
        "openai_tools.py",
        "requirements.txt",
        "Data/Table_feeds_v2.csv",
        "Data/encoder_params.json",
        "Data/encoder_schema.json",
        "Data/decoder_params.json",
        "Data/decoder_schema.json"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Missing required files:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    else:
        print("✅ All required files present")
        return True


def check_python_packages():
    """Check if required Python packages are installed."""
    required_packages = [
        "fastapi",
        "uvicorn", 
        "streamlit",
        "pandas",
        "openai",
        "jsonschema",
        "requests",
        "pydantic"
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\nTo install missing packages, run:")
        print("pip install -r requirements.txt")
        return False
    else:
        print("✅ All required packages installed")
        return True


def check_openai_key():
    """Check if OpenAI API key is configured."""
    # Try to load from .env file
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("❌ OpenAI API key not found")
        print("\nTo set up your API key:")
        print("1. Get your API key from: https://platform.openai.com/api-keys")
        print("2. Set it as environment variable:")
        print("   Windows: set OPENAI_API_KEY=your_key_here")
        print("   Linux/Mac: export OPENAI_API_KEY=your_key_here")
        print("3. Or create a .env file (copy from .env.example)")
        return False
    elif api_key == "your_openai_api_key_here":
        print("❌ OpenAI API key is still placeholder")
        print("Please replace 'your_openai_api_key_here' with your actual API key")
        return False
    else:
        print("✅ OpenAI API key is configured")
        return True


def test_data_loading():
    """Test if data can be loaded successfully."""
    try:
        from data_loader import data_loader
        data_loader.load_all_data()
        
        feeds_count = len(data_loader.get_feeds_dataframe())
        encoder_params = len(data_loader.get_encoder_params())
        decoder_params = len(data_loader.get_decoder_params())
        
        print(f"✅ Data loading successful:")
        print(f"   - Camera feeds: {feeds_count} records")
        print(f"   - Encoder params: {encoder_params} parameters")
        print(f"   - Decoder params: {decoder_params} parameters")
        return True
        
    except Exception as e:
        print(f"❌ Data loading failed: {e}")
        return False


def main():
    """Run all setup checks."""
    print("🎥 Agentic Query System - Setup Verification")
    print("=" * 50)
    
    checks = [
        ("Files", check_files),
        ("Python Packages", check_python_packages), 
        ("OpenAI API Key", check_openai_key),
        ("Data Loading", test_data_loading)
    ]
    
    all_passed = True
    
    for check_name, check_func in checks:
        print(f"\n🔍 Checking {check_name}...")
        if not check_func():
            all_passed = False
    
    print("\n" + "=" * 50)
    
    if all_passed:
        print("🎉 All checks passed! You're ready to run the application.")
        print("\nTo start the application:")
        print("1. Run: python start.py")
        print("   OR")
        print("2. Run manually:")
        print("   - Backend: python main.py")
        print("   - Frontend: streamlit run streamlit_app.py")
    else:
        print("❌ Some checks failed. Please fix the issues above before running the application.")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
