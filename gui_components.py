"""
Textifier GUI Components - Plain Tkinter Version
"""
import tkinter as tk
from tkinter import ttk
import os
import subprocess
import sys


class SubtitleRow(ttk.Frame):
    """A single row in the subtitle editor."""
    
    def __init__(self, master, index, start, end, text, **kwargs):
        super().__init__(master, **kwargs)
        self.index = index
        
        self.columnconfigure(4, weight=1)
        
        ttk.Label(self, text=str(index), width=4).grid(row=0, column=0, padx=2, pady=2)
        
        self.ent_start = ttk.Entry(self, width=15)
        self.ent_start.insert(0, start)
        self.ent_start.grid(row=0, column=1, padx=2, pady=2)
        
        ttk.Label(self, text="-->", width=4).grid(row=0, column=2, padx=2, pady=2)
        
        self.ent_end = ttk.Entry(self, width=15)
        self.ent_end.insert(0, end)
        self.ent_end.grid(row=0, column=3, padx=2, pady=2)
        
        self.ent_text = tk.Text(self, width=50, height=1, wrap="word", font=("Segoe UI", 10),
                                bg="#3c3f41", fg="#ffffff", insertbackground="#ffffff",
                                highlightthickness=1, highlightbackground="#3c3f41",
                                highlightcolor="#3d6a99")
        self.ent_text.insert("1.0", text)
        self.ent_text.grid(row=0, column=4, sticky="ew", padx=2, pady=2)
        
        # Bind events to update height dynamically
        self.ent_text.bind("<<Modified>>", self._on_text_modified)
        self._adjust_height()

    def _on_text_modified(self, event=None):
        if self.ent_text.edit_modified():
            self._adjust_height()
            self.ent_text.edit_modified(False)

    def _adjust_height(self, event=None):
        # Calculate number of lines needed
        text_content = self.ent_text.get("1.0", "end-1c")
        # For simplicity, count newlines + 1
        lines = text_content.count('\n') + 1
        # Set max height to prevent one row taking over the screen
        new_height = min(max(lines, 1), 5) 
        self.ent_text.configure(height=new_height)

    def get_data(self):
        return {
            'start': self.ent_start.get(),
            'end': self.ent_end.get(),
            'text': self.ent_text.get("1.0", "end-1c").strip()
        }


class SubtitleEditorFrame(ttk.Frame):
    """Scrollable frame for subtitle editing."""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.rows = []
        
        # Create canvas with scrollbar
        self.canvas = tk.Canvas(self, highlightthickness=0, bg="#2b2b2b")
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Ensure scrollable_frame expands to the width of the canvas
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        # Mouse wheel scrolling
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_canvas_configure(self, event):
        # Update the width of the scrollable_frame to match the canvas
        self.canvas.itemconfigure(self.canvas_window, width=event.width)
        
    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
    def load_cues(self, cues):
        # Clear existing
        for row in self.rows:
            row.destroy()
        self.rows = []
        
        for i, cue in enumerate(cues):
            row = SubtitleRow(self.scrollable_frame, i+1, cue['start'], cue['end'], cue['text'])
            row.pack(fill="x", padx=5, pady=1)
            self.rows.append(row)
            
    def get_cues(self):
        return [row.get_data() for row in self.rows]


class VideoControlFrame(ttk.LabelFrame):
    """
    Frame for media playback control.
    
    NOTE ON IMPLEMENTATION (Feedback Item 6):
    The 'Play in System Player' approach is used because implementing a full Video UI 
    within Tkinter (e.g., via OpenCV or libVLC) is complex, resource-heavy, and often 
    results in poor performance or platform-specific issues (like DirectShow vs FFmpeg). 
    By using the system's default player, we ensure the best possible playback 
    experience and broadest format support with zero overhead.
    """
    
    def __init__(self, master, **kwargs):
        super().__init__(master, text="Video Preview", **kwargs)
        self.video_path = None
        
        self.lbl_title = ttk.Label(self, text="No Video Selected", font=("Arial", 12, "bold"))
        self.lbl_title.pack(pady=20, padx=10)
        
        self.btn_open = ttk.Button(self, text="Play in System Player", command=self.open_video, state="disabled")
        self.btn_open.pack(pady=10)
        
        self.lbl_info = ttk.Label(self, text="Opens in your default media player", foreground="gray")
        self.lbl_info.pack(pady=5)
        
    def set_video(self, path):
        self.video_path = path
        if path:
            self.lbl_title.configure(text=os.path.basename(path))
            self.btn_open.configure(state="normal")
        else:
            self.lbl_title.configure(text="No Video Selected")
            self.btn_open.configure(state="disabled")
            
    def open_video(self):
        if self.video_path and os.path.exists(self.video_path):
            if sys.platform == 'win32':
                os.startfile(self.video_path)
            elif sys.platform == 'darwin':
                subprocess.call(['open', self.video_path])
            else:
                subprocess.call(['xdg-open', self.video_path])
