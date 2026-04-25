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
        self.tab_summarize = ttk.Frame(self.notebook)
        self.tab_pipeline = ttk.Frame(self.notebook)
        self.tab_whisper = ttk.Frame(self.notebook)
        self.tab_settings = ttk.Frame(self.notebook)
        self.tab_editor = ttk.Frame(self.notebook) # Hidden for now
        
        self.notebook.add(self.tab_batch, text="Transcribe/Translate")
        self.notebook.add(self.tab_summarize, text="Summarize")
        self.notebook.add(self.tab_pipeline, text="Pipeline")
        self.notebook.add(self.tab_whisper, text="Advanced Whisper")
        self.notebook.add(self.tab_settings, text="Utilities")
        
        self.setup_settings_tab()
        self.setup_batch_tab()
        self.setup_whisper_tab()
        self.setup_editor_tab()
        self.setup_summarize_tab()
        self.setup_pipeline_tab()
        
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
        self.style.configure("TCombobox", fieldbackground="#ffffff", foreground="#000000")
        self.style.map("TCombobox", fieldbackground=[("readonly", "#ffffff")], foreground=[("readonly", "#000000")])
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
        frm_transcribe = ttk.LabelFrame(self.tab_batch, text="Transcribe (Video/Audio → Text)")
        frm_transcribe.pack(fill="x", padx=10, pady=5)
        
        # Row 0: Model selection
        ttk.Label(frm_transcribe, text="Whisper Model:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.var_model = tk.StringVar(value="large-v3-turbo")
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
        
        # Row 2: Output Formats
        ttk.Label(frm_transcribe, text="Output Formats:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        frm_fmts = ttk.Frame(frm_transcribe)
        frm_fmts.grid(row=2, column=1, columnspan=2, sticky="w")
        
        self.var_out_vtt = tk.BooleanVar(value=True)
        self.var_out_srt = tk.BooleanVar(value=False)
        self.var_out_txt = tk.BooleanVar(value=True)
        self.var_out_csv = tk.BooleanVar(value=False)
        self.var_out_tsv = tk.BooleanVar(value=False)
        
        ttk.Checkbutton(frm_fmts, text="VTT", variable=self.var_out_vtt).pack(side="left", padx=5)
        ttk.Checkbutton(frm_fmts, text="SRT", variable=self.var_out_srt).pack(side="left", padx=5)
        ttk.Checkbutton(frm_fmts, text="TXT", variable=self.var_out_txt).pack(side="left", padx=5)
        ttk.Checkbutton(frm_fmts, text="CSV", variable=self.var_out_csv).pack(side="left", padx=5)
        ttk.Checkbutton(frm_fmts, text="TSV", variable=self.var_out_tsv).pack(side="left", padx=5)
        
        # Row 3: Action button
        ttk.Button(frm_transcribe, text="Transcribe to Text", command=self.start_transcribe).grid(row=3, column=0, columnspan=3, padx=20, pady=10)
        
        # TRANSLATE Section (converts VTT to other languages)
        frm_translate = ttk.LabelFrame(self.tab_batch, text="Translate (VTT → Other Language)")
        frm_translate.pack(fill="x", padx=10, pady=5)
        
        # Row 0: Source language
        ttk.Label(frm_translate, text="Source Language:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.var_translate_source = tk.StringVar(value="English")
        source_langs = [name for name, _ in MBART_LANGUAGES]
        self.opt_translate_source = ttk.Combobox(frm_translate, textvariable=self.var_translate_source,
                                                 values=source_langs, width=18, state="readonly")
        self.opt_translate_source.grid(row=0, column=1, padx=5, sticky="w")
        
        # Row 1: Target language 1
        ttk.Label(frm_translate, text="Target Language 1:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.var_translate_target = tk.StringVar(value="None")
        target_langs = ["None"] + source_langs
        self.opt_translate_target = ttk.Combobox(frm_translate, textvariable=self.var_translate_target,
                                                 values=target_langs, width=18, state="readonly")
        self.opt_translate_target.grid(row=1, column=1, padx=5, sticky="w")
        
        # Row 2: Target language 2 (Optional)
        ttk.Label(frm_translate, text="Target Language 2:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.var_translate_target2 = tk.StringVar(value="None")
        self.opt_translate_target2 = ttk.Combobox(frm_translate, textvariable=self.var_translate_target2,
                                                  values=target_langs, width=18, state="readonly")
        self.opt_translate_target2.grid(row=2, column=1, padx=5, sticky="w")
        
        self.var_enable_target2 = tk.BooleanVar(value=False)
        ttk.Checkbutton(frm_translate, text="Enable", variable=self.var_enable_target2).grid(row=2, column=2, padx=5, sticky="w")
        
        # Row 3: Action button
        ttk.Label(frm_translate, text="(supports VTT, SRT, TXT, CSV files)", foreground="gray").grid(row=3, column=0, padx=5, sticky="w")
        ttk.Button(frm_translate, text="Translate File", command=self.start_translate).grid(row=3, column=1, padx=5, pady=5, sticky="w")
        
        # Log with Scrollbar
        ttk.Label(self.tab_batch, text="Activity Log:").pack(anchor="w", padx=10)
        frm_log = ttk.Frame(self.tab_batch)
        frm_log.pack(fill="both", expand=True, padx=10, pady=5)
        
        scrl_log = ttk.Scrollbar(frm_log)
        scrl_log.pack(side="right", fill="y")
        
        self.txt_log = tk.Text(frm_log, height=12, bg="#1e1e1e", fg="#00ff00", 
                               insertbackground="white", state="disabled",
                               yscrollcommand=scrl_log.set)
        self.txt_log.pack(side="left", fill="both", expand=True)
        scrl_log.config(command=self.txt_log.yview)

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
            
        # Collect formats
        formats = []
        if self.var_out_vtt.get(): formats.append("vtt")
        if self.var_out_srt.get(): formats.append("srt")
        if self.var_out_txt.get(): formats.append("txt")
        if self.var_out_csv.get(): formats.append("csv")
        if self.var_out_tsv.get(): formats.append("tsv")
        
        if not formats:
            messagebox.showwarning("Warning", "Please select at least one output format.")
            return

        output_dir = self.get_output_dir()
        threading.Thread(target=self._run_transcribe, args=(input_path, output_dir, language_code, formats), daemon=True).start()
        
    def _run_transcribe(self, input_path, output_dir, language=None, formats=None, **kwargs):
        try:
            # Add language to kwargs if specified
            if language is not None:
                kwargs['language'] = language
            if formats:
                kwargs['output_formats'] = formats
            
            if os.path.isdir(input_path):
                files = [f for f in Path(input_path).glob('*') if f.suffix.lower() in {'.mp4', '.mov', '.avi', '.mkv', '.mp3', '.wav', '.m4a', '.aac'}]
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
        
        # Find source language code
        source_code = None
        for name, code in MBART_LANGUAGES:
            if name == source_display:
                source_code = code
                break

        # Find target language codes
        targets = []
        
        # Target 1
        target1_code = None
        for name, code in MBART_LANGUAGES:
            if name == self.var_translate_target.get():
                target1_code = code
                break
        if target1_code:
            targets.append((self.var_translate_target.get(), target1_code))
            
        # Target 2 (if enabled)
        if self.var_enable_target2.get():
            target2_code = None
            for name, code in MBART_LANGUAGES:
                if name == self.var_translate_target2.get():
                    target2_code = code
                    break
            if target2_code:
                targets.append((self.var_translate_target2.get(), target2_code))
        
        if not source_code or not targets:
            messagebox.showerror("Error", "Invalid language selection")
            return
        
        self.queue_status(f"Translating from {source_display} to: {', '.join([t[0] for t in targets])}...")
        output_dir = self.get_output_dir()
        threading.Thread(target=self._run_translate, args=(input_path, source_code, targets, output_dir), daemon=True).start()
        
    def _run_translate(self, input_path, source_lang, targets, output_dir):
        try:
            # targets is a list of (display_name, language_code)
            if os.path.isdir(input_path):
                # ... same logic but iterate targets
                files = []
                for ext in ['*.vtt', '*.srt', '*.txt', '*.csv']:
                    files.extend(Path(input_path).glob(ext))
                
                if not files:
                    self.queue_status(f"No translatable files found in {input_path}")
                    return
                
                self.queue_status(f"Found {len(files)} files to translate")
                for f in files:
                    for name, code in targets:
                        self.queue_status(f"Translating: {f.name} to {name}")
                        self.core.translate_file(str(f), source_lang=source_lang, target_lang=code, output_dir=output_dir)
            else:
                for name, code in targets:
                    self.queue_status(f"Translating: {os.path.basename(input_path)} to {name}")
                    self.core.translate_file(input_path, source_lang=source_lang, target_lang=code, output_dir=output_dir)
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
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind("<Enter>", lambda _: canvas.bind_all("<MouseWheel>", _on_mousewheel))
        canvas.bind("<Leave>", lambda _: canvas.unbind_all("<MouseWheel>"))
        
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
        self.adv_repetition_penalty = tk.DoubleVar(value=1.1)
        self.adv_word_timestamps = tk.BooleanVar(value=True)
        self.adv_vad_filter = tk.BooleanVar(value=True)
        self.adv_vad_threshold = tk.DoubleVar(value=0.5)
        
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
        
        # Repetition Penalty
        ttk.Label(lbl_decoding, text="Repetition Penalty (1.0-2.0):").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        ttk.Scale(lbl_decoding, from_=1.0, to=2.0, variable=self.adv_repetition_penalty, orient="horizontal", length=200).grid(row=4, column=1, padx=5, pady=5)
        ttk.Label(lbl_decoding, textvariable=self.adv_repetition_penalty).grid(row=4, column=2, padx=5)
        ttk.Label(lbl_decoding, text="Prevents stuck loops", foreground="gray").grid(row=4, column=3, padx=5, sticky="w")
         
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
        
        # VAD Toggle
        ttk.Checkbutton(lbl_thresh, text="Enable VAD Filter (Silero)", variable=self.adv_vad_filter).grid(row=3, column=0, padx=5, pady=5, sticky="w")
        ttk.Scale(lbl_thresh, from_=0.0, to=1.0, variable=self.adv_vad_threshold, orient="horizontal", length=150).grid(row=3, column=1, padx=5)
        ttk.Label(lbl_thresh, text="VAD Threshold").grid(row=3, column=2, padx=5, sticky="w")
        
        # --- Prompts & Context ---
        lbl_prompt = ttk.LabelFrame(scrollable_frame, text="Prompting & Context")
        lbl_prompt.pack(fill="x", padx=10, pady=5)
        
        ttk.Checkbutton(lbl_prompt, text="Condition on previous text", variable=self.adv_condition_on_prev).pack(anchor="w", padx=5, pady=5)
        
        ttk.Label(lbl_prompt, text="Initial Prompt (Context/Dictionary):").pack(anchor="w", padx=5)
        frm_adv_prompt = ttk.Frame(lbl_prompt)
        frm_adv_prompt.pack(fill="x", padx=5, pady=5)
        
        scrl_adv_p = ttk.Scrollbar(frm_adv_prompt)
        scrl_adv_p.pack(side="right", fill="y")
        
        self.txt_prompt = tk.Text(frm_adv_prompt, height=3, width=50, bg="#3c3f41", fg="white", 
                                  insertbackground="white", yscrollcommand=scrl_adv_p.set)
        self.txt_prompt.pack(side="left", fill="x", expand=True)
        scrl_adv_p.config(command=self.txt_prompt.yview)
        ttk.Label(lbl_prompt, text="Provide names, technical terms, or style examples.", foreground="gray").pack(anchor="w", padx=5)

        # --- Performance ---
        lbl_perf = ttk.LabelFrame(scrollable_frame, text="Performance")
        lbl_perf.pack(fill="x", padx=10, pady=5)
        
        ttk.Checkbutton(lbl_perf, text="Use FP16 (Half Precision)", variable=self.adv_fp16).pack(anchor="w", padx=5, pady=2)
        ttk.Checkbutton(lbl_perf, text="Word-Level Timestamps (JSON Export)", variable=self.adv_word_timestamps).pack(anchor="w", padx=5, pady=2)
        
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
            "repetition_penalty": self.adv_repetition_penalty.get(),
            "word_timestamps": self.adv_word_timestamps.get(),
            "vad_filter": self.adv_vad_filter.get(),
            "vad_parameters": {"threshold": self.adv_vad_threshold.get()} if self.adv_vad_filter.get() else None,
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
        # Create a canvas with scrollbar for the entire tab
        canvas = tk.Canvas(self.tab_settings, bg="#2b2b2b", highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.tab_settings, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Mouse wheel support for this tab
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind("<Enter>", lambda _: canvas.bind_all("<MouseWheel>", _on_mousewheel))
        canvas.bind("<Leave>", lambda _: canvas.unbind_all("<MouseWheel>"))

        ttk.Label(scrollable_frame, text="Model Manager", font=("Arial", 14, "bold")).pack(pady=15)
        
        # --- Whisper Models ---
        frm_whisper = ttk.LabelFrame(scrollable_frame, text="Whisper Models (Transcription)")
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
        frm_mbart = ttk.LabelFrame(scrollable_frame, text="mBART Model (Translation)")
        frm_mbart.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(frm_mbart, text="mBART-large-50", font=("Arial", 10, "bold")).grid(row=0, column=0, padx=10, pady=15, sticky="w")
        
        self.lbl_mbart_status = ttk.Label(frm_mbart, text="Checking...", width=20, foreground="gray")
        self.lbl_mbart_status.grid(row=0, column=1, padx=10, pady=15)
        
        self.btn_mbart_dl = ttk.Button(frm_mbart, text="Download", 
                   command=lambda: threading.Thread(target=self.core.download_translation_model, daemon=True).start())
        self.btn_mbart_dl.grid(row=0, column=2, padx=10, pady=10)        # Refresh status button
        ttk.Button(scrollable_frame, text="Refresh All Statuses", command=self.refresh_model_status).pack(pady=10)
        
        ttk.Label(scrollable_frame, text="Models are stored in local 'models' directory.", foreground="gray").pack(pady=5)

        # --- LLM Configuration Section ---
        frm_llm = ttk.LabelFrame(scrollable_frame, text="LLM Configuration")
        frm_llm.pack(fill="x", padx=10, pady=5)
        
        self.var_llm_type = tk.StringVar(value="local")
        frm_llm_toggle = ttk.Frame(frm_llm)
        frm_llm_toggle.pack(fill="x", padx=5, pady=5)
        ttk.Radiobutton(frm_llm_toggle, text="Local LLM", variable=self.var_llm_type, value="local", command=self._toggle_llm_view).pack(side="left", padx=10)
        ttk.Radiobutton(frm_llm_toggle, text="Cloud LLM", variable=self.var_llm_type, value="cloud", command=self._toggle_llm_view).pack(side="left", padx=10)
        
        # Local LLM Sub-frame
        self.frm_llm_local = ttk.Frame(frm_llm)
        self.frm_llm_local.pack(fill="x", padx=5, pady=5)
        
        self.var_local_provider = tk.StringVar(value="ollama")
        ttk.Radiobutton(self.frm_llm_local, text="Ollama", variable=self.var_local_provider, value="ollama", command=self._toggle_llm_view).grid(row=0, column=0, padx=5, pady=2, sticky="w")
        ttk.Radiobutton(self.frm_llm_local, text="LM Studio", variable=self.var_local_provider, value="lm_studio", command=self._toggle_llm_view).grid(row=0, column=1, padx=5, pady=2, sticky="w")
        
        ttk.Label(self.frm_llm_local, text="Models Directory:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.ent_llm_dir = ttk.Entry(self.frm_llm_local, width=40)
        self.ent_llm_dir.grid(row=1, column=1, padx=5, pady=2, sticky="we")
        ttk.Button(self.frm_llm_local, text="Browse", command=self._browse_llm_dir).grid(row=1, column=2, padx=2)
        
        ttk.Button(self.frm_llm_local, text="Scan for Models", command=self._scan_llm_models).grid(row=2, column=1, pady=5)
        self.lbl_local_models = ttk.Label(self.frm_llm_local, text="Local Models: None detected", foreground="gray", wraplength=400)
        self.lbl_local_models.grid(row=3, column=0, columnspan=3, padx=10, pady=5)
        
        # Cloud LLM Sub-frame
        self.frm_llm_cloud = ttk.Frame(frm_llm)
        # Hidden by default
        
        self.llm_cloud_fields = {}
        providers = [("Google AI Studio (Gemini) API Key", "gemini"), ("Claude API Key", "claude"), ("OpenAI API Key", "openai")]
        for i, (label, key) in enumerate(providers):
            ttk.Label(self.frm_llm_cloud, text=label + ":").grid(row=i, column=0, padx=5, pady=2, sticky="w")
            ent = ttk.Entry(self.frm_llm_cloud, width=40, show="*")
            ent.grid(row=i, column=1, padx=5, pady=2, sticky="we")
            self.llm_cloud_fields[key] = ent
            
        # --- System Info & Recommendations ---
        frm_sys = ttk.LabelFrame(scrollable_frame, text="System Info & Recommendations")
        frm_sys.pack(fill="x", padx=10, pady=5)
        
        self.btn_recommend = ttk.Button(frm_sys, text="Show System Specs & Recommendations", command=self._show_recommendations)
        self.btn_recommend.pack(pady=5)
        
        # System Info with Scrollbar
        frm_sys_info = ttk.Frame(frm_sys)
        frm_sys_info.pack(fill="x", padx=10, pady=5)
        
        scrl_sys = ttk.Scrollbar(frm_sys_info)
        scrl_sys.pack(side="right", fill="y")
        
        self.txt_sys_info = tk.Text(frm_sys_info, height=6, width=60, bg="#1e1e1e", fg="#ffffff", 
                                    state="disabled", yscrollcommand=scrl_sys.set)
        self.txt_sys_info.pack(side="left", fill="x", expand=True)
        scrl_sys.config(command=self.txt_sys_info.yview)
        
        # Initial status check
        self._toggle_llm_view()
        self.after(500, self.refresh_model_status)
        
    def _toggle_llm_view(self):
        """Show/Hide local vs cloud LLM configurations and update Summarize tab."""
        if self.var_llm_type.get() == "local":
            self.frm_llm_cloud.pack_forget()
            self.frm_llm_local.pack(fill="x", padx=5, pady=5)
            if hasattr(self, 'lbl_active_llm'):
                self.lbl_active_llm.configure(text=f"Active LLM: Local ({self.var_local_provider.get().capitalize()})")
        else:
            self.frm_llm_local.pack_forget()
            self.frm_llm_cloud.pack(fill="x", padx=5, pady=5)
            if hasattr(self, 'lbl_active_llm'):
                self.lbl_active_llm.configure(text="Active LLM: Cloud Provider")
        
        if hasattr(self, '_refresh_summarize_models'):
            self._refresh_summarize_models()
            
    def _browse_llm_dir(self):
        f = filedialog.askdirectory()
        if f:
            self.ent_llm_dir.delete(0, "end")
            self.ent_llm_dir.insert(0, f)
            self._scan_llm_models()
            
    def _scan_llm_models(self):
        directory = self.ent_llm_dir.get()
        if not directory: return
        models = self.core.summarizer.scan_local_models(directory)
        if models:
            self.lbl_local_models.configure(text=f"Local Models Found: {', '.join(models)}", foreground="#4caf50")
        else:
            self.lbl_local_models.configure(text="No .gguf models found in directory.", foreground="#ff9800")
        
        self._refresh_summarize_models()
            
    def _show_recommendations(self):
        """Detect system specs and recommend models."""
        self.txt_sys_info.configure(state="normal")
        self.txt_sys_info.delete("1.0", "end")
        
        import platform
        import torch
        
        cpu = platform.processor() or "Unknown CPU"
        ram = "Unknown RAM"
        try:
            import psutil
            ram_gb = psutil.virtual_memory().total / (1024**3)
            ram = f"{ram_gb:.1f} GB"
        except ImportError:
            pass
            
        vram = "No CUDA detected"
        vram_bytes = 0
        gpu_info = "None"

        if torch.cuda.is_available():
            vram_bytes = torch.cuda.get_device_properties(0).total_memory
            vram = f"{vram_bytes / (1024**3):.1f} GB"
            gpu_name = torch.cuda.get_device_name(0)
            gpu_info = f"{gpu_name} ({vram} VRAM)"
        
        vram_gb = (vram_bytes / (1024**3)) if torch.cuda.is_available() else 0
        
        info = f"System Specs:\n"
        info += f"- OS: {platform.system()} {platform.release()}\n"
        info += f"- CPU: {cpu}\n"
        info += f"- RAM: {ram}\n"
        info += f"- GPU: {gpu_info}\n\n"
        
        info += "Recommendations for Summarization (GGUF):\n"
        
        if vram_gb >= 24:
            info += "- Top Tier (GPU): Qwen 3 32B+, Mistral Large 2 (70B+ MoE), or Llama 3.1 70B\n"
            info += "  (You have massive headroom for high context length)\n"
        elif vram_gb >= 16:
            info += "- High Tier (GPU): Qwen 2.5 14B Q8_0, Mistral Small 24B, or DeepSeek R1 32B Distill\n"
        elif vram_gb >= 12:
            info += "- Mid-High Tier (GPU): Qwen 2.5 14B Q4_K_M, Mistral Nemo 12B, or Gemma 3 12B\n"
        elif vram_gb >= 8:
            info += "- Mid Tier (GPU): Llama 3 8B, Mistral 7B, Qwen 2.5 7B, or Gemma 3 4B/9B\n"
        elif vram_gb >= 6:
            info += "- Entry Tier (GPU): Phi-4 Mini (3.8B), Gemma 3 4B-IT, or Qwen 3 4B\n"
        elif vram_gb >= 4:
            info += "- Light Tier (GPU): Llama 3.2 1B Instruct, Qwen 3 1.5B, or Phi-3 Mini\n"
        else:
            info += "- CPU Mode: Use Phi-3 Mini or TinyLlama for usable speeds.\n"
            
        info += "\n- Cloud: Gemini 1.5 Pro (recommended for 2 hour+ transcripts) or Claude 3.5 Sonnet\n"
        
        self.txt_sys_info.insert("1.0", info)
        self.txt_sys_info.configure(state="disabled")

    def download_specific_model(self, model_name):
        """Start background download for a specific model."""
        self.queue_status(f"Starting download for {model_name} model...")
        threading.Thread(target=self._run_model_download, args=(model_name,), daemon=True).start()
        
    def _run_model_download(self, model_name):
        try:
            self.core.model_manager.download_whisper_model(model_name)
            self.queue_status(f"Model '{model_name}' download complete.")
            self.refresh_model_status()
            self._refresh_summarize_models()
        except Exception as e:
            self.queue_status(f"Error downloading {model_name}: {e}")

    def _refresh_summarize_models(self):
        """Populate the model list based on current provider."""
        if not hasattr(self, 'opt_sum_model'):
            return # Widget not created yet during startup
            
        current_type = self.var_llm_type.get()
        models = []
        
        if current_type == 'local':
            directory = self.ent_llm_dir.get()
            if directory:
                models = self.core.summarizer.scan_local_models(directory)
            if not models:
                models = ["gemma-3-4b-it", "llama3:latest", "mistral:latest"] # Fallbacks
        else:
            models = ["gemini-1.5-flash", "gemini-1.5-pro", "claude-3-5-sonnet", "gpt-4o"]
            
        self.opt_sum_model['values'] = models
        if self.var_sum_model.get() not in models and models:
            # Only reset if current selection isn't in new list
            # but keep gemma-3-4b-it if it's the default and we are starting
            if self.var_sum_model.get() == "gemma-3-4b-it" and "gemma-3-4b-it" not in models:
                pass # let it be for now, maybe Ollama has it even if not in scan dir
            else:
                 # self.var_sum_model.set(models[0])
                 pass
            
    def _update_model_buttons(self, model_name):
        """Show Delete/Download based on availability."""
        frame = self.model_action_frame.get(model_name)
        if not frame: return
        
        # Clear frame
        for widget in frame.winfo_children():
            widget.destroy()
            
        is_available = self.core.model_manager.is_whisper_model_available(model_name)
        
        if is_available:
            ttk.Button(frame, text="Delete", width=8, 
                       command=lambda m=model_name: self.delete_specific_model(m)).pack(side="right")
        else:
            ttk.Button(frame, text="Download", width=10, 
                       command=lambda m=model_name: self.download_specific_model(m)).pack(side="right")
                       
    def delete_specific_model(self, model_name):
        """Delete a model after confirmation."""
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete the '{model_name}' model?"):
            self.core.model_manager.delete_whisper_model(model_name)
            self.refresh_model_status()

    # ================= SUMMARIZE TAB =================
    def setup_summarize_tab(self):
        ttk.Label(self.tab_summarize, text="Note: Input file/folder is shared across tabs. Change it in Transcribe/Translate.", font=("Arial", 9, "italic")).pack(pady=5, anchor="w", padx=10)
        
        # Prompt Section
        frm_prompt = ttk.LabelFrame(self.tab_summarize, text="Summarization Prompt")
        frm_prompt.pack(fill="both", expand=True, padx=10, pady=5)
        
        frm_p_input = ttk.Frame(frm_prompt)
        frm_p_input.pack(fill="both", expand=True, padx=5, pady=5)
        
        scrl_p = ttk.Scrollbar(frm_p_input)
        scrl_p.pack(side="right", fill="y")
        
        self.txt_prompt = tk.Text(frm_p_input, height=10, bg="#1e1e1e", fg="#ffffff", 
                                  insertbackground="white", yscrollcommand=scrl_p.set)
        self.txt_prompt.pack(side="left", fill="both", expand=True)
        scrl_p.config(command=self.txt_prompt.yview)
        
        # Default prompt
        default_prompt = (
            "You are a Knowledge Management Specialist. Create a high-value summary of this transcript.\n\n"
            "Structure your response as follows:\n"
            "1. **Core Summary**: A 2-3 sentence overview.\n"
            "2. **Key Takeaways**: Bulleted list of the most important points.\n"
            "3. **Lists**: Extract all lists mentioned. It might be steps in a process, recommendations, or ideas.\n"
            "4. **Glossary/Terms**: Define any specific jargon or unique terms used."
        )
        self.txt_prompt.insert("1.0", default_prompt)
        
        frm_prompt_btns = ttk.Frame(frm_prompt)
        frm_prompt_btns.pack(fill="x", padx=5, pady=5)
        ttk.Button(frm_prompt_btns, text="Load Prompt (.md/.txt)", command=self._load_prompt).pack(side="left", padx=5)
        ttk.Button(frm_prompt_btns, text="Save Prompt (.md/.txt)", command=self._save_prompt).pack(side="left", padx=5)
        
        # Advanced LLM Options
        frm_adv_llm = ttk.LabelFrame(self.tab_summarize, text="Advanced LLM Settings")
        frm_adv_llm.pack(fill="x", padx=10, pady=5)
        
        # Row 1: Chunking Strategy & Size
        ttk.Label(frm_adv_llm, text="Strategy:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.var_llm_strategy = tk.StringVar(value="map_reduce")
        self.opt_llm_strategy = ttk.Combobox(frm_adv_llm, textvariable=self.var_llm_strategy, 
                                             values=["map_reduce", "single_pass"], width=12, state="readonly")
        self.opt_llm_strategy.grid(row=0, column=1, padx=5, sticky="w")
        
        ttk.Label(frm_adv_llm, text="Chunk Size:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.var_llm_chunk_size = tk.IntVar(value=8000)
        ttk.Entry(frm_adv_llm, textvariable=self.var_llm_chunk_size, width=8).grid(row=0, column=3, padx=5, sticky="w")
        
        ttk.Label(frm_adv_llm, text="Overlap:").grid(row=0, column=4, padx=5, pady=5, sticky="w")
        self.var_llm_overlap = tk.IntVar(value=500)
        ttk.Entry(frm_adv_llm, textvariable=self.var_llm_overlap, width=8).grid(row=0, column=5, padx=5, sticky="w")
        
        # Row 2: Generation Settings
        ttk.Label(frm_adv_llm, text="Temperature:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.var_llm_temp = tk.DoubleVar(value=0.3)
        self.sld_temp = ttk.Scale(frm_adv_llm, from_=0.0, to=1.5, variable=self.var_llm_temp, orient="horizontal", length=100)
        self.sld_temp.grid(row=1, column=1, padx=5, sticky="w")
        ttk.Label(frm_adv_llm, textvariable=self.var_llm_temp).grid(row=1, column=2, sticky="w")
        
        ttk.Label(frm_adv_llm, text="Max Output Tokens:").grid(row=1, column=3, padx=5, pady=5, sticky="w")
        self.var_llm_max_tokens = tk.IntVar(value=1500)
        ttk.Entry(frm_adv_llm, textvariable=self.var_llm_max_tokens, width=8).grid(row=1, column=4, padx=5, sticky="w")
        
        # Action Section
        frm_action = ttk.Frame(self.tab_summarize)
        frm_action.pack(fill="x", padx=10, pady=10)
        # Row 1: LLM Info & Model Selection
        frm_llm_info = ttk.Frame(frm_action)
        frm_llm_info.pack(side="left", fill="x", expand=True, padx=10, pady=5)
        
        self.lbl_active_llm = ttk.Label(frm_llm_info, text="Active LLM: [Checking...]", foreground="#4caf50")
        self.lbl_active_llm.pack(side="left", padx=5)
        
        ttk.Label(frm_llm_info, text="Model:").pack(side="left", padx=(15, 5))
        self.var_sum_model = tk.StringVar(value="gemma-3-4b-it")
        self.opt_sum_model = ttk.Combobox(frm_llm_info, textvariable=self.var_sum_model, width=30)
        self.opt_sum_model.pack(side="left", padx=5)
        
        # We also need a way to refresh this list
        ttk.Button(frm_llm_info, text="↻", width=3, command=self._refresh_summarize_models).pack(side="left", padx=2)
        
        ttk.Button(frm_action, text="Run Summarization", command=self.start_summarize).pack(side="right", padx=10)
        
        # Dedicated Log for Summarization with Scrollbar
        ttk.Label(self.tab_summarize, text="Summarization Progress & Output:").pack(anchor="w", padx=10)
        frm_sum_log = ttk.Frame(self.tab_summarize)
        frm_sum_log.pack(fill="both", expand=True, padx=10, pady=5)
        
        scrl_sum = ttk.Scrollbar(frm_sum_log)
        scrl_sum.pack(side="right", fill="y")
        
        self.txt_summary_log = tk.Text(frm_sum_log, height=10, bg="#1e1e1e", fg="#00ff00", 
                                       state="disabled", yscrollcommand=scrl_sum.set)
        self.txt_summary_log.pack(side="left", fill="both", expand=True)
        scrl_sum.config(command=self.txt_summary_log.yview)
        
        # Finally refresh models now that widget exists
        self._refresh_summarize_models()
        self._toggle_llm_view() # Ensure label is correct

    def _browse_summary_input(self):
        f = filedialog.askopenfilename(filetypes=[("Text/VTT/SRT Files", "*.vtt *.srt *.txt *.csv"), ("All files", "*.*")])
        if f:
            self.ent_summary_input.delete(0, "end")
            self.ent_summary_input.insert(0, f)

    def _load_prompt(self):
        f = filedialog.askopenfilename(filetypes=[("Markdown files", "*.md"), ("Text files", "*.txt")])
        if f:
            try:
                with open(f, "r", encoding="utf-8") as file:
                    content = file.read()
                self.txt_prompt.delete("1.0", "end")
                self.txt_prompt.insert("1.0", content)
                self.queue_status(f"Loaded prompt from {os.path.basename(f)}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not load prompt: {e}")

    def _save_prompt(self):
        f = filedialog.asksaveasfilename(defaultextension=".md", filetypes=[("Markdown files", "*.md"), ("Text files", "*.txt")])
        if f:
            try:
                content = self.txt_prompt.get("1.0", "end-1c")
                with open(f, "w", encoding="utf-8") as file:
                    file.write(content)
                self.queue_status(f"Saved prompt to {os.path.basename(f)}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save prompt: {e}")

    def start_summarize(self):
        input_path = self.ent_input.get()
        if not input_path or not os.path.exists(input_path):
            messagebox.showwarning("Warning", "Please select a valid input file or folder in Input Selection.")
            return
            
        prompt = self.txt_prompt.get("1.0", "end-1c")
        
        # Prepare provider config from Utilities tab
        config = {
            'type': self.var_llm_type.get(),
            'provider': self.var_local_provider.get() if self.var_llm_type.get() == 'local' else None,
            'model': self.var_sum_model.get(),
            'strategy': self.var_llm_strategy.get(),
            'chunk_size': self.var_llm_chunk_size.get(),
            'chunk_overlap': self.var_llm_overlap.get(),
            'temperature': self.var_llm_temp.get(),
            'max_tokens': self.var_llm_max_tokens.get()
        }
        
        if config['type'] == 'cloud':
            # Identify which cloud provider has an API key (highly simplified)
            for provider, ent in self.llm_cloud_fields.items():
                val = ent.get()
                if val:
                    config['provider'] = provider
                    config['api_key'] = val
                    break
        
        if not config.get('provider'):
            messagebox.showerror("Error", "No LLM provider configured or enabled.")
            return

        # Check provider status for local LLMs
        if config['type'] == 'local':
            provider = config['provider']
            if not self.core.summarizer.check_provider_status(provider):
                if messagebox.askyesno("Provider Offline", f"{provider.capitalize()} is not running. Attempt to launch it?"):
                    if self.core.summarizer.launch_provider(provider):
                        self.queue_status(f"Attempting to launch {provider}...")
                        messagebox.showinfo("Launching", f"Launching {provider.capitalize()}... Please wait a few seconds for it to initialize, then try again.")
                        return
                    else:
                        messagebox.showerror("Error", f"Could not find or launch {provider.capitalize()}. Please start it manually.")
                        return
                else:
                    return

        self.queue_status(f"Starting summarization with {config['provider']}...")
        threading.Thread(target=self._run_summarize, args=(input_path, prompt, config), daemon=True).start()

    def _run_summarize(self, input_path, prompt, config):
        try:
            files_to_process = []
            if os.path.isdir(input_path):
                files_to_process = [f for f in Path(input_path).glob('*') if f.is_file() and f.suffix.lower() in {'.txt', '.vtt', '.srt', '.csv', '.md'}]
            else:
                files_to_process = [Path(input_path)]
                
            for file_path in files_to_process:
                self._log_summary(f"Reading {file_path.name}...")
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                self._log_summary(f"Running summarizer on {file_path.name}...")
                result = self.core.summarizer.summarize(content, prompt, config)
                
                self._log_summary(f"\n--- SUMMARY FOR {file_path.name} ---\n")
                self._log_summary(result)
                
                # Save to file
                out_file = file_path.with_suffix(".summary.md")
                with open(out_file, "w", encoding="utf-8") as f:
                    f.write(result)
                    
                self.queue_status(f"Summary saved to: {out_file.name}")
                self._log_summary(f"\nSaved to: {out_file}\n")
            
        except Exception as e:
            self._log_summary(f"Error: {e}")

    def _log_summary(self, message):
        self.txt_summary_log.configure(state="normal")
        self.txt_summary_log.insert("end", message + "\n")
        self.txt_summary_log.see("end")
        self.txt_summary_log.configure(state="disabled")

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

    # ================= PIPELINE TAB =================
    def setup_pipeline_tab(self):
        ttk.Label(self.tab_pipeline, text="Note: Input file/folder is shared across tabs. Change it in Transcribe/Translate.", font=("Arial", 9, "italic")).pack(pady=5, anchor="w", padx=10)
        
        frm_steps = ttk.LabelFrame(self.tab_pipeline, text="Pipeline Steps")
        frm_steps.pack(fill="x", padx=10, pady=5)
        
        # Transcribe
        self.var_pipe_transcribe = tk.BooleanVar(value=True)
        ttk.Checkbutton(frm_steps, text="Transcribe", variable=self.var_pipe_transcribe).grid(row=0, column=0, sticky="w", padx=10, pady=5)
        
        # Transcribe formats
        frm_trans_fmts = ttk.Frame(frm_steps)
        frm_trans_fmts.grid(row=0, column=1, sticky="w", padx=10)
        
        self.var_pipe_vtt = tk.BooleanVar(value=True)
        self.var_pipe_srt = tk.BooleanVar(value=False)
        self.var_pipe_txt = tk.BooleanVar(value=True)
        self.var_pipe_csv = tk.BooleanVar(value=False)
        self.var_pipe_tsv = tk.BooleanVar(value=False)
        
        ttk.Checkbutton(frm_trans_fmts, text="VTT", variable=self.var_pipe_vtt).pack(side="left", padx=5)
        ttk.Checkbutton(frm_trans_fmts, text="SRT", variable=self.var_pipe_srt).pack(side="left", padx=5)
        ttk.Checkbutton(frm_trans_fmts, text="TXT", variable=self.var_pipe_txt).pack(side="left", padx=5)
        ttk.Checkbutton(frm_trans_fmts, text="CSV", variable=self.var_pipe_csv).pack(side="left", padx=5)
        ttk.Checkbutton(frm_trans_fmts, text="TSV", variable=self.var_pipe_tsv).pack(side="left", padx=5)
        
        # Translate
        self.var_pipe_translate = tk.BooleanVar(value=False)
        ttk.Checkbutton(frm_steps, text="Translate", variable=self.var_pipe_translate).grid(row=1, column=0, sticky="w", padx=10, pady=5)
        
        frm_trans_options = ttk.Frame(frm_steps)
        frm_trans_options.grid(row=2, column=0, sticky="w", padx=30, pady=(0, 10))
        
        # Files sub-frame
        frm_files = ttk.Frame(frm_trans_options)
        frm_files.pack(side="left", anchor="n", padx=(0, 10))
        
        ttk.Label(frm_files, text="Files to translate:").pack(anchor="w", pady=(0, 2))
        self.var_pipe_trans_vtt = tk.BooleanVar(value=True)
        ttk.Checkbutton(frm_files, text="vtt", variable=self.var_pipe_trans_vtt).pack(anchor="w", padx=10)
        self.var_pipe_trans_txt = tk.BooleanVar(value=False)
        ttk.Checkbutton(frm_files, text="txt", variable=self.var_pipe_trans_txt).pack(anchor="w", padx=10)
        self.var_pipe_trans_csv = tk.BooleanVar(value=False)
        ttk.Checkbutton(frm_files, text="csv", variable=self.var_pipe_trans_csv).pack(anchor="w", padx=10)
        
        # Vertical Separator
        ttk.Separator(frm_trans_options, orient="vertical").pack(side="left", fill="y", padx=15)
        
        # Languages sub-frame
        frm_langs = ttk.Frame(frm_trans_options)
        frm_langs.pack(side="left", anchor="n", padx=(10, 0))
        
        ttk.Label(frm_langs, text="Target Languages:").pack(anchor="w", pady=(0, 2))
        lang_names = ["None"] + [name for name, _ in MBART_LANGUAGES]
        
        self.var_pipe_lang1 = tk.StringVar(value="None")
        ttk.Combobox(frm_langs, textvariable=self.var_pipe_lang1, values=lang_names, state="readonly", width=15).pack(anchor="w", pady=2)
        
        self.var_pipe_lang2 = tk.StringVar(value="None")
        ttk.Combobox(frm_langs, textvariable=self.var_pipe_lang2, values=lang_names, state="readonly", width=15).pack(anchor="w", pady=2)
        
        self.var_pipe_lang3 = tk.StringVar(value="None")
        ttk.Combobox(frm_langs, textvariable=self.var_pipe_lang3, values=lang_names, state="readonly", width=15).pack(anchor="w", pady=2)
        
        # Summarize
        self.var_pipe_summarize = tk.BooleanVar(value=False)
        ttk.Checkbutton(frm_steps, text="Summarize", variable=self.var_pipe_summarize).grid(row=3, column=0, sticky="w", padx=10, pady=5)
        
        ttk.Button(frm_steps, text="Begin", command=self.start_pipeline).grid(row=4, column=0, pady=20)

        # Log
        ttk.Label(self.tab_pipeline, text="Pipeline Log:").pack(anchor="w", padx=10)
        frm_log = ttk.Frame(self.tab_pipeline)
        frm_log.pack(fill="both", expand=True, padx=10, pady=5)
        
        scrl_log = ttk.Scrollbar(frm_log)
        scrl_log.pack(side="right", fill="y")
        
        self.txt_pipe_log = tk.Text(frm_log, height=10, bg="#1e1e1e", fg="#00ff00", 
                                    insertbackground="white", state="disabled", yscrollcommand=scrl_log.set)
        self.txt_pipe_log.pack(side="left", fill="both", expand=True)
        scrl_log.config(command=self.txt_pipe_log.yview)

    def log_pipe(self, message):
        self.txt_pipe_log.configure(state="normal")
        self.txt_pipe_log.insert("end", message + "\n")
        self.txt_pipe_log.see("end")
        self.txt_pipe_log.configure(state="disabled")
        self.log_message(f"[Pipeline] {message}")

    def start_pipeline(self):
        input_path = self.ent_input.get()
        if not input_path or not os.path.exists(input_path):
            messagebox.showwarning("Warning", "Please select a valid input file or folder in the Input Selection.")
            return
            
        target_codes = []
        for lang_name in [self.var_pipe_lang1.get(), self.var_pipe_lang2.get(), self.var_pipe_lang3.get()]:
            if lang_name != "None":
                for name, code in MBART_LANGUAGES:
                    if name == lang_name:
                        target_codes.append((name, code))
                        break
        
        exts = []
        if self.var_pipe_trans_vtt.get(): exts.append(".vtt")
        if self.var_pipe_trans_txt.get(): exts.append(".txt")
        if self.var_pipe_trans_csv.get(): exts.append(".csv")
        
        source_display = self.var_translate_source.get()
        source_code = None
        for name, code in MBART_LANGUAGES:
            if name == source_display:
                source_code = code
                break
                
        llm_config = {
            'type': self.var_llm_type.get(),
            'provider': self.var_local_provider.get() if self.var_llm_type.get() == 'local' else None,
            'model': self.var_sum_model.get(),
            'strategy': self.var_llm_strategy.get(),
            'chunk_size': self.var_llm_chunk_size.get(),
            'chunk_overlap': self.var_llm_overlap.get(),
            'temperature': self.var_llm_temp.get(),
            'max_tokens': self.var_llm_max_tokens.get()
        }
        if llm_config['type'] == 'cloud':
            for provider, ent in self.llm_cloud_fields.items():
                val = ent.get()
                if val:
                    llm_config['provider'] = provider
                    llm_config['api_key'] = val
                    break
        
        summary_prompt = self.txt_prompt.get("1.0", "end-1c")
        output_dir = self.get_output_dir()
        
        whisper_kwargs = self.get_advanced_options()
        
        # Collect Transcribe formats
        trans_fmts = []
        if self.var_pipe_vtt.get(): trans_fmts.append("vtt")
        if self.var_pipe_srt.get(): trans_fmts.append("srt")
        if self.var_pipe_txt.get(): trans_fmts.append("txt")
        if self.var_pipe_csv.get(): trans_fmts.append("csv")
        if self.var_pipe_tsv.get(): trans_fmts.append("tsv")
        
        if self.var_pipe_transcribe.get() and not trans_fmts:
            messagebox.showwarning("Warning", "Please select at least one transcription output format.")
            return

        config = {
            'transcribe': self.var_pipe_transcribe.get(),
            'transcribe_fmts': trans_fmts,
            'translate': self.var_pipe_translate.get(),
            'translate_exts': exts,
            'translate_langs': target_codes,
            'translate_source_code': source_code,
            'summarize': self.var_pipe_summarize.get(),
            'whisper_kwargs': whisper_kwargs,
            'llm_config': llm_config,
            'summary_prompt': summary_prompt,
            'output_dir': output_dir
        }
        
        self.log_pipe(f"Starting pipeline on: {input_path}")
        threading.Thread(target=self._run_pipeline, args=(input_path, config), daemon=True).start()

    def _run_pipeline(self, input_path, config):
        try:
            files_to_process = []
            if os.path.isdir(input_path):
                files_to_process = [f for f in Path(input_path).glob('*') if f.is_file()]
            else:
                files_to_process = [Path(input_path)]
                
            media_exts = {'.mp4', '.mov', '.avi', '.mkv', '.mp3', '.wav', '.m4a', '.aac'}
            
            for file_path in files_to_process:
                # If Transcribe is not checked, we skip media files processing and only process text/subtitle files
                if not config['transcribe'] and file_path.suffix.lower() in media_exts:
                    continue
                
                # If we're only translating/summarizing, we only care about text/subtitle files, or files just generated
                is_media = file_path.suffix.lower() in media_exts
                base_stem = file_path.stem
                out_dir = Path(config['output_dir']) if config['output_dir'] else file_path.parent
                
                if config['transcribe'] or not is_media:
                    self.log_pipe(f"\n--- Processing {file_path.name} ---")
                
                # 1. Transcribe
                if config['transcribe'] and is_media:
                    self.log_pipe(f"Transcribing...")
                    model_name = self.var_model.get()
                    if self.core.whisper_model_name != model_name:
                        self.core.whisper_model_name = model_name
                        self.core.whisper_model = None
                    try:
                        # Pass requested formats
                        config['whisper_kwargs']['output_formats'] = config['transcribe_fmts']
                        self.core.transcribe_media(str(file_path), str(out_dir), **config['whisper_kwargs'])
                        self.log_pipe(f"Transcription finished.")
                    except Exception as e:
                        self.log_pipe(f"Transcription error: {e}")
                        
                # 2. Translate
                if config['translate'] and config['translate_langs']:
                    for ext in config['translate_exts']:
                        target_file = out_dir / f"{base_stem}{ext}"
                        if target_file.exists():
                            for lang_name, lang_code in config['translate_langs']:
                                self.log_pipe(f"Translating {ext} to {lang_name}...")
                                try:
                                    self.core.translate_file(str(target_file), source_lang=config['translate_source_code'], target_lang=lang_code, output_dir=str(out_dir))
                                except Exception as e:
                                    self.log_pipe(f"Translation error: {e}")
                                
                # 3. Summarize
                if config['summarize']:
                    target_txt = out_dir / f"{base_stem}.txt"
                    if target_txt.exists():
                        self.log_pipe(f"Summarizing {target_txt.name}...")
                        try:
                            with open(target_txt, "r", encoding="utf-8") as f:
                                content = f.read()
                            result = self.core.summarizer.summarize(content, config['summary_prompt'], config['llm_config'])
                            sum_file = out_dir / f"{base_stem}.summary.md"
                            with open(sum_file, "w", encoding="utf-8") as f:
                                f.write(result)
                            self.log_pipe(f"Summary saved to {sum_file.name}")
                            
                            # NEW: Also translate the summary if translation is enabled
                            if config['translate'] and config['translate_langs']:
                                for lang_name, lang_code in config['translate_langs']:
                                    self.log_pipe(f"Translating summary to {lang_name}...")
                                    try:
                                        self.core.translate_file(str(sum_file), source_lang=config['translate_source_code'], target_lang=lang_code, output_dir=str(out_dir))
                                    except Exception as e:
                                        self.log_pipe(f"Summary translation error: {e}")
                        except Exception as e:
                            self.log_pipe(f"Summarize error: {e}")
                            
            self.log_pipe("\nPipeline finished successfully!")
        except Exception as e:
            self.log_pipe(f"\nPipeline encountered a critical error: {e}")


if __name__ == "__main__":
    print("Opening window...")
    app = TextifierApp()
    print("\n" + "=" * 50)
    print("TEXTIFIER is ready!")
    print("=" * 50 + "\n")
    app.mainloop()
