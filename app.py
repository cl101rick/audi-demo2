import subprocess
import os
from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename
import io

app = Flask(__name__)

# Configure upload and output folders
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    if file:
        # Secure filename and save to uploads folder
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Build output path for MusicXML file
        base_filename, _ = os.path.splitext(filename)
        output_filename = base_filename + '.musicxml'
        output_filepath = os.path.join(OUTPUT_FOLDER, output_filename)

        # Build and run the Audiveris command-line process
        audiveris_command = [
            'java', '-jar', '/audiveris/Audiveris.jar', 
            '-batch', '-export', '-output', OUTPUT_FOLDER, filepath
        ]
        
        try:
            # Use subprocess to call Audiveris
            subprocess.run(audiveris_command, check=True, capture_output=True, text=True)
            
            # Serve the generated MusicXML file
            if os.path.exists(output_filepath):
                return send_file(output_filepath, as_attachment=True, download_name=output_filename)
            else:
                return "Audiveris did not produce the expected MusicXML output.", 500
        
        except subprocess.CalledProcessError as e:
            return f"Audiveris error: {e.stderr}", 500
        except FileNotFoundError:
            return "Audiveris executable not found. Check your Dockerfile.", 500
        except Exception as e:
            return f"An unexpected error occurred: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0')
