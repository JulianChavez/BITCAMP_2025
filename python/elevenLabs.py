import requests
import os
from dotenv import load_dotenv
from pydub import AudioSegment
import tempfile

load_dotenv()

API_KEY = os.getenv('ELEVENLABS_API_KEY')
VOICE_IDS = {
    "Host A": "pwMBn0SsmN1220Aorv15",
    "Host B": "UgBBYS2sOqTuMpoF3BR0"
}


class ElevenLabs:
    def __init__(self, script):
        self.script = script

    def script_parser(self):
        lines = self.script.split('\n')
        host_a_lines = []
        host_b_lines = []
        
        current_host = None
        current_text = []
        
        for line in lines:
            if line.startswith('Host A:'):
                # If we were collecting for another host, save their text
                if current_host == 'B' and current_text:
                    host_b_lines.append(' '.join(current_text))
                    current_text = []
                
                # Start collecting for Host A
                current_host = 'A'
                current_text.append(line.split(':', 1)[1].strip())
            elif line.startswith('Host B:'):
                # If we were collecting for another host, save their text
                if current_host == 'A' and current_text:
                    host_a_lines.append(' '.join(current_text))
                    current_text = []
                
                # Start collecting for Host B
                current_host = 'B'
                current_text.append(line.split(':', 1)[1].strip())
            elif line.strip() and current_host:  # Continue with the current host if line is not empty
                current_text.append(line.strip())
        
        # Don't forget to add the last segment
        if current_host == 'A' and current_text:
            host_a_lines.append(' '.join(current_text))
        elif current_host == 'B' and current_text:
            host_b_lines.append(' '.join(current_text))
        
        return host_a_lines, host_b_lines

    def generate_audio(self, text, voice_id, output_file):
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream"
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": API_KEY
        }
        
        data = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.5
            }
        }
        
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code == 200:
            with open(output_file, 'wb') as f:
                f.write(response.content)
            return True
        else:
            print(f"Error generating audio: {response.status_code}")
            return False

    def create_conversation(self, output_file):
        host_a_lines, host_b_lines = self.script_parser()
        combined_audio = AudioSegment.empty()
        
        # Create a temporary directory to store individual audio files
        with tempfile.TemporaryDirectory() as temp_dir:
            # Generate audio for each line and combine them in order
            for i in range(max(len(host_a_lines), len(host_b_lines))):
                if i < len(host_a_lines):
                    host_a_file = os.path.join(temp_dir, f"host_a_{i}.mp3")
                    if self.generate_audio(host_a_lines[i], VOICE_IDS["Host A"], host_a_file):
                        audio = AudioSegment.from_mp3(host_a_file)
                        combined_audio += audio
                
                if i < len(host_b_lines):
                    host_b_file = os.path.join(temp_dir, f"host_b_{i}.mp3")
                    if self.generate_audio(host_b_lines[i], VOICE_IDS["Host B"], host_b_file):
                        audio = AudioSegment.from_mp3(host_b_file)
                        combined_audio += audio
        
        # Export the final combined audio
        combined_audio.export(output_file, format="mp3")
        return True
