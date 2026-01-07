# Textifier

Textifier is a Python application that provides two main functionalities:
1. Transcribe video/audio files to VTT format with timestamps using OpenAI's Whisper
2. Translate VTT files from English to multiple languages while preserving timestamps using mBART

by Sergio Gonzalez

## Features

- High-quality transcription using OpenAI's Whisper model
- Accurate English to multiple language translations using mBART
- Supports English to French and Hindi translations
- Preserves timestamps and VTT formatting during translation
- Supports batch processing of files in folders
- Handles various video and audio formats
- Generates VTT files compatible with most video players
- Self-contained - all models are downloaded and stored locally
- Cross-platform support (Windows, Linux, macOS)

## Models Used

### Transcription: OpenAI Whisper
- Model: [Whisper Base](https://huggingface.co/openai/whisper-base)
- Capabilities: Speech recognition and transcription
- Features: Multilingual support, accurate timestamps, punctuation
- Size: ~1.5GB

### Translation: mBART
- Model: [mBART Large 50](https://huggingface.co/facebook/mbart-large-50-many-to-many-mmt)
- Capabilities: Multilingual translation
- Features: High-quality translations, context-aware, supports multiple language pairs
- Size: ~1.5GB
- Supported Languages:
  - French (fr_XX)
  - Hindi (hi_IN)

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- FFmpeg (for audio/video processing)

### Installing FFmpeg

#### Windows
1. Download FFmpeg from the official website: https://ffmpeg.org/download.html
2. Extract the downloaded zip file
3. Add the FFmpeg bin directory to your system PATH:
   - Open System Properties (Win + Pause/Break)
   - Click "Advanced system settings"
   - Click "Environment Variables"
   - Under "System variables", find and select "Path"
   - Click "Edit"
   - Click "New" and add the path to the FFmpeg bin directory (e.g., `C:\ffmpeg\bin`)
   - Click "OK" on all windows

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install ffmpeg
```

#### Linux (Fedora)
```bash
sudo dnf install ffmpeg
```

#### Linux (Arch Linux)
```bash
sudo pacman -S ffmpeg
```

### Installing the Application

1. Clone this repository:
```bash
git clone https://github.com/polyg00n/textifier.git
cd textifier
```

2. Create and activate a virtual environment (recommended):

#### Windows
```bash
python -m venv venv
venv\Scripts\activate
```

#### Linux/macOS
```bash
python -m venv venv
source venv/bin/activate
```

3. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Quick Start

### 1. Transcribe Your First Video

```bash
# Windows
python textifier.py transcribe "E:\videos\my_video.mp4"

# Linux/macOS
python textifier.py transcribe /home/user/videos/my_video.mp4
```

This will:
- Download the Whisper model (first time only, ~1.5GB)
- Transcribe the video to `my_video.vtt`
- Save the VTT file in the same directory

### 2. Download Translation Model (One-Time Setup)

```bash
python textifier.py download-translation-model
```

This downloads the mBART model (~1.5GB) for translation.

### 3. Translate Your Transcription

```bash
# Translate to French (default)
python textifier.py translate "E:\videos\my_video.vtt"

# Translate to Hindi
python textifier.py translate "E:\videos\my_video.vtt" -l hi
```

This creates `my_video_fr.vtt` or `my_video_hi.vtt` with translated subtitles.

## First Run Setup

### Step 1: Download Transcription Model (Whisper)

The Whisper model will be automatically downloaded on the first transcription run. When you run the `transcribe` command for the first time, the application will:
1. Create a `models` directory
2. Download and save the Whisper base model (~1.5GB)

**Note:** The transcription model downloads automatically - no separate command needed.

### Step 2: Download Translation Model (mBART) - Optional

The translation model must be downloaded separately before you can use the translation feature. To download it:

```bash
python textifier.py download-translation-model
```

This will download the mBART model (~1.5GB) and save it locally. This only needs to be done once.

**Important:** You must download the translation model before using the `translate` command, otherwise you'll get an error.

## Usage

### Command Overview

The application provides three main commands:
- `transcribe` - Transcribe video/audio files to VTT format
- `translate` - Translate VTT files from English to other languages
- `download-translation-model` - Download the translation model

### Transcribing Media Files

#### Single File Transcription

Transcribe a single video or audio file to VTT format:

**Windows:**
```bash
# Using backslashes
python textifier.py transcribe E:\projects\textifier\videos\video.mp4

# Using forward slashes (also works)
python textifier.py transcribe E:/projects/textifier/videos/video.mp4

# With quotes (handles spaces in paths)
python textifier.py transcribe "E:\projects\textifier\videos\my video.mp4"
```

**Linux/macOS:**
```bash
# Absolute path
python textifier.py transcribe /home/user/videos/video.mp4

# Relative path
python textifier.py transcribe ./videos/video.mp4

# With quotes (handles spaces)
python textifier.py transcribe "/home/user/videos/my video.mp4"
```

#### Batch Folder Transcription

To transcribe all video/audio files in a folder:

**Windows:**
```bash
python textifier.py transcribe E:\projects\textifier\videos -f
```

**Linux/macOS:**
```bash
python textifier.py transcribe /home/user/videos -f
```

**What happens:**
- The application scans the folder for supported media files
- Processes each file sequentially
- Creates a VTT file for each input file in the same directory
- Shows progress for each file

**Supported input formats:**
- Video: `.mp4`, `.avi`, `.mkv`, `.mov`, `.wmv`
- Audio: `.mp3`, `.wav`, `.m4a`, `.aac`

**Output:**
- The output VTT file is saved in the same directory as the input file
- The filename matches the input file but with `.vtt` extension
- Example: `video.mp4` → `video.vtt`

### Translating VTT Files

#### Prerequisites

Before translating, ensure you've downloaded the translation model:
```bash
python textifier.py download-translation-model
```

#### Single File Translation

Translate a single VTT file from English to French (default):

**Windows:**
```bash
python textifier.py translate E:\projects\textifier\videos\video.vtt
```

**Linux/macOS:**
```bash
python textifier.py translate /home/user/videos/video.vtt
```

Translate to Hindi:
```bash
python textifier.py translate path/to/video.vtt -l hi
```

#### Batch Folder Translation

Translate all VTT files in a folder to French:
```bash
python textifier.py translate path/to/folder -f
```

Translate all VTT files in a folder to Hindi:
```bash
python textifier.py translate path/to/folder -f -l hi
```

**What happens:**
- The application scans the folder for `.vtt` files
- Processes each file sequentially
- Preserves all timestamps and formatting
- Creates a translated VTT file for each input file

**Output:**
- The translated VTT file is saved in the same directory as the input file
- The filename has the language code appended: `video.vtt` → `video_fr.vtt` (French) or `video_hi.vtt` (Hindi)

**Supported target languages:**
- French (`fr`) - Default
- Hindi (`hi`)

### Command-Line Options

#### Transcribe Command
```bash
python textifier.py transcribe <input_file_or_folder> [options]

Arguments:
  input_file_or_folder    Path to video/audio file or folder containing media files

Options:
  -f, --folder            Process all supported files in the specified folder
```

**Examples:**
```bash
# Single file
python textifier.py transcribe video.mp4

# Batch folder processing
python textifier.py transcribe ./videos -f
```

#### Translate Command
```bash
python textifier.py translate <input_file_or_folder> [options]

Arguments:
  input_file_or_folder    Path to VTT file or folder containing VTT files

Options:
  -f, --folder            Process all VTT files in the specified folder
  -l, --lang {fr,hi}      Target language (default: fr)
                          fr = French, hi = Hindi
```

**Examples:**
```bash
# Single file, French (default)
python textifier.py translate video.vtt

# Single file, Hindi
python textifier.py translate video.vtt -l hi

# Batch folder, French
python textifier.py translate ./videos -f

# Batch folder, Hindi
python textifier.py translate ./videos -f -l hi
```

#### Download Translation Model Command
```bash
python textifier.py download-translation-model
```

This command downloads the mBART translation model. It only needs to be run once, or if you want to re-download the model.

### Path Format Support

The application supports various path formats for cross-platform compatibility:

**Windows:**
- `E:\projects\textifier\videos\file.vtt` (backslashes)
- `E:/projects/textifier/videos/file.vtt` (forward slashes)
- `"E:\projects\textifier\videos\file.vtt"` (quoted, handles spaces)
- `E:\\projects\\textifier\\videos\\file.vtt` (escaped backslashes)

**Linux/macOS:**
- `/home/user/videos/file.vtt` (absolute path)
- `./videos/file.vtt` (relative path)
- `~/videos/file.vtt` (home directory shortcut)
- `"/home/user/videos/file with spaces.vtt"` (quoted, handles spaces)

All formats are automatically normalized by the application.

## Linux-Specific Notes

1. **Permissions**: If you encounter permission issues when running the script, you can make it executable:
```bash
chmod +x textifier.py
```

2. **Virtual Environment**: When using a virtual environment, remember to activate it before running the script:
```bash
source venv/bin/activate
python textifier.py [command] [arguments]
```

3. **Path Handling**: Linux uses forward slashes (/) for paths. The application automatically handles path normalization, so both relative and absolute paths will work correctly.

4. **Model Storage**: On Linux, models are stored in the `models` directory in your home folder by default. You can change this location by modifying the `MODELS_DIR` variable in the script.

5. **System Dependencies**: Make sure you have all required system dependencies installed:
```bash
# For Ubuntu/Debian
sudo apt install python3-pip python3-venv ffmpeg

# For Fedora
sudo dnf install python3-pip python3-virtualenv ffmpeg

# For Arch Linux
sudo pacman -S python-pip python-virtualenv ffmpeg
```

## Output Format

### VTT File Structure

The application generates WebVTT (Web Video Text Tracks) files that are compatible with most video players and platforms (YouTube, Vimeo, HTML5 video players, etc.).

**File Format:**
```
WEBVTT

1
00:00:00.000 --> 00:00:11.080
Transcribed or translated text here

2
00:00:11.080 --> 00:00:16.680
Next segment of text

3
00:00:16.680 --> 00:00:22.500
Another segment continues here
```

**Components:**
- `WEBVTT` - File header (required)
- Empty line separator
- Cue number (sequential: 1, 2, 3, ...)
- Timestamp range (`HH:MM:SS.mmm --> HH:MM:SS.mmm`)
- Text content (the transcribed or translated text)
- Empty line between cues

### File Naming Convention

**Transcription:**
- Input: `video.mp4`
- Output: `video.vtt`

**Translation:**
- Input: `video.vtt`
- Output: `video_fr.vtt` (French) or `video_hi.vtt` (Hindi)

### Example Workflow

1. **Original video:** `presentation.mp4`
2. **After transcription:** `presentation.vtt` (English subtitles)
3. **After translation:** `presentation_fr.vtt` (French subtitles)

All files are saved in the same directory as the source file.

### Using VTT Files

**With Video Players:**
- Most modern video players support VTT files
- Load the VTT file as a subtitle track in your video player
- The timestamps ensure perfect synchronization

**With Video Platforms:**
- **YouTube:** Upload VTT file when uploading video
- **Vimeo:** Add as subtitle track in video settings
- **HTML5:** Use the `<track>` element in video tags

**Example HTML5 Usage:**
```html
<video controls>
  <source src="video.mp4" type="video/mp4">
  <track kind="subtitles" src="video.vtt" srclang="en" label="English">
  <track kind="subtitles" src="video_fr.vtt" srclang="fr" label="French">
</video>
```

## Complete Example Workflow

Here's a complete example of transcribing and translating a video:

### Step-by-Step Example

**1. Start with a video file:**
```
E:\projects\textifier\videos\presentation.mp4
```

**2. Transcribe the video:**
```bash
python textifier.py transcribe "E:\projects\textifier\videos\presentation.mp4"
```

**Output:**
```
Downloading Whisper model...
Transcription completed. Output saved to: E:\projects\textifier\videos\presentation.vtt
```

**3. Download translation model (first time only):**
```bash
python textifier.py download-translation-model
```

**Output:**
```
Downloading translation model...
Translation model downloaded and saved successfully!
```

**4. Translate to French:**
```bash
python textifier.py translate "E:\projects\textifier\videos\presentation.vtt"
```

**Output:**
```
Loading translation model...
Translation completed. Output saved to: E:\projects\textifier\videos\presentation_fr.vtt
```

**5. Translate to Hindi:**
```bash
python textifier.py translate "E:\projects\textifier\videos\presentation.vtt" -l hi
```

**Output:**
```
Loading translation model...
Translation completed. Output saved to: E:\projects\textifier\videos\presentation_hi.vtt
```

**Final Result:**
```
videos/
├── presentation.mp4          (original video)
├── presentation.vtt            (English subtitles)
├── presentation_fr.vtt       (French subtitles)
└── presentation_hi.vtt       (Hindi subtitles)
```

### Batch Processing Example

**Process an entire folder of videos:**

```bash
# Transcribe all videos in folder
python textifier.py transcribe "E:\projects\textifier\videos" -f

# Output:
# Found 5 files to transcribe
# Processing file 1/5: video1.mp4
# Transcription completed. Output saved to: E:\projects\textifier\videos\video1.vtt
# Processing file 2/5: video2.mp4
# ...

# Translate all VTT files to French
python textifier.py translate "E:\projects\textifier\videos" -f

# Output:
# Found 5 files to translate
# Processing file 1/5: video1.vtt
# Translation completed. Output saved to: E:\projects\textifier\videos\video1_fr.vtt
# ...
```

## Advanced Usage

### Changing Whisper Model Size

By default, the application uses the Whisper "base" model. You can change this in `textifier.py`:

```python
# In the __init__ method, change:
self.whisper_model = whisper.load_model("base", ...)

# Available options (from smallest to largest):
# "tiny"   - Fastest, least accurate (~75MB)
# "base"   - Balanced (default) (~150MB)
# "small"  - Better accuracy (~500MB)
# "medium" - High accuracy (~1.5GB)
# "large"  - Best accuracy (~3GB)
```

**Trade-offs:**
- Smaller models: Faster processing, lower accuracy, less memory
- Larger models: Slower processing, higher accuracy, more memory

### Model Storage Location

Models are stored in the `models` directory in your project folder:
```
textifier/
├── models/
│   ├── whisper/          # Whisper transcription model
│   └── translation/       # mBART translation model
├── textifier.py
└── requirements.txt
```

To use a different location, modify the `models_dir` variable in the `Textifier.__init__()` method.

### Processing Large Files

For very long videos or audio files:
- Transcription time scales with file length
- Consider using a smaller Whisper model for faster processing
- The application processes files sequentially, so batch processing may take time

### Memory Requirements

**Minimum:**
- 4GB RAM for base models
- 8GB RAM recommended for better performance

**Disk Space:**
- ~3GB for Whisper base model
- ~1.5GB for mBART translation model
- Additional space for input/output files

## Troubleshooting

### Common Issues

#### 1. "Translation model not found" Error

**Problem:** You're trying to translate without downloading the translation model first.

**Solution:**
```bash
python textifier.py download-translation-model
```

#### 2. FFmpeg Not Found

**Problem:** `FileNotFoundError` or errors related to audio processing.

**Solution:**
- Ensure FFmpeg is installed and in your system PATH
- Verify installation: `ffmpeg -version`
- See installation instructions above

#### 3. Out of Memory Errors

**Problem:** System runs out of memory during processing.

**Solutions:**
- Close other applications
- Use a smaller Whisper model (e.g., "tiny" or "base")
- Process files one at a time instead of batch processing
- Increase system swap/virtual memory

#### 4. Path Not Found Errors

**Problem:** `FileNotFoundError` when specifying file paths.

**Solutions:**
- Use absolute paths instead of relative paths
- Check that the file exists
- Ensure proper path formatting (see Path Format Support section)
- Use quotes around paths with spaces

#### 5. Symlink Warnings (Windows)

**Problem:** Warning about symlinks not being supported.

**Solutions:**
- **Option 1:** Enable Developer Mode in Windows Settings
- **Option 2:** Run Python as administrator
- **Option 3:** Ignore the warning (functionality not affected)

#### 6. Slow Processing

**Problem:** Transcription or translation takes too long.

**Solutions:**
- Use a smaller Whisper model
- Process shorter files
- Ensure you have sufficient CPU and RAM
- Check that models are loaded from disk (not downloading each time)

#### 7. Translation Quality Issues

**Problem:** Translations are not accurate.

**Solutions:**
- Ensure source text is in English
- Check that the correct target language is specified
- For better quality, consider using a larger Whisper model for transcription
- Review the source transcription for accuracy

### Getting Help

If you encounter issues not covered here:

1. Check that all dependencies are installed: `pip install -r requirements.txt`
2. Verify Python version: `python --version` (should be 3.8+)
3. Check that models are downloaded correctly
4. Review error messages for specific details
5. Ensure sufficient disk space and memory

## Notes

- **Model Downloads:** The first run of transcription will download the Whisper model automatically. The translation model must be downloaded separately using the `download-translation-model` command.
- **Model Reuse:** Models are stored locally in the `models` directory and will be reused on subsequent runs, making them faster.
- **Internet Required:** Internet connection is only needed for the initial model downloads. After that, the application works offline.
- **File Formats:** The application supports common video and audio formats. If your format isn't supported, convert it using FFmpeg first.
- **Batch Processing:** When processing folders, files are processed sequentially. Large batches may take considerable time.
- **Path Handling:** The application automatically normalizes paths, so you can use Windows, Linux, or macOS path formats interchangeably.
- **Language Support:** Currently supports English to French and Hindi translations. More languages can be added by modifying the language codes in the code.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
