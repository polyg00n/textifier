# Textifier

Textifier is a high-performance, professional-grade Python application designed for high-quality video/audio transcription, translation, and intelligent summarization. Powered by **faster-whisper** (CTranslate2), it offers significant speedups (4x-10x) over standard Whisper implementations while maintaining a lightweight footprint and maximum local privacy.

---

## ✨ Key Features & Capabilities

### 🎙️ World-Class Transcription
- **Ultra-Fast Engine**: Powered by `faster-whisper` for near-instant results on modern hardware.
- **Multi-Language Support**: 36+ languages supported with robust auto-detection.
- **Subtitle Re-Segmentation**: Automatic post-processing splits long Whisper segments into short **2-4 second subtitle cues**, ensuring subtitles display correctly in video players.
- **VAD Filter**: Built-in **Silero Voice Activity Detection** to filter noise and silence, preventing model "hallucinations."
- **Word-Level Timestamps**: Precise timing for every single word with detailed metadata export (`.words.json`).
- **Repetition Penalty**: Advanced control to prevent the model from getting stuck in loops.
- **Flexible Models**: Choose from `tiny` to `large-v3-turbo` or `Distil-Whisper`.

### 🌍 Global Translation
- **mBART-50 Many-to-Many**: Accurate multilingual translation using state-of-the-art neural models.
- **40+ Languages**: Bi-directional support (any source → any target).
- **Bi-Language Export**: Simultaneously translate into multiple target languages in a single pass.
- **Format Support**: Preserves timestamps across VTT, SRT, TXT, CSV, and TSV formats.

### 🧠 Intelligent Summarization
- **Flexible LLM Routing**: Connect to **Local LLMs** (Ollama, LM Studio) or **Cloud Providers** (Google Gemini, OpenAI, Claude).
- **Map-Reduce Strategy**: Advanced recursive chunking logic for summarizing hours-long transcripts using small models.
- **KM Framework Prompts**: Default prompts designed for high-value digests (Core Insights, Actionable Lists, Glossaries).
- **Advanced Settings**: Full control over Chunk Size, Overlap, Temperature, and Max Output Tokens.

### 🚀 Automation & Workflow
- **Pipeline Orchestration**: Automated, sequential execution of Transcribe → Translate → Summarize.
- **Batch Processing**: Handle hundreds of media or text files simultaneously.
- **Model Manager**: Integrated interface to download, verify, and manage your local model library.
- **Hardware-Aware**: Automatic detection of CPU, RAM, and GPU/VRAM with tiered model recommendations.

---

## 🛠️ Installation

### Prerequisites
- **Python 3.8 - 3.12**
- **FFmpeg**: Essential for audio extraction.
- **NVIDIA GPU** (Optional): Highly recommended (requires CUDA 12+).

### Quick Start
1. **Clone & Setup**:
   ```bash
   git clone https://github.com/polyg00n/textifier.git
   cd textifier
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```

---

## 📖 Usage Guide

### GUI (Graphical Interface)
```bash
python gui_main.py
```

- **Transcribe/Translate Tab**: Unified media processing with multiformat selectors.
- **Summarize Tab**: Turn transcripts into actionable knowledge with Map-Reduce support.
- **Pipeline Tab**: The "Set and Forget" mode for full documentation packages.
- **Advanced Whisper**: Fine-tune Beams, Patience, Repetition Penalty, VAD, and multi-format output selection.

---

### Command Line Interface (CLI)
Textifier provides a robust CLI (`textifier.py`) for headless operation and company pipeline automations.

