import argparse
import os
import logging
from pathlib import Path
from textifier_core import TextifierCore

class Textifier:
    """CLI Wrapper for TextifierCore."""
    def __init__(self, load_translation_model=False, whisper_model_name="large"):
        # The core now handles model management and lazy loading
        self.core = TextifierCore(
            load_translation_model=load_translation_model,
            whisper_model_name=whisper_model_name,
            status_callback=self._print_status
        )

    def _print_status(self, message):
        print(f"[*] {message}")

    def transcribe_media(self, input_path, output_format="vtt"):
        """Transcribe a video or audio file."""
        return self.core.transcribe_media(input_path, output_format=output_format)

    def translate_vtt(self, input_path, target_lang="fr"):
        """Translate a VTT file."""
        return self.core.translate_vtt(input_path, target_lang=target_lang)

    def download_translation_model(self):
        """Download the translation model."""
        self.core.download_translation_model()

def main():
    parser = argparse.ArgumentParser(description="Textifier - Video/Audio Transcription and Translation Tool")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Transcribe command
    transcribe_parser = subparsers.add_parser("transcribe", help="Transcribe a video/audio file")
    transcribe_parser.add_argument("input_file", help="Path to the input video/audio file or folder")
    transcribe_parser.add_argument("-f", "--folder", action="store_true", help="Process all files in the folder")
    transcribe_parser.add_argument("-m", "--model", default="large", 
                                help="Whisper model size (tiny, base, small, medium, large, large-v3-turbo)")
    transcribe_parser.add_argument("--format", choices=["vtt", "srt"], default="vtt", help="Output format (default: vtt)")
    
    # Translate command
    translate_parser = subparsers.add_parser("translate", help="Translate a VTT file")
    translate_parser.add_argument("input_file", help="Path to the input VTT file or folder")
    translate_parser.add_argument("-f", "--folder", action="store_true", help="Process all files in the folder")
    translate_parser.add_argument("-l", "--lang", choices=["fr", "hi"], default="fr", help="Target language (fr, hi)")
    
    # Download translation model command
    subparsers.add_parser("download-translation-model", help="Download the translation model (mBART)")
    
    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    # Initialize Textifier with requested model
    whisper_model_name = getattr(args, 'model', 'large')
    textifier = Textifier(whisper_model_name=whisper_model_name)
    
    try:
        if args.command == "transcribe":
            input_path = Path(args.input_file)
            if args.folder:
                if not input_path.is_dir():
                    raise NotADirectoryError(f"Not a directory: {args.input_file}")
                
                video_extensions = {'.mp4', '.avi', '.mkv', '.mov', '.wmv', '.mp3', '.wav', '.m4a', '.aac'}
                files = [f for f in input_path.glob('*') if f.suffix.lower() in video_extensions]
                
                if not files:
                    print(f"No supported video/audio files found in {args.input_file}")
                    return
                
                print(f"Found {len(files)} files to transcribe")
                for i, file in enumerate(files, 1):
                    print(f"\nProcessing {i}/{len(files)}: {file.name}")
                    textifier.transcribe_media(str(file), output_format=args.format)
            else:
                textifier.transcribe_media(args.input_file, output_format=args.format)
                
        elif args.command == "translate":
            input_path = Path(args.input_file)
            if args.folder:
                if not input_path.is_dir():
                    raise NotADirectoryError(f"Not a directory: {args.input_file}")
                
                files = list(input_path.glob('*.vtt'))
                if not files:
                    print(f"No VTT files found in {args.input_file}")
                    return
                
                print(f"Found {len(files)} files to translate")
                for i, file in enumerate(files, 1):
                    print(f"\nProcessing {i}/{len(files)}: {file.name}")
                    textifier.translate_vtt(str(file), args.lang)
            else:
                textifier.translate_vtt(args.input_file, args.lang)
        elif args.command == "download-translation-model":
            textifier.download_translation_model()
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()