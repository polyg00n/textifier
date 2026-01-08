import time
import sys

print("=== Quick Startup Test ===\n")
start = time.time()

try:
    print("Importing gui_main...")
    import gui_main
    elapsed = time.time() - start
    print(f"\nSUCCESS - Import took {elapsed:.2f} seconds")
except Exception as e:
    elapsed = time.time() - start
    print(f"\nFAILED after {elapsed:.2f}s: {e}")
