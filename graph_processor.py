import cv2
import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont
import os
from collections import defaultdict
import json

class GraphProcessor:
    """
    Advanced graph processing class for extracting stress-strain data from material testing graphs.
    
    This class uses computer vision techniques to:
    1. Detect and separate plot lines from legends and annotations
    2. Cluster similar colored pixels to identify distinct lines
    3. Extract coordinate data points from each line
    4. Generate structured output files (XLSX and annotated images)
    """
    
    def __init__(self):
        """
        Initialize the GraphProcessor with default parameters
        """
        # Color detection parameters
        self.color_threshold = 30  # Threshold for color similarity
        self.min_line_length = 50  # Minimum pixels for a valid line segment
        self.clustering_eps = 15   # DBSCAN clustering parameter
        self.min_samples = 10      # Minimum samples for DBSCAN clustering
        
        # Graph area detection parameters
        self.legend_area_ratio = 0.3  # Ratio of image area likely to contain legends
        self.axis_thickness = 5       # Expected thickness of axis lines
        
        # Output parameters
        self.point_marker_size = 3    # Size of markers in annotated image
        self.line_colors = [          # Colors for different lines in output
            (255, 0, 0),    # Red
            (0, 255, 0),    # Green  
            (0, 0, 255),    # Blue
            (255, 255, 0),  # Yellow
            (255, 0, 255),  # Magenta
            (0, 255, 255),  # Cyan
            (128, 0, 128),  # Purple
            (255, 165, 0),  # Orange
        ]
    
    def detect_graph_area(self, image):
        """
        Detect the main plotting area by identifying axis lines and excluding legend areas
        
        Args:
            image (numpy.ndarray): Input image in BGR format
            
        Returns:
            tuple: (x_min, y_min, x_max, y_max) coordinates of the graph area
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        height, width = gray.shape
        
        # Detect horizontal and vertical lines (likely axis lines)
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (width//20, 1))
        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, height//20))
        
        # Find horizontal lines (x-axis)
        horizontal_lines = cv2.morphologyEx(gray, cv2.MORPH_OPEN, horizontal_kernel)
        horizontal_lines = cv2.dilate(horizontal_lines, np.ones((3,3), np.uint8), iterations=2)
        
        # Find vertical lines (y-axis)
        vertical_lines = cv2.morphologyEx(gray, cv2.MORPH_OPEN, vertical_kernel)
        vertical_lines = cv2.dilate(vertical_lines, np.ones((3,3), np.uint8), iterations=2)
        
        # Find intersection points (likely axis origins)
        intersection = cv2.bitwise_and(horizontal_lines, vertical_lines)
        
        # Find contours of axis lines
        h_contours, _ = cv2.findContours(horizontal_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        v_contours, _ = cv2.findContours(vertical_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Estimate graph boundaries
        x_min, y_min = width, height
        x_max, y_max = 0, 0
        
        # Find the main axis lines (longest horizontal and vertical lines)
        if h_contours:
            main_h_line = max(h_contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(main_h_line)
            x_min = min(x_min, x)
            x_max = max(x_max, x + w)
            y_max = max(y_max, y + h)
        
        if v_contours:
            main_v_line = max(v_contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(main_v_line)
            y_min = min(y_min, y)
            y_max = max(y_max, y + h)
            x_min = min(x_min, x)
        
        # Add margins and ensure bounds are within image
        margin = 20
        x_min = max(0, x_min - margin)
        y_min = max(0, y_min - margin)
        x_max = min(width, x_max + margin)
        y_max = min(height, y_max + margin)
        
        # Fallback to default area if detection fails
        if x_max <= x_min or y_max <= y_min:
            x_min, y_min = int(width * 0.1), int(height * 0.1)
            x_max, y_max = int(width * 0.9), int(height * 0.9)
        
        return (x_min, y_min, x_max, y_max)
    
    def remove_axis_and_grid(self, image, graph_area):
        """
        Remove axis lines and grid lines from the image to focus on data lines
        
        Args:
            image (numpy.ndarray): Input image in BGR format
            graph_area (tuple): Graph area coordinates (x_min, y_min, x_max, y_max)
            
        Returns:
            numpy.ndarray: Image with axis and grid lines removed
        """
        x_min, y_min, x_max, y_max = graph_area
        roi = image[y_min:y_max, x_min:x_max].copy()
        gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        
        # Detect and remove grid lines
        # Horizontal grid lines
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, ((x_max-x_min)//10, 1))
        horizontal_mask = cv2.morphologyEx(gray_roi, cv2.MORPH_OPEN, horizontal_kernel)
        
        # Vertical grid lines  
        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, (y_max-y_min)//10))
        vertical_mask = cv2.morphologyEx(gray_roi, cv2.MORPH_OPEN, vertical_kernel)
        
        # Combine masks
        grid_mask = cv2.bitwise_or(horizontal_mask, vertical_mask)
        
        # Dilate mask to ensure complete removal
        grid_mask = cv2.dilate(grid_mask, np.ones((3,3), np.uint8), iterations=1)
        
        # Remove grid lines by setting them to white
        roi_cleaned = roi.copy()
        roi_cleaned[grid_mask > 0] = [255, 255, 255]
        
        # Update the original image
        result = image.copy()
        result[y_min:y_max, x_min:x_max] = roi_cleaned
        
        return result
    
    def extract_line_colors(self, image, graph_area):
        """
        Extract distinct colors present in the graph area to identify different data lines
        
        Args:
            image (numpy.ndarray): Input image in BGR format
            graph_area (tuple): Graph area coordinates
            
        Returns:
            list: List of distinct BGR colors found in the graph
        """
        x_min, y_min, x_max, y_max = graph_area
        roi = image[y_min:y_max, x_min:x_max]
        
        # Convert to RGB for better color analysis
        roi_rgb = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)
        
        # Reshape image to list of pixels
        pixels = roi_rgb.reshape(-1, 3)
        
        # Remove white and near-white pixels (background)
        non_white_mask = np.sum(pixels, axis=1) < 700  # Threshold for white detection
        pixels = pixels[non_white_mask]
        
        # Remove black and near-black pixels (text/axes)
        non_black_mask = np.sum(pixels, axis=1) > 50   # Threshold for black detection
        pixels = pixels[non_black_mask]
        
        if len(pixels) == 0:
            return []
        
        # Use DBSCAN clustering to group similar colors
        scaler = StandardScaler()
        pixels_scaled = scaler.fit_transform(pixels)
        
        clustering = DBSCAN(eps=0.3, min_samples=100).fit(pixels_scaled)
        labels = clustering.labels_
        
        # Extract representative colors from each cluster
        unique_colors = []
        for label in set(labels):
            if label == -1:  # Skip noise points
                continue
            
            cluster_pixels = pixels[labels == label]
            # Use median color as representative
            representative_color = np.median(cluster_pixels, axis=0).astype(int)
            
            # Convert back to BGR for OpenCV compatibility
            bgr_color = tuple(representative_color[::-1])
            unique_colors.append(bgr_color)
        
        return unique_colors
    
    def detect_line_points(self, image, color, graph_area, tolerance=30):
        """
        Detect all points belonging to a specific colored line in the graph
        
        Args:
            image (numpy.ndarray): Input image in BGR format
            color (tuple): BGR color to detect
            graph_area (tuple): Graph area coordinates
            tolerance (int): Color tolerance for detection
            
        Returns:
            list: List of (x, y) coordinates of detected points
        """
        x_min, y_min, x_max, y_max = graph_area
        roi = image[y_min:y_max, x_min:x_max]
        
        # Create color mask
        lower_bound = np.array([max(0, c - tolerance) for c in color])
        upper_bound = np.array([min(255, c + tolerance) for c in color])
        
        color_mask = cv2.inRange(roi, lower_bound, upper_bound)
        
        # Apply morphological operations to clean up the mask
        kernel = np.ones((2,2), np.uint8)
        color_mask = cv2.morphologyEx(color_mask, cv2.MORPH_CLOSE, kernel)
        color_mask = cv2.morphologyEx(color_mask, cv2.MORPH_OPEN, kernel)
        
        # Find contours
        contours, _ = cv2.findContours(color_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        
        points = []
        for contour in contours:
            # Filter out small contours (likely noise)
            if cv2.contourArea(contour) < 5:
                continue
                
            # Extract all points from the contour
            for point in contour:
                x, y = point[0]
                # Convert back to original image coordinates
                original_x = x + x_min
                original_y = y + y_min
                points.append((original_x, original_y))
        
        return points
    
    def cluster_line_points(self, points, expected_lines=None):
        """
        Cluster detected points into separate lines to handle overlapping colors
        
        Args:
            points (list): List of (x, y) coordinates
            expected_lines (int, optional): Expected number of lines for validation
            
        Returns:
            list: List of point clusters, each representing a separate line
        """
        if len(points) < 10:
            return [points] if points else []
        
        points_array = np.array(points)
        
        # Use DBSCAN clustering on spatial coordinates
        # Adjust eps based on image size - smaller for tighter clustering
        eps = max(5, len(points) // 500)  # Adaptive epsilon
        clustering = DBSCAN(eps=eps, min_samples=5).fit(points_array)
        labels = clustering.labels_
        
        # Group points by cluster
        clusters = defaultdict(list)
        for i, label in enumerate(labels):
            if label != -1:  # Skip noise points
                clusters[label].append(points[i])
        
        # Convert to list and filter small clusters
        line_clusters = []
        for cluster_points in clusters.values():
            if len(cluster_points) >= 10:  # Minimum points for a valid line
                # Sort points by x-coordinate for proper line representation
                cluster_points.sort(key=lambda p: p[0])
                line_clusters.append(cluster_points)
        
        # Sort clusters by the x-coordinate of their first point
        line_clusters.sort(key=lambda cluster: cluster[0][0] if cluster else float('inf'))
        
        return line_clusters
    
    def convert_to_stress_strain_data(self, line_clusters, graph_area, image_shape):
        """
        Convert pixel coordinates to stress-strain values based on graph scaling
        
        Args:
            line_clusters (list): List of point clusters for each line
            graph_area (tuple): Graph area coordinates
            image_shape (tuple): Original image shape (height, width)
            
        Returns:
            list: List of DataFrames, each containing stress-strain data for one line
        """
        x_min, y_min, x_max, y_max = graph_area
        
        # Estimate axis ranges from the provided graphs
        # These are typical ranges for stress-strain curves
        strain_min, strain_max = 0.0, 0.3      # True strain range
        stress_min, stress_max = 0, 2500       # True stress range (MPa)
        
        # Calculate scaling factors
        x_scale = (strain_max - strain_min) / (x_max - x_min)
        y_scale = (stress_max - stress_min) / (y_max - y_min)
        
        line_data = []
        
        for i, cluster in enumerate(line_clusters):
            # Convert pixel coordinates to stress-strain values
            strain_values = []
            stress_values = []
            
            for x_pixel, y_pixel in cluster:
                # Convert x (strain)
                strain = strain_min + (x_pixel - x_min) * x_scale
                
                # Convert y (stress) - note: y-axis is inverted in images
                stress = stress_max - (y_pixel - y_min) * y_scale
                
                strain_values.append(round(strain, 4))
                stress_values.append(round(stress, 2))
            
            # Create DataFrame for this line
            df = pd.DataFrame({
                'True_Strain': strain_values,
                'True_Stress_MPa': stress_values,
                'Line_ID': f'Line_{i+1}',
                'X_Pixel': [p[0] for p in cluster],
                'Y_Pixel': [p[1] for p in cluster]
            })
            
            # Remove duplicates and sort by strain
            df = df.drop_duplicates(subset=['True_Strain', 'True_Stress_MPa'])
            df = df.sort_values('True_Strain').reset_index(drop=True)
            
            line_data.append(df)
        
        return line_data
    
    def create_annotated_image(self, original_image, line_clusters, output_path):
        """
        Create an annotated version of the original image showing detected points
        
        Args:
            original_image (numpy.ndarray): Original input image
            line_clusters (list): List of point clusters for each line
            output_path (str): Path to save the annotated image
            
        Returns:
            str: Path to the saved annotated image
        """
        # Convert BGR to RGB for PIL
        image_rgb = cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(image_rgb)
        draw = ImageDraw.Draw(pil_image)
        
        # Draw points for each line with different colors
        for i, cluster in enumerate(line_clusters):
            color = self.line_colors[i % len(self.line_colors)]
            
            for x, y in cluster:
                # Draw a small circle for each detected point
                draw.ellipse([
                    x - self.point_marker_size, 
                    y - self.point_marker_size,
                    x + self.point_marker_size, 
                    y + self.point_marker_size
                ], fill=color, outline=color)
        
        # Add legend
        try:
            font = ImageFont.truetype("arial.ttf", 16)
        except:
            font = ImageFont.load_default()
        
        legend_y = 10
        for i in range(len(line_clusters)):
            color = self.line_colors[i % len(self.line_colors)]
            text = f"Line {i+1}: {len(line_clusters[i])} points"
            
            # Draw legend box
            draw.rectangle([10, legend_y, 30, legend_y + 15], fill=color)
            draw.text([35, legend_y], text, fill=(0, 0, 0), font=font)
            legend_y += 25
        
        # Save annotated image
        pil_image.save(output_path)
        return output_path
    
    def save_to_xlsx(self, line_data, output_path):
        """
        Save extracted data to an Excel file with multiple sheets
        
        Args:
            line_data (list): List of DataFrames containing line data
            output_path (str): Path to save the Excel file
            
        Returns:
            str: Path to the saved Excel file
        """
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Create summary sheet
            summary_data = []
            total_points = 0
            
            for i, df in enumerate(line_data):
                summary_data.append({
                    'Line_ID': f'Line_{i+1}',
                    'Number_of_Points': len(df),
                    'Min_Strain': df['True_Strain'].min(),
                    'Max_Strain': df['True_Strain'].max(),
                    'Min_Stress_MPa': df['True_Stress_MPa'].min(),
                    'Max_Stress_MPa': df['True_Stress_MPa'].max()
                })
                total_points += len(df)
            
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            # Create individual sheets for each line
            for i, df in enumerate(line_data):
                sheet_name = f'Line_{i+1}'
                df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            # Create combined data sheet
            if line_data:
                combined_df = pd.concat(line_data, ignore_index=True)
                combined_df.to_excel(writer, sheet_name='All_Lines_Combined', index=False)
        
        return output_path
    
    def process_graph(self, image_path, expected_lines=None, output_folder='outputs', unique_id=None):
        """
        Main processing function that orchestrates the entire analysis pipeline
        
        Args:
            image_path (str): Path to the input graph image
            expected_lines (int, optional): Expected number of lines for validation
            output_folder (str): Folder to save output files
            unique_id (str): Unique identifier for output files
            
        Returns:
            dict: Processing results including success status and output file paths
        """
        try:
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                return {'success': False, 'error': 'Could not load image'}
            
            print("Processing graph image...")
            
            # Step 1: Detect graph area
            print("1. Detecting graph area...")
            graph_area = self.detect_graph_area(image)
            print(f"   Graph area detected: {graph_area}")
            
            # Step 2: Remove axis and grid lines
            print("2. Removing axis and grid lines...")
            cleaned_image = self.remove_axis_and_grid(image, graph_area)
            
            # Step 3: Extract line colors
            print("3. Extracting line colors...")
            line_colors = self.extract_line_colors(cleaned_image, graph_area)
            print(f"   Found {len(line_colors)} distinct colors")
            
            # Step 4: Detect points for each color
            print("4. Detecting points for each line...")
            all_points = []
            for i, color in enumerate(line_colors):
                points = self.detect_line_points(cleaned_image, color, graph_area)
                if points:
                    all_points.extend(points)
                print(f"   Color {i+1}: {len(points)} points detected")
            
            # Step 5: Cluster points into separate lines
            print("5. Clustering points into lines...")
            line_clusters = self.cluster_line_points(all_points, expected_lines)
            print(f"   {len(line_clusters)} distinct lines identified")
            
            # Validate against expected lines if provided
            if expected_lines and len(line_clusters) != expected_lines:
                print(f"   Warning: Expected {expected_lines} lines, found {len(line_clusters)}")
            
            # Step 6: Convert to stress-strain data
            print("6. Converting to stress-strain data...")
            line_data = self.convert_to_stress_strain_data(line_clusters, graph_area, image.shape)
            
            # Step 7: Generate output files
            print("7. Generating output files...")
            
            # Generate unique filenames
            if unique_id is None:
                unique_id = "output"
            
            xlsx_filename = f"{unique_id}_stress_strain_data.xlsx"
            image_filename = f"{unique_id}_annotated.png"
            
            xlsx_path = os.path.join(output_folder, xlsx_filename)
            image_path = os.path.join(output_folder, image_filename)
            
            # Save Excel file
            self.save_to_xlsx(line_data, xlsx_path)
            
            # Create annotated image
            self.create_annotated_image(image, line_clusters, image_path)
            
            # Calculate total points
            total_points = sum(len(cluster) for cluster in line_clusters)
            
            print(f"Processing complete!")
            print(f"- Lines detected: {len(line_clusters)}")
            print(f"- Total points: {total_points}")
            print(f"- Excel file: {xlsx_filename}")
            print(f"- Annotated image: {image_filename}")
            
            return {
                'success': True,
                'lines_detected': len(line_clusters),
                'total_points': total_points,
                'xlsx_filename': xlsx_filename,
                'annotated_image_filename': image_filename,
                'line_data': line_data
            }
            
        except Exception as e:
            print(f"Error processing graph: {str(e)}")
            return {'success': False, 'error': str(e)}