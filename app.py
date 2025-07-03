from flask import Flask, render_template, request, send_file, url_for, redirect, session, flash
import os
import tempfile
import time
import asyncio
import edge_tts

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'default_secret_key')

#define a temporary directory for audio fils and upoaded files
AUDIO_UPLOAD_TEMP_DIR = os.path.join(tempfile.gettempdir(), 'tts_app_temp_files')
os.makedirs(AUDIO_UPLOAD_TEMP_DIR, exist_ok=True)

# List of Edge TTS voices
EDGE_TTS_VOICES = {
    "English (US) - Aria Female": "en-US-AriaNeural",
    "English (US) - Guy Male": "en-US-GuyNeural",
    "English (UK) - Sonia Female": "en-GB-SoniaNeural",
    "English (UK) - Ryan Male": "en-GB-RyanNeural",
    "English (AU) - Natasha Female": "en-AU-NatashaNeural"
}

#Cleanup old temporary files older than 1 hour
def cleanup_temp_files():
    now = time.time()
    for filename in os.listdir(AUDIO_UPLOAD_TEMP_DIR):
        file_path = os.path.join(AUDIO_UPLOAD_TEMP_DIR, filename)
        if os.path.isfile(file_path) and now - os.path.getmtime(file_path) > 3600:
            try:
                os.remove(file_path)
                print(f"Cleaned up old temporary file: {file_path}")
            except Exception as e :
                print(f"Error removing old temporary files {file_path}: {e}")


cleanup_temp_files()

async def synthesize_edge_tts(text, voice, output_path):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)

@app.route('/', methods=['GET', 'POST'])
def index():
    error_message = None
    processed_text = ""
    audio_filename = None
    custom_filename = ""
    selected_voice = list(EDGE_TTS_VOICES.values())[0]

    if request.method == 'POST':
        text_input = request.form.get('text', '').strip()
        uploaded_file = request.files.get('file')
        custom_filename = request.form.get('custom_filename', '').strip() or "speech"
        selected_voice = request.form.get('voice', selected_voice)

        # Handle file upload
        if uploaded_file and uploaded_file.filename != '':
            file_extension = os.path.splitext(uploaded_file.filename)[1].lower()
            if file_extension not in ['.txt', '.docx']:
                error_message = "Unsupported file type. Please upload a .txt or .docx file."
            else:
                temp_upload_path = os.path.join(AUDIO_UPLOAD_TEMP_DIR, uploaded_file.filename)
                uploaded_file.save(temp_upload_path)
                try:
                    if file_extension == '.txt':
                        with open(temp_upload_path, 'r', encoding='utf-8') as f:
                            processed_text = f.read()
                    else:
                        import docx
                        doc = docx.Document(temp_upload_path)
                        processed_text = '\n'.join([p.text for p in doc.paragraphs])
                except Exception as e:
                    error_message = f"Error reading file: {e}"
                finally:
                    os.remove(temp_upload_path)
        elif text_input:
            processed_text = text_input
        else:
            error_message = "Please provide text input or upload a file."

        # Convert text to speech and save to temp file
        if not error_message and processed_text.strip():
            try:
                audio_filename = f"{int(time.time())}_{os.getpid()}.mp3"
                audio_path = os.path.join(AUDIO_UPLOAD_TEMP_DIR, audio_filename)
                asyncio.run(synthesize_edge_tts(processed_text, selected_voice, audio_path))
                # Store info in session or pass as query params
                return redirect(url_for(
                    'index',
                    audio_filename=audio_filename,
                    custom_filename=custom_filename,
                    selected_voice=selected_voice
                ))
            except Exception as e:
                error_message = f"TTS Conversion Error: {e}."

    # GET request or after redirect
    audio_filename = request.args.get('audio_filename')
    custom_filename = request.args.get('custom_filename', '')
    selected_voice = request.args.get('selected_voice', selected_voice)

    return render_template(
        'index.html',
        error_message=error_message,
        processed_text=processed_text,
        audio_filename=audio_filename,
        custom_filename=custom_filename,
        edge_tts_voices=EDGE_TTS_VOICES,
        selected_voice=selected_voice
    )

@app.route('/download/<audio_filename>')
def download_audio(audio_filename):
    custom_filename = request.args.get('name', 'speech')
    # Sanitize filename
    custom_filename = "".join(c for c in custom_filename if c.isalnum() or c in (' ', '_', '-')).rstrip()
    if not custom_filename.lower().endswith('.mp3'):
        custom_filename += '.mp3'
    audio_path = os.path.join(AUDIO_UPLOAD_TEMP_DIR, audio_filename)
    if os.path.exists(audio_path):
        return send_file(audio_path, mimetype='audio/mp3', as_attachment=True, download_name=custom_filename)
    return "File not found", 404

@app.route('/audio/<audio_filename>')
def serve_audio(audio_filename):
    audio_path = os.path.join(AUDIO_UPLOAD_TEMP_DIR, audio_filename)
    if os.path.exists(audio_path):
        return send_file(audio_path, mimetype='audio/mp3')
    return "File not found", 404

if __name__ == '__main__':
    # Set debug=True for development
    app.run(debug=True, port=5000)
