# Textifier

Textifier is a Python application that provides two main functionalities:
1. Transcribe video/audio files to VTT format with timestamps using OpenAI's Whisper
2. Translate VTT files from English to multiple languages while preserving timestamps using mBART

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
git clone https://github.com/yourusername/textifier.git
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

## First Run Setup

On the first run, the application will:
1. Create a `models` directory
2. Download and save the Whisper model for transcription
3. Download and save the mBART model for translation

This initial setup might take some time depending on your internet connection, but subsequent runs will be faster as the models are stored locally.

## Usage

### Transcribing Media Files

To transcribe a single video or audio file to VTT format:
```bash
python textifier.py transcribe path/to/your/video.mp4
```

To transcribe all video/audio files in a folder:
```bash
python textifier.py transcribe path/to/folder -f
```

Supported input formats:
- Video: .mp4, .avi, .mkv, .mov, .wmv
- Audio: .mp3, .wav, .m4a, .aac

The output VTT file will be saved in the same directory as the input file with the same name but .vtt extension.

### Translating VTT Files

To translate a single VTT file from English to French (default):
```bash
python textifier.py translate path/to/your/subtitles.vtt
```

To translate a single VTT file from English to Hindi:
```bash
python textifier.py translate path/to/your/subtitles.vtt -l hi
```

To translate all VTT files in a folder to French:
```bash
python textifier.py translate path/to/folder -f
```

To translate all VTT files in a folder to Hindi:
```bash
python textifier.py translate path/to/folder -f -l hi
```

The translated VTT file will be saved in the same directory with the language code appended to the filename (e.g., "_fr" for French, "_hi" for Hindi).

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

The application generates VTT files in the following format:
```
WEBVTT

1
00:00:00.000 --> 00:00:11.080
Transcribed or translated text here

2
00:00:11.080 --> 00:00:16.680
Next segment of text
```

## Notes

- The transcription model can be changed by modifying the `whisper.load_model()` parameter in the code. Available options are: "tiny", "base", "small", "medium", "large"
- Models are stored in the `models` directory and will be reused on subsequent runs
- The first run will download the necessary models, which might take some time depending on your internet connection
- For Windows users: If you see a symlink warning, you can either:
  - Enable Developer Mode in Windows
  - Run Python as administrator
  - Ignore the warning (it won't affect functionality)

## License

This project is licensed under the MIT License - see the LICENSE file for details. 