#### 1. Transcribe Media
Transcribe audio/video files to multiple formats (VTT, SRT, TXT, CSV, TSV, JSON).
```bash
# Single file (auto-detect language, use default large-v3-turbo)
python textifier.py transcribe "video.mp4"

# Specify language, output directory, and select formats
python textifier.py transcribe "hindi_audio.mp3" --language hi -o ./results/ --output-formats vtt srt txt

# Enable word-level timestamps JSON export
python textifier.py transcribe "interview.m4a" --word-timestamps

# Fine-tune decoding parameters
python textifier.py transcribe "lecture.mp4" --beam-size 8 --temperature 0.2 --repetition-penalty 1.3

# Use CPU explicitly and disable VAD
python textifier.py transcribe "podcast.mp3" --device cpu --no-vad-filter

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
Generate AI summaries using local or cloud LLMs with Map-Reduce support.
```bash
# Summarize using Google Gemini (requires API key)
python textifier.py summarize "transcript.txt" --provider gemini --api-key YOUR_API_KEY

# Summarize using local Ollama (ensure Ollama is running)
python textifier.py summarize "meeting.vtt" --provider ollama --model llama3 --strategy map_reduce

# Batch summarize a folder with custom chunking
python textifier.py summarize "outputs/" --folder --provider gemini --api-key YOUR_KEY --chunk-size 4000
```

#### 4. Full Pipeline
Run transcription, translation, and summarization in one go.
```bash
# Transcribe, translate to Spanish, and summarize
python textifier.py pipeline "video.mp4" --translate-langs es --summarize --provider gemini --api-key YOUR_KEY

# Pipeline with custom Whisper settings and multiple languages
python textifier.py pipeline "lecture.mp4" --beam-size 8 --output-formats vtt txt --translate-langs fr es de --summarize --provider ollama --summary-model llama3

# Batch pipeline an entire folder
python textifier.py pipeline "videos/" --folder --translate-langs ja --summarize --api-key YOUR_KEY
```

---

## 📦 Models Used

### Whisper (Transcription)
- **Engine**: `faster-whisper` (CTranslate2)
- **Default**: `large-v3-turbo`
- **Recommended for Speed**: `large-v3-turbo` or `distil-large-v3`
- **Supported**: Full suite from `tiny` to `large-v3`.
- **Languages**: 36+ languages including English, Spanish, French, German, Italian, Portuguese, Dutch, Russian, Chinese, Japanese, Korean, Arabic, Hindi, Gujarati, Tamil, Telugu, Bengali, Urdu, Persian, Thai, Vietnamese, Indonesian, Hebrew, Greek, Czech, Finnish, Romanian, Danish, Hungarian, Norwegian, Marathi, Punjabi.

### mBART (Translation)
- **Model**: `mBART Large 50 Many-to-Many MMT`
- **Languages**: 40+ languages with bi-directional translation support.
- **Popular Pairs**: 
  - English ↔ French, Spanish, German, Italian, Portuguese, Dutch, Russian
  - English ↔ Hindi, Gujarati, Tamil, Telugu, Bengali, Urdu, Marathi
  - English ↔ Chinese, Japanese, Korean, Arabic, Thai, Vietnamese
  - **Any to Any**: e.g., Hindi → Gujarati, Spanish → French, Japanese → Korean.

---

## 🖥️ Hardware & VRAM Recommendations

| VRAM | Best For | Recommended LLMs |
| :--- | :--- | :--- |
| **24GB+** | High-speed processing / Massive Context | Qwen 3 32B+, Llama 3.1 70B |
| **12GB** | Professional Workflow | Qwen 2.5 14B, Mistral Nemo 12B |
| **8GB** | Standard Desktop | Llama 3 8B, Gemma 3 9B |
| **4GB-6GB** | Entry GPU / Laptops | Phi-4 Mini, Gemma 3 4B-IT |
| **CPU** | Legacy Hardware | Phi-3 Mini, TinyLlama |

---

## 🛠️ Troubleshooting

- **"float16 compute type" Error**: Textifier automatically handles this by falling back to `int8` or CPU. If you see this in the logs, it means the app is adapting to your GPU limitations.
- **FFmpeg Error**: Ensure `ffmpeg` is reachable (type `ffmpeg -version` in terminal).
- **Startup Latency**: Textifier uses lazy loading; it starts instantly and only loads models when transcription begins.
- **Context Window**: If a local model fails on long files, ensure you are using the **Map-Reduce** strategy with a smaller **Chunk Size**.

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
