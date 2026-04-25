# Textifier

Textifier is a high-performance Python application designed for high-quality video/audio transcription and translation. Powered by **faster-whisper** (CTranslate2), it offers significant speedups (4x-10x) over standard Whisper implementations while maintaining a lightweight footprint.

## Key Features

### ✨ New in v2.0.0
- **Multi-Language Transcription**: 36+ languages supported with auto-detection (English, Spanish, French, Hindi, Gujarati, Japanese, Arabic, Chinese, and many more)
- **Enhanced Translation**: Expanded from 2 to 40+ languages with bi-directional support (any source → any target)
- **Multi-Format Output**: Automatically generates VTT, SRT, TXT, CSV, and word-level JSON formats
- **Intelligent Summarization**: Integrated local (Ollama/LM Studio) and cloud (Gemini/Claude/OpenAI) LLM support for transcripts
- **VAD Filter**: Built-in Silero Voice Activity Detection to filter noise and prevent hallucinations
- **Word-Level Timestamps**: Precise timing for every word with detailed metadata export
- **Stability & Testing**: Comprehensive `pytest` suite and improved startup reliability

### Core Capabilities
- **Transcription**: Ultra-fast speech-to-text using `faster-whisper` with support for `large-v3-turbo` and `Distil-Whisper`.
- **Translation**: Accurate multilingual translation using mBART-50 (supports 40+ language pairs).
- **Core Architecture**: Decoupled, modular design for high maintainability and performance.
- **Audio Pre-processing**: Efficient audio extraction via FFmpeg pipes (zero intermediate disk writes).
- **GPU Fallback**: Robust hardware detection with multi-stage fallback (attempts CUDA float16 → int8 → CPU) to ensure stability on all hardware.
- **Subtitle Editor**: Built-in editor with word-wrap, dynamic height adjustments, and integrated system player for preview.
- **Model Manager**: Dedicated interface to download, verify, and delete models locally with disk usage reporting.
- **Summarization**: Sophisticated transcript summaries using local or cloud LLMs with tiered VRAM-based model recommendations.
- **Transcribe/Translate Tab**: Process entire folders of media, VTT, SRT, TXT, or CSV files in one go.
- **Pipeline Tab**: Automated, sequential execution of transcription, translation, and summarization in one batch.
- **Advanced Controls**: Integrated VAD filter, word-level timestamps, and repetition penalties.

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
- **Transcribe/Translate**: Unified workflow for single files or folders. 
  - **Transcription**: Select from 36+ languages or use auto-detect
  - **Translation**: Translate between any of 40+ supported language pairs
  - **Output**: Automatically generates VTT, SRT, TXT, and CSV formats
- **Summarize**: Intelligent summaries using flexible LLM routing (local/cloud) and custom prompt management. Supports processing entire folders of text/subtitles.
- **Pipeline**: Automated, sequential execution of transcription, translation, and summarization in one batch.
- **Advanced Whisper**: Detailed control over parameters (language, beams, patience, precision, device).
- **Utilities**: Hardware-aware settings and model management with automated system info detection.
- **Subtitle Editor**: (Hidden for now) Advanced editor with iterative saving (`_edit01.vtt`) to protect original files.

---

### Command Line Interface (CLI)

Textifier provides a robust CLI (`textifier.py`) for headless operation and pipeline integration.

#### 1. Transcribe Media
Transcribe audio/video files to multiple formats (VTT, SRT, TXT, CSV, JSON).
```bash
# Single file (auto-detect language, use default large-v3-turbo)
python textifier.py transcribe "video.mp4"

# Specify language and output directory
python textifier.py transcribe "hindi_audio.mp3" --language hi -o ./results/

# Enable word-level timestamps and VAD filter
python textifier.py transcribe "interview.m4a" --word-timestamps --vad-filter

# Batch process a folder
python textifier.py transcribe "meeting_recordings/" --folder
```

#### 2. Translate Subtitles/Text
Translate existing VTT, SRT, TXT, or CSV files.
```bash
# Translate English VTT to French
python textifier.py translate "subs.vtt" --target-lang fr

# Translate Hindi to Gujarati
python textifier.py translate "transcript.txt" --source-lang hi --target-lang gu

# Batch translate a folder
python textifier.py translate "subtitles_dir/" --folder -l ja
```

#### 3. Summarize Transcripts
Generate AI summaries using local or cloud LLMs.
```bash
# Summarize using Google Gemini (requires API key)
python textifier.py summarize "transcript.txt" --provider gemini --api-key YOUR_API_KEY

# Summarize using local Ollama (ensure Ollama is running)
python textifier.py summarize "meeting.vtt" --provider ollama --model llama3

# Batch summarize a folder
python textifier.py summarize "outputs/" --folder --provider gemini --api-key YOUR_API_KEY
```

#### 4. Full Pipeline
Run transcription, translation, and summarization in one go.
```bash
# Transcribe, translate to Spanish, and summarize
python textifier.py pipeline "video.mp4" --translate-langs es --summarize --api-key YOUR_KEY
```

---

## Models Used

### Whisper (Transcription)
- **Engine**: `faster-whisper` (CTranslate2)
- **Default**: `large-v3-turbo`
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

## 🧪 Development & Testing

Textifier includes a robust testing suite based on `pytest`.

### Running Tests
Ensure you have `pytest` installed:
```bash
pip install pytest
```

Run the full suite:
```bash
python -m pytest -v tests/
```

- **Core Tests**: Verifies transcription logic, parsers, and LLM communication.
- **UI Tests**: Verifies GUI responsiveness and state transitions.

---

## License
MIT License - Sergio Gonzalez
