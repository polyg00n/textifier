
import os
import logging
from pathlib import Path
import urllib.request
import sys
import time
import subprocess
import numpy as np

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
    def __init__(self, models_dir="models", status_callback=None):
        self.models_dir = Path(models_dir)
        self.whisper_dir = self.models_dir / "whisper"
        self.translation_dir = self.models_dir / "translation"
        self.status_callback = status_callback
        
        self.models_dir.mkdir(exist_ok=True)
        self.whisper_dir.mkdir(exist_ok=True)
        self.translation_dir.mkdir(exist_ok=True)

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
        return self.translation_dir.exists() and (self.translation_dir / "config.json").exists()

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

    def translate(self, text, target_lang="fr"):
        self.load_model()
        lang_codes = {"fr": "fr_XX", "hi": "hi_IN"}
        if target_lang not in lang_codes:
            raise ValueError(f"Unsupported language: {target_lang}")
            
        self.tokenizer.src_lang = "en_XX"
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
        output_format = kwargs.pop('output_format', 'vtt').lower()
        
        ext = f".{output_format}"
        output_path = (Path(output_dir) if output_dir else input_path.parent) / input_path.with_suffix(ext).name
        
        if not self.transcriber.whisper_model:
            self.load_whisper_model()
            
        result = self.transcriber.transcribe(str(input_path), **kwargs)
        if not result: return None
        segments, info = result
        
        self._update_status(f"Writing {output_format.upper()}...")
        if output_format == "srt":
            self.format_handler.save_srt(segments, output_path)
        else:
            self.format_handler.save_vtt(segments, output_path)
            
        return str(output_path)

    def translate_vtt(self, input_path, target_lang="fr", output_dir=None):
        input_path = self._normalize_path(input_path)
        cues = self.format_handler.parse_vtt(input_path)
        
        self._update_status(f"Translating {len(cues)} cues...")
        for i, cue in enumerate(cues):
            if i % 10 == 0: self._update_status(f"Translating... {i}/{len(cues)}")
            cue['text'] = self.translator.translate(cue['text'], target_lang)
            
        out_suffix = f"_{target_lang}.vtt"
        output_path = (Path(output_dir) if output_dir else input_path.parent) / (input_path.stem + out_suffix)
        self.format_handler.save_vtt_from_data(cues, output_path)
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
