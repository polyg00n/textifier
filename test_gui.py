import sys
import traceback

print("=== Starting GUI Test ===")
print(f"Python: {sys.version}")
print(f"Path: {sys.executable}")

try:
    print("\n1. Importing gui_main...")
    import gui_main
    
    print("2. Creating app instance...")
    app = gui_main.TextifierApp()
    
    print("3. Starting mainloop...")
    app.mainloop()
    
except Exception as e:
    print(f"\n!!! ERROR !!!")
    print(f"Type: {type(e).__name__}")
    print(f"Message: {e}")
    print("\nFull traceback:")
    traceback.print_exc()
