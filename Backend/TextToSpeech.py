import pygame
import random
import asyncio
import edge_tts
import os
from dotenv import dotenv_values

env_vars = dotenv_values(".env")
Assistantvoice = env_vars.get("Assistantvoice", "en-US-JennyNeural")  # Default to a valid voice

AUDIO_FILE = "Data/speech.mp3"

async def TextToAudioFile(text):
    """ Convert text to speech and save as an MP3 file. """
    try:
        if os.path.exists(AUDIO_FILE):
            os.remove(AUDIO_FILE)

        communicate = edge_tts.Communicate(text, Assistantvoice)
        await communicate.save(AUDIO_FILE)
    except Exception as e:
        print(f"Error generating speech: {e}")

def play_audio():
    """ Play the generated audio file. """
    try:
        pygame.mixer.init()
        pygame.mixer.music.load(AUDIO_FILE)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

        pygame.mixer.quit()
    except Exception as e:
        print(f"Error playing audio: {e}")

def TTS(Text):
    """ Convert text to speech and play it. """
    try:
        asyncio.run(TextToAudioFile(Text))  # Run async function once
        play_audio()
    except Exception as e:
        print(f"Error in TTS: {e}")

def TextToSpeech(Text):
    """ Handle long text by splitting and playing parts of it. """
    sentences = Text.split(".")

    responses = [
        "The rest of the result has been printed to the chat screen, kindly check it out.",
        "You can see the rest of the text on the chat screen.",
        "The chat screen holds the continuation of the text.",
        "Please review the chat screen for the rest of the text.",
    ]

    if len(sentences) > 4 and len(Text) >= 250:
        TTS(" ".join(sentences[:2]) + ". " + random.choice(responses))
    else:
        TTS(Text)

if __name__ == "__main__":
    while True:
        user_input = input("Enter text: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Exiting...")
            break
        TextToSpeech(user_input)
