# Missing Whisper and mBART Capabilities

## Analysis Date: 2026-01-25

This document identifies advanced Whisper (faster-whisper) and mBART parameters that are **not yet exposed** in the Textifier Advanced tab but could enhance user control.

---

## Missing Whisper (faster-whisper) Parameters

### 1. VAD (Voice Activity Detection) Filter
**Status**: ❌ Not Implemented  
**Priority**: HIGH  
**Description**: Integrates Silero VAD to filter out non-speech segments automatically
**Parameters**:
- `vad_filter`: Boolean to enable/disable
- `vad_parameters`: Dict with:
  - `threshold`: Speech detection sensitivity (0.0-1.0)
  - `min_silence_duration_ms`: Minimum silence to split segments (default: 2000ms)
  - `min_speech_duration_ms`: Minimum valid speech duration (default: 250ms)
  - `speech_pad_ms`: Padding around speech segments (default: 400ms)
  - `window_size_samples`: VAD analysis window (default: 1536)

**Benefits**:
- Dramatically improves quality for audio with long silences
- Prevents hallucinations in silent segments
- Reduces processing time by skipping non-speech

**Recommendation**: Add to Advanced tab with checkbox + expandable advanced VAD settings

---

### 2. Word-Level Timestamps
**Status**: ❌ Not Implemented  
**Priority**: MEDIUM  
**Description**: Provides timestamp for each individual word, not just segments
**Parameter**: `word_timestamps` (Boolean)

**Benefits**:
- Karaoke-style subtitle creation
- Precise synchronization for dubbing
- Better accessibility for hearing impaired

**Output Format**: Would need new export format or JSON output option

**Recommendation**: Add checkbox in Advanced tab, export as JSON when enabled

---

### 3. Advanced Sampling Controls

#### Temperature List
**Status**: ⚠️ Partially Implemented (single temperature only)  
**Priority**: LOW  
**Description**: Try multiple temperatures and pick best result
**Parameter**: `temperatures` (List[float])  
**Example**: `[0.0, 0.2, 0.4, 0.6, 0.8, 1.0]`

**Current**: User sets single temperature value  
**Enhancement**: Allow semicolon-separated list (e.g., "0.0;0.2;0.4")

#### Repetition Penalty
**Status**: ❌ Not Implemented  
**Priority**: MEDIUM  
**Description**: Penalize repeated tokens to prevent loops
**Parameter**: `repetition_penalty` (Float, default: 1.0)  
**Range**: 1.0 (no penalty) to 2.0 (strong penalty)

**Use Case**: Prevents "Thank you. Thank you. Thank you..." type failures

#### Length Penalty
**Status**: ❌ Not Implemented  
**Priority**: LOW  
**Description**: Control output length preference
**Parameter**: `length_penalty` (Float)  
**Range**: <1.0 (shorter), >1.0 (longer)

---

### 4. Token Suppression
**Status**: ❌ Not Implemented  
**Priority**: LOW  
**Description**: Prevent specific tokens from being generated
**Parameters**:
- `suppress_tokens`: List of token IDs to ban
- `suppress_blank`: Boolean to suppress blank outputs

**Use Case**: Block specific words/sounds that cause issues

**Complexity**: Requires token ID lookup - advanced users only

---

### 5. Output Control Parameters

#### Max New Tokens
**Status**: ❌ Not Implemented  
**Priority**: LOW  
**Parameter**: `max_new_tokens` (Int)  
**Description**: Limit maximum tokens per segment

#### Without Timestamps
**Status**: ❌ Not Implemented  
**Priority**: LOW  
**Parameter**: `without_timestamps` (Boolean)  
**Use Case**: Plain text output when timestamps not needed

#### Prepend/Append Punctuations
**Status**: ⚠️ Hardcoded (not user-configurable)  
**Priority**: LOW  
**Current Values**:
- `prepend_punctuations`: `"'\"¿([{-"`
- `append_punctuations`: `"'\"".。,，!！?？:：)]}、"`

**Enhancement**: Make these user-editable for different language conventions

---

### 6. Hallucination Detection Controls

