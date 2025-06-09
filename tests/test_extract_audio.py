import sys
import types

# Create dummy modules for optional dependencies so AudioTranscriber can be imported
dummy = types.ModuleType("dummy")
sys.modules.setdefault("whisper", dummy)
openai_dummy = types.ModuleType("openai")
openai_dummy.OpenAI = lambda *a, **k: None
sys.modules.setdefault("openai", openai_dummy)
torch_dummy = types.ModuleType("torch")
torch_dummy.cuda = types.SimpleNamespace(is_available=lambda: False, init=lambda: None)
sys.modules.setdefault("torch", torch_dummy)
tk_dummy = types.ModuleType("tkinter")
tk_dummy.filedialog = types.SimpleNamespace()
tk_dummy.messagebox = types.SimpleNamespace()
sys.modules.setdefault("tkinter", tk_dummy)
sys.modules.setdefault("pypandoc", dummy)
dummy.convert_file = lambda *a, **k: None
ffmpeg_stub = types.ModuleType("ffmpeg")
ffmpeg_stub.input = lambda *a, **k: None
sys.modules.setdefault("ffmpeg", ffmpeg_stub)

import importlib.util
import os

# Load AudioTranscriber module from file after stubbing dependencies
spec = importlib.util.spec_from_file_location("AudioTranscriber", os.path.join(os.path.dirname(__file__), "..", "AudioTranscriber.py"))
AudioTranscriber = importlib.util.module_from_spec(spec)
spec.loader.exec_module(AudioTranscriber)


def test_extract_audio_multiple_periods(monkeypatch):
    # Set globals used by extract_audio
    AudioTranscriber.pipelineFile = "example.v1.mp4"
    AudioTranscriber.audio_folder = "/tmp"

    # Mock ffmpeg chain to avoid actual processing
    class DummyStream:
        def output(self, *args, **kwargs):
            return self
        def run(self, overwrite_output=True):
            pass
    monkeypatch.setattr(AudioTranscriber.ffmpeg, 'input', lambda path: DummyStream())

    # Mock filesystem interactions
    monkeypatch.setattr(AudioTranscriber.os.path, 'exists', lambda path: True)
    monkeypatch.setattr(AudioTranscriber.os, 'makedirs', lambda path: None)
    monkeypatch.setattr(AudioTranscriber.os, 'replace', lambda src, dst: None)

    result = AudioTranscriber.extract_audio("example.v1.mp4")
    assert result == "example.v1.mp3"
