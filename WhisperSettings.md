# Whisper Advanced Settings Guide

This document explains the advanced parameters available in the **Advanced Whisper** tab of Textifier. These settings allow you to fine-tune the transcription process for better accuracy or faster performance.

---

## Model Selection

### Whisper Model Size
Select the size of the neural network.
- **Tiny/Base**: Extremely fast, lower accuracy. Good for clean audio with clear speech.
- **Small/Medium**: Balanced performance and accuracy.
- **Large/Large-v3**: Best accuracy, supports most languages. Requires significant VRAM (GPU) or time (CPU).

---

## Decoding Parameters

### Beam Size
The number of candidate sequences the model explores during decoding.
- **Range**: 1 to 10+
- **Default**: 5
- **Effect**: Higher values can improve accuracy but increase processing time and memory usage.

### Best Of
Number of candidate decodings to sample when `beam_size` is not used (non-zero temperature).
- **Default**: 5
- **Effect**: Helps the model find the most "stable" transcription by comparing multiple attempts.

### Patience
Beam search patience factor.
- **Default**: 1.0
- **Effect**: A value > 1.0 makes the beam search more "patient," continuing the search longer to potentially find better results.

---

## Temperature & Sampling

### Temperature
Controls the "creativity" or randomness of the model.
- **Range**: 0.0 to 1.0
- **Default**: 0.0 (Greedy Decoding)
- **Effect**: 
    - **0.0**: Always picks the most likely next word (most reliable).
    - **Higher (e.g., 0.8)**: Introduces randomness. Useful if the model gets stuck in a loop or fails to detect speech in difficult audio.

### Temperature Increment
If the model fails to transcribe a segment (due to low probability), it can retry with a higher temperature.
- **Default**: 0.2
- **Effect**: If the first attempt at Temp 0.0 fails, it retries at 0.2, then 0.4, etc.

---

## Audio & Padding

### Compression Ratio Threshold
A safety check to detect repetitive, low-quality output.
- **Default**: 2.4
- **Effect**: If the output text is too repetitive (compressed), the model flags it as a failure and may retry with different parameters.

### Log Probability Threshold
Threshold for the average log-probability of the generated text.
- **Default**: -1.0
- **Effect**: Filters out low-confidence transcriptions.

### No Speech Threshold
Threshold to determine if a segment contains actual speech.
- **Default**: 0.6
- **Effect**: If the model is > 60% sure there is no speech, it will leave the segment blank instead of "hallucinating" text from background noise.

---

## Performance Settings

### Local Models vs. Cloud
Textifier runs all models **locally**.
- **Privacy**: No audio ever leaves your computer.
- **Cost**: 100% free to use after downloading.
- **VRAM**: If using a GPU, "Large" models usually require 8GB+ of VRAM.

### FP16 (Half Precision)
- **Effect**: Using `fp16=True` (default on GPU) halves memory usage and nearly doubles speed on modern NVIDIA cards without significant loss in accuracy.