#### Compression Ratio Threshold
**Status**: ✅ Implemented  
**Current**: Exposed in Advanced tab

#### Log Prob Threshold  
**Status**: ✅ Implemented  
**Current**: Exposed in Advanced tab

#### No Speech Threshold
**Status**: ✅ Implemented  
**Current**: Exposed in Advanced tab

---

### 7. Prompt Controls

#### Initial Prompt
**Status**: ⚠️ Partially Implemented  
**Current**: User can set via text box in Advanced tab  
**Enhancement**: Add preset templates (e.g., "Technical", "Medical", "Formal", "Casual")

#### Prefix
**Status**: ❌ Not Implemented  
**Parameter**: `prefix` (String)  
**Description**: Text to prepend to audio for context

#### Prompt Reset on Temperature
**Status**: ❌ Not Implemented  
**Parameter**: `prompt_reset_on_temperature` (Float)  
**Description**: When to reset prompt based on temperature

---

## Missing mBART Parameters

### 1. Decoding Strategy
**Status**: ❌ Not Implemented  
**Parameters**: Currently hardcoded in `translate()` method:
- `num_beams`: Fixed at 5
- `max_length`: Fixed at 512
- `early_stopping`: Not configurable
- `no_repeat_ngram_size`: Not configurable
- `length_penalty`: Not configurable

**Recommendation**: Expose beam search parameters for translation quality tuning

---

### 2. Batch Translation
**Status**: ❌ Not Implemented  
**Description**: Currently translates one cue at a time
**Enhancement**: Batch multiple segments for faster translation

**Current Bottleneck**: Loop in `translate_vtt()` translates sequentially:
```python
for i, cue in enumerate(cues):
    cue['text'] = self.translator.translate(cue['text'], ...)
```

**Improvement**: Batch process with `tokenizer(..., batch_size=N)`

---

### 3. Quality Controls
**Status**: ❌ Not Implemented  
**Parameters**:
- `temperature`: Translation sampling temperature (default: 1.0)
- `top_k`: Top-k sampling
- `top_p`: Nucleus sampling
- `do_sample`: Enable sampling vs greedy

---

## Implementation Priority Recommendations

### High Priority (Significant User Value)
1. **VAD Filter** - Massive quality improvement for real-world audio
2. **Repetition Penalty** - Solves common failure mode
3. **Word Timestamps** - Enables new use cases

### Medium Priority (Nice to Have)
4. **Temperature List** - Better handling of difficult audio
5. **mBART Beam Parameters** - Translation quality tuning
6. **Batch Translation** - Performance improvement

### Low Priority (Advanced Users Only)
7. **Token Suppression** - Very specialized
8. **Length Penalty** - Niche use case
9. **Punctuation Customization** - Language-specific edge cases
10. **Max New Tokens** - Rarely needed

---

## Current Advanced Tab Coverage

### ✅ Implemented Parameters
- Task (transcribe/translate)
- Language selection
- Temperature (single value)
- Beam size
- Best of
- Patience
- Condition on previous text
- Initial prompt
- No speech threshold
- Log prob threshold
- Compression ratio threshold
- FP16 toggle
- Device selection
- Output format selection

### ❌ Missing Critical Parameters
- **VAD filter and settings**
- **Word timestamps**
- **Repetition penalty**
- **Temperature list (vs single)**
- **mBART decoding parameters**

---

## Recommendations for Next Version

### Quick Wins (Easy to Implement)
1. Add `repetition_penalty` slider (1.0 - 2.0)
2. Add `word_timestamps` checkbox
3. Add `vad_filter` checkbox with basic settings

### Future Enhancements
1. Create "Presets" system for common scenarios:
   - "Podcast" preset (VAD enabled, repetition penalty 1.2)
   - "Music/Lyrics" preset (word timestamps, low no_speech_threshold)
   - "Technical" preset (initial prompt with technical terms)
2. Export word-level timestamps as JSON or WebVTT with `<v>` tags
3. Add translation quality presets (Fast/Balanced/Quality)

---

## Notes

This analysis is based on faster-whisper v1.0+ and transformers v4.36+ API documentation. Parameters may change in future versions. Always refer to official documentation when implementing.
