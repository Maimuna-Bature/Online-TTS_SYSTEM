from flask import Flask, render_template, request, send_file, url_for, redirect, session, flash
import os
import tempfile
import time
import asyncio
import edge_tts

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'default_secret_key')

#define a temporary directory for audio files and uploaded files
mAUDIO_UPLOAD_TEMP_DIR = os.path.join(tempfile.gettempdir(), 'mtts_app_temp_files')
os.makedirs(mAUDIO_UPLOAD_TEMP_DIR, exist_ok=True)

# List of Edge TTS voices
EDGE_TTS_VOICES = {
    "English (US) - Aria Female": "en-US-AriaNeural",
    "English (US) - Guy Male": "en-US-GuyNeural",
    "English (UK) - Sonia Female": "en-GB-SoniaNeural",
    "English (UK) - Libby Female": "en-GB-LibbyNeural",
    "English (UK) - Ryan Male": "en-GB-RyanNeural"
}

#Cleanup old temporary files older than 1 hour
def cleanup_temp_files():
    now = time.time()
    for filename in os.listdir(mAUDIO_UPLOAD_TEMP_DIR):
        file_path = os.path.join(mAUDIO_UPLOAD_TEMP_DIR, filename)
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
    success_message = None

    if request.method == 'POST':
        text_input = request.form.get('text', '').strip()
        uploaded_file = request.files.get('file')
        custom_filename = request.form.get('custom_filename', '').strip() or "speech"
        selected_voice = request.form.get('voice', selected_voice)

        # Handle file upload
        if uploaded_file and uploaded_file.filename != '':
            file_extension = os.path.splitext(uploaded_file.filename)[1].lower()
            if file_extension not in ['.docx', '.pdf', '.xlsx', '.jpg', '.jpeg', '.png']:
                error_message = "Unsupported file type. Please upload a .docx, .pdf, .xlsx, .jpg, or .png file."
            else:
                temp_upload_path = os.path.join(mAUDIO_UPLOAD_TEMP_DIR, uploaded_file.filename)
                uploaded_file.save(temp_upload_path)
                try:
                    if file_extension == '.docx':
                        import docx
                        doc = docx.Document(temp_upload_path)
                        processed_text = '\n'.join([p.text for p in doc.paragraphs])
                    elif file_extension == '.pdf':
                        from pdfminer.high_level import extract_text
                        processed_text = extract_text(temp_upload_path)
                    elif file_extension == '.xlsx':
                        import openpyxl
                        wb = openpyxl.load_workbook(temp_upload_path, data_only=True)
                        text_chunks = []
                        for sheet in wb.worksheets:
                            for row in sheet.iter_rows(values_only=True):
                                for cell in row:
                                    if cell:
                                        text_chunks.append(str(cell))
                        processed_text = '\n'.join(text_chunks)
                    elif file_extension in ['.jpg', '.jpeg', '.png']:
                        from PIL import Image
                        import pytesseract
                        # If Tesseract is not in PATH, set the path:
                        # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
                        img = Image.open(temp_upload_path)
                        processed_text = pytesseract.image_to_string(img)
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
                audio_filename = f"m{int(time.time())}_{os.getpid()}.mp3"
                audio_path = os.path.join(mAUDIO_UPLOAD_TEMP_DIR, audio_filename)
                asyncio.run(synthesize_edge_tts(processed_text, selected_voice, audio_path))
                # Store info in session
                session['audio_filename'] = audio_filename
                session['custom_filename'] = custom_filename
                session['selected_voice'] = selected_voice
                session['success_message'] = "✅ Conversion complete! Your audio is ready."
                return redirect(url_for('index'))
            except Exception as e:
                error_message = f"TTS Conversion Error: {e}."

    # GET request or after redirect
    audio_filename = session.pop('audio_filename', None)
    custom_filename = session.pop('custom_filename', '')
    selected_voice = session.pop('selected_voice', list(EDGE_TTS_VOICES.values())[0])
    success_message = session.pop('success_message', None)

    return render_template(
        'index.html',
        error_message=error_message,
        processed_text=processed_text,
        audio_filename=audio_filename,
        custom_filename=custom_filename,
        edge_tts_voices=EDGE_TTS_VOICES,
        selected_voice=selected_voice,
        success_message=success_message
    )

@app.route('/download/<audio_filename>')
def download_audio(audio_filename):
    custom_name = request.args.get('name', None)
    audio_path = os.path.join(mAUDIO_UPLOAD_TEMP_DIR, audio_filename)
    if not os.path.exists(audio_path):
        return "File not found", 404
    # Add .mp3 extension if not present
    if custom_name:
        if not custom_name.lower().endswith('.mp3'):
            custom_name += '.mp3'
        return send_file(audio_path, as_attachment=True, download_name=custom_name)
    else:
        return send_file(audio_path, as_attachment=True)

@app.route('/audio/<audio_filename>')
def serve_audio(audio_filename):
    audio_path = os.path.join(mAUDIO_UPLOAD_TEMP_DIR, audio_filename)
    if os.path.exists(audio_path):
        return send_file(audio_path, mimetype='audio/mp3')
    return "File not found", 404

if __name__ == '__main__':
    # Set debug=True for development
    app.run(debug=True, port=5000)

# =====================================
# Author: Maimuna Abdulkadir Usman
# Project: Unique TTS System
# Custom Version: June-September 2025
# =====================================
