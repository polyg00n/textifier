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

    def transcribe_media(self, input_path, language=None):
        """Transcribe a video or audio file. Returns list of created file paths."""
        kwargs = {}
        if language:
            kwargs['language'] = language
        return self.core.transcribe_media(input_path, **kwargs)

    def translate_file(self, input_path, source_lang="en", target_lang="fr"):
        """Translate any supported file format (VTT, SRT, TXT, CSV)."""
        return self.core.translate_file(input_path, source_lang=source_lang, target_lang=target_lang)

    def download_translation_model(self):
        """Download the translation model."""
        self.core.download_translation_model()

def main():
    parser = argparse.ArgumentParser(
        description="Textifier v2.0.0 - Video/Audio Transcription and Translation Tool",
        epilog="Examples:\n"
               "  textifier.py transcribe video.mp4\n"
               "  textifier.py transcribe hindi_video.mp4 --language hi\n"
               "  textifier.py transcribe folder/ -f\n"
               "  textifier.py translate video.vtt --target-lang es\n"
               "  textifier.py translate subtitles.srt --source-lang hi --target-lang gu\n",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Transcribe command
    transcribe_parser = subparsers.add_parser("transcribe", help="Transcribe video/audio to text")
    transcribe_parser.add_argument("input_file", help="Path to input video/audio file or folder")
    transcribe_parser.add_argument("-f", "--folder", action="store_true", 
                                    help="Process all media files in the folder")
    transcribe_parser.add_argument("-m", "--model", default="large-v3", 
                                    help="Whisper model (tiny, base, small, medium, large, large-v3, large-v3-turbo) [default: large-v3]")
    transcribe_parser.add_argument("--language", 
                                    help="Source audio language (en, es, fr, hi, gu, ja, zh, ar, etc.) [default: auto-detect]")
    
    # Translate command
    translate_parser = subparsers.add_parser("translate", help="Translate subtitle/text files")
    translate_parser.add_argument("input_file", help="Path to input file (.vtt, .srt, .txt, .csv) or folder")
    translate_parser.add_argument("-f", "--folder", action="store_true", 
                                   help="Process all supported files in the folder")
    translate_parser.add_argument("--source-lang", default="en",
                                   help="Source language code (en, es, fr, hi, gu, ja, zh, ar, etc.) [default: en]")
    translate_parser.add_argument("--target-lang", "-l", default="fr",
                                   help="Target language code (en, es, fr, hi, gu, ja, zh, ar, etc.) [default: fr]")
    
    # Download translation model command
    subparsers.add_parser("download-translation-model", help="Download the mBART translation model")
    
    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    # Initialize Textifier with requested model
    whisper_model_name = getattr(args, 'model', 'large-v3')
    textifier = Textifier(whisper_model_name=whisper_model_name)
    
    try:
        if args.command == "transcribe":
            input_path = Path(args.input_file)
            if args.folder:
                if not input_path.is_dir():
                    raise NotADirectoryError(f"Not a directory: {args.input_file}")
                
                video_extensions = {'.mp4', '.avi', '.mkv', '.mov', '.wmv', '.mp3', '.wav', '.m4a', '.aac', '.flac', '.ogg'}
                files = [f for f in input_path.glob('*') if f.suffix.lower() in video_extensions]
                
                if not files:
                    print(f"No supported video/audio files found in {args.input_file}")
                    return
                
                print(f"Found {len(files)} files to transcribe")
                for i, file in enumerate(files, 1):
                    print(f"\nProcessing {i}/{len(files)}: {file.name}")
                    created_files = textifier.transcribe_media(str(file), language=args.language)
                    if created_files:
                        print(f"Created: {', '.join([Path(p).name for p in created_files])}")
            else:
                created_files = textifier.transcribe_media(args.input_file, language=args.language)
                if created_files:
                    print(f"\nCreated {len(created_files)} files:")
                    for filepath in created_files:
                        print(f"  - {Path(filepath).name}")
                
        elif args.command == "translate":
            input_path = Path(args.input_file)
            if args.folder:
                if not input_path.is_dir():
                    raise NotADirectoryError(f"Not a directory: {args.input_file}")
                
                # Support all translation formats
                files = []
                for ext in ['*.vtt', '*.srt', '*.txt', '*.csv']:
                    files.extend(input_path.glob(ext))
                
                if not files:
                    print(f"No translatable files (.vtt, .srt, .txt, .csv) found in {args.input_file}")
                    return
                
                print(f"Found {len(files)} files to translate")
                print(f"Translating from {args.source_lang} to {args.target_lang}")
                for i, file in enumerate(files, 1):
                    print(f"\nProcessing {i}/{len(files)}: {file.name}")
                    output_path = textifier.translate_file(str(file), args.source_lang, args.target_lang)
                    print(f"Created: {Path(output_path).name}")
            else:
                print(f"Translating from {args.source_lang} to {args.target_lang}")
                output_path = textifier.translate_file(args.input_file, args.source_lang, args.target_lang)
                print(f"Created: {Path(output_path).name}")
                
        elif args.command == "download-translation-model":
            print("Downloading mBART translation model (this may take a while)...")
            textifier.download_translation_model()
            print("Translation model downloaded successfully!")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()