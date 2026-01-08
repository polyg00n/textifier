
import time
print("Starting import test...")

print("Step 1: Importing os, sys...")
import os, sys
print("Done.")

print("Step 2: Importing torch...")
import torch
print(f"Done. Torch version: {torch.__version__}, CUDA: {torch.cuda.is_available()}")

print("Step 3: Importing whisper...")
start = time.time()
import whisper
end = time.time()
print(f"Done in {end - start:.2f} seconds.")

print("Step 4: Checking whisper version...")
print(f"Whisper version: {whisper.__version__ if hasattr(whisper, '__version__') else 'unknown'}")

print("Test complete.")
