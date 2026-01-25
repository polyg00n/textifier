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

---

## Language Selection

### Audio Language
**New in v2.0.0**: Specify the source language of your audio for improved accuracy.
- **Default**: Auto-detect (Whisper analyzes first 30 seconds)
- **Options**: 36+ languages supported
- **Effect**: 
    - **Auto-detect**: Let Whisper determine the language (recommended for most use cases)
    - **Explicit Language**: Better accuracy when you know the source language
    - **Mixed Language**: Use auto-detect; Whisper can handle multi-language audio

**Common Languages**:
- Western European: English, Spanish, French, German, Italian, Portuguese, Dutch
- Asian: Chinese, Japanese, Korean, Hindi, Gujarati, Tamil, Telugu, Vietnamese, Thai
- Eastern European: Russian, Polish, Ukrainian, Czech
- Middle Eastern: Arabic, Hebrew, Turkish, Persian

**Tip**: If transcription quality is poor with auto-detect, try explicitly setting the language.

---

## Punctuation & Capitalization Fix

### Initial Prompt
**New in v2.0.0**: Automatically applied to ensure proper punctuation and capitalization.

**Background**: Whisper sometimes produces lowercase text without punctuation when audio begins with silence. Textifier now automatically solves this by providing an `initial_prompt`.

**Default Prompt**:
```
"Hello, welcome to my lecture. I will use proper punctuation, capitalization, and grammar."
```

**Customization**: You can override this in the Advanced tab's "Initial Prompt" field to:
- Add domain-specific vocabulary (e.g., "React, TypeScript, and JavaScript")
- Set formatting style (e.g., "Dr. Smith discusses HIPAA compliance...")
- Provide speaker names for better accuracy

**Effect**: All transcriptions now have professional formatting without additional processing.

---

## Advanced Features Not Yet Exposed

For a complete list of additional Whisper parameters not yet available in the UI, see `MISSING_CAPABILITIES.md`. These include:
- **VAD (Voice Activity Detection)**: Automatic silence filtering
- **Word-level timestamps**: Per-word timing data
- **Repetition penalty**: Prevent looping text
- **Temperature lists**: Multi-pass decoding

---

## Tips & Best Practices

1. **For Podcasts**: Use larger models (medium/large) with default settings
2. **For Music/Lyrics**: Lower the "No Speech Threshold" to 0.3-0.4
3. **For Lectures**: Set explicit language and use initial prompt with technical terms
4. **For Noisy Audio**: Increase beam size to 10 and enable higher patience
5. **For Fast Processing**: Use distil-large-v3 or large-v3-turbo models

---

## Multi-Format Output

**New in v2.0.0**: Textifier now automatically generates **4 output formats**:
- **VTT**: Web-compatible subtitle format
- **SRT**: Industry-standard for video editors
- **TXT**: Plain text for reading/analysis
- **CSV**: Structured data with timestamps for processing

No need to choose a format upfront - you get all of them!

