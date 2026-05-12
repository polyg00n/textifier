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


def _add_whisper_options(parser):
    """Add shared Whisper transcription options to a parser."""
    parser.add_argument("-m", "--model", default="large-v3-turbo",
                        help="Whisper model [default: large-v3-turbo]")
    parser.add_argument("--language",
                        help="Source audio language code [default: auto-detect]")
    parser.add_argument("--task", choices=["transcribe", "translate"], default="transcribe",
                        help="Task: 'transcribe' keeps original language, 'translate' converts to English [default: transcribe]")
    parser.add_argument("--output-formats", nargs="+", default=["vtt", "srt", "txt", "csv", "tsv"],
                        help="Output formats to generate [default: vtt srt txt csv tsv]")
    parser.add_argument("--word-timestamps", action="store_true",
                        help="Export word-level timestamps to .words.json")
    parser.add_argument("--vad-filter", action="store_true", default=True,
                        help="Enable Silero VAD filter [default: True]")
    parser.add_argument("--no-vad-filter", action="store_true",
                        help="Disable VAD filter")
    parser.add_argument("--initial-prompt",
                        help="Context text to guide punctuation, capitalization, or terminology")
    parser.add_argument("--beam-size", type=int, default=5,
                        help="Number of beams for beam search [default: 5]")
    parser.add_argument("--best-of", type=int, default=5,
                        help="Number of candidates to sample from [default: 5]")
    parser.add_argument("--patience", type=float, default=1.0,
                        help="Beam search patience factor [default: 1.0]")
    parser.add_argument("--temperature", type=float, default=0.0,
                        help="Sampling temperature, 0=deterministic [default: 0.0]")
    parser.add_argument("--repetition-penalty", type=float, default=1.1,
                        help="Penalty for repeated tokens to prevent loops [default: 1.1]")
    parser.add_argument("--no-speech-threshold", type=float, default=0.6,
                        help="Threshold above which a segment is considered silent [default: 0.6]")
    parser.add_argument("--condition-on-previous-text", action="store_true", default=True,
                        help="Condition on previous text for context [default: True]")
    parser.add_argument("--no-condition-on-previous-text", action="store_true",
                        help="Disable conditioning on previous text")
    parser.add_argument("--device", choices=["auto", "cuda", "cpu"], default="auto",
                        help="Compute device [default: auto]")


def _build_whisper_kwargs(args):
    """Build the kwargs dict for transcribe_media from parsed args."""
    kwargs = {
        "task": args.task,
        "language": args.language,
        "word_timestamps": args.word_timestamps,
        "vad_filter": not args.no_vad_filter if args.no_vad_filter else args.vad_filter,
        "initial_prompt": args.initial_prompt,
        "beam_size": args.beam_size,
        "best_of": args.best_of,
        "patience": args.patience,
        "temperature": args.temperature,
        "repetition_penalty": args.repetition_penalty,
        "no_speech_threshold": args.no_speech_threshold,
        "condition_on_previous_text": not args.no_condition_on_previous_text,
        "output_formats": args.output_formats,
    }
    return kwargs


