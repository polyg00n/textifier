# Changelog

All notable changes to Textifier will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-01-25

### 🎉 Major Features

#### Whisper Punctuation Fix
- **Fixed**: Resolved issue where Whisper produced lowercase text without punctuation due to silent audio at the beginning
- **Implementation**: Automatic `initial_prompt` injection guides Whisper to use proper capitalization and punctuation
- **Impact**: All transcriptions now have professional formatting without requiring model retraining or user configuration

#### Multi-Format Output
- **Changed**: `transcribe_media()` now automatically generates **4 output formats** instead of requiring format selection:
  - **VTT** - WebVTT subtitle format for web players
  - **SRT** - SubRip subtitle format for video editors
  - **TXT** - Plain text for reading and analysis
  - **CSV** - Structured data with timestamps for data processing
- **Benefit**: Maximum flexibility without requiring upfront format selection

#### Comprehensive Multi-Language Support

**Transcription (Whisper)**:
- **Added**: Language selection dropdown in both Batch and Advanced tabs
- **Languages**: 36+ supported languages including:
  - Western European: English, Spanish, French, German, Italian, Portuguese, Dutch
  - Eastern European: Russian, Polish, Ukrainian, Czech, Romanian, Hungarian
  - Asian: Chinese, Japanese, Korean, Hindi, Gujarati, Tamil, Telugu, Bengali, Thai, Vietnamese, Indonesian
  - Middle Eastern: Arabic, Hebrew, Turkish, Persian, Urdu
  - Nordic: Swedish, Norwegian, Danish, Finnish
  - And more: Greek, Punjabi, Marathi
- **Default**: "Auto-detect" lets Whisper determine the source language automatically
- **Benefit**: Accurate transcription for global content without manual configuration

**Translation (mBART-50)**:
- **Expanded**: From 2 languages (French, Hindi) to **40+ languages**
- **Added**: Source language selection - no longer limited to English-only input
- **Bi-directional**: Translate between any supported language pair
  - Examples: Hindi → Gujarati, Spanish → French, Japanese → English
- **Languages Added**: Persian, Swahili, Tagalog, Afrikaans, Azerbaijani, Burmese, Croatian, Estonian, Georgian, Kazakh, Khmer, Latvian, Lithuanian, Macedonian, Malayalam, Mongolian, Nepali, Pashto, Sinhala, Xhosa, and more
- **Use Case**: Serve international teams with diverse language requirements

---

### ✨ Enhancements

#### Backend (`textifier_core.py`)
- **Added**: CSV module import for structured data export
- **Added**: `FormatHandler.save_txt()` - Export plain text transcriptions
- **Added**: `FormatHandler.save_csv()` - Export CSV with Start/End/Text columns
- **Enhanced**: `Translator.translate()` now accepts `source_lang` parameter
- **Enhanced**: `translate_vtt()` supports source language specification
- **Expanded**: mBART language code dictionary from 2 to 46+ languages

#### Frontend (`gui_main.py`)
- **Added**: `WHISPER_LANGUAGES` constant with 36 language definitions
- **Added**: `MBART_LANGUAGES` constant with 40 language definitions
- **Enhanced**: Batch tab transcription section with "Audio Language" dropdown
- **Enhanced**: Batch tab translation section with "Source Language" and "Target Language" dropdowns
- **Enhanced**: Advanced Whisper tab with language selection
- **Improved**: Activity log now reports all created files after transcription
- **Updated**: Section titles for clarity (e.g., "Transcribe (Video/Audio → Text)")

---

### 🔧 Changes

#### Breaking Changes
- **BREAKING**: `TextifierCore.transcribe_media()` return value changed
  - **Before**: Returns single file path as string (e.g., `"video.vtt"`)
  - **After**: Returns list of file paths (e.g., `["video.vtt", "video.srt", "video.txt", "video.csv"]`)
  - **Impact**: External scripts calling this method directly must update to handle list return type
  - **GUI Impact**: None - all GUI workflows remain fully compatible

#### Non-Breaking Changes
- **Updated**: `Translator.translate()` signature - added `source_lang` parameter with default `"en"`
- **Updated**: `translate_vtt()` signature - added `source_lang` parameter with default `"en"`
- **Backward Compatible**: Existing calls without `source_lang` default to English as before

---

### 📝 Documentation

- **Added**: Comprehensive walkthrough documenting all changes
- **Updated**: README.md with multi-language support information
- **Updated**: WhisperSettings.md with language parameter documentation
- **Added**: CHANGELOG.md (this file)

---

### 🧪 Testing

- **Added**: `test_enhancements.py` verification script
- **Verified**: Module imports and new methods exist
- **Verified**: Language constants contain requested languages
- **Verified**: CSV module properly imported

---

### 🎯 Use Cases Enabled

1. **Global Content Creators**: Transcribe videos in 36+ languages
2. **International Teams**: Translate subtitles between any language pair
3. **Data Analysis**: Export transcriptions as CSV for processing
4. **Video Editors**: Get all subtitle formats in one operation
5. **Accessibility**: Provide proper punctuation for better screen reader experience
6. **Mumbai Office**: Full Hindi and Gujarati support for transcription and translation

---

### 📦 Files Modified

- `textifier_core.py` - ~80 lines changed
- `gui_main.py` - ~120 lines changed
- `test_enhancements.py` - New verification script
- `CHANGELOG.md` - New file (this changelog)
- `README.md` - Updated for v2.0.0
- `WhisperSettings.md` - Added language parameter docs

---

### 🚀 Upgrade Notes

**For GUI Users**: No action required - all changes are backward compatible in the GUI

**For CLI/Script Users**: 
- Update code using `transcribe_media()` to handle list return value:
  ```python
  # Before (v1.x)
  output_path = core.transcribe_media("video.mp4")
  print(f"Created: {output_path}")
  
  # After (v2.0.0)
  output_files = core.transcribe_media("video.mp4")
  print(f"Created: {', '.join(output_files)}")
  ```

**For Translation Users**:
- To translate from non-English sources, specify `source_lang`:
  ```python
  # Translate Hindi to Gujarati
  core.translate_vtt("subtitles.vtt", source_lang="hi", target_lang="gu")
  ```

---

### 🙏 Credits

- Punctuation fix inspired by community feedback on Whisper behavior with silent audio
- Language expansion requested by international users (Mumbai office team)
- Multi-format output based on workflow efficiency improvements

---

## [1.x.x] - Previous Versions

See git history for previous releases.
