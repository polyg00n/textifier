"""
VTT Processor CLI Tool
======================
A tool to convert .vtt transcript files into clean prose or tutorial-ready formats.

Usage:
    python vtt_processor.py <input_file.vtt> [options]

Arguments:
    input_file            Path to the source .vtt file.

Options:
    -o, --output          Path for the output file. (Defaults to input_name_format.ext)
    -f, --format          Output type: 'plain' (default), 'tutorial', or 'html'.
    -n, --chunk-size      Number of sentences per block (default: 3).
    --no-timestamps       Remove time hints from image placeholders in tutorial mode.

Examples:
    1. Basic text extraction:
       python vtt_processor.py transcript.vtt
       
    2. Create a tutorial layout with image placeholders every 5 sentences:
       python vtt_processor.py transcript.vtt -f tutorial -n 5
       
    3. Generate HTML snippets for a web page:
       python vtt_processor.py transcript.vtt -f html -o tutorial.html
"""

import re
import argparse
import sys
from pathlib import Path

class VTTProcessor:
    def __init__(self, filepath):
        self.filepath = Path(filepath)
        self.blocks = []  # Will store dicts: {'start': str, 'end': str, 'text': str}
        self.full_text = ""
        
    def parse(self):
        """
        Parses the VTT file into structured blocks and a full text stream.
        """
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except FileNotFoundError:
            print(f"Error: File not found: {self.filepath}")
            sys.exit(1)
        except UnicodeDecodeError:
             # Fallback for other encodings if utf-8 fails
            with open(self.filepath, 'r', encoding='latin-1') as f:
                content = f.read()

        # Split content into blocks based on double newlines or VTT format specifics
        lines = content.splitlines()
        
        # Regex for VTT timestamp: 00:00:00.000 --> 00:00:05.000
        time_pattern = re.compile(r'(\d{2}:\d{2}:\d{2}\.\d{3})\s-->\s(\d{2}:\d{2}:\d{2}\.\d{3})')
        
        current_block = {'text': []}
        
        for line in lines:
            line = line.strip()
            
            if not line:
                continue
            
            if line == "WEBVTT":
                continue
                
            # Check if it's a simple number (sequence ID)
            if line.isdigit():
                continue
                
            # Check if it's a timestamp
            time_match = time_pattern.search(line)
            if time_match:
                # Save previous block if it has text
                if 'start' in current_block and current_block['text']:
                    self._add_block(current_block)
                    current_block = {'text': []}
                
                current_block['start'] = time_match.group(1)
                current_block['end'] = time_match.group(2)
                continue
            
            # If we are here, it's text content
            current_block['text'].append(line)

        # Add the final block
        if 'start' in current_block and current_block['text']:
            self._add_block(current_block)
            
        # Create a clean full text version
        self.full_text = " ".join([b['text'] for b in self.blocks])

    def _add_block(self, block_data):
        """Helper to finalize a block before adding to list."""
        clean_text = " ".join(block_data['text'])
        # Basic cleanup of HTML-like tags if present in VTT (e.g., <b>)
        clean_text = re.sub(r'<[^>]+>', '', clean_text)
        self.blocks.append({
            'start': block_data.get('start'),
            'end': block_data.get('end'),
            'text': clean_text
        })

    def get_plain_text(self):
        """Returns the text as a single continuous string."""
        return self.full_text

    def get_tutorial_format(self, chunk_size=3, include_timestamps=True):
        """
        Returns text broken into chunks with placeholders for images.
        """
        # Split full text into sentences
        sentences = re.split(r'(?<=[.!?])\s+', self.full_text)
        
        output_lines = []
        current_chunk = []
        
        for i, sentence in enumerate(sentences):
            current_chunk.append(sentence)
            
            is_last = (i + 1) == len(sentences)
            is_chunk_end = (i + 1) % chunk_size == 0
            
            if is_chunk_end or is_last:
                text_block = " ".join(current_chunk)
                output_lines.append(text_block)
                output_lines.append("") # Empty line
                
                if include_timestamps:
                    output_lines.append(f"[IMAGE PLACEHOLDER - Approx Time: {self._find_time_for_text(sentence)}]")
                else:
                    output_lines.append("[IMAGE PLACEHOLDER]")
                
                output_lines.append("-" * 40)
                output_lines.append("")
                current_chunk = []
                
        return "\n".join(output_lines)

    def get_html_format(self, chunk_size=3):
        """Generates simple HTML markup for the tutorial."""
        sentences = re.split(r'(?<=[.!?])\s+', self.full_text)
        html = ["<article class='tutorial'>"]
        
        current_chunk = []
        for i, sentence in enumerate(sentences):
            current_chunk.append(sentence)
            
            if (i + 1) % chunk_size == 0 or (i + 1) == len(sentences):
                text_block = " ".join(current_chunk)
                html.append(f"  <p>{text_block}</p>")
                html.append("  <!-- Insert Image Here -->")
                html.append("  <figure class='tutorial-image'>")
                html.append(f"    <img src='placeholder.jpg' alt='Tutorial step {(i+1)//max(1, chunk_size)}'>")
                html.append("  </figure>")
                current_chunk = []
        
        html.append("</article>")
        return "\n".join(html)

    def _find_time_for_text(self, snippet):
        """Attempts to find the timestamp for a specific snippet of text."""
        snippet_start = snippet[:20] # Take first few chars
        for block in self.blocks:
            if snippet_start in block['text']:
                return block['start']
        return "N/A"

def main():
    parser = argparse.ArgumentParser(description="Convert VTT transcripts to readable text or tutorial formats.")
    
    # Arguments
    parser.add_argument("input_file", help="Path to the input .vtt file")
    parser.add_argument("-o", "--output", help="Path to save the output file")
    parser.add_argument("-f", "--format", choices=['plain', 'tutorial', 'html'], default='plain', 
                        help="Output format: 'plain', 'tutorial', or 'html'")
    parser.add_argument("-n", "--chunk-size", type=int, default=3, 
                        help="Sentences per block for tutorial/html modes")
    parser.add_argument("--no-timestamps", action="store_true", 
                        help="Remove timestamps from tutorial placeholders")

    args = parser.parse_args()

    # 1. Setup paths
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"Error: Input file '{input_path}' does not exist.")
        return

    # Determine output filename if not provided
    if args.output:
        output_path = Path(args.output)
    else:
        new_stem = f"{input_path.stem}_{args.format}"
        ext = ".html" if args.format == 'html' else ".txt"
        output_path = input_path.with_name(f"{new_stem}{ext}")

    # 2. Process
    processor = VTTProcessor(input_path)
    processor.parse()

    # 3. Generate Content
    if args.format == 'plain':
        content = processor.get_plain_text()
    elif args.format == 'tutorial':
        content = processor.get_tutorial_format(
            chunk_size=args.chunk_size, 
            include_timestamps=not args.no_timestamps
        )
    elif args.format == 'html':
        content = processor.get_html_format(chunk_size=args.chunk_size)

    # 4. Save
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Success! Processed content saved to: {output_path}")
    except IOError as e:
        print(f"Error writing to file: {e}")

if __name__ == "__main__":
    main()