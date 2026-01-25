"""
Test script for multi-format translation support.
Creates sample files in all formats and verifies they can be parsed.
"""

import os
from pathlib import Path

print("=" * 60)
print("MULTI-FORMAT TRANSLATION VERIFICATION TEST")
print("=" * 60)

# Test 1: Import and check new methods exist
print("\n[Test 1] Checking new FormatHandler methods...")
try:
    from textifier_core import FormatHandler, TextifierCore
    
    # Check parsers
    assert hasattr(FormatHandler, 'parse_srt'), "parse_srt missing"
    assert hasattr(FormatHandler, 'parse_csv'), "parse_csv missing"
    assert hasattr(FormatHandler, 'parse_txt'), "parse_txt missing"
    print("✓ All parsers exist")
    
    # Check savers
    assert hasattr(FormatHandler, 'save_srt_from_data'), "save_srt_from_data missing"
    assert hasattr(FormatHandler, 'save_csv_from_data'), "save_csv_from_data missing"
    assert hasattr(FormatHandler, 'save_txt_from_data'), "save_txt_from_data missing"
    print("✓ All savers exist")
    
    # Check translate_file method
    assert hasattr(TextifierCore, 'translate_file'), "translate_file missing"
    print("✓ translate_file() method exists")
    
except Exception as e:
    print(f"✗ Failed: {e}")
    exit(1)

# Test 2: Create sample files
print("\n[Test 2] Creating sample files...")
test_dir = Path("test_translation_files")
test_dir.mkdir(exist_ok=True)

# Sample VTT
vtt_content = """WEBVTT

1
00:00:00.000 --> 00:00:05.000
Hello, this is a test

2
00:00:05.000 --> 00:00:10.000
Testing multi-format translation
"""

# Sample SRT
srt_content = """1
00:00:00,000 --> 00:00:05,000
Hello, this is a test

2
00:00:05,000 --> 00:00:10,000
Testing multi-format translation
"""

# Sample TXT
txt_content = """Hello, this is a test
Testing multi-format translation
"""

# Sample CSV
csv_content = """Start,End,Text
00:00:00.000,00:00:05.000,Hello, this is a test
00:00:05.000,00:00:10.000,Testing multi-format translation
"""

files = {
    'test.vtt': vtt_content,
    'test.srt': srt_content,
    'test.txt': txt_content,
    'test.csv': csv_content
}

for filename, content in files.items():
    filepath = test_dir / filename
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✓ Created: {filename}")

# Test 3: Parse each format
print("\n[Test 3] Testing parsers...")
try:
    # Parse VTT
    vtt_data = FormatHandler.parse_vtt(test_dir / 'test.vtt')
    assert len(vtt_data) == 2, f"Expected 2 VTT segments, got {len(vtt_data)}"
    print(f"✓ VTT parsed: {len(vtt_data)} segments")
    
    # Parse SRT
    srt_data = FormatHandler.parse_srt(test_dir / 'test.srt')
    assert len(srt_data) == 2, f"Expected 2 SRT segments, got {len(srt_data)}"
    print(f"✓ SRT parsed: {len(srt_data)} segments")
    
    # Parse CSV
    csv_data = FormatHandler.parse_csv(test_dir / 'test.csv')
    assert len(csv_data) == 2, f"Expected 2 CSV segments, got {len(csv_data)}"
    print(f"✓ CSV parsed: {len(csv_data)} segments")
    
    # Parse TXT
    txt_data = FormatHandler.parse_txt(test_dir / 'test.txt')
    assert len(txt_data) == 2, f"Expected 2 TXT lines, got {len(txt_data)}"
    print(f"✓ TXT parsed: {len(txt_data)} lines")
    
except Exception as e:
    print(f"✗ Parsing failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Test 4: Test savers
print("\n[Test 4] Testing savers...")
try:
    # Save VTT
    FormatHandler.save_vtt_from_data(vtt_data, test_dir / 'test_output.vtt')
    print("✓ VTT saver works")
    
    # Save SRT
    FormatHandler.save_srt_from_data(srt_data, test_dir / 'test_output.srt')
    print("✓ SRT saver works")
    
    # Save CSV
    FormatHandler.save_csv_from_data(csv_data, test_dir / 'test_output.csv')
    print("✓ CSV saver works")
    
    # Save TXT
    FormatHandler.save_txt_from_data(txt_data, test_dir / 'test_output.txt')
    print("✓ TXT saver works")
    
except Exception as e:
    print(f"✗ Saver failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Cleanup
print("\n[Cleanup] Removing test files...")
import shutil
shutil.rmtree(test_dir)
print("✓ Test directory cleaned up")

print("\n" + "=" * 60)
print("ALL TESTS PASSED ✓")
print("=" * 60)
print("\nMulti-format translation is ready!")
print("Supported formats: VTT, SRT, TXT, CSV")
print("\nNote: Actual translation requires mBART model to be downloaded.")
print("Use the GUI Settings tab to download the translation model.")
