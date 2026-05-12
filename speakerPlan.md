# Speaker Diarization Implementation Plan

**Goal**: Enhance Textifier with the ability to detect "who spoke when" (Speaker Diarization) and tag output transcripts with speaker labels (e.g., `[Speaker A]`, `[Speaker B]`).

---

## 1. Available Options

### Option A: Free / Open-Source (Local Execution)

These options run entirely on the user's hardware, maintaining Textifier's commitment to local privacy and zero recurring costs.

1.  **PyAnnote.audio (The Gold Standard)**
    *   **How it works**: A standalone neural network built on PyTorch specifically designed for speaker diarization. It outputs time-coded speaker segments (e.g., Speaker 1: 0.0s - 4.5s).
    *   **Pros**: Highly accurate, active development, industry standard for open-source.
    *   **Cons**: Requires users to accept an agreement on HuggingFace and generate a free access token to download the model. Can be VRAM intensive.
2.  **WhisperX**
    *   **How it works**: A popular wrapper library that combines `faster-whisper` + `Wav2Vec2` (for forced alignment) + `PyAnnote` (for diarization) into a single pipeline.
    *   **Pros**: Extremely fast, handles the alignment math for you.
    *   **Cons**: It is an all-in-one library. Integrating it would likely mean replacing our custom `faster-whisper` implementation entirely, potentially breaking our custom VAD, chunking, and fallback logic.
3.  **NVIDIA NeMo**
    *   **How it works**: NVIDIA's conversational AI toolkit.
    *   **Pros**: State-of-the-art accuracy, highly configurable.
    *   **Cons**: Massive dependency footprint, steep learning curve, complex installation on Windows.

### Option B: Paid / Cloud APIs (Remote Execution)

These options send the audio to a remote server. They are ideal for users without powerful GPUs or those who want instant, highly accurate results without local compute overhead.

1.  **AssemblyAI**
    *   **Pros**: Widely considered one of the best out-of-the-box APIs for diarization and transcription. Very developer-friendly Python SDK.
    *   **Cost**: ~$0.37 per hour of audio (Core Transcription).
2.  **Deepgram**
    *   **Pros**: Unbelievably fast (can transcribe an hour of audio in seconds). Excellent diarization accuracy.
    *   **Cost**: ~$0.26 per hour of audio (Nova-2 model).
3.  **Google Cloud Speech-to-Text (Vertex AI)**
    *   **Pros**: Enterprise-grade, good if the user is already in the Google ecosystem.
    *   **Cost**: ~$1.44 per hour of audio (standard models).

---

## 2. Proposed Architecture for Textifier

To maintain Textifier's identity as a local-first application while leveraging the work we've already done, **we should integrate `PyAnnote.audio` alongside our existing `faster-whisper` engine.** 

Since we already built a robust Word-Level Timestamp extraction and Subtitle Re-segmentation engine in v2.2, we have the perfect foundation for this.

### The Alignment Strategy (Intersection)
Whisper outputs *what* was said and *when* (word-level). PyAnnote outputs *who* spoke and *when*. The integration math is simply intersecting the two timecodes:
1.  Run `faster-whisper` (already implemented).
2.  Run `PyAnnote` on the same `.mp3` file to get speaker time blocks.
3.  For each word from Whisper, check which PyAnnote speaker block it falls into, and assign that speaker to the word.
4.  Group the words back into `SubtitleSegment` objects, now with a `.speaker` attribute.

---

## 3. Implementation Phases

### Phase 1: Core Integration (Local PyAnnote)
1.  **Dependency Update**: Add `pyannote.audio` to `requirements.txt`.
2.  **Model Management**: 
    *   Update the **Utilities** tab to include a "HuggingFace Token" input field.
    *   Add logic in `ModelManager` to securely save this token and authorize the PyAnnote model download.
3.  **Core Engine (`textifier_core.py`)**:
    *   Create an `AudioAnalyzer` class to wrap PyAnnote.
    *   Update `transcribe_media` to conditionally run `AudioAnalyzer.diarize(audio_path, num_speakers)` if requested.
    *   Write the alignment logic (matching Whisper words to PyAnnote segments).
