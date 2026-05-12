# Whisper Advanced Settings Guide

This document explains the advanced parameters available in the **Advanced Whisper** tab of Textifier, and their equivalent CLI flags. These settings allow you to fine-tune the transcription process for better accuracy or faster performance.

---

## Model Selection

### Whisper Model Size
Select the size of the neural network.
- **Tiny/Base**: Extremely fast, lower accuracy.
- **Small/Medium**: Balanced performance and accuracy.
- **Large/Large-v3-turbo**: Best accuracy/speed ratio. **large-v3-turbo** is the default for v2.1.0.
- **Distil-Whisper**: Optimized for speed on specific language pairs.
- **CLI**: `--model large-v3-turbo` (or `tiny`, `base`, `small`, `medium`, `large-v3`, etc.)

### Task
Choose whether to keep the original language or translate to English.
- **Transcribe**: Keeps the original language (default).
- **Translate**: Converts speech to English using Whisper's built-in translation.
- **CLI**: `--task transcribe` or `--task translate`

---

## Decoding Parameters

### Beam Size
The number of candidate sequences the model explores during decoding.
- **Default**: 5
- **Effect**: Higher values can improve accuracy but increase processing time.
- **CLI**: `--beam-size 5`

### Best Of
Number of candidates to sample from when using sampling-based decoding.
- **Default**: 5
- **CLI**: `--best-of 5`

### Patience
Beam search patience factor.
- **Default**: 1.0
- **Effect**: A value > 1.0 makes the beam search more "patient," continuing the search longer.
- **CLI**: `--patience 1.0`

### Repetition Penalty
**New in v2.1.0**: Penalty applied to repeated tokens.
- **Default**: 1.1
- **Effect**: Prevents the model from getting stuck in loops (e.g., repeating the same word infinitely).
- **CLI**: `--repetition-penalty 1.1`

---

## Audio & Filtering

### VAD (Voice Activity Detection)
**New in v2.1.0**: Uses Silero VAD to automatically filter out non-speech segments.
- **Default**: ON
- **Benefit**: Significantly reduces "hallucinations" (model making up text from background noise or silence).
- **CLI**: `--vad-filter` (enabled by default) or `--no-vad-filter` to disable.

### Word-Level Timestamps
**New in v2.1.0**: Generates precise timing for every single word.
- **Output**: Exports a `.words.json` file with detailed timing and probability metadata.
- **Note**: Word timestamps are always enabled internally (since v2.2.0) to power the subtitle re-segmentation engine. The JSON checkbox/flag controls whether the `.words.json` file is written to disk.
- **CLI**: `--word-timestamps`

### No Speech Threshold
Threshold to determine if a segment contains actual speech.
- **Default**: 0.6
- **Effect**: If the model is > 60% sure there is no speech, it will leave the segment blank.
- **CLI**: `--no-speech-threshold 0.6`

### Condition on Previous Text
Whether the model uses the previous segment's text as context for the next.
- **Default**: ON
- **Effect**: Helps maintain consistency across segments, but can propagate errors.
- **CLI**: `--condition-on-previous-text` (default) or `--no-condition-on-previous-text`

---

## Temperature & Sampling

### Temperature
Controls the "creativity" or randomness of the model.
- **Range**: 0.0 to 1.0
- **Default**: 0.0 (Greedy Decoding)
- **Effect**: 
    - **0.0**: Always picks the most likely next word (most reliable).
    - **Higher**: Introduces randomness. Useful if the model fails in difficult audio.
- **CLI**: `--temperature 0.0`

---

## Performance Settings

### GPU Acceleration
Textifier automatically detects CUDA-capable GPUs.
- **FP16 (Half Precision)**: Default on GPU. Nearly doubles speed with zero accuracy loss.
- **Fallback**: If FP16 is not supported or VRAM is low, Textifier automatically falls back to `int8` or CPU.

### Device Selection
Choose the compute device explicitly.
- **Options**: `auto` (default), `cuda`, `cpu`.
- **CLI**: `--device auto`

---

## Punctuation & Formatting

### Initial Prompt
**New in v2.0.0**: Guide the model to use proper punctuation and capitalization.
- **Default**: "Hello, welcome to my lecture. I will use proper punctuation, capitalization, and grammar."
- **Customization**: Add technical terms (e.g., "React, TypeScript") to help the model spell them correctly.
- **CLI**: `--initial-prompt "Your custom prompt here"`

---

## Subtitle Re-Segmentation

**New in v2.2.0**: Automatic post-processing that ensures subtitle cues are short and uniform.

### How It Works
Whisper's native segments can vary wildly in length (30+ seconds at the start, under 5 seconds later). This makes subtitles unreadable in video players. Textifier now:
1. Always collects word-level timestamps during transcription.
2. Post-processes segments into short cues of **~3 seconds / max 12 words** each.
3. Writes these short cues to all timed formats (VTT, SRT, CSV, TSV).
4. Preserves original full paragraphs for TXT output (no timecodes needed).

### Parameters
- **Max Duration**: 3.0 seconds per subtitle cue.
- **Max Words**: 12 words per subtitle cue.

---

## Output Formats

Textifier generates multiple formats simultaneously. Select which formats to produce in the GUI checkboxes or via `--output-formats` in the CLI.

- **VTT**: Web-compatible subtitles (re-segmented to short cues).
- **SRT**: Video editor subtitles (re-segmented to short cues).
- **TXT**: Plain text transcripts (full paragraphs, no timecodes).
- **CSV**: Structured data with Start/End/Text columns (re-segmented).
- **TSV**: Tab-separated structured data (re-segmented).
- **JSON**: Word-level timing data with probabilities (when enabled via checkbox or `--word-timestamps`).

**CLI**: `--output-formats vtt srt txt csv tsv`
