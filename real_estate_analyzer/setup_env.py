#!/usr/bin/env python3
"""
Environment setup script for Real Estate Analyzer.
This script helps users create a .env file with the appropriate settings.
"""

import os
import shutil
from pathlib import Path


def setup_environment_file():
    """Create a .env file based on the template."""
    project_root = Path(__file__).parent
    config_template = project_root / 'config.env'
    env_file = project_root / '.env'
    
    print("🔧 Real Estate Analyzer Environment Setup")
    print("=" * 50)
    
    # Check if template exists
    if not config_template.exists():
        print(f"❌ Template file not found: {config_template}")
        return False
    
    # Check if .env already exists
    if env_file.exists():
        response = input(f"📁 .env file already exists. Overwrite? (y/N): ")
        if response.lower() not in ['y', 'yes']:
            print("✅ Keeping existing .env file")
            return True
    
    try:
        # Copy template to .env
        shutil.copy2(config_template, env_file)
        print(f"✅ Created .env file: {env_file}")
        
        # Show the contents
        print("\n📋 Current .env file contents:")
        print("-" * 30)
        with open(env_file, 'r') as f:
            content = f.read()
            print(content)
        
        print("\n🎯 Next Steps:")
        print("1. Review the .env file and modify values as needed")
        print("2. Set DEBUG=false for production deployment")
        print("3. Adjust PORT if 8051 is already in use")
        print("4. Run: pip install -r requirements.txt")
        print("5. Start the application!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False


def check_requirements():
    """Check if required packages are installed."""
    try:
        import dotenv
        print("✅ python-dotenv is installed")
        return True
    except ImportError:
        print("⚠️  python-dotenv not found. Install with:")
        print("   pip install python-dotenv")
        print("   Or: pip install -r requirements.txt")
        return False


def main():
    """Main setup function."""
    print("🚀 Setting up Real Estate Analyzer environment...")
    
    # Setup environment file
    env_success = setup_environment_file()
    
    # Check requirements
    print("\n🔍 Checking requirements...")
    req_success = check_requirements()
    
    if env_success and req_success:
        print("\n🎉 Environment setup complete!")
        print("   You can now run the Real Estate Analyzer application.")
    elif env_success:
        print("\n⚠️  Environment file created, but please install requirements:")
        print("   pip install -r requirements.txt")
    else:
        print("\n❌ Setup failed. Please check the errors above.")


if __name__ == "__main__":
    main() 