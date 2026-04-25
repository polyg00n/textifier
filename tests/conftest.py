import pytest
import os
import shutil
from pathlib import Path
from textifier_core import TextifierCore, ModelManager

@pytest.fixture
def tmp_models_dir(tmp_path):
    """Provides a temporary directory for models."""
    d = tmp_path / "models"
    d.mkdir()
    (d / "whisper").mkdir()
    (d / "translation").mkdir()
    return d

@pytest.fixture
def core_instance(tmp_models_dir):
    """Provides a TextifierCore instance with a temp models directory."""
    # We monkeypatch the default models_dir in ModelManager for this instance
    core = TextifierCore(whisper_model_name="tiny")
    core.model_manager.models_dir = tmp_models_dir
    core.model_manager.whisper_dir = tmp_models_dir / "whisper"
    core.model_manager.translation_dir = tmp_models_dir / "translation"
    return core

@pytest.fixture
def sample_vtt_content():
    return """WEBVTT

1
00:00:00.000 --> 00:00:05.000
Hello, this is a test segment.

2
00:00:05.000 --> 00:00:10.000
Testing the second segment output.
"""

@pytest.fixture
def sample_srt_content():
    return """1
00:00:00,000 --> 00:00:05,000
Hello, this is a test segment.

2
00:00:05,000 --> 00:00:10,000
Testing the second segment output.
"""
