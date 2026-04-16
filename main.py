import os
import sys
from datetime import datetime

from flask import Flask, render_template, request, url_for, redirect
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import SubmitField
from werkzeug.utils import secure_filename

# Ensure the root directory and src can be discovered
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from src.Captured import analyze_pcap

app = Flask(__name__, template_folder='template', static_folder='static')
app.config['SECRET_KEY'] = 'nids_secret_key_12345'
app.config['UPLOAD_FOLDER'] = 'uploads'

# Form class for file uploads via Flask-WTF
class UploadForm(FlaskForm):
    file = FileField('PCAP/PCAPNG Trace', validators=[FileRequired()])
    submit = SubmitField('Analyze Trace')

@app.route('/')
def home():
    """Renders the main dashboard overview."""
    return render_template('index.html')

@app.route('/predicting', methods=['GET', 'POST'])
def predicting():
    """Handles PCAP uploads and triggers the prediction pipeline."""
    form = UploadForm()
    result = None
    
    if form.validate_on_submit():
        f = form.file.data
        filename = secure_filename(f.filename)
        
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
            
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        f.save(filepath)
        
        # Pass the PCAP to our analysis pipeline
        result = analyze_pcap(filepath)
        
    return render_template('prediction.html', form=form, result=result)

@app.route('/model')
def model():
    """Renders the diagnostic dashboard for model health."""
    model_dir = "models"
    models_metadata = {}
    
    phases = [
        ('phase1', 'model_phase1.pkl', '99.1%', '0.99', 'Classifier Core'),
        ('phase2', 'model_phase2.pkl', '98.5%', '0.98', 'Classifier Core')
    ]
    
    for phase_key, filename, acc, f1, mtype in phases:
        filepath = os.path.join(model_dir, filename)
        if os.path.exists(filepath):
            size_mb = os.path.getsize(filepath) / (1024 * 1024)
            mtime = os.path.getmtime(filepath)
            date_str = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
            
            models_metadata[phase_key] = {
                'accuracy': acc,
                'f1': f1,
                'date': date_str,
                'type': mtype,
                'size': f"{size_mb:.2f} MB"
            }
            
    return render_template('model.html', models=models_metadata)

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)
