import argparse
import os
import logging
import json
from pathlib import Path
from textifier_core import TextifierCore

class Textifier:
    """CLI Wrapper for TextifierCore."""
    def __init__(self, load_translation_model=False, whisper_model_name="large-v3-turbo"):
        # The core now handles model management and lazy loading
        self.core = TextifierCore(
            load_translation_model=load_translation_model,
            whisper_model_name=whisper_model_name,
            status_callback=self._print_status
        )

    def _print_status(self, message):
        print(f"[*] {message}")

    def transcribe_media(self, input_path, output_dir=None, **kwargs):
        """Transcribe a video or audio file. Returns list of created file paths."""
        return self.core.transcribe_media(input_path, output_dir=output_dir, **kwargs)

    def translate_file(self, input_path, source_lang="en", target_lang="fr", output_dir=None):
        """Translate any supported file format (VTT, SRT, TXT, CSV)."""
        return self.core.translate_file(input_path, source_lang=source_lang, target_lang=target_lang, output_dir=output_dir)

    def summarize_text(self, input_path, prompt, config):
        """Summarize text file."""
        with open(input_path, "r", encoding="utf-8") as f:
            content = f.read()
        return self.core.summarizer.summarize(content, prompt, config)

    def download_translation_model(self):
        """Download the translation model."""
        self.core.model_manager.download_translation_model()

