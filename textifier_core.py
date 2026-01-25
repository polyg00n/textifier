
import os
import logging
from pathlib import Path
import urllib.request
import sys
import time
import subprocess
import numpy as np
import csv

# Confgure logger
# import whisper
# import transformers

# Supported Whisper models and their CTranslate2 (faster-whisper) HuggingFace repos
# We use faster-whisper compatible naming
_WHISPER_MODELS = {
    "tiny": "Systran/faster-whisper-tiny",
    "tiny.en": "Systran/faster-whisper-tiny.en",
    "base": "Systran/faster-whisper-base",
    "base.en": "Systran/faster-whisper-base.en",
    "small": "Systran/faster-whisper-small",
    "small.en": "Systran/faster-whisper-small.en",
    "medium": "Systran/faster-whisper-medium",
    "medium.en": "Systran/faster-whisper-medium.en",
    "large-v1": "Systran/faster-whisper-large-v1",
    "large-v2": "Systran/faster-whisper-large-v2",
    "large-v3": "Systran/faster-whisper-large-v3",
    "large-v3-turbo": "deepdml/faster-whisper-large-v3-turbo-ct2",
    "large": "Systran/faster-whisper-large-v3",
    "distil-large-v3": "Systran/faster-distil-whisper-large-v3",
    "distil-medium.en": "Systran/faster-distil-whisper-medium.en",
    "distil-small.en": "Systran/faster-distil-whisper-small.en",
    "distil-large-v2": "Systran/faster-distil-whisper-large-v2",
}

