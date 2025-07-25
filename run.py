#!/usr/bin/env python3
"""
Startup script for the Stress-Strain Graph Analyzer web application.
This script configures and runs the Flask application with appropriate settings.
"""

import os
import sys
from app import app

def main():
    """
    Main function to start the Flask application.
    Configures environment variables and starts the server.
    """
    
    # Set environment variables for Flask
    os.environ['FLASK_APP'] = 'app.py'
    os.environ['FLASK_ENV'] = 'development'  # Change to 'production' for production use
    
    # Create necessary directories if they don't exist
    directories = ['uploads', 'outputs', 'templates']
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✅ Created directory: {directory}")
    
    # Display startup information
    print("🚀 Starting Stress-Strain Graph Analyzer")
    print("=" * 50)
    print(f"📂 Working directory: {os.getcwd()}")
    print(f"🐍 Python version: {sys.version.split()[0]}")
    print(f"🌐 Server will be available at: http://localhost:5000")
    print("=" * 50)
    print("📊 Features available:")
    print("   • Advanced line detection using computer vision")
    print("   • Smart color clustering to identify distinct lines")
    print("   • Legend area exclusion")
    print("   • Excel export with structured data")
    print("   • Annotated image generation")
    print("=" * 50)
    print("💡 Tips:")
    print("   • Upload clear, high-resolution images for best results")
    print("   • Ensure legends/labels are clearly separated from plot area")
    print("   • Supported formats: PNG, JPG, JPEG, GIF, BMP, TIFF")
    print("=" * 50)
    
    try:
        # Start the Flask development server
        app.run(
            host='0.0.0.0',  # Allow connections from any IP
            port=5000,       # Port number
            debug=True,      # Enable debug mode for development
            threaded=True    # Enable threading for better performance
        )
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()