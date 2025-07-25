#!/usr/bin/env python3
"""
Script to create a downloadable zip file of the Stress-Strain Graph Analyzer application.
This packages all necessary files for distribution and deployment.
"""

import os
import zipfile
import shutil
from datetime import datetime

def create_application_zip():
    """
    Creates a comprehensive zip file containing the entire application.
    Excludes unnecessary files like virtual environments and cache files.
    """
    
    # Define the zip filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_filename = f"stress_strain_analyzer_{timestamp}.zip"
    
    # Files and directories to include
    files_to_include = [
        'app.py',
        'graph_processor.py',
        'run.py',
        'setup.py',
        'test_cv.py',
        'requirements.txt',
        'README.md',
        'DEPLOYMENT_GUIDE.md',
        'templates/',
        'sample_graph.png'
    ]
    
    # Files and directories to exclude
    exclude_patterns = [
        '__pycache__',
        '*.pyc',
        '.git',
        'venv/',
        'env/',
        '.env',
        'uploads/',
        'outputs/',
        '*.zip'
    ]
    
    print(f"📦 Creating zip file: {zip_filename}")
    print("=" * 50)
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add individual files
        for item in files_to_include:
            if os.path.isfile(item):
                zipf.write(item)
                print(f"✅ Added file: {item}")
            elif os.path.isdir(item):
                # Add directory and all its contents
                for root, dirs, files in os.walk(item):
                    # Skip excluded directories
                    dirs[:] = [d for d in dirs if not any(pattern in d for pattern in exclude_patterns)]
                    
                    for file in files:
                        # Skip excluded files
                        if not any(pattern in file for pattern in exclude_patterns):
                            file_path = os.path.join(root, file)
                            zipf.write(file_path)
                            print(f"✅ Added: {file_path}")
        
        # Create a deployment script inside the zip
        deployment_script = """#!/bin/bash
# Quick deployment script for Stress-Strain Graph Analyzer

echo "🚀 Setting up Stress-Strain Graph Analyzer..."

# Create virtual environment
python3 -m venv venv
echo "✅ Virtual environment created"

# Activate virtual environment and install dependencies
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Dependencies installed"

# Create necessary directories
mkdir -p uploads outputs
echo "✅ Directories created"

# Test the installation
echo "🔍 Testing installation..."
python test_cv.py

echo ""
echo "🎉 Setup complete!"
echo "💡 To start the application:"
echo "   source venv/bin/activate"
echo "   python run.py"
echo ""
echo "📱 Then open: http://localhost:5000"
"""
        
        zipf.writestr('deploy.sh', deployment_script)
        print("✅ Added: deploy.sh")
        
        # Create a Windows batch file
        windows_script = """@echo off
echo Setting up Stress-Strain Graph Analyzer...

REM Create virtual environment
python -m venv venv
echo Virtual environment created

REM Activate virtual environment and install dependencies
call venv\\Scripts\\activate.bat
pip install --upgrade pip
pip install -r requirements.txt
echo Dependencies installed

REM Create necessary directories
mkdir uploads 2>nul
mkdir outputs 2>nul
echo Directories created

REM Test the installation
echo Testing installation...
python test_cv.py

echo.
echo Setup complete!
echo To start the application:
echo   venv\\Scripts\\activate.bat
echo   python run.py
echo.
echo Then open: http://localhost:5000
"""
        
        zipf.writestr('deploy.bat', windows_script)
        print("✅ Added: deploy.bat")
    
    # Get file size
    file_size = os.path.getsize(zip_filename)
    file_size_mb = file_size / (1024 * 1024)
    
    print("=" * 50)
    print(f"🎉 SUCCESS! Zip file created: {zip_filename}")
    print(f"📏 File size: {file_size_mb:.2f} MB")
    print(f"📍 Location: {os.path.abspath(zip_filename)}")
    
    return zip_filename

if __name__ == "__main__":
    try:
        zip_file = create_application_zip()
        print(f"\n✅ Ready to download: {zip_file}")
    except Exception as e:
        print(f"❌ Error creating zip file: {e}")