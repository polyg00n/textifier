
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.append(os.getcwd())

from textifier_core import TextifierCore

def log_callback(msg):
    print(f"[CALLBACK] {msg}")

def test_transcription():
    print("Initializing Core...")
    core = TextifierCore(whisper_model_name="tiny", status_callback=log_callback)
    
    input_file = r"D:\Videos\pt1_Whiteboard_2014.mp4"
    if not os.path.exists(input_file):
        print(f"Error: File not found at {input_file}")
        # Let's check D:\Videos directory to see what's there if it fails
        return

    print(f"Starting transcription for: {input_file}")
    try:
        # Using tiny model for speed in this test
        output_path = core.transcribe_media(input_file)
        print(f"Success! VTT saved at: {output_path}")
    except Exception as e:
        print(f"Transcription failed: {e}")

if __name__ == "__main__":
    test_transcription()
