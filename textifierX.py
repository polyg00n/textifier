import argparse
import os
from pathlib import Path
import whisperx # Changed from 'whisper'
import torch
import gc # For GPU memory management
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

class Textifier:
    def __init__(self, load_translation_model=False):
        # Create models directory if it doesn't exist
        self.models_dir = Path("models")
        self.models_dir.mkdir(exist_ok=True)
        
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
                "python textifierX.py download-translation-model"
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

    def transcribe_media(self, input_path, model_name, device, compute_type, batch_size, language=None):
        """
        Transcribe a video or audio file to VTT format with timestamps using WhisperX.
        
        Args:
            input_path (str): Path to the input media file
            model_name (str): Name of the WhisperX model to use (e.g., "large-v2", "base")
            device (str): Device to run the model on ("cuda" or "cpu")
            compute_type (str): Compute type ("float16" for GPU, "int8" for CPU)
            batch_size (int): Batch size for transcription
            language (str, optional): Language code (e.g., "en", "fr"). If None, WhisperX detects.
            
        Returns:
            str: Path to the generated VTT file
        """
        # Normalize input path
        input_path = self._normalize_path(input_path)
        
        # Get the base name without extension
        output_path = input_path.with_suffix('.vtt')
        
        print(f"Loading WhisperX model: {model_name} on {device} with {compute_type} compute type...")
        # 1. Transcribe with WhisperX (batched)
        # download_root specifies where WhisperX models are cached
        whisperx_model = whisperx.load_model(
            model_name, 
            device, 
            compute_type=compute_type, 
            download_root=str(self.models_dir / "whisperx_asr_models")
        )
        
        print(f"Loading audio: {input_path}")
        audio = whisperx.load_audio(str(input_path))
        
        print(f"Transcribing audio with batch size {batch_size}...")
        result = whisperx_model.transcribe(audio, batch_size=batch_size, language=language)
        
        # Clean up ASR model to free GPU memory
        del whisperx_model
        gc.collect()
        if device == "cuda":
            torch.cuda.empty_cache()

        print(f"Detected language: {result['language']}")
        
        print("Loading alignment model...")
        # 2. Align whisper output for accurate word-level timestamps
        # download_root specifies where alignment models are cached
        model_a, metadata = whisperx.load_align_model(
            language_code=result["language"], 
            device=device, 
            download_root=str(self.models_dir / "whisperx_align_models")
        )
        
        print("Aligning segments...")
        result = whisperx.align(
            result["segments"], 
            model_a, 
            metadata, 
            audio, 
            device, 
            return_char_alignments=False
        )
        
        # Clean up alignment model to free GPU memory
        del model_a
        gc.collect()
        if device == "cuda":
            torch.cuda.empty_cache()

        # Optional: Speaker Diarization (requires Hugging Face token and specific models)
        # Uncomment and provide your Hugging Face token if you want to use this feature.
        # print("Performing speaker diarization (if enabled)...")
        # YOUR_HF_TOKEN = os.getenv("HF_TOKEN") # It's recommended to set this as an environment variable
        # if YOUR_HF_TOKEN:
        #     try:
        #         diarize_model = whisperx.diarize.DiarizationPipeline(use_auth_token=YOUR_HF_TOKEN, device=device)
        #         diarize_segments = diarize_model(audio)
        #         result = whisperx.assign_word_speakers(diarize_segments, result)
        #         print("Diarization complete.")
        #     except Exception as e:
        #         print(f"Warning: Speaker diarization failed. Ensure HF_TOKEN is valid and models are accessible. Error: {e}")
        # else:
        #     print("Skipping speaker diarization: HF_TOKEN not found.")


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
    
    # Determine default device based on CUDA availability
    default_device = "cuda" if torch.cuda.is_available() else "cpu"
    default_compute_type = "float16" if default_device == "cuda" else "int8"

    # Transcribe command
    transcribe_parser = subparsers.add_parser("transcribe", help="Transcribe a video/audio file to VTT")
    transcribe_parser.add_argument("input_file", help="Path to the input video/audio file or folder")
    transcribe_parser.add_argument("-f", "--folder", action="store_true", help="Process all files in the specified folder")
    transcribe_parser.add_argument("-m", "--model_name", default="large-v2", 
                                help="WhisperX model name (e.g., 'base', 'large-v2')")
    transcribe_parser.add_argument("-d", "--device", default=default_device, 
                                help="Device to use for transcription ('cuda' or 'cpu')")
    transcribe_parser.add_argument("-c", "--compute_type", default=default_compute_type, 
                                help="Compute type ('float16' for GPU, 'int8' for CPU)")
    transcribe_parser.add_argument("-b", "--batch_size", type=int, default=16, 
                                help="Batch size for transcription")
    transcribe_parser.add_argument("-l", "--language", default=None, 
                                help="Language code (e.g., 'en', 'fr'). If not specified, WhisperX detects.")
    
    # Translate command (remains the same)
    translate_parser = subparsers.add_parser("translate", help="Translate a VTT file from English to another language")
    translate_parser.add_argument("input_file", help="Path to the input VTT file or folder")
    translate_parser.add_argument("-f", "--folder", action="store_true", help="Process all files in the specified folder")
    translate_parser.add_argument("-lt", "--lang", choices=["fr", "hi"], default="fr", 
                                help="Target language (fr for French, hi for Hindi)")
    
    # Download translation model command
    download_parser = subparsers.add_parser("download-translation-model", 
                                          help="Download the translation model (mBART)")
    
    args = parser.parse_args()
    textifier = Textifier()
    
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
                    output_path = textifier.transcribe_media(
                        str(file), 
                        args.model_name, 
                        args.device, 
                        args.compute_type, 
                        args.batch_size,
                        args.language
                    )
                    print(f"Transcription completed. Output saved to: {output_path}")
            else:
                # Process single file
                output_path = textifier.transcribe_media(
                    args.input_file, 
                    args.model_name, 
                    args.device, 
                    args.compute_type, 
                    args.batch_size,
                    args.language
                )
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
