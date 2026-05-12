import pytest
import os
from unittest.mock import patch, MagicMock
from textifier_core import FormatHandler, Summarizer, SubtitleSegment

def test_format_handler_parsers(sample_vtt_content, sample_srt_content, tmp_path):
    # Test VTT parsing
    vtt_file = tmp_path / "test.vtt"
    vtt_file.write_text(sample_vtt_content, encoding="utf-8")
    vtt_data = FormatHandler.parse_vtt(vtt_file)
    assert len(vtt_data) == 2
    assert vtt_data[0]['text'].strip() == "Hello, this is a test segment."
    
    # Test SRT parsing
    srt_file = tmp_path / "test.srt"
    srt_file.write_text(sample_srt_content, encoding="utf-8")
    srt_data = FormatHandler.parse_srt(srt_file)
    assert len(srt_data) == 2
    assert srt_data[1]['text'].strip() == "Testing the second segment output."

def test_summarizer_scan_models(tmp_path):
    summarizer = Summarizer()
    
    # Create fake models dir
    models_dir = tmp_path / "my_models"
    models_dir.mkdir()
    (models_dir / "model1.gguf").touch()
    (models_dir / "model2.bin").touch() # Should be ignored if not manifest
    
    # Create Ollama manifest structure
    manifest_dir = models_dir / "manifests" / "registry.ollama.ai" / "library" / "gemma"
    manifest_dir.mkdir(parents=True)
    (manifest_dir / "latest").touch()
    
    models = summarizer.scan_local_models(str(models_dir))
    assert "model1.gguf" in models
    assert "gemma:latest" in models
    assert "model2.bin" not in models

@patch("requests.post")
def test_summarizer_local_routing(mock_post):
    summarizer = Summarizer()
    
    # Mock successful responses
    mock_post.return_value.json.return_value = {"response": "Mocked Ollama Response"}
    mock_post.return_value.status_code = 200
    
    config = {
        'type': 'local',
        'provider': 'ollama',
        'model': 'gemma3:4b',
        'base_url': 'http://localhost:11434/api/generate'
    }
    
    result = summarizer.summarize("test text", "test prompt", config)
    assert result == "Mocked Ollama Response"
    
    # Verify the payload
    called_args, called_kwargs = mock_post.call_args
    assert called_kwargs['json']['model'] == 'gemma3:4b'
    assert "test prompt" in called_kwargs['json']['prompt']

def test_model_manager_availability(core_instance, tmp_models_dir):
    # Check whisper model availability
    model_name = "tiny"
    whisper_path = tmp_models_dir / "whisper" / model_name
    whisper_path.mkdir()
    (whisper_path / "model.bin").touch() # Fake model file
    
    assert core_instance.model_manager.is_whisper_model_available(model_name) is True
    assert core_instance.model_manager.is_whisper_model_available("large-v3") is False

@patch("faster_whisper.WhisperModel")
def test_transcribe_with_advanced_params(mock_whisper_class, core_instance, tmp_path):
    import json
    # Mock segments with words
    mock_word = MagicMock()
    mock_word.start = 0.0
    mock_word.end = 0.5
    mock_word.word = "Hello"
    mock_word.probability = 0.99
    
    mock_segment = MagicMock()
    mock_segment.start = 0.0
    mock_segment.end = 1.0
    mock_segment.text = "Hello world"
    mock_segment.words = [mock_word]
    
    mock_info = MagicMock()
    mock_info.language = "en"
    mock_info.language_probability = 1.0
    
    # Configure mock
    mock_instance = mock_whisper_class.return_value
    mock_instance.transcribe.return_value = ([mock_segment], mock_info)
    
    input_file = tmp_path / "test.mp3"
    input_file.touch()
    
    # Run transcription with word timestamps
    output_dir = tmp_path / "out"
    output_dir.mkdir()
    
    results = core_instance.transcribe_media(
        str(input_file), 
        output_dir=str(output_dir),
        word_timestamps=True,
        repetition_penalty=1.2,
        vad_filter=True
    )
    
    # Check if JSON file was created
    json_files = [r for r in results if r.endswith(".words.json")]
    assert len(json_files) == 1
    
    # Verify JSON content
    with open(json_files[0], 'r', encoding='utf-8') as f:
        data = json.load(f)
        assert len(data) == 1
        assert data[0]["words"][0]["word"] == "Hello"
    
    # Verify kwargs passed to whisper
    args, kwargs = mock_instance.transcribe.call_args
    assert kwargs["word_timestamps"] is True
    assert kwargs["repetition_penalty"] == 1.2
    assert kwargs["vad_filter"] is True


