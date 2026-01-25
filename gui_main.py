"""
Textifier GUI - Plain Tkinter Version
Fast startup, no external GUI dependencies.
"""
print("=" * 50)
print("TEXTIFIER - Starting up...")
print("=" * 50)

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import queue
import os
from pathlib import Path

print("Loading core modules...")
from textifier_core import TextifierCore, _WHISPER_MODELS
from gui_components import SubtitleEditorFrame, VideoControlFrame

print("Initializing interface...")

# Whisper supported languages (most common ones for dropdown)
WHISPER_LANGUAGES = [
    ("Auto-detect", None),
    ("English", "en"), ("Spanish", "es"), ("French", "fr"), ("German", "de"),
    ("Italian", "it"), ("Portuguese", "pt"), ("Dutch", "nl"), ("Russian", "ru"),
    ("Chinese", "zh"), ("Japanese", "ja"), ("Korean", "ko"),
    ("Arabic", "ar"), ("Hindi", "hi"), ("Turkish", "tr"),
    ("Polish", "pl"), ("Ukrainian", "uk"), ("Vietnamese", "vi"),
    ("Thai", "th"), ("Swedish", "sv"), ("Indonesian", "id"),
    ("Hebrew", "he"), ("Greek", "el"), ("Czech", "cs"),
    ("Finnish", "fi"), ("Romanian", "ro"), ("Danish", "da"),
    ("Hungarian", "hu"), ("Tamil", "ta"), ("Norwegian", "no"),
    ("Gujarati", "gu"), ("Marathi", "mr"), ("Telugu", "te"),
    ("Bengali", "bn"), ("Urdu", "ur"), ("Punjabi", "pa"),
]

# mBART-50 supported languages for translation
MBART_LANGUAGES = [
    ("English", "en"), ("French", "fr"), ("Spanish", "es"), ("German", "de"),
    ("Italian", "it"), ("Portuguese", "pt"), ("Dutch", "nl"), ("Russian", "ru"),
    ("Chinese", "zh"), ("Japanese", "ja"), ("Korean", "ko"),
    ("Arabic", "ar"), ("Hindi", "hi"), ("Turkish", "tr"),
    ("Polish", "pl"), ("Ukrainian", "uk"), ("Vietnamese", "vi"),
    ("Thai", "th"), ("Swedish", "sv"), ("Indonesian", "id"),
    ("Hebrew", "he"), ("Czech", "cs"), ("Finnish", "fi"),
    ("Romanian", "ro"), ("Gujarati", "gu"), ("Marathi", "mr"),
    ("Tamil", "ta"), ("Telugu", "te"), ("Bengali", "bn"),
    ("Urdu", "ur"), ("Persian", "fa"), ("Swahili", "sw"),
    ("Tagalog", "tl"), ("Afrikaans", "af"), ("Azerbaijani", "az"),
    ("Burmese", "my"), ("Croatian", "hr"), ("Estonian", "et"),
    ("Georgian", "ka"), ("Kazakh", "kk"), ("Khmer", "km"),
    ("Latvian", "lv"), ("Lithuanian", "lt"), ("Macedonian", "mk"),
    ("Malayalam", "ml"), ("Mongolian", "mn"), ("Nepali", "ne"),
    ("Pashto", "ps"), ("Sinhala", "si"), ("Xhosa", "xh"),
]


