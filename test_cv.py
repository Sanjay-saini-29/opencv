#!/usr/bin/env python3
"""
Test script to verify OpenCV installation and basic computer vision functionality.
This script tests all the major components used in the graph analyzer.
"""

import sys
import cv2
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import DBSCAN
import pandas as pd
from PIL import Image
import os

def test_opencv():
    """Test OpenCV installation and basic functionality"""
    print("🔍 Testing OpenCV...")
    try:
        # Test OpenCV version
        cv_version = cv2.__version__
        print(f"   ✅ OpenCV version: {cv_version}")
        
        # Test basic image operations
        test_image = np.zeros((100, 100, 3), dtype=np.uint8)
        test_image[25:75, 25:75] = [255, 0, 0]  # Red square
        
        # Test color conversion
        gray = cv2.cvtColor(test_image, cv2.COLOR_BGR2GRAY)
        print(f"   ✅ Color conversion working - Gray image shape: {gray.shape}")
        
        # Test edge detection
        edges = cv2.Canny(gray, 50, 150)
        print(f"   ✅ Edge detection working - Found {np.sum(edges > 0)} edge pixels")
        
        return True
        
    except Exception as e:
        print(f"   ❌ OpenCV test failed: {e}")
        return False

def test_numpy():
    """Test NumPy functionality"""
    print("🔢 Testing NumPy...")
    try:
        np_version = np.__version__
        print(f"   ✅ NumPy version: {np_version}")
        
        # Test array operations
        test_array = np.random.rand(100, 100)
        mean_val = np.mean(test_array)
        print(f"   ✅ Array operations working - Mean: {mean_val:.4f}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ NumPy test failed: {e}")
        return False

def test_sklearn():
    """Test scikit-learn clustering functionality"""
    print("🧠 Testing scikit-learn...")
    try:
        from sklearn import __version__ as sklearn_version
        print(f"   ✅ scikit-learn version: {sklearn_version}")
        
        # Test DBSCAN clustering
        test_data = np.random.rand(50, 2)
        clustering = DBSCAN(eps=0.3, min_samples=3).fit(test_data)
        n_clusters = len(set(clustering.labels_)) - (1 if -1 in clustering.labels_ else 0)
        print(f"   ✅ DBSCAN clustering working - Found {n_clusters} clusters")
        
        return True
        
    except Exception as e:
        print(f"   ❌ scikit-learn test failed: {e}")
        return False

def test_matplotlib():
    """Test matplotlib functionality"""
    print("📊 Testing matplotlib...")
    try:
        import matplotlib
        plt_version = matplotlib.__version__
        print(f"   ✅ matplotlib version: {plt_version}")
        
        # Test basic plotting (without display)
        plt.ioff()  # Turn off interactive mode
        fig, ax = plt.subplots()
        x = np.linspace(0, 10, 100)
        y = np.sin(x)
        ax.plot(x, y)
        plt.close(fig)
        print("   ✅ Basic plotting working")
        
        return True
        
    except Exception as e:
        print(f"   ❌ matplotlib test failed: {e}")
        return False

def test_pandas():
    """Test pandas functionality"""
    print("🐼 Testing pandas...")
    try:
        pd_version = pd.__version__
        print(f"   ✅ pandas version: {pd_version}")
        
        # Test DataFrame operations
        test_df = pd.DataFrame({
            'x': np.random.rand(10),
            'y': np.random.rand(10),
            'line': np.random.randint(0, 3, 10)
        })
        grouped = test_df.groupby('line').size()
        print(f"   ✅ DataFrame operations working - Groups: {len(grouped)}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ pandas test failed: {e}")
        return False

def test_pil():
    """Test PIL/Pillow functionality"""
    print("🖼️ Testing PIL/Pillow...")
    try:
        from PIL import __version__ as pil_version
        print(f"   ✅ Pillow version: {pil_version}")
        
        # Test image creation and manipulation
        test_img = Image.new('RGB', (100, 100), color='red')
        test_array = np.array(test_img)
        print(f"   ✅ Image operations working - Image shape: {test_array.shape}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ PIL test failed: {e}")
        return False

def create_sample_graph():
    """Create a sample stress-strain graph for testing"""
    print("📈 Creating sample stress-strain graph...")
    try:
        # Create figure
        plt.ioff()
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Generate sample stress-strain curves for different temperatures
        strain = np.linspace(0, 0.1, 100)
        
        # Different temperature curves
        temperatures = [20, 50, 100, 150, 200]  # Celsius
        colors = ['blue', 'green', 'red', 'orange', 'purple']
        
        for temp, color in zip(temperatures, colors):
            # Simple stress-strain relationship with temperature effect
            modulus = 200000 - temp * 500  # Young's modulus decreases with temperature
            stress = modulus * strain * (1 + 0.5 * strain)  # Non-linear relationship
            
            ax.plot(strain * 100, stress / 1000, color=color, linewidth=2, 
                   label=f'{temp}°C')
        
        ax.set_xlabel('Strain (%)')
        ax.set_ylabel('Stress (MPa)')
        ax.set_title('Stress-Strain Curves at Different Temperatures')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Save the sample graph
        sample_path = 'sample_stress_strain_graph.png'
        plt.savefig(sample_path, dpi=300, bbox_inches='tight')
        plt.close(fig)
        
        if os.path.exists(sample_path):
            print(f"   ✅ Sample graph created: {sample_path}")
            return sample_path
        else:
            print("   ❌ Failed to create sample graph")
            return None
            
    except Exception as e:
        print(f"   ❌ Sample graph creation failed: {e}")
        return None

def main():
    """Run all tests"""
    print("🧪 Starting Computer Vision Library Tests")
    print("=" * 60)
    
    tests = [
        test_numpy,
        test_opencv,
        test_sklearn,
        test_matplotlib,
        test_pandas,
        test_pil
    ]
    
    results = []
    for test_func in tests:
        result = test_func()
        results.append(result)
        print()
    
    # Create sample graph
    sample_path = create_sample_graph()
    
    print("=" * 60)
    print("📊 Test Summary:")
    print(f"   ✅ Passed: {sum(results)}/{len(results)} tests")
    print(f"   ❌ Failed: {len(results) - sum(results)}/{len(results)} tests")
    
    if all(results):
        print("🎉 All tests passed! The application should work correctly.")
        if sample_path:
            print(f"📸 You can test the application with the sample graph: {sample_path}")
    else:
        print("⚠️ Some tests failed. Please check the installation.")
        
    print("=" * 60)
    return all(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)