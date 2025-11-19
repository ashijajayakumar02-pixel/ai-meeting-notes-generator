
import whisper
import os
import tempfile
from pydub import AudioSegment
import torch

class SpeechToTextService:
    def __init__(self):
        """Initialize Whisper model"""
        print("Loading Whisper model...")
        # Use base model for balance of speed and accuracy
        self.model = whisper.load_model("base")
        print("Whisper model loaded successfully!")

    def transcribe_audio(self, audio_path):
        """
        Transcribe audio file to text using Whisper
        Args:
            audio_path (str): Path to audio file
        Returns:
            str: Transcribed text
        """
        try:
            # Convert audio to supported format if needed
            converted_path = self._prepare_audio(audio_path)

            print(f"Transcribing audio file: {converted_path}")
            result = self.model.transcribe(converted_path)

            # Clean up temporary file if created
            if converted_path != audio_path:
                os.remove(converted_path)

            return result["text"].strip()

        except Exception as e:
            print(f"Error in transcription: {str(e)}")
            raise Exception(f"Failed to transcribe audio: {str(e)}")

    def _prepare_audio(self, audio_path):
        """
        Convert audio to WAV format if needed
        Args:
            audio_path (str): Original audio file path
        Returns:
            str: Path to converted audio (or original if no conversion needed)
        """
        file_ext = os.path.splitext(audio_path)[1].lower()

        # Whisper supports many formats, but WAV is most reliable
        if file_ext in ['.wav', '.mp3', '.m4a', '.flac']:
            return audio_path

        try:
            # Convert to WAV
            audio = AudioSegment.from_file(audio_path)
            temp_path = tempfile.mktemp(suffix='.wav')
            audio.export(temp_path, format="wav")
            print(f"Converted {audio_path} to {temp_path}")
            return temp_path

        except Exception as e:
            print(f"Error converting audio: {str(e)}")
            return audio_path  # Return original if conversion fails

    def get_model_info(self):
        """Get information about the loaded model"""
        return {
            "model_name": "whisper-base",
            "languages": "multilingual",
            "parameters": "74M",
            "device": "cuda" if torch.cuda.is_available() else "cpu"
        }