# Confgure logger
logging.basicConfig(
    filename='textifier.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class ModelManager:
    """Handles downloading, verifying, and deleting models."""
    def __init__(self, models_dir=None, status_callback=None):
        # Resolve models_dir relative to this file to ensure consistency
        if models_dir is None:
            base_dir = Path(__file__).parent.absolute()
            self.models_dir = base_dir / "models"
        else:
            self.models_dir = Path(models_dir).absolute()
            
        self.whisper_dir = self.models_dir / "whisper"
        self.translation_dir = self.models_dir / "translation"
        self.status_callback = status_callback
        
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.whisper_dir.mkdir(parents=True, exist_ok=True)
        self.translation_dir.mkdir(parents=True, exist_ok=True)

    def _update_status(self, message):
        logging.info(message)
        if self.status_callback:
            self.status_callback(message)

    def get_whisper_model_path(self, model_name):
        return self.whisper_dir / model_name

    def is_whisper_model_available(self, model_name):
        path = self.get_whisper_model_path(model_name)
        # Faster-whisper models are directories with model.bin
        return path.exists() and (path / "model.bin").exists()

    def get_model_size(self, path):
        """Calculate total size of a directory or file in MB."""
        if not path.exists():
            return 0
        if path.is_file():
            return path.stat().st_size / (1024 * 1024)
        total_size = 0
        for f in path.glob('**/*'):
            if f.is_file():
                total_size += f.stat().st_size
        return total_size / (1024 * 1024)

    def download_whisper_model(self, model_name):
        """Download a faster-whisper model using huggingface_hub."""
        if model_name not in _WHISPER_MODELS:
            raise ValueError(f"Unknown model: {model_name}")
            
        repo_id = _WHISPER_MODELS[model_name]
        dest = self.get_whisper_model_path(model_name)
        
        self._update_status(f"Downloading model '{model_name}' from {repo_id}...")
        
        try:
            from huggingface_hub import snapshot_download
            snapshot_download(
                repo_id=repo_id,
                local_dir=str(dest),
                local_dir_use_symlinks=False
            )
            self._update_status(f"Model '{model_name}' downloaded successfully.")
        except Exception as e:
            self._update_status(f"Error downloading model: {e}")
            raise e

    def delete_whisper_model(self, model_name):
        """Delete a local Whisper model."""
        dest = self.get_whisper_model_path(model_name)
        if dest.exists():
            import shutil
            self._update_status(f"Deleting model '{model_name}'...")
            shutil.rmtree(dest)
            self._update_status(f"Model '{model_name}' deleted.")
            return True
        return False

    def is_translation_model_available(self):
        # mBART needs config and the sentencepiece model
        return (self.translation_dir.exists() and 
                (self.translation_dir / "config.json").exists() and 
                (self.translation_dir / "sentencepiece.bpe.model").exists())

    def download_translation_model(self):
        """Download mBART model."""
        self._update_status("Downloading translation model (mBART-large-50)...")
        try:
            from huggingface_hub import snapshot_download
            model_id = "facebook/mbart-large-50-many-to-many-mmt"
            snapshot_download(repo_id=model_id, local_dir=str(self.translation_dir), local_dir_use_symlinks=False)
            self._update_status("Translation model downloaded successfully.")
        except Exception as e:
            self._update_status(f"Error downloading translation model: {e}")
            raise e

class Transcriber:
    """Handles audio extraction and Whisper transcription."""
    def __init__(self, model_manager, status_callback=None):
        self.model_manager = model_manager
        self.status_callback = status_callback
        self.whisper_model = None
        self.whisper_model_name = None
        self.stop_requested = False

    def _update_status(self, message):
        if self.status_callback:
            self.status_callback(message)

    def load_audio(self, file_path, sr=16000):
        """Extract audio using ffmpeg pipe to avoid intermediate disk writes."""
        cmd = [
            "ffmpeg",
            "-v", "quiet",
            "-i", str(file_path),
            "-f", "s16le",
            "-acodec", "pcm_s16le",
            "-ar", str(sr),
            "-ac", "1",
            "-"
        ]
        try:
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
            if process.returncode != 0:
                raise RuntimeError(f"FFmpeg failed: {stderr.decode()}")
            
            return np.frombuffer(stdout, dtype=np.int16).astype(np.float32) / 32768.0
        except Exception as e:
            self._update_status(f"FFmpeg error: {e}. Falling back to standard loading.")
            return str(file_path) # Fallback to letting faster-whisper handle it

    def load_model(self, model_name, device="auto", compute_type="default"):
        if self.whisper_model and self.whisper_model_name == model_name:
            if device != "auto" and getattr(self, '_last_device', None) == device:
                return
        
        if not self.model_manager.is_whisper_model_available(model_name):
            self.model_manager.download_whisper_model(model_name)
            
        from faster_whisper import WhisperModel
        import torch
        
        # 1. Device Detection
        if device == "auto":
            device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # 2. Compute Type Multi-stage Fallback
        model_path = str(self.model_manager.get_whisper_model_path(model_name))
        
        # Sequence of types to try per device
        cuda_types = ["float16", "int8_float16", "int8", "float32"]
        cpu_types = ["int8", "float32"]
        
        if device == "cuda":
            # If user explicitly requested a type (not "default"), put it first
            if compute_type != "default" and compute_type in cuda_types:
                cuda_types.remove(compute_type)
                cuda_types.insert(0, compute_type)
            
            for ctype in cuda_types:
                try:
                    self._update_status(f"Trying {model_name} on CUDA ({ctype})...")
                    self.whisper_model = WhisperModel(model_path, device="cuda", compute_type=ctype)
                    self._last_compute_type = ctype
                    self._last_device = "cuda"
                    break 
                except Exception as e:
                    self._update_status(f"CUDA {ctype} failed: {str(e).split('.')[0]}.")
                    continue
            
        # If CUDA failed or was never selected, try CPU
        if not self.whisper_model:
            device = "cpu"
            for ctype in cpu_types:
                try:
                    self._update_status(f"Trying {model_name} on CPU ({ctype})...")
                    self.whisper_model = WhisperModel(model_path, device="cpu", compute_type=ctype)
                    self._last_compute_type = ctype
                    self._last_device = "cpu"
                    break
                except Exception as e:
                    self._update_status(f"CPU {ctype} failed: {e}")
                    continue

        if not self.whisper_model:
            raise RuntimeError(f"Could not load Whisper model '{model_name}' on any device/compute type.")

        self.whisper_model_name = model_name
        self._update_status(f"READY: {model_name} on {self._last_device} ({self._last_compute_type}).")

    def transcribe(self, input_path, **kwargs):
        self.stop_requested = False
        audio = self.load_audio(input_path)
        
        segments, info = self.whisper_model.transcribe(audio, **kwargs)
        self._update_status(f"Detected language: {info.language} ({info.language_probability:.2f})")
        
        result_segments = []
        for segment in segments:
            if self.stop_requested:
                return None
            result_segments.append(segment)
            self._update_status(f"[{FormatHandler.format_vtt_time(segment.start)}] {segment.text}")
        
        return result_segments, info

class Translator:
    """Handles text translation using mBART."""
    def __init__(self, model_manager, status_callback=None):
        self.model_manager = model_manager
        self.status_callback = status_callback
        self.model = None
        self.tokenizer = None

    def _update_status(self, message):
        if self.status_callback:
            self.status_callback(message)

    def load_model(self):
        if self.model: return
        if not self.model_manager.is_translation_model_available():
            self.model_manager.download_translation_model()
            
        from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
        model_path = str(self.model_manager.translation_dir)
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_path)
        self._update_status("Translation model loaded.")

    def translate(self, text, source_lang="en", target_lang="fr"):
        self.load_model()
        # Comprehensive mBART-50 language code mapping
        lang_codes = {
            "en": "en_XX", "fr": "fr_XX", "es": "es_XX", "de": "de_DE", "it": "it_IT",
            "pt": "pt_XX", "nl": "nl_XX", "ru": "ru_RU", "pl": "pl_PL", "tr": "tr_TR",
            "hi": "hi_IN", "gu": "gu_IN", "mr": "mr_IN", "ta": "ta_IN", "te": "te_IN",
            "bn": "bn_IN", "ml": "ml_IN", "ja": "ja_XX", "ko": "ko_KR", "zh": "zh_CN",
            "ar": "ar_AR", "he": "he_IL", "fa": "fa_IR", "ur": "ur_PK", "vi": "vi_VN",
            "th": "th_TH", "id": "id_ID", "ms": "ms_MY", "tl": "tl_XX", "sw": "sw_KE",
            "af": "af_ZA", "xh": "xh_ZA", "cs": "cs_CZ", "sk": "sk_SK", "hr": "hr_HR",
            "sr": "sr_RS", "bg": "bg_BG", "mk": "mk_MK", "uk": "uk_UA", "ro": "ro_RO",
            "hu": "hu_HU", "fi": "fi_FI", "sv": "sv_SE", "no": "no_XX", "da": "da_DK",
            "et": "et_EE", "lv": "lv_LV", "lt": "lt_LT", "ka": "ka_GE", "az": "az_AZ",
            "kk": "kk_KZ", "mn": "mn_MN", "ne": "ne_NP", "si": "si_LK", "my": "my_MM",
            "km": "km_KH", "ps": "ps_AF"
        }
        
        # Get mBART codes or use input as-is if already in mBART format
        src_code = lang_codes.get(source_lang, source_lang)
        tgt_code = lang_codes.get(target_lang, target_lang)
        
        if tgt_code not in self.tokenizer.lang_code_to_id:
            raise ValueError(f"Unsupported target language: {target_lang}")
            
        self.tokenizer.src_lang = src_code
        inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
        translated = self.model.generate(
            **inputs,
            forced_bos_token_id=self.tokenizer.lang_code_to_id[lang_codes[target_lang]],
            max_length=512, num_beams=5
        )
        return self.tokenizer.batch_decode(translated, skip_special_tokens=True)[0]