4.  **Format Exporters**:
    *   Update `FormatHandler` so that if a segment has a speaker, it prefixes the text.
    *   *TXT/SRT/VTT Output*: `[Speaker 1]: I think we should...`
    *   *CSV/TSV Output*: Add a new "Speaker" column.

### Phase 2: GUI & CLI Updates
1.  **GUI**:
    *   Add an **"Identify Speakers"** checkbox to the Transcribe, Batch, and Pipeline tabs.
    *   Add a numeric entry for **"Number of Speakers (Optional)"**. Providing the exact number of speakers drastically improves PyAnnote's accuracy.
2.  **CLI**:
    *   Add `--diarize` and `--num-speakers <int>` flags to the `textifier.py` CLI.

### Phase 3: Cloud Provider Dispatcher (Optional/Future)
Similar to how we handle Summarization (Local vs Cloud), we could build a `TranscriptionDispatcher` that allows the user to use AssemblyAI or Deepgram instead of the local Whisper/PyAnnote stack. This provides an "escape hatch" for users with weak hardware.

---

## 4. Next Steps

If you approve of this strategy, the immediate next steps are:
1. Install `pyannote.audio` in the local `.venv`.
2. Add the HuggingFace token field to the GUI's Utilities tab.
3. Build the standalone `AudioAnalyzer` class to test PyAnnote's output on one of our `testaudio` MP3s before wiring it into the main pipeline.

---

## 5. Case Study: Speaker Name Mapping

**The Problem**: AI models (like PyAnnote) don't know the actual names of the people speaking. They output generic labels like `SPEAKER_00`, `SPEAKER_01`, and `SPEAKER_02`. It is impossible to know *before* the transcription completes whether `SPEAKER_00` is the interviewer or the guest.

Here is how we will implement name mapping in Textifier so that your final outputs use real names (e.g., `[Lex Fridman]: ...`).

### Workflow 1: The "Post-Processing GUI Tool" (Recommended)
This is a deterministic, high-speed, and zero-cost approach. For users who want to modify the raw `.vtt`, `.srt`, `.txt`, and `.csv` files directly without burning API tokens or relying on LLM context windows.

1. **Transcribe**: The media is transcribed with generic labels (e.g., `SPEAKER_00`).
2. **Review**: The user opens the `.txt` file and quickly reads the first few lines to deduce the identities (e.g., "Ah, SPEAKER_00 introduces the show, that's John").
3. **New GUI Utility**: We add a "Speaker Mapper" tool in the Utilities tab.
   * **Input**: You select the output folder (e.g., `results/podcast1`).
   * **Fields**: You define the mapping: `SPEAKER_00 -> John`, `SPEAKER_01 -> Sarah`.
   * **Action**: You click "Apply".
4. **Result**: Textifier instantly opens all `.vtt`, `.srt`, `.txt`, and `.csv` files in that folder, does a high-speed search-and-replace, and saves the final versions with the correct real names.

### Workflow 2: The "LLM Context" Approach (Optional / Token Heavy)
Since Textifier already has a powerful Summarization engine powered by LLMs (Gemini, Claude, Ollama), you *can* use the LLM to replace names, though this uses tokens and is slower.

1. **Transcribe**: You run the transcription with Diarization enabled.
2. **Summarize Tab**: You go to the Summarize tab, load the transcript, and select a special system prompt called **"Rename Speakers"**. 
3. **Prompt**: You type: *"In this transcript, SPEAKER_00 is Lex Fridman and SPEAKER_01 is Sam Altman. Replace the labels and return the clean transcript."*
4. **Result**: The LLM processes the text and outputs the mapped transcript.

### Workflow 3: CLI Name Mapping
For headless automation, you can provide a mapping string if you already know the speaker distribution (e.g., if you have distinct audio tracks or predictable formats).

```bash
# Provide the mapping string directly
python textifier.py transcribe "interview.mp4" --diarize --speaker-map "SPEAKER_00=John,SPEAKER_01=Sarah"
```
*(Note: This is risky if PyAnnote decides to assign `SPEAKER_00` to Sarah based on who spoke first in that specific recording. Workflows 1 and 2 are much safer).*
