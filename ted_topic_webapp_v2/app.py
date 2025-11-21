from flask import Flask, render_template, request, redirect, url_for
import os
import pandas as pd
from utils import transcribe_audio, recommend_by_topic
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'audio_upload'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Load once
df = pd.read_csv('stm_topic.csv')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['audio_file']
    if not file:
        return redirect('/')

    path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename))
    file.save(path)

    transcript = transcribe_audio(path)
    topic, recommendations = recommend_by_topic(df, transcript)

    return render_template('result.html', transcript=transcript, topic=topic, recommendations=recommendations)