class FormatHandler:
    """Handles VTT/SRT parsing and saving."""
    @staticmethod
    def format_vtt_time(seconds):
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = seconds % 60
        return f"{h:02d}:{m:02d}:{s:06.3f}"

    @staticmethod
    def format_srt_time(seconds):
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = seconds % 60
        return f"{h:02d}:{m:02d}:{int(s):02d},{int((s % 1) * 1000):03d}"

    @staticmethod
    def save_vtt(segments, path):
        with open(path, "w", encoding="utf-8") as f:
            f.write("WEBVTT\n\n")
            for i, s in enumerate(segments):
                f.write(f"{i+1}\n{FormatHandler.format_vtt_time(s.start)} --> {FormatHandler.format_vtt_time(s.end)}\n{s.text.strip()}\n\n")

    @staticmethod
    def save_srt(segments, path):
        with open(path, "w", encoding="utf-8") as f:
            for i, s in enumerate(segments):
                f.write(f"{i+1}\n{FormatHandler.format_srt_time(s.start)} --> {FormatHandler.format_srt_time(s.end)}\n{s.text.strip()}\n\n")
    
    @staticmethod
    def save_txt(segments, path):
        with open(path, "w", encoding="utf-8") as f:
            for s in segments:
                f.write(s.text.strip() + "\n")
    
    @staticmethod
    def save_csv(segments, path):
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Start", "End", "Text"])
            for s in segments:
                writer.writerow([
                    FormatHandler.format_vtt_time(s.start),
                    FormatHandler.format_vtt_time(s.end),
                    s.text.strip()
                ])

    @staticmethod
    def parse_vtt(file_path):
        """Parse a VTT file into a list of dictionaries."""
        cues = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            blocks = content.split('\n\n')
            for block in blocks:
                lines = block.strip().split('\n')
                if not lines or lines[0] == "WEBVTT": continue
                timestamp_line_index = -1
                for i, line in enumerate(lines):
                    if " --> " in line:
                        timestamp_line_index = i
                        break
                if timestamp_line_index != -1:
                    times = lines[timestamp_line_index].split(" --> ")
                    if len(times) == 2:
                        start, end = times[0].strip(), times[1].strip()
                        text = "\n".join(lines[timestamp_line_index+1:])
                        cues.append({'start': start, 'end': end, 'text': text})
        except Exception as e:
            logging.error(f"Error parsing VTT: {e}")
        return cues

    @staticmethod
    def save_vtt_from_data(data, output_path):
        """Save VTT data (list of dicts) to a file."""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("WEBVTT\n\n")
            for i, cue in enumerate(data):
                f.write(f"{i+1}\n{cue['start']} --> {cue['end']}\n{cue['text']}\n\n")
    
    @staticmethod
    def parse_srt(file_path):
        """Parse an SRT file into a list of dictionaries."""
        segments = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            blocks = content.strip().split('\n\n')
            for block in blocks:
                lines = block.strip().split('\n')
                if len(lines) >= 3:
                    # Skip index line, get timestamp and text
                    timestamp_line = lines[1] if '-->' in lines[1] else (lines[0] if '-->' in lines[0] else None)
                    if timestamp_line and '-->' in timestamp_line:
                        times = timestamp_line.split(' --> ')
                        if len(times) == 2:
                            start, end = times[0].strip(), times[1].strip()
                            # Join remaining lines as text
                            text_start_idx = 2 if '-->' in lines[1] else 1
                            text = '\n'.join(lines[text_start_idx:])
                            segments.append({'start': start, 'end': end, 'text': text})
        except Exception as e:
            logging.error(f"Error parsing SRT: {e}")
        return segments
    
    @staticmethod
    def save_srt_from_data(data, output_path):
        """Save SRT data (list of dicts) to a file."""
        with open(output_path, 'w', encoding='utf-8') as f:
            for i, segment in enumerate(data, 1):
                f.write(f"{i}\n{segment['start']} --> {segment['end']}\n{segment['text']}\n\n")
    
    @staticmethod
    def parse_csv(file_path):
        """Parse a CSV file into a list of dictionaries."""
        segments = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if 'Start' in row and 'End' in row and 'Text' in row:
                        segments.append({
                            'start': row['Start'],
                            'end': row['End'],
                            'text': row['Text']
                        })
        except Exception as e:
            logging.error(f"Error parsing CSV: {e}")
        return segments
    
    @staticmethod
    def save_csv_from_data(data, output_path):
        """Save CSV data (list of dicts) to a file."""
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Start', 'End', 'Text'])
            for segment in data:
                writer.writerow([segment['start'], segment['end'], segment['text']])
    
    @staticmethod
    def parse_txt(file_path):
        """Parse a TXT file into a list of text lines."""
        lines = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f.readlines() if line.strip()]
        except Exception as e:
            logging.error(f"Error parsing TXT: {e}")
        return lines
    
    @staticmethod
    def save_txt_from_data(lines, output_path):
        """Save text lines to a TXT file."""
        with open(output_path, 'w', encoding='utf-8') as f:
            for line in lines:
                f.write(line + '\n')

