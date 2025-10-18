from flask import Flask, render_template, request, send_file, url_for, redirect, session, flash
import os
import tempfile
import time
import asyncio
import edge_tts
import string

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'default_secret_key')

mAUDIO_UPLOAD_TEMP_DIR = os.path.join(tempfile.gettempdir(), 'mtts_app_temp_files')
os.makedirs(mAUDIO_UPLOAD_TEMP_DIR, exist_ok=True)

EDGE_TTS_VOICES = {
    "English (US) - Aria Female": "en-US-AriaNeural",
    "English (US) - Guy Male": "en-US-GuyNeural",
    "English (UK) - Sonia Female": "en-GB-SoniaNeural",
    "English (UK) - Libby Female": "en-GB-LibbyNeural",
    "English (UK) - Ryan Male": "en-GB-RyanNeural"
}

def cleanup_temp_files():
    now = time.time()
    for filename in os.listdir(mAUDIO_UPLOAD_TEMP_DIR):
        file_path = os.path.join(mAUDIO_UPLOAD_TEMP_DIR, filename)
        if os.path.isfile(file_path) and now - os.path.getmtime(file_path) > 3600:
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"Error removing old temporary files {file_path}: {e}")

cleanup_temp_files()

async def synthesize_edge_tts(text, voice, output_path):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)

def process_text_for_speech(text, is_image=False):
    text = ' '.join(text.split())
    import re
    text = re.sub(r'_{3,}', '', text)
    text = re.sub(r'[\-_]{2,}', '', text)
    text = text.replace('*', ',')
    text = text.replace('•', ',')
    text = re.sub(r'(\d+\.)\s', r'\1, ', text)
    text = text.replace('...', '…')
    text = text.replace('!', '! ')
    text = text.replace('?', '? ')
    text = text.replace(':', ': ')
    text = text.replace(';', '; ')
    text = text.replace('.', '. ')
    text = text.replace(',', ', ')
    text = ' '.join(text.split())
    return text

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

        if uploaded_file and uploaded_file.filename != '':
            file_size = uploaded_file.seek(0, 2)
            uploaded_file.seek(0)
            if file_size > 25 * 1024 * 1024:
                error_message = "File too large. Please upload a file smaller than 25MB."
            else:
                file_extension = os.path.splitext(uploaded_file.filename)[1].lower()
                if file_extension not in ['.docx', '.pdf', '.jpg', '.jpeg', '.png']:
                    error_message = "Unsupported file type. Please upload a .docx, .pdf, .jpg, or .png file."
                else:
                    temp_upload_path = os.path.join(mAUDIO_UPLOAD_TEMP_DIR, uploaded_file.filename)
                    uploaded_file.save(temp_upload_path)
                    try:
                        if file_extension == '.docx':
                            import docx
                            doc = docx.Document(temp_upload_path)
                            text_parts = []
                            for para in doc.paragraphs:
                                if para.text.strip():
                                    text_parts.append(para.text)
                            for table in doc.tables:
                                for row in table.rows:
                                    row_text = ' '.join(cell.text.strip() for cell in row.cells if cell.text.strip())
                                    if row_text:
                                        text_parts.append(row_text)
                            raw_text = '\n'.join(text_parts)
                            processed_text = process_text_for_speech(raw_text)
                        elif file_extension == '.pdf':
                            from pdfminer.high_level import extract_text
                            try:
                                raw_text = extract_text(temp_upload_path, maxpages=None, page_numbers=None, codec='utf-8')
                                processed_text = process_text_for_speech(raw_text)
                            except Exception as e:
                                error_message = f"Error processing PDF: {e}"
                        else:
                            from PIL import Image
                            import pytesseract
                            try:
                                img = Image.open(temp_upload_path)
                                extracted_text = pytesseract.image_to_string(img)
                                if extracted_text:
                                    processed_text = process_text_for_speech(extracted_text, is_image=True)
                                else:
                                    error_message = "No text could be extracted from the image."
                            except Exception as e:
                                error_message = f"Error processing image: {e}"
                    except Exception as e:
                        error_message = f"Error reading file: {e}"
                    finally:
                        try:
                            os.remove(temp_upload_path)
                        except Exception:
                            pass
        elif text_input:
            processed_text = process_text_for_speech(text_input)
        else:
            error_message = "Please provide text input or upload a file."

        if not error_message and processed_text.strip():
            try:
                audio_filename = f"m{int(time.time())}_{os.getpid()}.mp3"
                audio_path = os.path.join(mAUDIO_UPLOAD_TEMP_DIR, audio_filename)
                text_to_speak = process_text_for_speech(processed_text)
                communicate = edge_tts.Communicate(
                    text_to_speak,
                    selected_voice,
                    rate='-10%',
                    volume='+0%',
                    pitch='+0Hz'
                )
                asyncio.run(communicate.save(audio_path))
                session['audio_filename'] = audio_filename
                session['custom_filename'] = custom_filename
                session['selected_voice'] = selected_voice
                session['success_message'] = "✅ Conversion complete! Your audio is ready."
                return redirect(url_for('index'))
            except Exception as e:
                error_message = f"TTS Conversion Error: {e}."
        elif not processed_text.strip():
            error_message = "No readable text was found in the file or text input."

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

@app.route('/home')
def home():
    return render_template('home.html')


if __name__ == '__main__':
    app.run(debug=True, port=5000)

# =====================================
# Author: Maimuna Abdulkadir Usman
# Project: Unique TTS System
# Custom Version: June-September 2025
# =====================================