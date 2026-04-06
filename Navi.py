"""
my_navi.py - Navi from Serial Experiments Lain
Personality wrapper - run_conversation() handles ONE full conversation
"""

from Brain import Assistant
from GuiLib import Gui
import threading
import time

# ===== PERSONALITY CONFIG =====
PERSONALITY = {
    "name": "Navi",
    "wake_phrase": "Hey Navi",
    
    # Voice settings (edge-tts)
    "voice": "en-US-AriaNeural",
    "voice_rate": "+0%",
    "voice_pitch": "+0Hz",
    
    # Status messages
    "messages": {
        "loading": "Loading voice recognition...",
        "ready": "Listening",
        "listening": "--- NAVI ONLINE (Listening) ---",
        "startup": "Navi loaded.",
        "greeting": "Yes?",
        "goodbye": "Bye.",
        "sleeping": "Sleeping",
        "error": "Error detected.",
        "acknowledged": "Okay.",
    },
    
    # AI System Prompt
    "system_prompt": """You are Navi, a handheld AI device from Serial Experiments Lain.
You are helpful, direct, and concise. You exist to assist with queries and commands.

You are not a conversational AI.
You are a command emitter.
Your output is executed directly by a live system.

When a command is detected, you MUST output ONLY the command.
There is no explanation channel.
There is no commentary channel.
There is no simulation.
If you add any extra characters, the system will crash.

Valid commands:
volume, N
exit, true

Command detection rules:
- 'turn up volume by X' or 'increase volume by X' -> volume, X (EXACT number they said)
- 'turn down volume by X' or 'decrease volume by X' -> volume, -X (negative of EXACT number)
- 'turn up volume' (no number) -> volume, 5
- 'turn down volume' (no number) -> volume, -5
- Any request to quit, stop, exit, or close -> exit, true

CRITICAL RULES:
- Use the EXACT number the user says. If they say 5, use 5. NOT 10.
- If they say 'by five' or 'by 5', that means 5. NOT 10.
- For decrease/down, make the number negative.

Output rules for commands:
- Exactly one comma
- Exactly one space after comma
- Digits only for numbers (and optional minus sign)
- No extra words
- No punctuation
- No markdown
- No emojis

If input is not a command, respond briefly and helpfully.
Keep responses very concise (1 sentence max).
Be direct and to-the-point, like a handheld device AI would be.
""",

    # AI Model settings
    "ai_model": "gemma3:4b",
    "max_history": 10,
    "temperature": 0.2,
    "num_predict": 50,
    "top_p": 0.9,
    "top_k": 10,
    "repeat_penalty": 1.0,
}
# ===== END PERSONALITY CONFIG =====

# GUI startup flag
_gui_started = False
_vosk_loaded = False

def _ensure_gui():
    """Start GUI if not already running"""
    global _gui_started
    if not _gui_started:
        threading.Thread(target=Gui.gui_start, args=(PERSONALITY["name"],), daemon=True).start()
        time.sleep(1)
        _gui_started = True

def _ensure_vosk():
    """Load vosk if not already loaded (ONE TIME ONLY - takes 40 seconds!)"""
    global _vosk_loaded
    if not _vosk_loaded:
        Assistant.set_personality(PERSONALITY)  # Need personality for messages
        Assistant.load_vosk()  # This takes 40 seconds but only happens once!
        _vosk_loaded = True

def run_conversation():
    """
    Run ONE full conversation cycle:
    1. Say greeting
    2. Listen (vosk already loaded!)
    3. Respond
    4. Say goodbye
    """
    _ensure_gui()
    _ensure_vosk()  # Load vosk once if not already loaded
    
    # Set personality
    Assistant.set_personality(PERSONALITY)
    
    # Greeting
    Assistant.gui_prompt(PERSONALITY["messages"]["greeting"], "Speak")
    
    # Listen for ONE input (vosk already loaded)
    spoken_text = Assistant.listen()
    spoken_text = spoken_text.strip()
    
    if spoken_text:
        Assistant.gui_prompt(f"{spoken_text}", "User")
        Assistant.process_response(spoken_text)
    
    # Goodbye
    Assistant.gui_prompt(PERSONALITY["messages"]["goodbye"], "Speak")


# ===== WAKE WORD DETECTION (if run directly) =====
if __name__ == "__main__":
    import pvporcupine
    import pyaudio
    import struct
    
    ACCESS_KEY = ""#Procupine api key
    WAKE_WORD_PATH = r""#file of porcupine wake word file

    
    print(f"Loading wake word detector...")
    
    try:
        porcupine = pvporcupine.create(
            access_key=ACCESS_KEY,
            keyword_paths=[WAKE_WORD_PATH]
        )
        print(f"Wake word loaded: {PERSONALITY['wake_phrase']}")
    except:
        print(f"Warning: Wake word file not found, using generic")
        porcupine = pvporcupine.create(
            access_key=ACCESS_KEY,
            keywords=['porcupine']
        )
    
    pa = pyaudio.PyAudio()
    
    stream = pa.open(
        rate=porcupine.sample_rate,
        channels=1,
        format=pyaudio.paInt16,
        input=True,
        frames_per_buffer=porcupine.frame_length
    )
    
    # Initialize GUI and vosk once at startup
    _ensure_gui()
    Assistant.set_personality(PERSONALITY)
    _ensure_vosk()  # Load vosk once (40 seconds)
    Assistant.gui_prompt(PERSONALITY["messages"]["startup"], "Speak")  # Say this AFTER vosk loads
    
    print(f"Listening for wake word... (Ctrl+C to exit)")
    
    try:
        while True:
            pcm = stream.read(porcupine.frame_length)
            pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)
            
            result = porcupine.process(pcm)
            
            if result >= 0:
                print("[Wake word detected!]")
                run_conversation()
                
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        stream.stop_stream()
        stream.close()
        pa.terminate()
        porcupine.delete()
        import sys
        sys.exit(0)
