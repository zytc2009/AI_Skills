#!/usr/bin/env python3
"""
claude-speak — Push-to-Talk Voice Input for Claude Code
Hold a key to record, release to transcribe and paste via local Whisper.
No API key needed. Runs fully offline.
"""

import sys
import time
import threading
import signal
import atexit
import argparse

# ── Dependency check ────────────────────────────────────────────────────────
_missing = []
for pkg, name in [("numpy", "numpy"), ("sounddevice", "sounddevice"),
                   ("keyboard", "keyboard"), ("pyperclip", "pyperclip")]:
    try:
        __import__(pkg)
    except ImportError:
        _missing.append(name)

if _missing:
    print(f"Missing dependencies: {', '.join(_missing)}")
    print(f"Run: pip install {' '.join(_missing)}")
    sys.exit(1)

import numpy as np
import sounddevice as sd
import keyboard
import pyperclip

# ── Cleanup registry — ensures hooks are removed even on crash ────────────
_hooks_registered = False

def _cleanup():
    """Remove all keyboard hooks to prevent terminal hotkey corruption."""
    global _hooks_registered
    if _hooks_registered:
        try:
            keyboard.unhook_all()
        except Exception:
            pass
        _hooks_registered = False

atexit.register(_cleanup)

# ── Whisper loader ───────────────────────────────────────────────────────────
USING_FASTER_WHISPER = False
model = None

def load_model(model_size: str) -> None:
    global model, USING_FASTER_WHISPER
    try:
        from faster_whisper import WhisperModel
        print(f"Loading faster-whisper [{model_size}] ...", flush=True)
        model = WhisperModel(model_size, device="cpu", compute_type="int8")
        USING_FASTER_WHISPER = True
        print("faster-whisper ready.")
    except ImportError:
        try:
            import whisper as ow
            print(f"Loading openai-whisper [{model_size}] ...", flush=True)
            model = ow.load_model(model_size)
            print("openai-whisper ready.")
        except ImportError:
            print("No whisper found. Install one of:\n"
                  "  pip install faster-whisper   # recommended\n"
                  "  pip install openai-whisper")
            sys.exit(1)

# ── Recording state ──────────────────────────────────────────────────────────
SAMPLE_RATE = 16000
_chunks: list = []
_recording = False
_lock = threading.Lock()
_stream = None

def _audio_cb(indata, frames, t, status):
    if _recording:
        _chunks.append(indata.copy())

def start_recording() -> None:
    global _recording, _chunks, _stream
    with _lock:
        if _recording:
            return
        _recording = True
        _chunks = []
        _stream = sd.InputStream(samplerate=SAMPLE_RATE, channels=1,
                                  dtype="float32", callback=_audio_cb,
                                  blocksize=1024)
        _stream.start()
    print("\r🔴 Recording... (release to stop)", end="", flush=True)

def stop_and_transcribe(language: str) -> None:
    global _recording, _stream
    with _lock:
        if not _recording:
            return
        _recording = False
        if _stream:
            _stream.stop()
            _stream.close()
            _stream = None
        chunks = list(_chunks)

    if not chunks:
        print("\r⚪ No audio captured.        ", flush=True)
        return

    print("\r🔄 Transcribing...            ", end="", flush=True)
    audio = np.concatenate(chunks, axis=0).flatten().astype("float32")

    if np.sqrt(np.mean(audio ** 2)) < 0.005:
        print("\r⚪ Silence detected.          ", flush=True)
        return

    try:
        if USING_FASTER_WHISPER:
            lang = None if language == "auto" else language
            segs, _ = model.transcribe(audio, beam_size=5,
                                        language=lang, vad_filter=True)
            text = "".join(s.text for s in segs).strip()
        else:
            import whisper as ow
            lang = None if language == "auto" else language
            text = ow.transcribe(model, audio, language=lang, fp16=False
                                 )["text"].strip()
    except Exception as exc:
        print(f"\r[Error] Transcription failed: {exc}", flush=True)
        return

    if not text:
        print("\r⚪ Nothing detected.          ", flush=True)
        return

    print(f"\r✅ {text}", flush=True)
    print(f"   📋 (also copied to clipboard)", flush=True)
    _paste(text)

def _paste(text: str) -> None:
    try:
        pyperclip.copy(text)
        time.sleep(0.15)  # Give focus time to return to the target window
        keyboard.send("ctrl+v")
    except Exception as exc:
        print(f"[Paste failed] {exc}. Trying typewrite...")
        try:
            keyboard.write(text, delay=0.02)
        except Exception as exc2:
            print(f"[Type failed] {exc2}\nText: {text}")

# ── Key bindings ─────────────────────────────────────────────────────────────
_tx_thread: threading.Thread | None = None

def _on_down(e):
    global _tx_thread
    if _tx_thread and _tx_thread.is_alive():
        return
    start_recording()

def _on_up(e, language: str):
    global _tx_thread
    _tx_thread = threading.Thread(target=stop_and_transcribe,
                                   args=(language,), daemon=True)
    _tx_thread.start()

# ── Entry point ──────────────────────────────────────────────────────────────
def main():
    global _hooks_registered

    parser = argparse.ArgumentParser(
        description="Push-to-talk voice input for Claude Code")
    parser.add_argument("--model", "-m", default="base",
                        choices=["tiny", "base", "small", "medium",
                                 "large-v2", "large-v3"],
                        help="Whisper model size (default: base)")
    parser.add_argument("--lang", "-l", default="auto",
                        help="Language code: zh / en / ja / auto (default: auto)")
    parser.add_argument("--key", "-k", default="right_alt",
                        help="Trigger key (default: right_alt)")
    args = parser.parse_args()

    load_model(args.model)
    print(f"\n🎙  Voice input active")
    print(f"   Hold [{args.key}] to record, release to transcribe & paste")
    print(f"   Language: {args.lang}   Model: {args.model}")
    print("   Ctrl+C to quit\n")

    # suppress=False: do not intercept keys at OS level.
    # This prevents terminal hotkey corruption if the process is force-killed.
    # Trade-off: the trigger key character may appear briefly in the input box,
    # which is usually invisible for right_alt / caps_lock / function keys.
    keyboard.on_press_key(args.key, _on_down, suppress=False)
    keyboard.on_release_key(args.key,
                             lambda e: _on_up(e, args.lang), suppress=False)
    _hooks_registered = True

    # Use threading.Event instead of keyboard.wait() so Ctrl+C always works.
    # keyboard.wait() can swallow SIGINT on Windows.
    _stop_event = threading.Event()

    def _sigint_handler(*_):
        print("\nBye.")
        _cleanup()
        _stop_event.set()

    signal.signal(signal.SIGINT, _sigint_handler)
    signal.signal(signal.SIGTERM, _sigint_handler)

    try:
        while not _stop_event.is_set():
            _stop_event.wait(timeout=0.2)
    except KeyboardInterrupt:
        print("\nBye.")
        _cleanup()

if __name__ == "__main__":
    main()
