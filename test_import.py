import time
import sys

print("Test 1: Importing textifier_core...")
start = time.time()

try:
    import textifier_core
    elapsed = time.time() - start
    print(f"SUCCESS - took {elapsed:.2f} seconds")
except Exception as e:
    elapsed = time.time() - start
    print(f"FAILED after {elapsed:.2f} seconds: {e}")