class TextifierApp(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Textifier")
        self.geometry("1000x700")
        self.configure(bg="#2b2b2b")
        
        # Apply a dark theme using ttk styles
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self._configure_dark_theme()
        
        # Initialize backend
        self.msg_queue = queue.Queue()
        self.core = TextifierCore(status_callback=self.queue_status)
        
        # Create main notebook (tabs)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create tabs
        self.tab_batch = ttk.Frame(self.notebook)
        self.tab_whisper = ttk.Frame(self.notebook)
        self.tab_editor = ttk.Frame(self.notebook)
        self.tab_settings = ttk.Frame(self.notebook)
        
        self.notebook.add(self.tab_batch, text="Batch Processor")
        self.notebook.add(self.tab_whisper, text="Advanced Whisper")
        self.notebook.add(self.tab_editor, text="Subtitle Editor")
        self.notebook.add(self.tab_settings, text="Settings")
        
        self.setup_batch_tab()
        self.setup_whisper_tab()
        self.setup_editor_tab()
        self.setup_settings_tab()
        
        # Start queue processing
        self.after(100, self.process_queue)
        
        # Start queue processing
        self.after(100, self.process_queue)
        
    def _configure_dark_theme(self):
        """Configure a dark color scheme for ttk widgets."""
        bg = "#2b2b2b"
        fg = "#ffffff"
        select_bg = "#3d6a99"
        
        self.style.configure(".", background=bg, foreground=fg, fieldbackground=bg)
        self.style.configure("TFrame", background=bg)
        self.style.configure("TLabel", background=bg, foreground=fg)
        self.style.configure("TButton", background="#3c3f41", foreground=fg)
        self.style.configure("TEntry", fieldbackground="#3c3f41", foreground=fg)
        self.style.configure("TNotebook", background=bg)
        self.style.configure("TNotebook.Tab", background="#3c3f41", foreground=fg, padding=[10, 5])
        self.style.map("TNotebook.Tab", background=[("selected", select_bg)])
        self.style.configure("TRadiobutton", background=bg, foreground=fg)
        self.style.configure("TLabelframe", background=bg, foreground=fg)
        self.style.configure("TLabelframe.Label", background=bg, foreground=fg)
        
    # Startup backend initialization removed to prevent blocking/slow start.
    # Models are now loaded lazily when needed.
        
    def queue_status(self, message):
        self.msg_queue.put(message)
        
    def process_queue(self):
        try:
            while True:
                msg = self.msg_queue.get_nowait()
                self.log_message(msg)
        except queue.Empty:
            pass
        finally:
            self.after(100, self.process_queue)
            
    def log_message(self, message):
        if hasattr(self, 'txt_log'):
            self.txt_log.configure(state="normal")
            self.txt_log.insert("end", message + "\n")
            self.txt_log.see("end")
            self.txt_log.configure(state="disabled")
        print(f"[LOG] {message}")

    # ================= BATCH TAB =================
    def setup_batch_tab(self):
        # Input Frame
        frm_input = ttk.LabelFrame(self.tab_batch, text="Input")
        frm_input.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(frm_input, text="Source:").grid(row=0, column=0, padx=5, pady=5)
        self.ent_input = ttk.Entry(frm_input, width=60)
        self.ent_input.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(frm_input, text="Browse File", command=self.browse_file).grid(row=0, column=2, padx=2)
        ttk.Button(frm_input, text="Browse Folder", command=self.browse_folder).grid(row=0, column=3, padx=2)
        
        # Output Location
        frm_output = ttk.LabelFrame(self.tab_batch, text="Output Location")
        frm_output.pack(fill="x", padx=10, pady=5)
        
        self.var_output = tk.StringVar(value="source")
        ttk.Radiobutton(frm_output, text="Same as Source", variable=self.var_output, value="source").grid(row=0, column=0, padx=10, pady=5)
        ttk.Radiobutton(frm_output, text="Custom Folder:", variable=self.var_output, value="custom").grid(row=0, column=1, padx=5, pady=5)
        self.ent_custom_out = ttk.Entry(frm_output, width=40)
        self.ent_custom_out.grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(frm_output, text="...", width=3, command=self.browse_custom_out).grid(row=0, column=3, padx=2)
        
        # TRANSCRIBE Section (outputs English VTT)
        frm_transcribe = ttk.LabelFrame(self.tab_batch, text="Step 1: Transcribe (Video/Audio → Text)")
        frm_transcribe.pack(fill="x", padx=10, pady=5)
        
        # Row 0: Model selection
        ttk.Label(frm_transcribe, text="Whisper Model:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.var_model = tk.StringVar(value="large-v3")
        self.opt_model = ttk.Combobox(frm_transcribe, textvariable=self.var_model, 
                                       values=sorted(list(_WHISPER_MODELS.keys())), 
                                       width=18, state="readonly")
        self.opt_model.grid(row=0, column=1, padx=5, sticky="w")
        ttk.Label(frm_transcribe, text="(larger = more accurate, slower)", foreground="gray").grid(row=0, column=2, padx=5, sticky="w")
        
        # Row 1: Source language selection
        ttk.Label(frm_transcribe, text="Audio Language:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.var_transcribe_lang = tk.StringVar(value="Auto-detect")
        lang_display = [f"{name}" for name, _ in WHISPER_LANGUAGES]
        self.opt_transcribe_lang = ttk.Combobox(frm_transcribe, textvariable=self.var_transcribe_lang,
                                                values=lang_display, width=18, state="readonly")
        self.opt_transcribe_lang.grid(row=1, column=1, padx=5, sticky="w")
        ttk.Label(frm_transcribe, text="(or let Whisper auto-detect)", foreground="gray").grid(row=1, column=2, padx=5, sticky="w")
        
        # Row 2: Action button
        ttk.Button(frm_transcribe, text="Transcribe to Text", command=self.start_transcribe).grid(row=2, column=0, columnspan=3, padx=20, pady=10)
        
        # TRANSLATE Section (converts VTT to other languages)
        frm_translate = ttk.LabelFrame(self.tab_batch, text="Step 2: Translate (VTT → Other Language)")
        frm_translate.pack(fill="x", padx=10, pady=5)
        
        # Row 0: Source language
        ttk.Label(frm_translate, text="Source Language:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.var_translate_source = tk.StringVar(value="English")
        source_langs = [name for name, _ in MBART_LANGUAGES]
        self.opt_translate_source = ttk.Combobox(frm_translate, textvariable=self.var_translate_source,
                                                 values=source_langs, width=18, state="readonly")
        self.opt_translate_source.grid(row=0, column=1, padx=5, sticky="w")
        
        # Row 1: Target language
        ttk.Label(frm_translate, text="Target Language:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.var_translate_target = tk.StringVar(value="French")
        self.opt_translate_target = ttk.Combobox(frm_translate, textvariable=self.var_translate_target,
                                                 values=source_langs, width=18, state="readonly")
        self.opt_translate_target.grid(row=1, column=1, padx=5, sticky="w")
        
        # Row 2: Action button
        ttk.Label(frm_translate, text="(supports VTT, SRT, TXT, CSV files)", foreground="gray").grid(row=2, column=0, padx=5, sticky="w")
        ttk.Button(frm_translate, text="Translate File", command=self.start_translate).grid(row=2, column=1, padx=5, pady=5, sticky="w")
        
        # Log
        ttk.Label(self.tab_batch, text="Activity Log:").pack(anchor="w", padx=10)
        self.txt_log = tk.Text(self.tab_batch, height=12, bg="#1e1e1e", fg="#00ff00", 
                               insertbackground="white", state="disabled")
        self.txt_log.pack(fill="both", expand=True, padx=10, pady=5)

    def browse_file(self):
        f = filedialog.askopenfilename()
        if f:
            self.ent_input.delete(0, "end")
            self.ent_input.insert(0, f)
            
    def browse_folder(self):
        f = filedialog.askdirectory()
        if f:
            self.ent_input.delete(0, "end")
            self.ent_input.insert(0, f)
            
    def browse_custom_out(self):
        f = filedialog.askdirectory()
        if f:
            self.ent_custom_out.delete(0, "end")
            self.ent_custom_out.insert(0, f)

    def get_output_dir(self):
        if self.var_output.get() == "custom":
            return self.ent_custom_out.get()
        return None

    def start_transcribe(self):
        input_path = self.ent_input.get()
        if not input_path:
            messagebox.showwarning("Warning", "Please select an input file or folder.")
            return
        
        # Check if file/folder exists
        if not os.path.exists(input_path):
            messagebox.showerror("Error", f"Path does not exist: {input_path}")
            return
        
        model_name = self.var_model.get()
        self.queue_status(f"Starting transcription with model: {model_name}")
        
        # If model changed, update the core's model name (will load on demand)
        if self.core.whisper_model_name != model_name:
            self.queue_status(f"Switching model from {self.core.whisper_model_name} to {model_name}...")
            self.core.whisper_model_name = model_name
            self.core.whisper_model = None  # Force reload on next use
        
        # Get language selection
        lang_display = self.var_transcribe_lang.get()
        # Find the language code from the display name
        language_code = None
        for name, code in WHISPER_LANGUAGES:
            if name == lang_display:
                language_code = code
                break
        
        if language_code:
            self.queue_status(f"Language set to: {lang_display}")
        else:
            self.queue_status("Using auto-detect for language")
        
        output_dir = self.get_output_dir()
        threading.Thread(target=self._run_transcribe, args=(input_path, output_dir, language_code), daemon=True).start()
        
    def _run_transcribe(self, input_path, output_dir, language=None, **kwargs):
        try:
            # Add language to kwargs if specified
            if language is not None:
                kwargs['language'] = language
            
            if os.path.isdir(input_path):
                files = [f for f in Path(input_path).glob('*') if f.suffix.lower() in {'.mp4', '.avi', '.mkv', '.mp3', '.wav', '.m4a', '.aac'}]
                if not files:
                    self.queue_status(f"No media files found in {input_path}")
                    return
                self.queue_status(f"Found {len(files)} media files to transcribe")
                for i, f in enumerate(files, 1):
                    self.queue_status(f"Processing {i}/{len(files)}: {f.name}")
                    result = self.core.transcribe_media(str(f), output_dir, **kwargs)
                    if result:
                        self.queue_status(f"Created: {', '.join([Path(p).name for p in result])}")
            else:
                self.queue_status(f"Processing: {os.path.basename(input_path)}")
                result = self.core.transcribe_media(input_path, output_dir, **kwargs)
                if result:
                    self.queue_status(f"Created: {', '.join([Path(p).name for p in result])}")
            self.queue_status("Transcription Finished!")
        except Exception as e:
            self.queue_status(f"Error during transcription: {e}")

    def start_translate(self):
        input_path = self.ent_input.get()
        if not input_path:
            messagebox.showwarning("Warning", "Please select an input file or folder.")
            return
        
        # Get source and target language selections
        source_display = self.var_translate_source.get()
        target_display = self.var_translate_target.get()
        
        # Find language codes
        source_code = None
        target_code = None
        for name, code in MBART_LANGUAGES:
            if name == source_display:
                source_code = code
            if name == target_display:
                target_code = code
        
        if not source_code or not target_code:
            messagebox.showerror("Error", "Invalid language selection")
            return
        
        self.queue_status(f"Translating from {source_display} to {target_display}...")
        output_dir = self.get_output_dir()
        threading.Thread(target=self._run_translate, args=(input_path, source_code, target_code, output_dir), daemon=True).start()
        
    def _run_translate(self, input_path, source_lang, target_lang, output_dir):
        try:
            if os.path.isdir(input_path):
                # Support all translation formats
                files = []
                for ext in ['*.vtt', '*.srt', '*.txt', '*.csv']:
                    files.extend(Path(input_path).glob(ext))
                
                if not files:
                    self.queue_status(f"No translatable files found in {input_path}")
                    return
                
                self.queue_status(f"Found {len(files)} files to translate")
                for f in files:
                    self.queue_status(f"Translating: {f.name}")
                    self.core.translate_file(str(f), source_lang=source_lang, target_lang=target_lang, output_dir=output_dir)
            else:
                self.core.translate_file(input_path, source_lang=source_lang, target_lang=target_lang, output_dir=output_dir)
            self.queue_status("Batch Translation Finished.")
        except Exception as e:
            self.queue_status(f"Error: {e}")

    # ================= WHISPER ADVANCED TAB =================
    def setup_whisper_tab(self):
        # Create a canvas with scrollbar for the advanced options
        canvas = tk.Canvas(self.tab_whisper, bg="#2b2b2b",  highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.tab_whisper, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Mouse wheel support
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        
        # --- Variables ---
        self.adv_task = tk.StringVar(value="transcribe")
        self.adv_language = tk.StringVar(value="Auto-detect")
        self.adv_temp = tk.DoubleVar(value=0.0)
        self.adv_best_of = tk.IntVar(value=5)
        self.adv_beam_size = tk.IntVar(value=5)
        self.adv_patience = tk.DoubleVar(value=1.0)
        self.adv_fp16 = tk.BooleanVar(value=True)
        self.adv_condition_on_prev = tk.BooleanVar(value=True)
        self.adv_init_prompt = tk.StringVar(value="")
        self.adv_prepend_punctuations = tk.StringVar(value="\"\'“¿([{-")
        self.adv_append_punctuations = tk.StringVar(value="\"\'”.。,，!！?？:：)]}、")
        self.adv_no_speech_threshold = tk.DoubleVar(value=0.6)
        self.adv_log_prob_threshold = tk.DoubleVar(value=-1.0)
        self.adv_compression_ratio_threshold = tk.DoubleVar(value=2.4)
        self.adv_device = tk.StringVar(value="auto")
        self.adv_output_format = tk.StringVar(value="vtt")
        
        # --- Shared Input Section (Sync with Batch Tab) ---
        lbl_input = ttk.LabelFrame(scrollable_frame, text="Input Selection (Shared with Batch Tab)")
        lbl_input.pack(fill="x", padx=10, pady=5)
        
        # Note: self.ent_input is already defined in Batch tab, we just show it here if we want or just add buttons
        # For better UX, let's just add the browse buttons that modify the main ent_input
        ttk.Label(lbl_input, text="Note: Input file/folder is shared across tabs.", font=("Arial", 9, "italic")).pack(pady=2)
        
        frm_btns_input = ttk.Frame(lbl_input)
        frm_btns_input.pack(pady=5)
        ttk.Button(frm_btns_input, text="Select Input File...", command=self.browse_file).pack(side="left", padx=5)
        ttk.Button(frm_btns_input, text="Select Input Folder...", command=self.browse_folder).pack(side="left", padx=5)
        
        # --- Model Section ---
        lbl_model = ttk.LabelFrame(scrollable_frame, text="Model Configuration")
        lbl_model.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(lbl_model, text="Task:", font=("Arial", 10, "bold")).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ttk.Radiobutton(lbl_model, text="Transcribe (Keep original language)", variable=self.adv_task, value="transcribe").grid(row=0, column=1, padx=5, columnspan=2)
        ttk.Radiobutton(lbl_model, text="Translate (Convert to English)", variable=self.adv_task, value="translate").grid(row=0, column=3, padx=5)
        
        ttk.Label(lbl_model, text="Language:", font=("Arial", 10, "bold")).grid(row=1, column=0, padx=5, pady=5, sticky="w")
        lang_display = [f"{name}" for name, _ in WHISPER_LANGUAGES]
        ttk.Combobox(lbl_model, textvariable=self.adv_language, values=lang_display, width=18, state="readonly").grid(row=1, column=1, padx=5, sticky="w")
        ttk.Label(lbl_model, text="(Auto-detect or specify source language)", foreground="gray").grid(row=1, column=2, padx=5, sticky="w", columnspan=2)
        
        # --- Audio Decoding ---
        lbl_decoding = ttk.LabelFrame(scrollable_frame, text="Decoding Options")
        lbl_decoding.pack(fill="x", padx=10, pady=5)
        
        # Temperature
        ttk.Label(lbl_decoding, text="Temperature (0.0 - 1.0):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        scale_temp = ttk.Scale(lbl_decoding, from_=0.0, to=1.0, variable=self.adv_temp, orient="horizontal", length=200)
        scale_temp.grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(lbl_decoding, textvariable=self.adv_temp).grid(row=0, column=2, padx=5)
        ttk.Label(lbl_decoding, text="0=deterministic, 1=random", foreground="gray").grid(row=0, column=3, padx=5, sticky="w")
        
        # Beam Size
        ttk.Label(lbl_decoding, text="Beam Size (1-10):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        ttk.Spinbox(lbl_decoding, from_=1, to=10, textvariable=self.adv_beam_size, width=5).grid(row=1, column=1, padx=5, sticky="w")
        ttk.Label(lbl_decoding, text="Number of beams for beam search", foreground="gray").grid(row=1, column=3, padx=5, sticky="w")
        
        # Best Of
        ttk.Label(lbl_decoding, text="Best Of (1-10):").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        ttk.Spinbox(lbl_decoding, from_=1, to=10, textvariable=self.adv_best_of, width=5).grid(row=2, column=1, padx=5, sticky="w")
        ttk.Label(lbl_decoding, text="Candidates to sample from", foreground="gray").grid(row=2, column=3, padx=5, sticky="w")
        
        # Patience
        ttk.Label(lbl_decoding, text="Patience (0.0 - 2.0):").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(lbl_decoding, textvariable=self.adv_patience, width=8).grid(row=3, column=1, padx=5, sticky="w")
         
        # --- Thresholds ---
        lbl_thresh = ttk.LabelFrame(scrollable_frame, text="Filtering Thresholds")
        lbl_thresh.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(lbl_thresh, text="No Speech Threshold:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(lbl_thresh, textvariable=self.adv_no_speech_threshold, width=8).grid(row=0, column=1, padx=5)
        ttk.Label(lbl_thresh, text="(Skips silent segments)", foreground="gray").grid(row=0, column=2, padx=5, sticky="w")
        
        ttk.Label(lbl_thresh, text="Log Prob Threshold:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(lbl_thresh, textvariable=self.adv_log_prob_threshold, width=8).grid(row=1, column=1, padx=5)
        
        ttk.Label(lbl_thresh, text="Compression Ratio:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(lbl_thresh, textvariable=self.adv_compression_ratio_threshold, width=8).grid(row=2, column=1, padx=5)
        
        # --- Prompts & Context ---
        lbl_prompt = ttk.LabelFrame(scrollable_frame, text="Prompting & Context")
        lbl_prompt.pack(fill="x", padx=10, pady=5)
        
        ttk.Checkbutton(lbl_prompt, text="Condition on previous text", variable=self.adv_condition_on_prev).pack(anchor="w", padx=5, pady=5)
        
        ttk.Label(lbl_prompt, text="Initial Prompt (Context/Dictionary):").pack(anchor="w", padx=5)
        self.txt_prompt = tk.Text(lbl_prompt, height=3, width=50, bg="#3c3f41", fg="white", insertbackground="white")
        self.txt_prompt.pack(fill="x", padx=5, pady=5)
        ttk.Label(lbl_prompt, text="Provide names, technical terms, or style examples.", foreground="gray").pack(anchor="w", padx=5)

        # --- Performance ---
        lbl_perf = ttk.LabelFrame(scrollable_frame, text="Performance")
        lbl_perf.pack(fill="x", padx=10, pady=5)
        
        ttk.Checkbutton(lbl_perf, text="Use FP16 (Half Precision)", variable=self.adv_fp16).pack(anchor="w", padx=5, pady=2)
        
        frm_extra = ttk.Frame(lbl_perf)
        frm_extra.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(frm_extra, text="Device:").pack(side="left", padx=5)
        ttk.Combobox(frm_extra, textvariable=self.adv_device, values=["auto", "cuda", "cpu"], width=10).pack(side="left", padx=5)
        
        ttk.Label(frm_extra, text="Format:").pack(side="left", padx=15)
        ttk.Combobox(frm_extra, textvariable=self.adv_output_format, values=["vtt", "srt"], width=10).pack(side="left", padx=5)
        
        # --- Action ---
        ttk.Button(lbl_perf, text="START ADVANCED TRANSCRIPTION", command=self.start_advanced_transcribe).pack(pady=20)

    def get_advanced_options(self):
        """Collect all advanced options into a dictionary."""
        # Get language code
        lang_display = self.adv_language.get()
        language_code = None
        for name, code in WHISPER_LANGUAGES:
            if name == lang_display:
                language_code = code
                break
        
        options = {
            "task": self.adv_task.get(),
            "temperature": self.adv_temp.get(),
            "beam_size": self.adv_beam_size.get(),
            "patience": self.adv_patience.get(),
            "condition_on_previous_text": self.adv_condition_on_prev.get(),
            "initial_prompt": self.txt_prompt.get("1.0", "end-1c").strip() or None,
            "no_speech_threshold": self.adv_no_speech_threshold.get(),
            "log_prob_threshold": self.adv_log_prob_threshold.get(),
            "compression_ratio_threshold": self.adv_compression_ratio_threshold.get(),
        }
        
        # Only add language if not auto-detect
        if language_code is not None:
            options["language"] = language_code
        
        return options

    def start_advanced_transcribe(self):
        """Start transcription using advanced options."""
        input_path = self.ent_input.get()
        if not input_path:
             messagebox.showwarning("Warning", "Please select an input file in the 'Batch Processor' tab first.")
             return
             
        kwargs = self.get_advanced_options()
        device = self.adv_device.get()
        compute_type = "float16" if self.adv_fp16.get() and device != "cpu" else "int8"
        
        self.queue_status(f"Starting ADVANCED transcription with options: {kwargs}")
        
        # Check if we need to reload model with different device/precision
        model_name = self.var_model.get()
        
        # Force reload if anything changed
        if (self.core.whisper_model_name != model_name or 
            getattr(self.core, '_last_device', None) != device or
            getattr(self.core, '_last_compute_type', None) != compute_type):
            
             self.queue_status(f"Reloading model {model_name} on {device}...")
             self.core.whisper_model = None # Force reload
             self.core._last_device = device
             self.core._last_compute_type = compute_type
        
        output_dir = self.get_output_dir()
        # Add output format to kwargs (transcribe_media doesn't take it yet, we'll fix that)
        kwargs['output_format'] = self.adv_output_format.get()
        
        threading.Thread(target=self._run_transcribe, args=(input_path, output_dir), kwargs=kwargs, daemon=True).start()

    # ================= EDITOR TAB =================
    def setup_editor_tab(self):
        # Top: Media Info & Action Bar
        self.frm_editor_top = ttk.Frame(self.tab_editor)
        self.frm_editor_top.pack(fill="x", padx=10, pady=5)
        
        self.lbl_editor_media = ttk.Label(self.frm_editor_top, text="No Media Loaded", font=("Arial", 10, "italic"))
        self.lbl_editor_media.pack(side="left", padx=5)
        
        self.btn_editor_play = ttk.Button(self.frm_editor_top, text="Play in System Player", command=self.editor_play_media, state="disabled")
        self.btn_editor_play.pack(side="left", padx=10)
        
        ttk.Button(self.frm_editor_top, text="Open Media/VTT...", command=self.editor_open_file).pack(side="right", padx=5)
        ttk.Button(self.frm_editor_top, text="Save VTT", command=self.editor_save_file).pack(side="right", padx=5)

        # Center: Subtitle Editor (takes most space now)
        self.editor_frame = SubtitleEditorFrame(self.tab_editor)
        self.editor_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.current_vtt_path = None
        self.current_media_path = None

    def editor_play_media(self):
        if self.current_media_path and os.path.exists(self.current_media_path):
            import sys, subprocess
            if sys.platform == 'win32':
                os.startfile(self.current_media_path)
            elif sys.platform == 'darwin':
                subprocess.call(['open', self.current_media_path])
            else:
                subprocess.call(['xdg-open', self.current_media_path])

    def _get_next_iteration_path(self, base_path):
        p = Path(base_path)
        import re
        stem = p.stem
        # Remove any existing _editNN suffix to find the true base
        match = re.search(r'_edit\d+$', stem)
        if match:
             stem = stem[:match.start()]
             
        num = 1
        while True:
            new_path = p.with_name(f"{stem}_edit{num:02d}.vtt")
            if not new_path.exists():
                return str(new_path)
            num += 1

    def editor_open_file(self):
        path = filedialog.askopenfilename(filetypes=[("Media/VTT", "*.mp4 *.mp3 *.vtt"), ("All Files", "*.*")])
        if not path:
            return
            
        p = Path(path)
        if p.suffix == '.vtt':
            self.load_vtt_in_editor(path)
            for ext in ['.mp4', '.mp3', '.mkv', '.wav']:
                media = p.with_suffix(ext)
                if media.exists():
                    self.lbl_editor_media.configure(text=f"Media: {media.name}")
                    self.btn_editor_play.configure(state="normal")
                    self.current_media_path = str(media)
                    break
        else:
            self.lbl_editor_media.configure(text=f"Media: {p.name}")
            self.btn_editor_play.configure(state="normal")
            self.current_media_path = path
            vtt = p.with_suffix('.vtt')
            if vtt.exists():
                self.load_vtt_in_editor(str(vtt))
            else:
                self.queue_status(f"No VTT found for {path}. Transcribe it first.")
                
    def load_vtt_in_editor(self, path):
        try:
            cues = self.core.parse_vtt(path)
            self.editor_frame.load_cues(cues)
            self.current_vtt_path = path
            self.queue_status(f"Loaded VTT: {path}")
        except Exception as e:
            self.queue_status(f"Error loading VTT: {e}")
            
    def editor_save_file(self):
        if not self.current_vtt_path:
            path = filedialog.asksaveasfilename(defaultextension=".vtt")
            if not path:
                return
            save_path = path
        else:
            # Generate iterative name to protect original
            save_path = self._get_next_iteration_path(self.current_vtt_path)
            
        try:
            data = self.editor_frame.get_cues()
            self.core.save_vtt_from_data(data, save_path)
            self.queue_status(f"Saved Iteration: {save_path}")
            messagebox.showinfo("Success", f"File saved as:\n{os.path.basename(save_path)}")
            self.current_vtt_path = save_path
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ================= SETTINGS TAB =================
    def setup_settings_tab(self):
        ttk.Label(self.tab_settings, text="Model Manager", font=("Arial", 14, "bold")).pack(pady=15)
        
        # --- Whisper Models ---
        frm_whisper = ttk.LabelFrame(self.tab_settings, text="Whisper Models (Transcription)")
        frm_whisper.pack(fill="x", padx=10, pady=5)
        
        # Grid layout for models
        self.model_status_labels = {}
        self.model_action_frame = {}
        
        # Get models from core
        models = list(_WHISPER_MODELS.keys())
        
        # Use a canvas for scrolling if the list is long
        canvas_models = tk.Canvas(frm_whisper, bg="#2b2b2b", highlightthickness=0)
        scrollbar_models = ttk.Scrollbar(frm_whisper, orient="vertical", command=canvas_models.yview)
        scrollable_models = ttk.Frame(canvas_models)
        
        scrollable_models.bind(
            "<Configure>",
            lambda e: canvas_models.configure(scrollregion=canvas_models.bbox("all"))
        )
        
        canvas_models.create_window((0, 0), window=scrollable_models, anchor="nw")
        canvas_models.configure(yscrollcommand=scrollbar_models.set)
        
        canvas_models.pack(side="left", fill="both", expand=True)
        scrollbar_models.pack(side="right", fill="y", pady=5)
        
        for i, model in enumerate(models):
            row_frame = ttk.Frame(scrollable_models)
            row_frame.pack(fill="x", padx=5, pady=2)
            
            # Model Name
            ttk.Label(row_frame, text=f"{model}", width=20, font=("Arial", 10, "bold")).pack(side="left", padx=5)
            
            # Status & Size Label
            lbl_status = ttk.Label(row_frame, text="Checking...", width=25, foreground="gray")
            lbl_status.pack(side="left", padx=5)
            self.model_status_labels[model] = lbl_status
            
            # Action Frame
            act_frame = ttk.Frame(row_frame)
            act_frame.pack(side="right", padx=5)
            self.model_action_frame[model] = act_frame
            
            self._update_model_buttons(model)
            
        # --- Translation Model ---
        frm_mbart = ttk.LabelFrame(self.tab_settings, text="mBART Model (Translation)")
        frm_mbart.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(frm_mbart, text="mBART-large-50", font=("Arial", 10, "bold")).grid(row=0, column=0, padx=10, pady=15, sticky="w")
        
        self.lbl_mbart_status = ttk.Label(frm_mbart, text="Checking...", width=20, foreground="gray")
        self.lbl_mbart_status.grid(row=0, column=1, padx=10, pady=15)
        
        self.btn_mbart_dl = ttk.Button(frm_mbart, text="Download", 
                   command=lambda: threading.Thread(target=self.core.download_translation_model, daemon=True).start())
        self.btn_mbart_dl.grid(row=0, column=2, padx=10, pady=15)
        
        # Refresh status button
        ttk.Button(self.tab_settings, text="Refresh All Statuses", command=self.refresh_model_status).pack(pady=15)
        
        ttk.Label(self.tab_settings, text="Models are stored in local 'models' directory.", foreground="gray").pack(pady=5)
        
        # Initial status check
        self.after(500, self.refresh_model_status)
        
    def download_specific_model(self, model_name):
        """Start background download for a specific model."""
        self.queue_status(f"Starting download for {model_name} model...")
        threading.Thread(target=self._run_model_download, args=(model_name,), daemon=True).start()
        
    def _run_model_download(self, model_name):
        try:
            self.core.download_whisper_model(model_name)
            self.queue_status(f"Finished downloading {model_name} model.")
            self.after(0, self.refresh_model_status)
        except Exception as e:
            self.queue_status(f"Error downloading {model_name}: {e}")

    def _update_model_buttons(self, model_name):
        """Update the action buttons (Download/Delete) for a model."""
        frame = self.model_action_frame.get(model_name)
        if not frame: return
        
        # Clear frame
        for child in frame.winfo_children():
            child.destroy()
            
        is_available = self.core.model_manager.is_whisper_model_available(model_name)
        
        if is_available:
            ttk.Button(frame, text="Delete", width=10, 
                       command=lambda m=model_name: self.delete_specific_model(m)).pack(side="right")
        else:
            ttk.Button(frame, text="Download", width=10, 
                       command=lambda m=model_name: self.download_specific_model(m)).pack(side="right")

    def delete_specific_model(self, model_name):
        """Delete a model after confirmation."""
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete the '{model_name}' model?"):
            self.core.model_manager.delete_whisper_model(model_name)
            self.refresh_model_status()

    def refresh_model_status(self):
        """Check and display model download status for all models."""
        # Whisper Models
        from textifier_core import _WHISPER_MODELS
        for model in _WHISPER_MODELS.keys():
            is_available = self.core.model_manager.is_whisper_model_available(model)
            lbl = self.model_status_labels.get(model)
            
            if lbl:
                if is_available:
                    path = self.core.model_manager.get_whisper_model_path(model)
                    size_mb = self.core.model_manager.get_model_size(path)
                    lbl.configure(text=f"✓ Ready ({size_mb:.0f} MB)", foreground="#4caf50")
                else:
                    lbl.configure(text="✗ Not Found", foreground="#ff9800")
            
            self._update_model_buttons(model)

        # mBART
        if self.core.model_manager.is_translation_model_available():
             size_mb = self.core.model_manager.get_model_size(self.core.model_manager.translation_dir)
             self.lbl_mbart_status.configure(text=f"✓ Ready ({size_mb:.0f} MB)", foreground="#4caf50")
             self.btn_mbart_dl.configure(state="disabled", text="Installed")
        else:
             self.lbl_mbart_status.configure(text="✗ Not Found", foreground="#ff9800")
             self.btn_mbart_dl.configure(state="normal", text="Download")


if __name__ == "__main__":
    print("Opening window...")
    app = TextifierApp()
    print("\n" + "=" * 50)
    print("TEXTIFIER is ready!")
    print("=" * 50 + "\n")
    app.mainloop()
