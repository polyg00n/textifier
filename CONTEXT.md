# Project Context: Textifier

## 🎯 Mission
Textifier is a unified, high-performance toolkit for converting media into actionable knowledge. It prioritizes local execution, hardware optimization, and professional-grade accuracy.

## 🏗️ Architecture Overview

### 1. Core Engine (`textifier_core.py`)
- **Transcription**: Implements `faster-whisper` with a robust fallback system (CUDA float16 → int8 → CPU). It includes Silero VAD for audio cleaning and a specialized `FormatHandler` for VTT, SRT, TXT, CSV, TSV, and JSON output.
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
- **Responsiveness**: Uses scrollable canvas frames to support varying display resolutions and long lists of models/languages.

### 4. CLI Harness (`textifier.py`)
Exposes the full power of the core engine for headless automation. Supports `transcribe`, `translate`, `summarize`, and `pipeline` commands with parity for all GUI-accessible parameters.

## 📈 Evolution (v2.0 → v2.1)
- **v2.0**: Focused on multi-language support (mBART-50) and punctuation stability.
- **v2.1**: Introduced the **Summarization Engine**, **Pipeline Tab**, **VAD Filter**, **Word-Level Timestamps**, and **Map-Reduce** context management.

## 🛠️ Development Standards
- **Lazy Loading**: Models must only load when explicitly called to keep startup times low.
- **Hardware Fallback**: Always implement automatic precision fallback for CTranslate2 (faster-whisper).
- **Parity**: Any new feature added to the GUI should ideally be exposed in the CLI.
- **Testing**: All core logic must be verified via `pytest` before release.

## 🚀 Future Roadmap
- [ ] **Speaker Diarization**: Integrating speaker identification.
- [ ] **VertexAI Integration**: Support for enterprise Google Cloud models.
- [ ] **Advanced Subtitle Editor**: Restoring the editor with improved video player stability.
- [ ] **Real-time Transcription**: Experimental low-latency streaming mode.
