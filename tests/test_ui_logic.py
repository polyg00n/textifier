import pytest
import tkinter as tk
from unittest.mock import MagicMock, patch
from gui_main import TextifierApp

@pytest.fixture
def app():
    # Patch mainloop to avoid blocking
    with patch('tkinter.Tk.mainloop'):
        # Patch initial checks to avoid actual system scans during test
        with patch('gui_main.TextifierApp.refresh_model_status'):
            with patch('gui_main.TextifierApp._refresh_summarize_models'):
                app = TextifierApp()
                return app

def test_ui_llm_toggle(app):
    # Initial state should be local
    assert app.var_llm_type.get() == "local"
    
    # Toggle to cloud
    app.var_llm_type.set("cloud")
    app._toggle_llm_view()
    
    assert "Cloud" in app.lbl_active_llm.cget("text")
    
    # Toggle back to local
    app.var_llm_type.set("local")
    app.var_local_provider.set("ollama")
    app._toggle_llm_view()
    
    assert "Ollama" in app.lbl_active_llm.cget("text")

def test_refresh_summarize_models_logic(app):
    # Mock scanning
    mock_models = ["gemma3:latest", "llama3"]
    app.core.summarizer.scan_local_models = MagicMock(return_value=mock_models)
    app.ent_llm_dir.get = MagicMock(return_value="fake_dir")
    
    app.var_llm_type.set("local")
    app._refresh_summarize_models()
    
    assert list(app.opt_sum_model['values']) == mock_models
    
    # Switch to cloud
    app.var_llm_type.set("cloud")
    app._refresh_summarize_models()
    
    # Check if cloud models are populated (defined in gui_main)
    assert "gemini-1.5-flash" in app.opt_sum_model['values']

def test_start_summarize_validation(app):
    # Mock messagebox
    with patch('tkinter.messagebox.showwarning') as mock_warn:
        app.ent_input.get = MagicMock(return_value="")
        app.start_summarize()
        mock_warn.assert_called_once()

def test_pipeline_ui_setup(app):
    # Ensure pipeline variables exist and have defaults
    assert app.var_pipe_transcribe.get() is True
    assert app.var_pipe_translate.get() is False
    assert app.var_pipe_summarize.get() is False
    assert app.var_pipe_lang1.get() == "None"

def test_transcribe_translate_defaults(app):
    # Ensure default target languages are "None" in the new Transcribe/Translate tab
    assert app.var_translate_target.get() == "None"
    assert app.var_translate_target2.get() == "None"
