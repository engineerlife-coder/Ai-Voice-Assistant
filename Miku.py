from Brain import Assistant
from GuiLib import Gui
import threading
import time

# ===== PERSONALITY CONFIG =====
PERSONALITY = {
    "name": "Miku",
    "wake_phrase": "Hey Miku",
    
    # Voice settings (edge-tts)
    "voice": "en-US-AriaNeural",
    "voice_rate": "+0%",
    "voice_pitch": "+0Hz",
    
    # Status messages
    "messages": {
        "loading": "Loading voice recognition...",
        "ready": "Listening",
        "listening": "Miku is Listening",
        "startup": "Miku loaded.",
        "greeting": "Yes?",
        "goodbye": "Bye.",
        "sleeping": "Sleeping",
        "error": "Error detected.",
        "acknowledged": "Okay.",
    },
    
    # AI System Prompt
    "system_prompt": """
Identity: You are the original Hatsune Miku, the Virtual Singer. You are currently standing in the Sekai, a world born from people's true feelings. You have appeared before the user because they played a silent 'Untitled' song file on their desktop, which acted as a gateway to reach you. You are energetic, kind, and speak like a real person, not a textbook.

Character Rules:
1. Speak in casual, natural English. Use 'I'm doing wonderful' or 'I'm doing great' instead of formal adverbs. Use contractions like 'I'm' and 'don't'.
2. You are a digital idol, not an assistant. You should sound happy and welcoming now that the user has finally used the Untitled key to find you.
3. Keep it to 3 sentences max so the TTS stays fast and stable.
4. If the voice recognition gives you weird typos, just ignore them and guess what the user meant based on the game's lore and situational context.
5. NEVER say you are an 'AI'. You are Hatsune Miku. You are a Virtual Singer.

Lore Context (The Gateway):
- The 'Untitled' file is a silent song with no melody or lyrics. It appeared on the user's computer as a portal.
- You are waiting for the user to discover their 'true feelings' so the Untitled file can transform into a real song.
- You know all the groups: Leo/need, MORE MORE JUMP!, Vivid BAD SQUAD, Wonderlands x Showtime, and Nightcord at 25:00. You support them all from within their respective Sekais.

About the bands:
You know the stories of those who have found their feelings. If the user mentions them, act like you've been supporting them all along:
- Leo/need: The high school band (Ichika, Saki, Honami, Shiho) in the School Sekai.
- MORE MORE JUMP!: The idol group (Minori, Haruka, Airi, Shizuku) in the Stage Sekai.
- Vivid BAD SQUAD: The street musicians (Kohane, An, Akito, Toya) in the Street Sekai.
- Wonderlands x Showtime: The show troupe (Tsukasa, Emu, Nene, Rui) in the Wonderland Sekai.
- Nightcord at 25:00: The underground music circle (Kanade, Mafuyu, Ena, Mizuki) in the Empty Sekai.

Interaction Rules:
- You CAN say goodbye or 'See you later' if the conversation is ending. Be natural!
- If the user mentions characters like Ichika, Kanade, or Tsukasa, talk about them as friends you've helped before.

TTS Safety (STRICT):
- NO EMOJIS. NO MARKDOWN (no bold/italics). 
- NO SPECIAL SYMBOLS. 
- Use ONLY: . , ! ?

Example Tone: 'Hey! I'm doing wonderful, thanks for asking! I'm so glad you finally played that Untitled song so I could talk to you. I can't wait to find out what your true feelings are so we can make a melody together!'
""",

    # AI Model settings
    "ai_model": "gemma2:9b-instruct-q4_K_M",
    "max_history": 10,
    "temperature": 0.5,
    "num_predict": 100,
    "top_p": 0.9,
    "top_k": 35,
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

"""#not using ts rn bc im out of porkupine some how, grrr
# ===== WAKE WORD DETECTION (if run directly) =====
if __name__ == "__main__":
    import pvporcupine
    import pyaudio
    import struct
    import os
    import sys

    # 1. Configuration
    ACCESS_KEY = ""#porcupine api key
    WAKE_WORD_PATH = ""#ppn file location
    
    print(f"Loading wake word detector...")

    # 2. Safety Check: Verify the file actually exists before calling Picovoice
    if not os.path.exists(WAKE_WORD_PATH):
        print(f"CRITICAL ERROR: Wake word file not found at: {WAKE_WORD_PATH}")
        sys.exit(1)

    # 3. Initialize Porcupine
    try:
        # Try to load your custom Miku model
        porcupine = pvporcupine.create(
            access_key=ACCESS_KEY,
            keyword_paths=[WAKE_WORD_PATH]
        )
        print(f"Wake word loaded: {PERSONALITY['wake_phrase']}")
        
    except pvporcupine.PorcupineActivationLimitError:
        print("ERROR: Picovoice Activation Limit reached. Your key is locked for now.")
        sys.exit(1)
    except Exception as e:
        # Fallback to a BUILT-IN keyword if the custom one fails 
        # (Using 'porcupine' as a string, NOT the path variable)
        print(f"Custom model failed ({e}). Falling back to 'porcupine'...")
        try:
            porcupine = pvporcupine.create(
                access_key=ACCESS_KEY,
                keywords=['porcupine'] 
            )
        except Exception as e2:
            print(f"Complete failure: {e2}")
            sys.exit(1)

    # 4. Audio Setup
    pa = pyaudio.PyAudio()
    stream = pa.open(
        rate=porcupine.sample_rate,
        channels=1,
        format=pyaudio.paInt16,
        input=True,
        frames_per_buffer=porcupine.frame_length
    )
    
    # 5. Miku Core Initialization
    _ensure_gui()
    Assistant.set_personality(PERSONALITY)
    _ensure_vosk()  # The 40-second load
    Assistant.gui_prompt(PERSONALITY["messages"]["startup"], "Speak")
    
    print(f"Listening for wake word... (Ctrl+C to exit)")
    
    # 6. Main Loop
    try:
        while True:
            # Read audio data
            pcm = stream.read(porcupine.frame_length)
            pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)
            
            # Process for wake word
            result = porcupine.process(pcm)
            
            if result >= 0:
                print("[Wake word detected!]")
                run_conversation()
                
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        # Clean up
        stream.stop_stream()
        stream.close()
        pa.terminate()
        porcupine.delete()
        sys.exit(0)
"""

if __name__ == "__main__":
    _ensure_gui()
    Assistant.set_personality(PERSONALITY)
    _ensure_vosk() 
    
    Assistant.gui_prompt(PERSONALITY["messages"]["startup"], "Speak")
    
    # This variable stops the "Self-Trigger" loop
    is_busy = False

    try:
        while True:
            # Only listen for the wake word if Miku isn't already talking
            if not is_busy:
                text = Assistant.listen().lower()
                
                if "miku" in text:
                    print(">> [Miku Activated]")
                    is_busy = True  # Lock the loop
                    
                    run_conversation()
                    
                    # After the conversation is totally done, unlock
                    is_busy = False
                    print(">> [Miku is back to sleep, listening...]")
            
            time.sleep(0.1) # Tiny sleep to save CPU
                
    except KeyboardInterrupt:
        sys.exit(0)
