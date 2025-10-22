import os
import io
import uuid
from flask import Flask, request, render_template, send_file, jsonify, redirect, url_for
from werkzeug.utils import secure_filename
import cv2
import numpy as np
import pandas as pd
from PIL import Image
import matplotlib.pyplot as plt
from graph_processor import GraphProcessor
import json

# Initialize Flask app
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload and output directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'}

def allowed_file(filename):
    """
    Check if the uploaded file has an allowed extension
    
    Args:
        filename (str): Name of the uploaded file
        
    Returns:
        bool: True if file extension is allowed, False otherwise
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """
    Main page route - displays the upload form
    
    Returns:
        HTML template for the main page
    """
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """
    Handle file upload and processing
    
    Returns:
        JSON response with processing results or error message
    """
    try:
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        
        # Check if file was selected
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Check if file type is allowed
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Please upload an image file.'}), 400
        
        # Generate unique filename
        unique_id = str(uuid.uuid4())
        filename = secure_filename(file.filename)
        file_extension = filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{unique_id}.{file_extension}"
        
        # Save uploaded file
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(input_path)
        
        # Get number of expected lines from form (optional)
        expected_lines = request.form.get('expected_lines', type=int)
        
        # Initialize graph processor
        processor = GraphProcessor()
        
        # Process the graph image
        result = processor.process_graph(
            input_path, 
            expected_lines=expected_lines,
            output_folder=app.config['OUTPUT_FOLDER'],
            unique_id=unique_id
        )
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': 'Graph processed successfully!',
                'data': {
                    'lines_detected': result['lines_detected'],
                    'total_points': result['total_points'],
                    'xlsx_file': result['xlsx_filename'],
                    'annotated_image': result['annotated_image_filename'],
                    'unique_id': unique_id
                }
            })
        else:
            return jsonify({'error': result['error']}), 500
            
    except Exception as e:
        return jsonify({'error': f'Processing failed: {str(e)}'}), 500

@app.route('/download/<file_type>/<unique_id>')
def download_file(file_type, unique_id):
    """
    Download processed files (XLSX or annotated image)
    
    Args:
        file_type (str): Type of file to download ('xlsx' or 'image')
        unique_id (str): Unique identifier for the processed files
        
    Returns:
        File download response
    """
    try:
        if file_type == 'xlsx':
            filename = f"{unique_id}_stress_strain_data.xlsx"
            filepath = os.path.join(app.config['OUTPUT_FOLDER'], filename)
            return send_file(filepath, as_attachment=True, download_name=filename)
        
        elif file_type == 'image':
            filename = f"{unique_id}_annotated.png"
            filepath = os.path.join(app.config['OUTPUT_FOLDER'], filename)
            return send_file(filepath, as_attachment=True, download_name=filename)
        
        else:
            return jsonify({'error': 'Invalid file type'}), 400
            
    except Exception as e:
        return jsonify({'error': f'Download failed: {str(e)}'}), 500

@app.route('/download-source')
def download_source():
    """
    Route to download the complete source code as a zip file.
    This allows users to get the entire application for deployment elsewhere.
    """
    try:
        import subprocess
        
        # Run the complete package creation script
        result = subprocess.run(['python3', 'create_complete_package.py'], 
                              capture_output=True, text=True, cwd='.')
        
        if result.returncode != 0:
            return jsonify({'error': 'Failed to create complete package'}), 500
        
        # Check if the complete package exists
        package_file = 'stress_strain_analyzer_complete.zip'
        if not os.path.exists(package_file):
            return jsonify({'error': 'Package file not found'}), 404
        
        return send_file(
            package_file,
            as_attachment=True,
            download_name='stress_strain_analyzer_complete.zip',
            mimetype='application/zip'
        )
        
    except Exception as e:
        return jsonify({'error': f'Failed to create download: {str(e)}'}), 500

@app.route('/status')
def status():
    """
    Health check endpoint
    
    Returns:
        JSON response indicating app status
    """
    return jsonify({'status': 'running', 'message': 'Stress-Strain Graph Analyzer is ready!'})

if __name__ == '__main__':
    # Run the Flask app in debug mode
    app.run(debug=True, host='0.0.0.0', port=5000)