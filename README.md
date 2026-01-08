# Textifier

Textifier is a high-performance Python application designed for high-quality video/audio transcription and translation. Powered by **faster-whisper** (CTranslate2), it offers significant speedups (4x-10x) over standard Whisper implementations while maintaining a lightweight footprint.

## Key Features

- **Transcription**: Ultra-fast speech-to-text using `faster-whisper` with support for `large-v3-turbo` and `Distil-Whisper`.
- **Translation**: Accurate English-to-multiple language translation using mBART (supports French and Hindi).
- **Core Architecture**: Decoupled, modular design for high maintainability and performance.
- **Audio Pre-processing**: Efficient audio extraction via FFmpeg pipes (zero intermediate disk writes).
- **GPU Fallback**: Robust hardware detection with multi-stage fallback (attempts CUDA float16 -> int8 -> CPU) to ensure stability on all hardware.
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
- **Batch Processor**: Unified workflow for single files or folders. Supports VTT and SRT output.
- **Advanced Whisper**: Detailed control over parameters (beams, patience, precision, device).
- **Subtitle Editor**: Advanced editor with iterative saving (`_edit01.vtt`) to protect original files.
- **Settings**: Complete model lifecycle management (Download/Delete/Status).

---

### Command Line Interface (CLI)

Textifier provides a modern CLI wrapper around the core engine.

#### 1. Transcribe Media
```bash
# Single file with default model (large-v3)
python textifier.py transcribe "video.mp4"

# Entire folder to SRT format
python textifier.py transcribe "my_folder" -f --format srt

# Use specific model
python textifier.py transcribe "video.mp4" -m large-v3-turbo
```

#### 2. Translate VTT
```bash
# Translate to French (default)
python textifier.py translate "subtitles.vtt"

# Batch translate a folder to Hindi
python textifier.py translate "folder_path" -f -l hi
```

---

## Models Used

### Whisper (Transcription)
- **Engine**: `faster-whisper` (CTranslate2)
- **Default**: `large-v3`
- **Recommended for Speed**: `large-v3-turbo` or `distil-large-v3`
- **Supported**: Full suite from `tiny` to `large-v3`, including `.en` variants.

### mBART (Translation)
- **Model**: `mBART Large 50 Many-to-Many MMT`
- **Languages**: 
  - English (en_XX) -> French (fr_XX)
  - English (en_XX) -> Hindi (hi_IN)

---

## Troubleshooting

- **"float16 compute type" Error**: Textifier now automatically handles this by falling back to `int8` or CPU. If you see this in the logs, it means the app is adapting to your GPU limitations.
- **FFmpeg Error**: Ensure `ffmpeg` is reachable (type `ffmpeg -version` in terminal).
- **Startup Latency**: Textifier uses lazy loading; it starts instantly and only loads models when transcription begins.

---

## License
MIT License - Sergio Gonzalez