# ============== RE-SEGMENTATION TESTS ==============

def _make_word(start, end, text):
    """Helper to create a mock word object."""
    w = MagicMock()
    w.start = start
    w.end = end
    w.word = text
    return w

def _make_segment(start, end, text, words=None):
    """Helper to create a mock segment object."""
    s = MagicMock()
    s.start = start
    s.end = end
    s.text = text
    s.words = words or []
    return s


def test_resegment_splits_long_segment_by_duration():
    """A 12-second segment with word data should be split into ~3-second cues."""
    words = []
    for i in range(12):
        words.append(_make_word(float(i), float(i) + 0.8, f" word{i}"))
    
    segment = _make_segment(0.0, 12.0, " ".join(f"word{i}" for i in range(12)), words)
    
    result = FormatHandler.resegment_for_subtitles([segment], max_duration=3.0, max_words=12)
    
    # Should produce multiple cues, each <= 3 seconds
    assert len(result) > 1
    for cue in result:
        duration = cue.end - cue.start
        assert duration <= 4.0  # Tolerance for word boundary alignment
        assert len(cue.text) > 0


def test_resegment_splits_by_word_count():
    """Segments should also split when word count exceeds max_words."""
    words = []
    for i in range(20):
        # All words within 1 second (so duration limit won't trigger)
        words.append(_make_word(0.0 + i * 0.04, 0.04 + i * 0.04, f" w{i}"))
    
    segment = _make_segment(0.0, 0.8, " ".join(f"w{i}" for i in range(20)), words)
    
    result = FormatHandler.resegment_for_subtitles([segment], max_duration=30.0, max_words=5)
    
    # 20 words / 5 per cue = 4 cues
    assert len(result) == 4


def test_resegment_fallback_for_no_word_data():
    """Segments without word-level data should pass through unchanged."""
    segment = _make_segment(0.0, 15.0, "This is a long segment without word data")
    segment.words = None
    
    result = FormatHandler.resegment_for_subtitles([segment])
    
    assert len(result) == 1
    assert result[0].start == 0.0
    assert result[0].end == 15.0
    assert result[0].text == "This is a long segment without word data"


def test_resegment_preserves_short_segments():
    """Segments already shorter than max_duration should remain as a single cue."""
    words = [
        _make_word(0.0, 0.3, " Hello"),
        _make_word(0.3, 0.8, " world"),
    ]
    segment = _make_segment(0.0, 0.8, "Hello world", words)
    
    result = FormatHandler.resegment_for_subtitles([segment], max_duration=3.0, max_words=12)
    
    assert len(result) == 1
    assert result[0].text == "Hello world"


def test_resegment_handles_multiple_segments():
    """Multiple input segments should all be re-segmented independently."""
    seg1_words = [_make_word(float(i), float(i) + 0.8, f" a{i}") for i in range(8)]
    seg2_words = [_make_word(10.0 + float(i), 10.0 + float(i) + 0.8, f" b{i}") for i in range(4)]
    
    seg1 = _make_segment(0.0, 8.0, "long segment one", seg1_words)
    seg2 = _make_segment(10.0, 14.0, "short segment two", seg2_words)
    
    result = FormatHandler.resegment_for_subtitles([seg1, seg2], max_duration=3.0, max_words=12)
    
    # seg1 (8s) should split into ~3 cues, seg2 (4s) into ~2 cues
    assert len(result) >= 3
    # Verify chronological ordering
    for i in range(len(result) - 1):
        assert result[i].start <= result[i + 1].start

