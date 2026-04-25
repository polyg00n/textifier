# Whisper Advanced Settings Guide

This document explains the advanced parameters available in the **Advanced Whisper** tab of Textifier. These settings allow you to fine-tune the transcription process for better accuracy or faster performance.

---

## Model Selection

### Whisper Model Size
Select the size of the neural network.
- **Tiny/Base**: Extremely fast, lower accuracy.
- **Small/Medium**: Balanced performance and accuracy.
- **Large/Large-v3-turbo**: Best accuracy/speed ratio. **large-v3-turbo** is the default for v2.1.0.
- **Distil-Whisper**: Optimized for speed on specific language pairs.

---

## Decoding Parameters

### Beam Size
The number of candidate sequences the model explores during decoding.
- **Default**: 5
- **Effect**: Higher values can improve accuracy but increase processing time.

### Patience
Beam search patience factor.
- **Default**: 1.0
- **Effect**: A value > 1.0 makes the beam search more "patient," continuing the search longer.

### Repetition Penalty
**New in v2.1.0**: Penalty applied to repeated tokens.
- **Default**: 1.1
- **Effect**: Prevents the model from getting stuck in loops (e.g., repeating the same word infinitely).

---

## Audio & Filtering

### VAD (Voice Activity Detection)
**New in v2.1.0**: Uses Silero VAD to automatically filter out non-speech segments.
- **Default**: ON
- **Benefit**: Significantly reduces "hallucinations" (model making up text from background noise or silence).

### Word-Level Timestamps
**New in v2.1.0**: Generates precise timing for every single word.
- **Output**: Exports a `.words.json` file with detailed timing and probability metadata.

### No Speech Threshold
Threshold to determine if a segment contains actual speech.
- **Default**: 0.6
- **Effect**: If the model is > 60% sure there is no speech, it will leave the segment blank.

---

## Temperature & Sampling

### Temperature
Controls the "creativity" or randomness of the model.
- **Range**: 0.0 to 1.0
- **Default**: 0.0 (Greedy Decoding)
- **Effect**: 
    - **0.0**: Always picks the most likely next word (most reliable).
    - **Higher**: Introduces randomness. Useful if the model fails in difficult audio.

---

## Performance Settings

### GPU Acceleration
Textifier automatically detects CUDA-capable GPUs.
- **FP16 (Half Precision)**: Default on GPU. Nearly doubles speed with zero accuracy loss.
- **Fallback**: If FP16 is not supported or VRAM is low, Textifier automatically falls back to `int8` or CPU.

---

## Punctuation & Formatting

### Initial Prompt
**New in v2.0.0**: Guide the model to use proper punctuation and capitalization.
- **Default**: "Hello, welcome to my lecture. I will use proper punctuation, capitalization, and grammar."
- **Customization**: Add technical terms (e.g., "React, TypeScript") to help the model spell them correctly.

---

## Output Formats

Textifier generates multiple formats simultaneously:
- **VTT**: Web-compatible subtitles.
- **SRT**: Video editor subtitles.
- **TXT**: Plain text transcripts.
- **CSV**: Structured data (Start, End, Text).
- **TSV**: Tab-separated structured data (new in v2.1.0).
- **JSON**: Word-level timing data (when enabled).
