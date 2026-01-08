Each item below:

Edit the status to keep the user informed about what has been worked on. The user will also edit the status to inform the system.

Add information to tne Notes section to provide context for future work. Always add, never remove from Notes.





1.Status: Pending



When he app starts up it automatically initializes Whisper large, this should not happen because I might want to use another model instead.

Notes:



2\. Status: Pending



In the Subtitle Editor:

The text boxes truncate the text of that segment, we should be able to view the whole block of text, expand the text box dynamically to 

Use word wrap.

Notes:





3\. 

In the Subtitle Editor:

The large white box is just wasted space, remove it to provide more space for the text editing boxes.

Notes:





4.Status: Pending



The app works with my windows environment but not the venv. The venv is broken, delete it and recreate it.

Notes:



5.Status: Pending



Add support for choosing between CPU and GPU for the workload. This is so that if I use the app on another computer and the GPU drivers or cuda setup aren't the same, for example the computer has a 2080Ti or another video card, then I can still operate the app. 

Notes:



6\. Status: Pending



Why can't we have video playback in the Subtitle editor interface? Add the reason and potential solutions in Notes below. Don't code anything yet.

Notes:





7\. Status: Pending

In the model manager, for each downloaded model, add a button that will delete the model.

Notes:



8\. Status: Pending

Create a WhisperSettings.md markdown file detailing what each setting in the Advanced Whisper tab does

Notes:



9\. Status: Pending

The Advanced Whisper tab should include the options that the Batch Processor tab does, like choosing the video or folder, etc. It seems like there are more Whisper options that we aren't seeing in this tab, for examply choosing the output format.  This should be a comprehensive tool.

Notes:







10\. Status: Pending

What options exist to improve the speed of the tool? What if we strip the audio to an mp3 file using ffmpeg before sending it to the Whisper process?

The audio file shoud have the same name as the souve video file and save to the same place as the vtt file.

Notes:

Recommended FFmpeg Command

To get the best results for Whisper, you should extract the audio and downsample it to exactly what the model expects:



Bash

ffmpeg -i input\_video.mp4 -ar 16000 -ac 1 -c:a pcm\_s16le output\_audio.wav

What this command does:

-ar 16000: Sets the audio rate to 16kHz (Whisper's native requirement).

-ac 1: Converts it to mono (Whisper doesn't need stereo).

-c:a pcm\_s16le: Converts it to a raw 16-bit PCM format, which is extremely fast for Python libraries to read.









11\. Status: Pending

Include these model options

Whisper Large-v3-Turbo: A newer, "pruned" version released by OpenAI that has fewer layers but maintains very similar accuracy. It is roughly 2x faster than the full Large-v3.



Distil-Whisper: A distilled version of the model. It is significantly smaller and faster (up to 6x faster) while staying within 1% Word Error Rate (WER) of the original for many languages.



Notes:



12\. Status: Pending

Precision (FP16/INT8): Ensure you are running in half-precision (fp16=True). This halves memory usage and doubles speed on most modern GPUs.



Nots:





13\. Status: Pending

When I load up a video with the vtt file into the subtitle editor it seems to delete the vtt file, assuming that the  edited one will be saved. This should not happen, the original vtt file should be untouched, and the new saved vtt file should be saved with a name indicating the iteration, so name\_edit01.vtt

Notes:





14\. Status: Pending

Add a dropdown selection for the output type. vtt should be the default.

Nots:



15\. Status: Pending

&nbsp;Performance: Switch to faster-whisper

Your current implementation uses the standard openai-whisper library. While official, it is not optimized for production speed.



Change: Replace import whisper with faster-whisper (CTranslate2 backend).



Impact: This typically yields a 4x-10x speedup and significantly lowers memory usage (VRAM), allowing you to run "Large-v3" on smaller cards.



Implementation: faster-whisper natively supports 8-bit quantization (int8), which maintains near-identical accuracy while halving the model size in memory.



16\. Status: Pending
 Architecture: Decouple Monolithic Class

The TextifierCore class currently handles downloading, transcribing, translating, and file parsing. This violates the "Single Responsibility Principle."



Change: Split the class into smaller, specialized classes:



ModelManager: Handles checking, downloading, and verifying model hashes.



Transcriber: Wraps the Whisper engine.



Translator: Wraps the mBART engine.



FormatHandler: Handles VTT/SRT parsing and saving.



Benefit: This makes it easier to swap out the transcription engine (e.g., to a cloud API or a different local model) without breaking the translation or file saving logic.



17\.  Status Pending

Audio Pre-processing (The "FFmpeg Pipe")

Currently, transcribe\_media passes the file path directly to Whisper. For large video files, this forces Whisper to internally decode the video, which is slow and memory-intensive.



Change: Use ffmpeg-python or subprocess to extract audio to a memory buffer (16kHz mono) before passing it to the model.



Code Concept:

import subprocess

import numpy as np



def load\_audio(file\_path):

&nbsp;   # Extract audio to stdout (pipe) as raw 32-bit float

&nbsp;   cmd = \[

&nbsp;       "ffmpeg", "-i", file\_path,

&nbsp;       "-ar", "16000", "-ac", "1", "-f", "s16le", "-"

&nbsp;   ]

&nbsp;   process = subprocess.run(cmd, capture\_output=True)

&nbsp;   # Convert raw bytes to numpy array

&nbsp;   return np.frombuffer(process.stdout, np.int16).flatten().astype(np.float32) / 32768.0



Benefit: Massive speedup on file loading and reduced RAM usage for large video files.



18\. Status: Pending

Robustness: Add Cancellation \& Progress Support

Your transcribe\_media function is blocking. If the user clicks "Cancel" in your UI, the Python script will currently continue until finished.



Change: Since standard whisper blocks, you cannot easily cancel it. faster-whisper returns a generator of segments.



Implementation: Iterate through the generator and check a self.stop\_requested flag after every segment. This allows you to "break" the loop instantly.

\# Logic with faster-whisper

segments, info = model.transcribe(audio)

for segment in segments:

&nbsp;   if self.stop\_requested:

&nbsp;        break

&nbsp;   # Process segment...



