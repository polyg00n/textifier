# Textifier

Textifier is a high-performance Python application designed for high-quality video/audio transcription and translation. Powered by **faster-whisper** (CTranslate2), it offers significant speedups (4x-10x) over standard Whisper implementations while maintaining a lightweight footprint.

## Key Features

### ✨ New in v2.0.0
- **Multi-Language Transcription**: 36+ languages supported with auto-detection (English, Spanish, French, Hindi, Gujarati, Japanese, Arabic, Chinese, and many more)
- **Enhanced Translation**: Expanded from 2 to 40+ languages with bi-directional support (any source → any target)
- **Multi-Format Output**: Automatically generates VTT, SRT, TXT, and CSV formats
- **Punctuation Fix**: Automatic proper capitalization and punctuation (no more lowercase-only output)

### Core Capabilities
- **Transcription**: Ultra-fast speech-to-text using `faster-whisper` with support for `large-v3-turbo` and `Distil-Whisper`.
- **Translation**: Accurate multilingual translation using mBART-50 (supports 40+ language pairs).
- **Core Architecture**: Decoupled, modular design for high maintainability and performance.
- **Audio Pre-processing**: Efficient audio extraction via FFmpeg pipes (zero intermediate disk writes).
- **GPU Fallback**: Robust hardware detection with multi-stage fallback (attempts CUDA float16 → int8 → CPU) to ensure stability on all hardware.
- **Subtitle Editor**: Built-in editor with word-wrap, dynamic height adjustments, and integrated system player for preview.
- **Model Manager**: Dedicated interface to download, verify, and delete models locally with disk usage reporting.
- **Batch Processing**: Process entire folders of media or VTT/SRT files in one go.

---

## Installation

### Prerequisites

- **Python 3.8 - 3.12**
- **FFmpeg**: Essential for high-performance audio extraction.
- **NVIDIA GPU** (Optional): Highly recommended for GPU acceleration (requires CUDA 12+).

### Installing FFmpeg

#### Windows
1. Download from [ffmpeg.org](https://ffmpeg.org/download.html).
2. Extract and add the `bin` folder to your system **PATH**.

#### Linux (Ubuntu/Debian)
```bash
sudo apt update && sudo apt install ffmpeg
```

### Application Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/polyg00n/textifier.git
   cd textifier
   ```

2. **Setup virtual environment**:
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # Linux/macOS:
   source .venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

---

## Usage

### GUI (Recommended)
```bash
python gui_main.py
```

#### GUI Tabs:
- **Batch Processor**: Unified workflow for single files or folders. 
  - **Transcription**: Select from 36+ languages or use auto-detect
  - **Translation**: Translate between any of 40+ supported language pairs
  - **Output**: Automatically generates VTT, SRT, TXT, and CSV formats
- **Advanced Whisper**: Detailed control over parameters (language, beams, patience, precision, device).
- **Subtitle Editor**: Advanced editor with iterative saving (`_edit01.vtt`) to protect original files.
- **Settings**: Complete model lifecycle management (Download/Delete/Status).

---

### Command Line Interface (CLI)

Textifier provides a modern CLI wrapper around the core engine.

#### 1. Transcribe Media
```bash
# Single file with default model (large-v3) - auto-detect language
python textifier.py transcribe "video.mp4"

# Specify language for better accuracy
python textifier.py transcribe "hindi_video.mp4" --language hi

# Entire folder - generates VTT, SRT, TXT, CSV for each file
python textifier.py transcribe "my_folder" -f

# Use specific model with language
python textifier.py transcribe "video.mp4" -m large-v3-turbo --language es
```

#### 2. Translate VTT
```bash
# Translate English to French
python textifier.py translate "subtitles.vtt" -l fr

# Translate Hindi to Gujarati
python textifier.py translate "hindi_subtitles.vtt" --source-lang hi -l gu

# Batch translate a folder
python textifier.py translate "folder_path" -f -l ja
```

---

## Models Used

### Whisper (Transcription)
- **Engine**: `faster-whisper` (CTranslate2)
- **Default**: `large-v3`
- **Recommended for Speed**: `large-v3-turbo` or `distil-large-v3`
- **Supported**: Full suite from `tiny` to `large-v3`, including `.en` variants.
- **Languages**: 36+ languages including English, Spanish, French, German, Italian, Portuguese, Dutch, Russian, Chinese, Japanese, Korean, Arabic, Hindi, Gujarati, Tamil, Telugu, Bengali, Urdu, Persian, Thai, Vietnamese, Indonesian, Hebrew, Greek, Czech, Finnish, Romanian, Danish, Hungarian, Tamil, Norwegian, Marathi, Punjabi

### mBART (Translation)
- **Model**: `mBART Large 50 Many-to-Many MMT`
- **Languages**: 40+ languages with bi-directional translation support
- **Popular Pairs**: 
  - English ↔ French, Spanish, German, Italian, Portuguese, Dutch, Russian
  - English ↔ Hindi, Gujarati, Tamil, Telugu, Bengali, Urdu, Marathi
  - English ↔ Chinese, Japanese, Korean, Arabic, Thai, Vietnamese
  - **Any to Any**: e.g., Hindi → Gujarati, Spanish → French, Japanese → Korean

---

## Troubleshooting

- **"float16 compute type" Error**: Textifier now automatically handles this by falling back to `int8` or CPU. If you see this in the logs, it means the app is adapting to your GPU limitations.
- **FFmpeg Error**: Ensure `ffmpeg` is reachable (type `ffmpeg -version` in terminal).
- **Startup Latency**: Textifier uses lazy loading; it starts instantly and only loads models when transcription begins.

---

## License
MIT License - Sergio Gonzalez