def main():
    parser = argparse.ArgumentParser(
        description="Textifier v2.0.0 - Video/Audio Transcription, Translation, and Summarization Tool",
        epilog="Examples:\n"
               "  textifier.py transcribe video.mp4 --model large-v3-turbo --word-timestamps\n"
               "  textifier.py translate video.vtt --target-lang es\n"
               "  textifier.py summarize transcript.txt --provider gemini --api-key YOUR_KEY\n"
               "  textifier.py pipeline video.mp4 --translate-langs fr es --summarize --provider ollama\n",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Transcribe command
    transcribe_parser = subparsers.add_parser("transcribe", help="Transcribe video/audio to text")
    transcribe_parser.add_argument("input_file", help="Path to input video/audio file or folder")
    transcribe_parser.add_argument("-f", "--folder", action="store_true", help="Process all media files in the folder")
    transcribe_parser.add_argument("-o", "--output-dir", help="Directory to save output files")
    transcribe_parser.add_argument("-m", "--model", default="large-v3-turbo", help="Whisper model [default: large-v3-turbo]")
    transcribe_parser.add_argument("--language", help="Source audio language [default: auto-detect]")
    transcribe_parser.add_argument("--word-timestamps", action="store_true", help="Export word-level timestamps to JSON")
    transcribe_parser.add_argument("--vad-filter", action="store_true", default=True, help="Enable VAD filter [default: True]")
    transcribe_parser.add_argument("--initial-prompt", help="Optional text to provide as context for the first window")
    
    # Translate command
    translate_parser = subparsers.add_parser("translate", help="Translate subtitle/text files")
    translate_parser.add_argument("input_file", help="Path to input file or folder")
    translate_parser.add_argument("-f", "--folder", action="store_true", help="Process all supported files in the folder")
    translate_parser.add_argument("-o", "--output-dir", help="Directory to save translated files")
    translate_parser.add_argument("--source-lang", default="en", help="Source language code [default: en]")
    translate_parser.add_argument("--target-lang", "-l", default="fr", help="Target language code [default: fr]")
    
    # Summarize command
    summarize_parser = subparsers.add_parser("summarize", help="Summarize text/subtitle files using LLM")
    summarize_parser.add_argument("input_file", help="Path to input text/subtitle file or folder")
    summarize_parser.add_argument("-f", "--folder", action="store_true", help="Process all text files in the folder")
    summarize_parser.add_argument("--prompt", default="Please summarize the following transcript concisely.", help="Summarization prompt")
    summarize_parser.add_argument("--provider", choices=['ollama', 'lm_studio', 'gemini', 'claude', 'openai'], default='gemini', help="LLM provider")
    summarize_parser.add_argument("--api-key", help="API Key for cloud providers")
    summarize_parser.add_argument("--model", help="LLM Model name (e.g., gemini-1.5-flash, llama3)")
    summarize_parser.add_argument("--base-url", help="Base URL for local providers (Ollama/LM Studio)")
    
    # Pipeline command
    pipeline_parser = subparsers.add_parser("pipeline", help="Run full pipeline: transcribe -> translate -> summarize")
    pipeline_parser.add_argument("input_file", help="Path to input media file or folder")
    pipeline_parser.add_argument("-o", "--output-dir", help="Directory for all outputs")
    pipeline_parser.add_argument("--model", default="large-v3-turbo", help="Whisper model")
    pipeline_parser.add_argument("--language", help="Source language for transcription")
    pipeline_parser.add_argument("--translate-langs", nargs="+", help="One or more target language codes for translation")
    pipeline_parser.add_argument("--summarize", action="store_true", help="Run summarization after processing")
    pipeline_parser.add_argument("--provider", default='gemini', help="LLM provider for summarization")
    pipeline_parser.add_argument("--api-key", help="API Key for summarization")
    pipeline_parser.add_argument("--summary-model", help="LLM Model name for summarization")
    
    # Download translation model command
    subparsers.add_parser("download-translation-model", help="Download the mBART translation model")
    
    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    whisper_model_name = getattr(args, 'model', 'large-v3-turbo')
    textifier = Textifier(whisper_model_name=whisper_model_name)
    
    try:
        if args.command == "transcribe":
            input_path = Path(args.input_file)
            kwargs = {
                "language": args.language,
                "word_timestamps": args.word_timestamps,
                "vad_filter": args.vad_filter,
                "initial_prompt": args.initial_prompt
            }
            if args.folder:
                video_extensions = {'.mp4', '.avi', '.mkv', '.mov', '.wmv', '.mp3', '.wav', '.m4a', '.aac', '.flac', '.ogg'}
                files = [f for f in input_path.glob('*') if f.suffix.lower() in video_extensions]
                for file in files:
                    textifier.transcribe_media(str(file), output_dir=args.output_dir, **kwargs)
            else:
                textifier.transcribe_media(args.input_file, output_dir=args.output_dir, **kwargs)
                
        elif args.command == "translate":
            input_path = Path(args.input_file)
            if args.folder:
                files = []
                for ext in ['*.vtt', '*.srt', '*.txt', '*.csv']:
                    files.extend(input_path.glob(ext))
                for file in files:
                    textifier.translate_file(str(file), args.source_lang, args.target_lang, output_dir=args.output_dir)
            else:
                textifier.translate_file(args.input_file, args.source_lang, args.target_lang, output_dir=args.output_dir)

        elif args.command == "summarize":
            config = {
                'type': 'cloud' if args.provider in ['gemini', 'claude', 'openai'] else 'local',
                'provider': args.provider,
                'api_key': args.api_key,
                'model': args.model,
                'base_url': args.base_url
            }
            input_path = Path(args.input_file)
            if args.folder:
                files = [f for f in input_path.glob('*') if f.suffix.lower() in {'.txt', '.vtt', '.srt', '.csv'}]
                for file in files:
                    summary = textifier.summarize_text(str(file), args.prompt, config)
                    out_path = file.with_suffix(".summary.md")
                    with open(out_path, "w", encoding="utf-8") as f:
                        f.write(summary)
            else:
                summary = textifier.summarize_text(args.input_file, args.prompt, config)
                out_path = input_path.with_suffix(".summary.md")
                with open(out_path, "w", encoding="utf-8") as f:
                    f.write(summary)
                print(f"\n--- SUMMARY ---\n{summary}")

        elif args.command == "pipeline":
            # Simplified pipeline for CLI
            # 1. Transcribe
            trans_files = textifier.transcribe_media(args.input_file, output_dir=args.output_dir, language=args.language)
            
            # 2. Translate
            if args.translate_langs and trans_files:
                txt_file = next((f for f in trans_files if f.endswith(".txt")), None)
                if txt_file:
                    for lang in args.translate_langs:
                        textifier.translate_file(txt_file, source_lang="en", target_lang=lang, output_dir=args.output_dir)
            
            # 3. Summarize
            if args.summarize and trans_files:
                txt_file = next((f for f in trans_files if f.endswith(".txt")), None)
                if txt_file:
                    sum_config = {'type': 'cloud', 'provider': args.provider, 'api_key': args.api_key, 'model': args.summary_model}
                    summary = textifier.summarize_text(txt_file, "Summarize this transcript.", sum_config)
                    out_path = Path(txt_file).with_suffix(".summary.md")
                    with open(out_path, "w", encoding="utf-8") as f:
                        f.write(summary)

        elif args.command == "download-translation-model":
            textifier.download_translation_model()
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()