def main():
    parser = argparse.ArgumentParser(
        description="Textifier v2.1.0 - Video/Audio Transcription, Translation, and Summarization Tool",
        epilog="Examples:\n"
               "  textifier.py transcribe video.mp4\n"
               "  textifier.py transcribe video.mp4 --output-formats vtt srt txt --beam-size 8\n"
               "  textifier.py transcribe folder/ --folder --language hi --word-timestamps\n"
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
    _add_whisper_options(transcribe_parser)
    
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
    summarize_parser.add_argument("--prompt", default="Create a high-value summary with core insights and actionable items.", help="Summarization prompt")
    summarize_parser.add_argument("--provider", choices=['ollama', 'lm_studio', 'gemini', 'claude', 'openai'], default='gemini', help="LLM provider")
    summarize_parser.add_argument("--api-key", help="API Key for cloud providers")
    summarize_parser.add_argument("--model", help="LLM Model name (e.g., gemini-1.5-flash, llama3)")
    summarize_parser.add_argument("--base-url", help="Base URL for local providers (Ollama/LM Studio)")
    summarize_parser.add_argument("--strategy", choices=['single_pass', 'map_reduce'], default='map_reduce', help="Summarization strategy [default: map_reduce]")
    summarize_parser.add_argument("--chunk-size", type=int, default=8000, help="Chunk size for Map-Reduce [default: 8000]")
    summarize_parser.add_argument("--overlap", type=int, default=500, help="Chunk overlap [default: 500]")
    summarize_parser.add_argument("--temp", type=float, default=0.3, help="LLM Temperature [default: 0.3]")
    summarize_parser.add_argument("--max-tokens", type=int, default=1500, help="Max output tokens [default: 1500]")
    
    # Pipeline command
    pipeline_parser = subparsers.add_parser("pipeline", help="Run full pipeline: transcribe -> translate -> summarize")
    pipeline_parser.add_argument("input_file", help="Path to input media file or folder")
    pipeline_parser.add_argument("-f", "--folder", action="store_true", help="Process all media files in the folder")
    pipeline_parser.add_argument("-o", "--output-dir", help="Directory for all outputs")
    _add_whisper_options(pipeline_parser)
    # Pipeline-specific translation & summarization options
    pipeline_parser.add_argument("--translate-langs", nargs="+", help="One or more target language codes for translation")
    pipeline_parser.add_argument("--source-lang", default="en", help="Source language for translation [default: en]")
    pipeline_parser.add_argument("--summarize", action="store_true", help="Run summarization after processing")
    pipeline_parser.add_argument("--provider", default='gemini', help="LLM provider for summarization")
    pipeline_parser.add_argument("--api-key", help="API Key for summarization")
    pipeline_parser.add_argument("--summary-model", help="LLM Model name for summarization")
    pipeline_parser.add_argument("--strategy", choices=['single_pass', 'map_reduce'], default='map_reduce', help="Summarization strategy")
    pipeline_parser.add_argument("--summary-prompt", default="Summarize this transcript.", help="Prompt for summarization")
    pipeline_parser.add_argument("--summary-temp", type=float, default=0.3, help="LLM Temperature for summarization [default: 0.3]")
    pipeline_parser.add_argument("--summary-max-tokens", type=int, default=1500, help="Max output tokens for summarization [default: 1500]")
    
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
            kwargs = _build_whisper_kwargs(args)
            if args.folder:
                video_extensions = {'.mp4', '.avi', '.mkv', '.mov', '.wmv', '.mp3', '.wav', '.m4a', '.aac', '.flac', '.ogg'}
                files = [f for f in input_path.glob('*') if f.suffix.lower() in video_extensions]
                if not files:
                    print(f"[!] No media files found in {input_path}")
                    return
                print(f"[*] Found {len(files)} media files to transcribe")
                for i, file in enumerate(files, 1):
                    print(f"\n[*] Processing {i}/{len(files)}: {file.name}")
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
                'base_url': args.base_url,
                'strategy': args.strategy,
                'chunk_size': args.chunk_size,
                'chunk_overlap': args.overlap,
                'temperature': args.temp,
                'max_tokens': args.max_tokens
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
            whisper_kwargs = _build_whisper_kwargs(args)

            # Determine files to process
            input_path = Path(args.input_file)
            video_extensions = {'.mp4', '.avi', '.mkv', '.mov', '.wmv', '.mp3', '.wav', '.m4a', '.aac', '.flac', '.ogg'}
            
            if args.folder:
                media_files = [f for f in input_path.glob('*') if f.suffix.lower() in video_extensions]
                if not media_files:
                    print(f"[!] No media files found in {input_path}")
                    return
                print(f"[*] Pipeline: Found {len(media_files)} media files")
            else:
                media_files = [input_path]

            for i, media_file in enumerate(media_files, 1):
                print(f"\n{'='*50}")
                print(f"[*] Pipeline {i}/{len(media_files)}: {media_file.name}")
                print(f"{'='*50}")
                
                # 1. Transcribe
                trans_files = textifier.transcribe_media(str(media_file), output_dir=args.output_dir, **whisper_kwargs)
                if not trans_files:
                    print(f"[!] Transcription failed for {media_file.name}, skipping.")
                    continue
                
                # 2. Translate
                if args.translate_langs:
                    # Find all translatable files from transcription output
                    translatable_exts = {'.vtt', '.srt', '.txt', '.csv'}
                    for trans_file in trans_files:
                        if Path(trans_file).suffix.lower() in translatable_exts:
                            for lang in args.translate_langs:
                                print(f"[*] Translating {Path(trans_file).name} to {lang}...")
                                textifier.translate_file(trans_file, source_lang=args.source_lang, target_lang=lang, output_dir=args.output_dir)
                
                # 3. Summarize
                if args.summarize:
                    txt_file = next((f for f in trans_files if f.endswith(".txt")), None)
                    if txt_file:
                        sum_config = {
                            'type': 'cloud' if args.provider in ['gemini', 'claude', 'openai'] else 'local',
                            'provider': args.provider,
                            'api_key': args.api_key,
                            'model': args.summary_model,
                            'strategy': args.strategy,
                            'temperature': args.summary_temp,
                            'max_tokens': args.summary_max_tokens,
                        }
                        summary = textifier.summarize_text(txt_file, args.summary_prompt, sum_config)
                        out_path = Path(txt_file).with_suffix(".summary.md")
                        with open(out_path, "w", encoding="utf-8") as f:
                            f.write(summary)
                        print(f"[*] Summary saved to {out_path.name}")
                        
                        # Translate the summary if target languages are provided
                        if args.translate_langs:
                            for lang in args.translate_langs:
                                textifier.translate_file(str(out_path), source_lang=args.source_lang, target_lang=lang, output_dir=args.output_dir)

            print(f"\n[*] Pipeline complete!")

        elif args.command == "download-translation-model":
            textifier.download_translation_model()
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()