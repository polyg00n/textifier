import argparse
import os
from pathlib import Path
import whisper
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch

class Textifier:
    def __init__(self, load_translation_model=False, whisper_model_name="large"):
        # Create models directory if it doesn't exist
        self.models_dir = Path("models")
        self.models_dir.mkdir(exist_ok=True)
        
        # Initialize Whisper model
        self.whisper_model_name = whisper_model_name
        whisper_model_path = self.models_dir / "whisper"
        if not whisper_model_path.exists():
            print(f"Downloading Whisper model ({whisper_model_name})...")
            self.whisper_model = whisper.load_model(whisper_model_name, download_root=str(whisper_model_path))
        else:
            self.whisper_model = whisper.load_model(whisper_model_name, download_root=str(whisper_model_path))
        
        # Translation model will be loaded lazily when needed
        self.translation_tokenizer = None
        self.translation_model = None
        self.translation_model_path = self.models_dir / "translation"
        
        # Only load translation model if explicitly requested
        if load_translation_model:
            self._load_translation_model()
    
    def _load_translation_model(self):
        """Lazy load the translation model when needed."""
        if self.translation_model is not None:
            return  # Already loaded
        
        if not self.translation_model_path.exists():
            raise FileNotFoundError(
                "Translation model not found. Please download it first using: "
                "python textifier.py download-translation-model"
            )
        
        print("Loading translation model...")
        self.translation_tokenizer = AutoTokenizer.from_pretrained(
            "facebook/mbart-large-50-many-to-many-mmt",
            cache_dir=str(self.translation_model_path)
        )
        self.translation_model = AutoModelForSeq2SeqLM.from_pretrained(
            "facebook/mbart-large-50-many-to-many-mmt",
            cache_dir=str(self.translation_model_path)
        )
    
    def download_translation_model(self):
        """Download and save the translation model."""
        print("Downloading translation model...")
        self.translation_tokenizer = AutoTokenizer.from_pretrained(
            "facebook/mbart-large-50-many-to-many-mmt",
            cache_dir=str(self.translation_model_path)
        )
        self.translation_model = AutoModelForSeq2SeqLM.from_pretrained(
            "facebook/mbart-large-50-many-to-many-mmt",
            cache_dir=str(self.translation_model_path)
        )
        
        # Save models to disk
        torch.save(self.translation_model.state_dict(), self.translation_model_path / "model.pt")
        self.translation_tokenizer.save_pretrained(self.translation_model_path)
        print("Translation model downloaded and saved successfully!")

    def _normalize_path(self, path_str):
        """
        Normalize a path string to handle different formats and operating systems.
        
        Args:
            path_str (str): Input path string
            
        Returns:
            Path: Normalized path object
        """
        # Remove quotes if present
        path_str = path_str.strip('"\'')
        
        # Convert to Path object and resolve
        path = Path(path_str)
        
        # Check if path exists
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path_str}")
        
        return path

    def transcribe_media(self, input_path):
        """
        Transcribe a video or audio file to VTT format with timestamps.
        
        Args:
            input_path (str): Path to the input media file
            
        Returns:
            str: Path to the generated VTT file
        """
        # Normalize input path
        input_path = self._normalize_path(input_path)
        
        # Get the base name without extension
        output_path = input_path.with_suffix('.vtt')
        
        # Transcribe the audio
        result = self.whisper_model.transcribe(str(input_path))
        
        # Write VTT file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("WEBVTT\n\n")
            
            for i, segment in enumerate(result['segments']):
                start_time = self._format_time(segment['start'])
                end_time = self._format_time(segment['end'])
                text = segment['text'].strip()
                
                f.write(f"{i+1}\n")
                f.write(f"{start_time} --> {end_time}\n")
                f.write(f"{text}\n\n")
        
        return str(output_path)

    def translate_vtt(self, input_path, target_lang="fr"):
        """
        Translate a VTT file from English to the specified language while preserving timestamps.
        
        Args:
            input_path (str): Path to the input VTT file
            target_lang (str): Target language code (fr for French, hi for Hindi)
            
        Returns:
            str: Path to the translated VTT file
        """
        # Load translation model if not already loaded
        self._load_translation_model()
        
        # Normalize input path
        input_path = self._normalize_path(input_path)
        
        # Create output path with language suffix
        output_path = input_path.with_name(f"{input_path.stem}_{target_lang}{input_path.suffix}")
        
        # Set up language codes for mBART
        lang_codes = {
            "fr": "fr_XX",  # French
            "hi": "hi_IN"   # Hindi
        }
        
        if target_lang not in lang_codes:
            raise ValueError(f"Unsupported target language: {target_lang}. Supported languages: {list(lang_codes.keys())}")
        
        # Set source and target language for mBART
        self.translation_tokenizer.src_lang = "en_XX"
        target_lang_code = lang_codes[target_lang]
        
        with open(input_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                
                # Write header and empty lines as is
                if line == "WEBVTT" or not line:
                    f.write(f"{line}\n")
                    i += 1
                    continue
                
                # Write cue number
                if line.isdigit():
                    f.write(f"{line}\n")
                    i += 1
                    continue
                
                # Write timestamp line
                if " --> " in line:
                    f.write(f"{line}\n")
                    i += 1
                    continue
                
                # Only translate if the line contains actual text (not just numbers or timestamps)
                if line and not line.isdigit() and " --> " not in line:
                    # Prepare text for translation
                    inputs = self.translation_tokenizer(
                        line,
                        return_tensors="pt",
                        padding=True,
                        truncation=True,
                        max_length=512
                    )
                    
                    # Generate translation with improved parameters
                    translated = self.translation_model.generate(
                        **inputs,
                        forced_bos_token_id=self.translation_tokenizer.lang_code_to_id[target_lang_code],
                        max_length=512,
                        num_beams=5,
                        early_stopping=True,
                        no_repeat_ngram_size=3,
                        length_penalty=1.0
                    )
                    
                    # Decode the translation
                    translated_text = self.translation_tokenizer.batch_decode(
                        translated,
                        skip_special_tokens=True
                    )[0]
                    
                    f.write(f"{translated_text}\n")
                else:
                    f.write(f"{line}\n")
                
                i += 1
        
        return str(output_path)

    def _format_time(self, seconds):
        """Format seconds into VTT timestamp format (HH:MM:SS.mmm)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:06.3f}"

def main():
    parser = argparse.ArgumentParser(description="Textifier - Video/Audio Transcription and Translation Tool")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Transcribe command
    transcribe_parser = subparsers.add_parser("transcribe", help="Transcribe a video/audio file to VTT")
    transcribe_parser.add_argument("input_file", help="Path to the input video/audio file or folder")
    transcribe_parser.add_argument("-f", "--folder", action="store_true", help="Process all files in the specified folder")
    transcribe_parser.add_argument("-m", "--model", default="large", 
                                choices=["tiny", "base", "small", "medium", "large"],
                                help="Whisper model size (default: large)")
    
    # Translate command
    translate_parser = subparsers.add_parser("translate", help="Translate a VTT file from English to another language")
    translate_parser.add_argument("input_file", help="Path to the input VTT file or folder")
    translate_parser.add_argument("-f", "--folder", action="store_true", help="Process all files in the specified folder")
    translate_parser.add_argument("-l", "--lang", choices=["fr", "hi"], default="fr", 
                                help="Target language (fr for French, hi for Hindi)")
    
    # Download translation model command
    download_parser = subparsers.add_parser("download-translation-model", 
                                          help="Download the translation model (mBART)")
    
    args = parser.parse_args()
    
    # Get model name from args if transcribe command, otherwise use default
    whisper_model_name = getattr(args, 'model', 'large')
    textifier = Textifier(whisper_model_name=whisper_model_name)
    
    try:
        if args.command == "transcribe":
            if args.folder:
                # Process all files in the folder
                input_path = Path(args.input_file)
                if not input_path.is_dir():
                    raise NotADirectoryError(f"Not a directory: {args.input_file}")
                
                # Get all video/audio files
                video_extensions = {'.mp4', '.avi', '.mkv', '.mov', '.wmv', '.mp3', '.wav', '.m4a', '.aac'}
                files = [f for f in input_path.glob('*') if f.suffix.lower() in video_extensions]
                
                if not files:
                    print(f"No supported video/audio files found in {args.input_file}")
                    return
                
                print(f"Found {len(files)} files to transcribe")
                for i, file in enumerate(files, 1):
                    print(f"\nProcessing file {i}/{len(files)}: {file.name}")
                    output_path = textifier.transcribe_media(str(file))
                    print(f"Transcription completed. Output saved to: {output_path}")
            else:
                # Process single file
                output_path = textifier.transcribe_media(args.input_file)
                print(f"Transcription completed. Output saved to: {output_path}")
                
        elif args.command == "translate":
            if args.folder:
                # Process all files in the folder
                input_path = Path(args.input_file)
                if not input_path.is_dir():
                    raise NotADirectoryError(f"Not a directory: {args.input_file}")
                
                # Get all VTT files
                files = list(input_path.glob('*.vtt'))
                
                if not files:
                    print(f"No VTT files found in {args.input_file}")
                    return
                
                print(f"Found {len(files)} files to translate")
                for i, file in enumerate(files, 1):
                    print(f"\nProcessing file {i}/{len(files)}: {file.name}")
                    output_path = textifier.translate_vtt(str(file), args.lang)
                    print(f"Translation completed. Output saved to: {output_path}")
            else:
                # Process single file
                output_path = textifier.translate_vtt(args.input_file, args.lang)
                print(f"Translation completed. Output saved to: {output_path}")
        elif args.command == "download-translation-model":
            textifier.download_translation_model()
        else:
            parser.print_help()
    except FileNotFoundError as e:
        print(f"Error: {e}")
    except NotADirectoryError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main() 