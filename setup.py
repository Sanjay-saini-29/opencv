#!/usr/bin/env python3
"""
Setup script for Stress-Strain Graph Analyzer
This script automates the installation process and sets up the required directories.
"""

import os
import sys
import subprocess
import urllib.request

def check_python_version():
    """Check if Python version is 3.8 or higher"""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def create_directories():
    """Create necessary directories for the application"""
    directories = ['uploads', 'outputs', 'templates']
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✅ Created directory: {directory}")
        else:
            print(f"✅ Directory already exists: {directory}")

def install_dependencies():
    """Install Python dependencies from requirements.txt"""
    print("\n📦 Installing Python dependencies...")
    
    try:
        # Upgrade pip first
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'])
        
        # Install requirements
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("✅ All dependencies installed successfully!")
        return True
    
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        print("   Try running: pip install -r requirements.txt manually")
        return False

def test_imports():
    """Test if all required packages can be imported"""
    print("\n🧪 Testing package imports...")
    
    packages = [
        ('cv2', 'OpenCV'),
        ('numpy', 'NumPy'),
        ('pandas', 'Pandas'),
        ('sklearn', 'Scikit-learn'),
        ('flask', 'Flask'),
        ('PIL', 'Pillow'),
        ('openpyxl', 'OpenPyXL')
    ]
    
    all_good = True
    for package, name in packages:
        try:
            __import__(package)
            print(f"✅ {name}")
        except ImportError:
            print(f"❌ {name} - Failed to import")
            all_good = False
    
    return all_good

def check_opencv_issues():
    """Check for common OpenCV issues and provide solutions"""
    print("\n🔍 Checking for OpenCV issues...")
    
    try:
        import cv2
        # Test basic OpenCV functionality
        test_image = cv2.imread('test_dummy.jpg')  # This will return None but shouldn't crash
        print("✅ OpenCV basic functionality test passed")
        
        # Check if we're in a headless environment
        try:
            cv2.namedWindow('test')
            cv2.destroyWindow('test')
            print("✅ OpenCV GUI support available")
        except:
            print("⚠️  OpenCV GUI not available (headless environment)")
            print("   This is fine for web applications")
        
    except Exception as e:
        print(f"⚠️  OpenCV issue detected: {e}")
        print("   If you see 'waiting for opencv to load' errors, try:")
        print("   pip uninstall opencv-python")
        print("   pip install opencv-python-headless")

def create_sample_test_script():
    """Create a simple test script to verify the installation"""
    test_script = """#!/usr/bin/env python3
# Test script for Stress-Strain Graph Analyzer

def test_basic_imports():
    print("Testing basic imports...")
    
    try:
        import cv2
        import numpy as np
        import pandas as pd
        from sklearn.cluster import DBSCAN
        import flask
        from PIL import Image
        import openpyxl
        print("✅ All imports successful!")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_opencv_functionality():
    print("Testing OpenCV functionality...")
    
    try:
        import cv2
        import numpy as np
        
        # Create a test image
        test_img = np.zeros((100, 100, 3), dtype=np.uint8)
        test_img[25:75, 25:75] = [0, 255, 0]  # Green square
        
        # Test basic operations
        gray = cv2.cvtColor(test_img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        print(f"✅ OpenCV test passed - found {len(contours)} contours")
        return True
        
    except Exception as e:
        print(f"❌ OpenCV test failed: {e}")
        return False

def test_graph_processor():
    print("Testing GraphProcessor class...")
    
    try:
        from graph_processor import GraphProcessor
        processor = GraphProcessor()
        print("✅ GraphProcessor imported successfully!")
        return True
    except ImportError as e:
        print(f"❌ GraphProcessor import failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Running Stress-Strain Graph Analyzer Tests\\n")
    
    tests = [
        test_basic_imports,
        test_opencv_functionality, 
        test_graph_processor
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"📊 Test Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All tests passed! The application is ready to use.")
        print("   Run: python app.py to start the web server")
    else:
        print("⚠️  Some tests failed. Check the error messages above.")
"""
    
    with open('test_installation.py', 'w') as f:
        f.write(test_script)
    print("✅ Created test_installation.py")

def main():
    """Main setup function"""
    print("🚀 Setting up Stress-Strain Graph Analyzer")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Create directories
    print("\n📁 Creating directories...")
    create_directories()
    
    # Install dependencies
    if not install_dependencies():
        return False
    
    # Test imports
    if not test_imports():
        print("\n❌ Some packages failed to import. Please check the error messages above.")
        return False
    
    # Check OpenCV issues
    check_opencv_issues()
    
    # Create test script
    print("\n📝 Creating test script...")
    create_sample_test_script()
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Run the test script: python test_installation.py")
    print("2. Start the application: python app.py")
    print("3. Open your browser to: http://localhost:5000")
    print("\n📚 For help, see README.md")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)