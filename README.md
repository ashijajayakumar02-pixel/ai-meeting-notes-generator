# AI Meeting Notes and Action-Item Generator

A comprehensive AI-powered application that converts audio recordings into meeting summaries and actionable items using state-of-the-art speech recognition and natural language processing.

## 🚀 Features

### Core Functionality
- **Audio Processing**: Upload audio files or record meetings directly
- **Speech-to-Text**: Powered by OpenAI Whisper for accurate transcription
- **AI Summarization**: Uses local LLM (Ollama + Llama 3.1) for intelligent summaries
- **Action Item Extraction**: Automatically identifies and categorizes tasks
- **Export Options**: PDF and text export formats
- **Calendar Integration**: Sync action items with Google Calendar

### Technical Highlights
- **100% Free Tools**: No API costs for core functionality
- **Local Processing**: All AI processing runs locally for privacy
- **Responsive Web UI**: Modern, mobile-friendly interface
- **Docker Support**: Easy deployment and scaling
- **Offline Capable**: Works without internet after setup

## 🛠 Technology Stack

### Backend
- **Framework**: Flask (Python)
- **Speech Recognition**: OpenAI Whisper (local)
- **Large Language Model**: Ollama + Llama 3.1 (local)
- **Database**: SQLite (development) / PostgreSQL (production)
- **File Processing**: FFmpeg, pydub

### Frontend
- **HTML/CSS**: Bootstrap 5 for responsive design
- **JavaScript**: Vanilla JS with modern APIs
- **Audio Recording**: Web Audio API

### Infrastructure
- **Containerization**: Docker & Docker Compose
- **Calendar API**: Google Calendar (optional)
- **Email**: SMTP (optional notifications)

## 📋 Prerequisites

### System Requirements
- Python 3.9+
- Docker and Docker Compose (recommended)
- 4GB+ RAM (for Whisper and Ollama)
- 10GB+ disk space (for models)

### Required Software
1. **Ollama** - For local LLM processing
   ```bash
   # Install Ollama
   curl -fsSL https://ollama.com/install.sh | sh

   # Pull the Llama model
   ollama pull llama3.1:8b
   ```

2. **FFmpeg** - For audio processing
   ```bash
   # Ubuntu/Debian
   sudo apt update && sudo apt install ffmpeg

   # macOS
   brew install ffmpeg

   # Windows
   # Download from https://ffmpeg.org/download.html
   ```

## 🚀 Quick Start

### Method 1: Docker Compose (Recommended)

1. **Clone or download the project files**
2. **Configure environment**:
   ```bash
   cp .env.template .env
   # Edit .env file with your preferences
   ```

3. **Start the application**:
   ```bash
   docker-compose up -d
   ```

4. **Access the application**:
   - Web Interface: http://localhost:5000
   - Ollama API: http://localhost:11434

### Method 2: Manual Setup

1. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Start Ollama service**:
   ```bash
   ollama serve
   ```

3. **Run the application**:
   ```bash
   python run.py
   ```

## 📖 Usage Guide

### 1. Upload Audio Recording

1. Navigate to the upload page
2. Fill in meeting details:
   - Meeting title
   - Date
   - Attendees (optional)
3. Upload audio file (MP3, WAV, M4A, FLAC, AAC)
4. Click "Process Audio with AI"

### 2. Live Recording

1. Click "Record Live Meeting" on the home page
2. Allow microphone access
3. Click "Start Recording"
4. Stop recording when meeting ends
5. Save and upload the recording

### 3. Review Results

- **Summary**: AI-generated meeting overview
- **Action Items**: Extracted tasks with:
  - Description
  - Assignee (if mentioned)
  - Due date (if mentioned) 
  - Priority level
- **Transcription**: Full meeting transcript

### 4. Export and Share

- **PDF Export**: Professional formatted summary
- **Text Export**: Plain text for sharing
- **Calendar Sync**: Add action items to Google Calendar

## 🔧 Configuration

### Environment Variables

Create a `.env` file (copy from `.env.template`):

```env
# Basic Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
HOST=127.0.0.1
PORT=5000

# AI Configuration
WHISPER_MODEL=base  # tiny, base, small, medium, large
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b

# Optional: Google Calendar Integration
GOOGLE_CREDENTIALS_FILE=credentials.json
```

### Google Calendar Setup (Optional)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Google Calendar API
4. Create credentials (OAuth 2.0)
5. Download `credentials.json` to project root

## 📁 Project Structure

```
ai-meeting-notes-generator/
├── app/
│   ├── __init__.py
│   ├── main.py              # Main Flask application
│   ├── models/
│   │   ├── meeting.py       # Meeting database model
│   │   └── action_item.py   # Action item database model
│   ├── services/
│   │   ├── speech_to_text.py    # Whisper integration
│   │   ├── llm_service.py       # Ollama LLM service
│   │   ├── calendar_service.py  # Google Calendar API
│   │   └── file_service.py      # File export utilities
│   ├── templates/               # HTML templates
│   └── static/                  # CSS, JS, images
├── config.py                # Configuration management
├── run.py                   # Application runner
├── requirements.txt         # Python dependencies
├── Dockerfile              # Container configuration
├── docker-compose.yml      # Multi-container setup
├── .env.template           # Environment template
└── README.md               # This file
```

## 🐛 Troubleshooting

### Common Issues

1. **Ollama Connection Failed**
   ```bash
   # Check if Ollama is running
   curl http://localhost:11434/api/tags

   # Restart Ollama
   ollama serve
   ```

2. **Whisper Model Loading Issues**
   ```bash
   # Install torch with CUDA support (if you have GPU)
   pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118
   ```

3. **Audio File Processing Errors**
   ```bash
   # Install additional audio codecs
   sudo apt install libavcodec-extra
   ```

4. **Google Calendar Authentication**
   - Ensure `credentials.json` is in the project root
   - Check OAuth consent screen configuration
   - Verify Calendar API is enabled

### Debug Mode

Run with debug logging:
```bash
export LOG_LEVEL=DEBUG
python run.py
```

## 🔒 Privacy & Security

- **Local Processing**: All AI processing happens on your machine
- **Data Storage**: Meeting data stored locally in SQLite database
- **No External APIs**: Core functionality doesn't require internet
- **Secure Upload**: File validation and size limits
- **Optional Cloud**: Google Calendar integration is optional

## 📈 Performance Optimization

### Model Selection
- **Whisper tiny**: Fastest, less accurate
- **Whisper base**: Good balance (recommended)
- **Whisper small/medium**: Better accuracy, slower
- **Whisper large**: Best accuracy, requires more resources

### Hardware Recommendations
- **CPU**: 4+ cores recommended
- **RAM**: 8GB+ for medium/large Whisper models
- **GPU**: CUDA-compatible GPU speeds up Whisper significantly
- **Storage**: SSD recommended for model loading

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- OpenAI Whisper team for excellent speech recognition
- Ollama team for making local LLMs accessible
- Flask community for the excellent web framework
- Bootstrap team for the responsive UI components

## 📞 Support

For issues and questions:
- Check the troubleshooting section above
- Search existing issues in the repository
- Create a new issue with detailed description

---

**Made with ❤️ using free and open-source tools**