class CallbackStream:
    """Redirects writes to a callback function."""
    def __init__(self, callback):
        self.callback = callback
        self.buffer = ""

    def write(self, message):
        if message.strip():
            self.callback(message.strip())
            
    def flush(self):
        pass

class TextifierCore:
    def __init__(self, load_translation_model=False, whisper_model_name="large", status_callback=None):
        self.status_callback = status_callback
        logging.info("Initializing TextifierCore")
        
        self.model_manager = ModelManager(status_callback=status_callback)
        self.transcriber = Transcriber(self.model_manager, status_callback=status_callback)
        self.translator = Translator(self.model_manager, status_callback=status_callback)
        self.format_handler = FormatHandler()
        
        self.whisper_model_name = whisper_model_name
        
        if load_translation_model:
            self.translator.load_model()

    def _update_status(self, message):
        logging.info(message)
        if self.status_callback:
            self.status_callback(message)

    def load_whisper_model(self, **kwargs):
        self.transcriber.load_model(self.whisper_model_name, **kwargs)

    @property
    def whisper_model(self):
        return self.transcriber.whisper_model

    @whisper_model.setter
    def whisper_model(self, value):
        self.transcriber.whisper_model = value

    @property
    def stop_requested(self):
        return self.transcriber.stop_requested

    @stop_requested.setter
    def stop_requested(self, value):
        self.transcriber.stop_requested = value

    def transcribe_media(self, input_path, output_dir=None, **kwargs):
        input_path = self._normalize_path(input_path)
        
        # CRITICAL FIX FOR GUI COMPATIBILITY:
        # The GUI passes 'output_format' in kwargs, but faster-whisper will crash
        # if it receives an unknown argument. We remove it here.
        # We ignore the requested format and simply output ALL formats.
        _ = kwargs.pop('output_format', None)
        
        # IMPLEMENTATION OF PUNCTUATION FIX
        # If no initial prompt is provided, we supply a standard one to force punctuation/capitalization style.
        # This prevents the model from "drifting" into lowercase/no-punctuation mode.
        if 'initial_prompt' not in kwargs or kwargs['initial_prompt'] is None:
            kwargs['initial_prompt'] = "Hello, welcome to my lecture. I will use proper punctuation, capitalization, and grammar."
        
        if not self.transcriber.whisper_model:
            self.load_whisper_model()
            
        result = self.transcriber.transcribe(str(input_path), **kwargs)
        if not result: return None
        segments, info = result
        
        self._update_status(f"Writing all formats (VTT, SRT, TXT, CSV)...")
        
        base_output_path = (Path(output_dir) if output_dir else input_path.parent) / input_path.stem
        created_files = []

        # Save VTT
        vtt_path = base_output_path.with_suffix(".vtt")
        self.format_handler.save_vtt(segments, vtt_path)
        created_files.append(str(vtt_path))

        # Save SRT
        srt_path = base_output_path.with_suffix(".srt")
        self.format_handler.save_srt(segments, srt_path)
        created_files.append(str(srt_path))

        # Save TXT
        txt_path = base_output_path.with_suffix(".txt")
        self.format_handler.save_txt(segments, txt_path)
        created_files.append(str(txt_path))

        # Save CSV
        csv_path = base_output_path.with_suffix(".csv")
        self.format_handler.save_csv(segments, csv_path)
        created_files.append(str(csv_path))
            
        return created_files

    def translate_vtt(self, input_path, source_lang="en", target_lang="fr", output_dir=None):
        """Legacy method for VTT translation. Calls translate_file() internally."""
        return self.translate_file(input_path, source_lang, target_lang, output_dir)
    
    def translate_file(self, input_path, source_lang="en", target_lang="fr", output_dir=None):
        """Translate any supported file format (VTT, SRT, TXT, CSV) to target language."""
        input_path = self._normalize_path(input_path)
        
        # Detect format from extension
        ext = input_path.suffix.lower()
        
        if ext == '.vtt':
            data = self.format_handler.parse_vtt(input_path)
            data_type = 'segments'
        elif ext == '.srt':
            data = self.format_handler.parse_srt(input_path)
            data_type = 'segments'
        elif ext == '.csv':
            data = self.format_handler.parse_csv(input_path)
            data_type = 'segments'
        elif ext == '.txt':
            data = self.format_handler.parse_txt(input_path)
            data_type = 'lines'
        else:
            raise ValueError(f"Unsupported file format: {ext}. Supported: .vtt, .srt, .txt, .csv")
        
        # Translate content
        if data_type == 'segments':
            self._update_status(f"Translating {len(data)} segments from {source_lang} to {target_lang}...")
            for i, segment in enumerate(data):
                if i % 10 == 0:
                    self._update_status(f"Translating... {i}/{len(data)}")
                segment['text'] = self.translator.translate(segment['text'], source_lang=source_lang, target_lang=target_lang)
        else:  # lines
            self._update_status(f"Translating {len(data)} lines from {source_lang} to {target_lang}...")
            for i in range(len(data)):
                if i % 10 == 0:
                    self._update_status(f"Translating... {i}/{len(data)}")
                data[i] = self.translator.translate(data[i], source_lang=source_lang, target_lang=target_lang)
        
        # Save translated content in same format
        out_suffix = f"_{target_lang}{ext}"
        output_path = (Path(output_dir) if output_dir else input_path.parent) / (input_path.stem + out_suffix)
        
        if ext == '.vtt':
            self.format_handler.save_vtt_from_data(data, output_path)
        elif ext == '.srt':
            self.format_handler.save_srt_from_data(data, output_path)
        elif ext == '.csv':
            self.format_handler.save_csv_from_data(data, output_path)
        elif ext == '.txt':
            self.format_handler.save_txt_from_data(data, output_path)
        
        self._update_status(f"Translation complete: {output_path.name}")
        return str(output_path)

    def _normalize_path(self, path_str):
        p = Path(str(path_str).strip('"\''))
        if not p.exists(): raise FileNotFoundError(f"Not found: {p}")
        return p

    def parse_vtt(self, path): return self.format_handler.parse_vtt(path)
    def save_vtt_from_data(self, data, path): self.format_handler.save_vtt_from_data(data, path)

    def download_translation_model(self):
        self.model_manager.download_translation_model()

    def download_whisper_model(self, model_name):
         self.model_manager.download_whisper_model(model_name)
