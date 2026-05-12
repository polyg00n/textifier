# Project Context: Textifier

## 🎯 Mission
Textifier is a unified, high-performance toolkit for converting media into actionable knowledge. It prioritizes local execution, hardware optimization, and professional-grade accuracy.

## 🏗️ Architecture Overview

### 1. Core Engine (`textifier_core.py`)
- **Transcription**: Implements `faster-whisper` with a robust fallback system (CUDA float16 → int8 → CPU). It includes Silero VAD for audio cleaning and a specialized `FormatHandler` for VTT, SRT, TXT, CSV, TSV, and JSON output.
- **Subtitle Re-Segmentation**: A post-processing step (`resegment_for_subtitles`) that uses word-level timestamps to split Whisper's variable-length segments into short **2-4 second subtitle cues**, ensuring subtitles display correctly in video players. Uses the lightweight `SubtitleSegment` class for output compatibility.
- **Translation**: Uses `mBART-50` with bi-directional support for 40+ languages.
- **Summarization**: A flexible dispatcher supporting local (Ollama/LM Studio) and cloud (Gemini/OpenAI/Claude) providers.

### 2. Intelligent Synthesis (Map-Reduce)
To solve the "Context Window" problem on consumer GPUs, Textifier uses a recursive Map-Reduce pattern:
- **Map**: Chunks large text files (default 8000 chars) with semantic overlap.
- **Extract**: Summarizes each chunk to extract core concepts.
- **Reduce**: Re-synthesizes the batch of summaries into a structured, high-value final digest.

### 3. UI Framework (`gui_main.py`)
- **Threading**: Every core operation runs in a background thread to maintain GUI fluidity.
- **State Management**: Shared input variables across tabs ensure a unified workflow from Transcribe to Summarize.
- **Format Parity**: All tabs (Batch, Advanced Whisper, Pipeline) expose the same set of output format checkboxes (VTT, SRT, TXT, CSV, TSV, JSON).
- **Responsiveness**: Uses scrollable canvas frames to support varying display resolutions and long lists of models/languages.

### 4. CLI Harness (`textifier.py`)
Exposes the full power of the core engine for headless automation. Supports `transcribe`, `translate`, `summarize`, and `pipeline` commands with full parity for all GUI-accessible parameters including all Advanced Whisper options (beam size, patience, repetition penalty, temperature, device selection, output format selection, etc.).

## 📈 Evolution (v2.0 → v2.2)
- **v2.0**: Focused on multi-language support (mBART-50) and punctuation stability.
- **v2.1**: Introduced the **Summarization Engine**, **Pipeline Tab**, **VAD Filter**, **Word-Level Timestamps**, and **Map-Reduce** context management.
- **v2.2**: Added **Subtitle Re-Segmentation** for short timecodes (2-4s cues), achieved **full GUI format parity** across all tabs, and brought the **CLI to full parity** with all Advanced Whisper options.

## 🛠️ Development Standards
- **Lazy Loading**: Models must only load when explicitly called to keep startup times low.
- **Hardware Fallback**: Always implement automatic precision fallback for CTranslate2 (faster-whisper).
- **Parity**: Any new feature added to the GUI must be exposed in the CLI. Shared option helpers (`_add_whisper_options`, `_build_whisper_kwargs`) prevent drift.
- **Testing**: All core logic must be verified via `pytest` before release. Re-segmentation logic has dedicated unit tests.

## 🚀 Future Roadmap
- [ ] **Speaker Diarization**: Integrating speaker identification.
- [ ] **VertexAI Integration**: Support for enterprise Google Cloud models.
- [ ] **Advanced Subtitle Editor**: Restoring the editor with improved video player stability.
- [ ] **Real-time Transcription**: Experimental low-latency streaming mode.
