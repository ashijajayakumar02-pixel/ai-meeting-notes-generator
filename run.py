#!/usr/bin/env python3
"""
AI Meeting Notes Generator - Main Application Runner
"""

import os
import sys
from app.main import app
from config import config

def create_app():
    """Create and configure the Flask application"""

    # Get configuration environment
    config_name = os.environ.get('FLASK_ENV', 'development')

    # Apply configuration
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    return app

if __name__ == '__main__':
    # Create the application
    application = create_app()

    # Get port from environment or default to 5000
    port = int(os.environ.get('PORT', 5000))

    # Get host from environment or default to localhost
    host = os.environ.get('HOST', '127.0.0.1')

    # Development vs Production settings
    if os.environ.get('FLASK_ENV') == 'production':
        # Production settings
        application.run(
            host='0.0.0.0',
            port=port,
            debug=False,
            threaded=True
        )
    else:
        # Development settings
        print(f"""
🚀 AI Meeting Notes Generator Starting...

📊 Configuration: {os.environ.get('FLASK_ENV', 'development')}
🌐 Server: http://{host}:{port}
📁 Upload Directory: {application.config['UPLOAD_FOLDER']}
🤖 Whisper Model: {application.config['WHISPER_MODEL']}
🦙 Ollama URL: {application.config['OLLAMA_BASE_URL']}

📝 Make sure you have:
   ✅ Ollama installed and running
   ✅ Required Python packages installed
   ✅ Google credentials file (for calendar integration)

Press Ctrl+C to stop the server
        """)

        application.run(
            host=host,
            port=port,
            debug=True,
            threaded=True
        )