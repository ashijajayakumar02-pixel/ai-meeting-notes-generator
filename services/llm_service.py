
import requests
import json
import re
from typing import List, Dict

class LLMService:
    def __init__(self):
        """Initialize Ollama LLM service"""
        self.base_url = "http://localhost:11434"
        self.model = "llama3.1:8b"  # Default model
        self._check_ollama_connection()

    def _check_ollama_connection(self):
        """Check if Ollama is running and model is available"""
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                models = response.json().get('models', [])
                available_models = [model['name'] for model in models]
                print(f"Available Ollama models: {available_models}")

                if not any(self.model in model for model in available_models):
                    print(f"Warning: {self.model} not found. Using first available model.")
                    if available_models:
                        self.model = available_models[0]
            else:
                print("Warning: Could not connect to Ollama. Make sure it's running.")
        except Exception as e:
            print(f"Warning: Ollama connection check failed: {str(e)}")

    def _call_ollama(self, prompt: str, system_prompt: str = "") -> str:
        """
        Make API call to Ollama
        Args:
            prompt (str): User prompt
            system_prompt (str): System instruction
        Returns:
            str: Generated response
        """
        try:
            data = {
                "model": self.model,
                "prompt": prompt,
                "system": system_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "top_p": 0.9,
                    "max_tokens": 2000
                }
            }

            response = requests.post(
                f"{self.base_url}/api/generate",
                json=data,
                timeout=60
            )

            if response.status_code == 200:
                result = response.json()
                return result.get('response', '').strip()
            else:
                raise Exception(f"Ollama API error: {response.status_code}")

        except Exception as e:
            print(f"Error calling Ollama: {str(e)}")
            raise Exception(f"LLM service unavailable: {str(e)}")

    def generate_summary(self, transcription: str) -> str:
        """
        Generate meeting summary from transcription
        Args:
            transcription (str): Raw meeting transcription
        Returns:
            str: Formatted meeting summary
        """
        system_prompt = """You are an expert meeting assistant. Generate a clear, professional meeting summary that includes:
1. Main topics discussed
2. Key decisions made
3. Important points raised
4. Next steps mentioned

Format the summary in a structured way with clear sections."""

        prompt = f"""Please analyze the following meeting transcription and create a comprehensive summary:

TRANSCRIPTION:
{transcription}

Generate a well-structured meeting summary with clear sections for topics, decisions, and next steps."""

        try:
            summary = self._call_ollama(prompt, system_prompt)
            return self._format_summary(summary)
        except Exception as e:
            return f"Error generating summary: {str(e)}"

    def extract_action_items(self, transcription: str) -> List[Dict]:
        """
        Extract action items from transcription
        Args:
            transcription (str): Meeting transcription
        Returns:
            List[Dict]: List of action items with details
        """
        system_prompt = """You are an expert at identifying action items from meeting transcriptions. 
Extract action items and format them as a JSON array. Each action item should have:
- description: What needs to be done
- assignee: Who is responsible (if mentioned, otherwise "Unassigned")
- due_date: When it's due (if mentioned, otherwise "No due date specified")
- priority: High/Medium/Low based on context

Return ONLY valid JSON array, no other text."""

        prompt = f"""Analyze this meeting transcription and extract all action items:

TRANSCRIPTION:
{transcription}

Return a JSON array of action items with description, assignee, due_date, and priority fields."""

        try:
            response = self._call_ollama(prompt, system_prompt)
            return self._parse_action_items(response)
        except Exception as e:
            print(f"Error extracting action items: {str(e)}")
            return []

    def _format_summary(self, raw_summary: str) -> str:
        """Format and clean up the generated summary"""
        # Add consistent formatting
        if not raw_summary.startswith('#'):
            raw_summary = f"# Meeting Summary\n\n{raw_summary}"

        return raw_summary

    def _parse_action_items(self, response: str) -> List[Dict]:
        """
        Parse action items from LLM response
        Args:
            response (str): Raw response from LLM
        Returns:
            List[Dict]: Parsed action items
        """
        try:
            # Try to extract JSON from response
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                action_items = json.loads(json_str)

                # Validate and clean up action items
                cleaned_items = []
                for item in action_items:
                    if isinstance(item, dict) and 'description' in item:
                        cleaned_item = {
                            'description': item.get('description', '').strip(),
                            'assignee': item.get('assignee', 'Unassigned').strip(),
                            'due_date': item.get('due_date', 'No due date specified').strip(),
                            'priority': item.get('priority', 'Medium').strip()
                        }
                        if cleaned_item['description']:  # Only add if description exists
                            cleaned_items.append(cleaned_item)

                return cleaned_items
            else:
                # Fallback: parse line by line
                return self._parse_text_action_items(response)

        except json.JSONDecodeError as e:
            print(f"JSON parsing failed: {e}")
            return self._parse_text_action_items(response)
        except Exception as e:
            print(f"Error parsing action items: {e}")
            return []

    def _parse_text_action_items(self, text: str) -> List[Dict]:
        """Fallback method to parse action items from plain text"""
        action_items = []
        lines = text.split('\n')

        for line in lines:
            line = line.strip()
            if line and (line.startswith('-') or line.startswith('*') or 'action' in line.lower()):
                # Simple action item extraction
                clean_line = re.sub(r'^[-*]\s*', '', line)
                if clean_line:
                    action_items.append({
                        'description': clean_line,
                        'assignee': 'Unassigned',
                        'due_date': 'No due date specified',
                        'priority': 'Medium'
                    })

        return action_items[:10]  # Limit to 10 items

    def get_model_info(self):
        """Get information about the current LLM model"""
        return {
            "model": self.model,
            "service": "Ollama",
            "base_url": self.base_url,
            "status": "connected" if self._check_connection() else "disconnected"
        }

    def _check_connection(self):
        """Check if Ollama service is available"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
