import os
import json
import time
import queue
import sys
import threading
import gc
import ollama
import sounddevice as sd
from vosk import Model, KaldiRecognizer
from CommandRunner import CP
from GuiLib import Gui

# Global state
audio_queue = queue.Queue()
recognizer = None
model = None
chat_history = []
shutdown_event = threading.Event()

class Assistant():
    personality = None 

    @staticmethod
    def set_personality(config):
        Assistant.personality = config
        print(f"Loaded personality: {config['name']}")

    @staticmethod
    def load_vosk():
        global recognizer, model
        MODEL_PATH = r""#vosk model location here
        
        Assistant.gui_prompt(Assistant.personality["messages"]["loading"], "System")
        model = Model(MODEL_PATH)
        recognizer = KaldiRecognizer(model, 16000)
        Assistant.gui_prompt(Assistant.personality["messages"]["ready"], "System")
    
    @staticmethod
    def deload_vosk():
        global recognizer, model
        recognizer = None
        model = None
        gc.collect()

    @staticmethod
    def ask_llama(text):
        global chat_history
        system_prompt = Assistant.personality["system_prompt"]
        chat_history.append({"role": "user", "content": text})
        
        if len(chat_history) > Assistant.personality["max_history"]:
            chat_history = chat_history[-Assistant.personality["max_history"]:]

        try:
            response = ollama.chat(
                model=Assistant.personality["ai_model"],
                messages=[{"role": "system", "content": system_prompt}] + chat_history,
                options={"temperature": Assistant.personality["temperature"]}
            )
            ai_reply = response["message"]["content"].strip()
            chat_history.append({"role": "assistant", "content": ai_reply})
            return ai_reply
        except Exception as e:
            return f"AI Error: {e}"

    @staticmethod
    def audio_callback(indata, frames, time_info, status):
        audio_queue.put(bytes(indata))

    @staticmethod
    def listen():
        global recognizer
        recognizer.Reset()
        Assistant.gui_prompt(Assistant.personality["messages"]["listening"], "System")
        
        last_sound_time = time.time()
        with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype="int16", 
                               channels=1, callback=Assistant.audio_callback):
            while not shutdown_event.is_set():
                data = audio_queue.get()
                if recognizer.AcceptWaveform(data):
                    return json.loads(recognizer.Result()).get("text", "")
                
                # Timeout if silent
                if time.time() - last_sound_time > 5:
                    return json.loads(recognizer.FinalResult()).get("text", "")
        return ""

    @staticmethod
    def gui_prompt(text, speaker):
        """Passes text to GUI and triggers Piper if needed"""
        if speaker == "Speak":
            Gui.gui_prompt(text, "Ai")
            Assistant.speak(text)
        else:
            Gui.gui_prompt(text, speaker)

    @staticmethod
    def speak(text):
        """OFFLINE: Sends text to GuiLib's Piper engine"""
        print(f"[Piper] Saying: {text}")
        Gui.speak(text)

    @staticmethod
    def process_response(text):
        ai_reply = Assistant.ask_llama(text)
        if not Assistant.perform_action(ai_reply):
            Assistant.gui_prompt(ai_reply, "Speak")

    @staticmethod
    def perform_action(cmd):
        code, arguments = CP.get_input(cmd)
        if CP.test_code(code, arguments):
            output = CP.run_code(code, arguments)
            Assistant.gui_prompt(output, "Speak")
            return True
        return False
