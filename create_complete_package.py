#!/usr/bin/env python3
"""
Complete Package Creator for Stress-Strain Graph Analyzer
Creates a clean, ready-to-use zip file with all necessary components
"""

import os
import zipfile
import shutil
from datetime import datetime

def create_complete_package():
    """
    Creates a comprehensive, clean package with everything needed to run the application
    """
    
    # Package name
    package_name = "stress_strain_analyzer_complete"
    zip_filename = f"{package_name}.zip"
    
    print("🚀 Creating Complete Stress-Strain Graph Analyzer Package")
    print("=" * 60)
    
    # Remove old zip if exists
    if os.path.exists(zip_filename):
        os.remove(zip_filename)
        print(f"🗑️  Removed old package: {zip_filename}")
    
    # Core application files
    core_files = [
        'app.py',
        'graph_processor.py', 
        'run.py',
        'requirements.txt',
        'README.md',
        'test_cv.py'
    ]
    
    # Template files
    template_files = [
        'templates/index.html',
        'templates/results.html'
    ]
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        
        # Add core files
        for file in core_files:
            if os.path.exists(file):
                zipf.write(file)
                print(f"✅ Added: {file}")
        
        # Add template files
        for file in template_files:
            if os.path.exists(file):
                zipf.write(file)
                print(f"✅ Added: {file}")
        
        # Create installation script for Linux/Mac
        install_script = '''#!/bin/bash
echo "🚀 Installing Stress-Strain Graph Analyzer..."
echo "================================================"

# Check Python version
python3 --version || { echo "❌ Python 3 is required"; exit 1; }

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Create directories
echo "📁 Creating directories..."
mkdir -p uploads outputs

# Test installation
echo "🔍 Testing installation..."
python test_cv.py

echo ""
echo "🎉 Installation Complete!"
echo "🚀 To start the application:"
echo "   source venv/bin/activate"
echo "   python run.py"
echo ""
echo "📱 Then open: http://localhost:5000"
echo "================================================"
'''
        
        zipf.writestr('install.sh', install_script)
        print("✅ Added: install.sh")
        
        # Create installation script for Windows
        install_bat = '''@echo off
echo Installing Stress-Strain Graph Analyzer...
echo ================================================

REM Check Python
python --version >nul 2>&1 || (echo Python is required & exit /b 1)

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv
call venv\\Scripts\\activate.bat

REM Upgrade pip
echo Upgrading pip...
pip install --upgrade pip

REM Install requirements
echo Installing dependencies...
pip install -r requirements.txt

REM Create directories
echo Creating directories...
mkdir uploads 2>nul
mkdir outputs 2>nul

REM Test installation
echo Testing installation...
python test_cv.py

echo.
echo Installation Complete!
echo To start the application:
echo   venv\\Scripts\\activate.bat
echo   python run.py
echo.
echo Then open: http://localhost:5000
echo ================================================
'''
        
        zipf.writestr('install.bat', install_bat)
        print("✅ Added: install.bat")
        
        # Create quick start guide
        quick_start = '''# 🚀 QUICK START GUIDE

## Your Stress-Strain Graph Analyzer is Ready!

### 📥 What You Downloaded:
- Complete web application for analyzing stress-strain graphs
- Advanced computer vision that accurately detects plot lines
- Solves the "too many lines detected" problem with smart clustering
- Exports data to Excel with separate sheets per temperature line
- Shows annotated images of detected points

### 🛠️ Installation (Choose Your OS):

#### 🐧 Linux/Mac:
```bash
# Extract this zip file first, then:
chmod +x install.sh
./install.sh
```

#### 🪟 Windows:
```cmd
# Extract this zip file first, then:
install.bat
```

### 🚀 Running the Application:

#### Linux/Mac:
```bash
source venv/bin/activate
python run.py
```

#### Windows:
```cmd
venv\\Scripts\\activate.bat
python run.py
```

### 📱 Using the App:
1. Open: http://localhost:5000
2. Upload your stress-strain graph image
3. Download Excel file with extracted data
4. Download annotated image showing detected points

### 🎯 Key Features:
- ✅ Accurate line counting (no more 20 lines when you have 5!)
- ✅ Ignores legends and temperature indicators
- ✅ Groups similar colored pixels into single lines
- ✅ Excel output with data organized by temperature
- ✅ Visual verification of detected points

### 🆘 Need Help?
- Run: `python test_cv.py` to verify installation
- Check README.md for detailed documentation
- All code is well-commented for easy understanding

### 🎉 You're Ready to Analyze!
Upload your graphs and get accurate, structured data in seconds!
'''
        
        zipf.writestr('QUICK_START.md', quick_start)
        print("✅ Added: QUICK_START.md")
        
        # Create sample requirements for offline installation
        offline_reqs = '''# Alternative requirements for offline installation
# If online installation fails, try installing these one by one:

pip install Flask==2.3.3
pip install opencv-python==4.8.1.78  
pip install numpy==1.24.3
pip install pandas==2.0.3
pip install scikit-learn==1.3.0
pip install matplotlib==3.7.2
pip install Pillow==10.0.0
pip install openpyxl==3.1.2
pip install Werkzeug==2.3.7

# For older Python versions, try:
pip install Flask>=2.0.0
pip install opencv-python>=4.5.0
pip install numpy>=1.21.0
pip install pandas>=1.3.0
pip install scikit-learn>=1.0.0
pip install matplotlib>=3.5.0
pip install Pillow>=8.0.0
pip install openpyxl>=3.0.0
pip install Werkzeug>=2.0.0
'''
        
        zipf.writestr('requirements_offline.txt', offline_reqs)
        print("✅ Added: requirements_offline.txt")
    
    # Get file size
    file_size = os.path.getsize(zip_filename)
    file_size_kb = file_size / 1024
    
    print("=" * 60)
    print(f"🎉 SUCCESS! Complete package created!")
    print(f"📁 File: {zip_filename}")
    print(f"📏 Size: {file_size_kb:.1f} KB")
    print(f"📍 Location: {os.path.abspath(zip_filename)}")
    print("=" * 60)
    print("🚀 READY TO DOWNLOAD AND USE ON YOUR SETUP!")
    
    return zip_filename

if __name__ == "__main__":
    try:
        package_file = create_complete_package()
        print(f"\n✅ Download this file: {package_file}")
        print("📋 Extract it and run install.sh (Linux/Mac) or install.bat (Windows)")
    except Exception as e:
        print(f"❌ Error creating package: {e}")