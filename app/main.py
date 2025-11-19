
import os
from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for
from werkzeug.utils import secure_filename
import whisper
import requests
import json
import tempfile
from datetime import datetime, timedelta
import sqlite3
from services.speech_to_text import SpeechToTextService
from services.llm_service import LLMService
from services.calendar_service import CalendarService
from services.file_service import FileService
from models.meeting import Meeting
from models.action_item import ActionItem

app = Flask(__name__, template_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates'))
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize services
speech_service = SpeechToTextService()
llm_service = LLMService()
calendar_service = CalendarService()
file_service = FileService()

@app.route('/')
def index():
    """Main landing page"""
    return render_template('index.html')

@app.route('/upload')
def upload_page():
    """Upload page for audio files"""
    return render_template('upload.html')

@app.route('/process_audio', methods=['POST'])
def process_audio():
    """Process uploaded audio file"""
    try:
        if 'audio_file' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400

        file = request.files['audio_file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        # Save uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Get meeting details from form
        meeting_title = request.form.get('meeting_title', 'Untitled Meeting')
        meeting_date = request.form.get('meeting_date', datetime.now().strftime('%Y-%m-%d'))
        attendees = request.form.get('attendees', '')

        # Process audio file
        print("Starting audio processing...")

        # Step 1: Speech to Text
        print("Converting speech to text...")
        transcription = speech_service.transcribe_audio(filepath)

        # Step 2: Generate summary and action items using LLM
        print("Generating summary and action items...")
        summary = llm_service.generate_summary(transcription)
        action_items = llm_service.extract_action_items(transcription)

        # Step 3: Save to database
        meeting = Meeting(
            title=meeting_title,
            date=meeting_date,
            attendees=attendees,
            transcription=transcription,
            summary=summary
        )

        meeting_id = meeting.save()

        # Save action items
        for item in action_items:
            action_item = ActionItem(
                meeting_id=meeting_id,
                description=item.get('description', ''),
                assignee=item.get('assignee', ''),
                due_date=item.get('due_date', ''),
                priority=item.get('priority', 'Medium')
            )
            action_item.save()

        # Clean up uploaded file
        os.remove(filepath)

        return jsonify({
            'success': True,
            'meeting_id': meeting_id,
            'summary': summary,
            'action_items': action_items,
            'transcription': transcription[:500] + '...' if len(transcription) > 500 else transcription
        })

    except Exception as e:
        print(f"Error processing audio: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/meeting/<int:meeting_id>')
def view_meeting(meeting_id):
    """View specific meeting results"""
    try:
        meeting = Meeting.get_by_id(meeting_id)
        action_items = ActionItem.get_by_meeting_id(meeting_id)

        return render_template('results.html', 
                             meeting=meeting, 
                             action_items=action_items)
    except Exception as e:
        flash(f'Error loading meeting: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/export/<int:meeting_id>/<format>')
def export_meeting(meeting_id, format):
    """Export meeting in various formats"""
    try:
        meeting = Meeting.get_by_id(meeting_id)
        action_items = ActionItem.get_by_meeting_id(meeting_id)

        if format == 'pdf':
            pdf_path = file_service.export_to_pdf(meeting, action_items)
            return send_file(pdf_path, as_attachment=True, 
                           download_name=f"{meeting['title']}_summary.pdf")
        elif format == 'txt':
            txt_content = file_service.export_to_text(meeting, action_items)
            return txt_content, 200, {'Content-Type': 'text/plain'}
        else:
            return jsonify({'error': 'Unsupported format'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/calendar_integration', methods=['POST'])
def calendar_integration():
    """Add action items to Google Calendar"""
    try:
        data = request.get_json()
        meeting_id = data.get('meeting_id')
        selected_items = data.get('action_items', [])

        results = []
        for item_id in selected_items:
            action_item = ActionItem.get_by_id(item_id)
            calendar_event = calendar_service.create_event(action_item)
            results.append({
                'item_id': item_id,
                'event_id': calendar_event.get('id'),
                'status': 'success'
            })

        return jsonify({'success': True, 'results': results})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    # Initialize database
    Meeting.init_db()
    ActionItem.init_db()

    app.run(host='0.0.0.0', port=5000, debug=True)
