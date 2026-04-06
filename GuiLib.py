import tkinter as tk
import threading
import time
import sys
import os
import queue
import tempfile
import wave
from pydub import AudioSegment
from pydub.playback import play
from piper.voice import PiperVoice

class Gui:
    root = None
    chat_box = None
    status_text = None
    state = "idle"
    
    # --- FIXED PIPER PATH ---
    model_path = r"C:\Program Fast Access\models\piper\en_US-amy-medium.onnx" 
    voice = None

    tts_queue = queue.Queue()
    tts_thread = None
    personality_name = "Assistant"

    @staticmethod
    def gui_start(title="Assistant"):
        Gui.personality_name = title
        try:
            # Load local Piper voice
            Gui.voice = PiperVoice.load(Gui.model_path)
            print(f"Success! Piper loaded from: {Gui.model_path}")
        except Exception as e:
            print(f"ERROR: Could not load Piper model: {e}")

        Gui.root = tk.Tk()
        Gui.root.title(title)
        Gui.root.geometry("550x600")
        Gui.root.configure(bg="#0f0f0f")
        Gui.root.protocol("WM_DELETE_WINDOW", Gui.on_closing)

        Gui.chat_box = tk.Text(
            Gui.root, bg="#111111", fg="white", font=("Consolas", 11), wrap="word"
        )
        Gui.chat_box.pack(fill="both", expand=True, padx=10, pady=10)
        Gui.chat_box.config(state="disabled")

        Gui.status_text = tk.Label(
            Gui.root, text="Idle", bg="#0f0f0f", fg="#4da6ff", font=("Segoe UI", 12)
        )
        Gui.status_text.pack(pady=5)

        Gui.start_tts()
        Gui.root.mainloop()

    @staticmethod
    def _tts_worker():
        """Processes text via Piper and plays it locally"""
        while True:
            text = Gui.tts_queue.get()
            if text is None: break
            
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_wav:
                    tmp_path = tmp_wav.name
                
                with wave.open(tmp_path, "wb") as wav_file:
                    Gui.voice.synthesize(text, wav_file)
                
                audio = AudioSegment.from_wav(tmp_path)
                play(audio)
                
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
                
            except Exception as e:
                print(f"Local TTS error: {e}")
            
            Gui.tts_queue.task_done()

    @staticmethod
    def speak(text):
        """Adds text to the offline TTS queue"""
        if not text or not text.strip():
            return
        Gui.tts_queue.put(text)

    @staticmethod
    def start_tts():
        if Gui.tts_thread is None:
            Gui.tts_thread = threading.Thread(target=Gui._tts_worker, daemon=True)
            Gui.tts_thread.start()

    @staticmethod
    def on_closing():
        Gui.root.destroy()
        sys.exit(0)

    @staticmethod
    def gui_prompt(text, speaker):
        if Gui.root is None or Gui.chat_box is None:
            return
        Gui.root.after(0, lambda: Gui._gui_prompt_on_tk(text, speaker))

    @staticmethod
    def _gui_prompt_on_tk(text, speaker):
        Gui.chat_box.config(state="normal")
        ts = time.strftime("%H:%M:%S")
        
        if speaker == "User":
            Gui.chat_box.insert("end", f"[{ts}] You: {text}\n")
        elif speaker == "Ai":
            Gui.chat_box.insert("end", f"[{ts}] {Gui.personality_name}: {text}\n")
        else:
            Gui.chat_box.insert("end", f"[{ts}] {speaker}: {text}\n")

        Gui.chat_box.see("end")
        Gui.chat_box.config(state="disabled")