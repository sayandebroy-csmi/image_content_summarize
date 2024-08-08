# Import necessary libraries
import os
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
from PIL import Image
import pytesseract
from transformers import pipeline

# Initialize Flask application
app = Flask(__name__)

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initialize the summarization pipeline using BART model
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# Function to check if the file extension is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Function to extract text from an image using OCR
def extract_text_from_image(image_path):
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image)
    return text

# Function to summarize the extracted text
def summarize_text(text):
    summary = summarizer(text, max_length=150, min_length=50, do_sample=False)
    return summary[0]['summary_text']

# Route for the home page
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle image upload and summarization
@app.route('/summarize', methods=['POST'])
def summarize_image():
    # Check if the post request has the file part
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    
    # If user does not select file, browser also submits an empty part without filename
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    # If file exists and has an allowed extension
    if file and allowed_file(file.filename):
        # Secure the filename to prevent malicious file names
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # Extract text from the image
            extracted_text = extract_text_from_image(filepath)
            # Summarize the extracted text
            summary = summarize_text(extracted_text)
            
            # Clean up the uploaded file
            os.remove(filepath)
            
            # Return the summary as JSON
            return jsonify({'summary': summary})
        except Exception as e:
            # If an error occurs during processing, return the error message
            return jsonify({'error': str(e)}), 500
    
    # If file type is not allowed
    return jsonify({'error': 'Invalid file type'}), 400

# Run the Flask app if this script is executed
if __name__ == '__main__':
    # Create the upload folder if it doesn't exist
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    # Run the app in debug mode
    app.run(debug=True)