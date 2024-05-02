import pyttsx3
from openai import OpenAI
from pathlib import Path
import pygame
import os
import sys

# Redirect stderr to a null device
sys.stderr = open(os.devnull, 'w')

class Speaker:
    def __init__(self, client=None, enable_tts=True):
        self.client = client
        self.enable_tts = enable_tts
        if not client:
            import pyttsx3
            self.engine = pyttsx3.init()
            voices = self.engine.getProperty('voices')
            self.engine.setProperty('voice', voices[1].id)

    def speak(self, message):
        if not self.enable_tts:
            return ""
        if self.client is None:
            self.engine.say(message)
            self.engine.runAndWait()
        else:
            from pathlib import Path
            try:
                speech_file_path = Path(__file__).parent / "speech.mp3"
                response = self.client.audio.speech.create(
                    model="tts-1",
                    voice="nova",
                    input=message,
                )
                audio_content = response.content
                with open(speech_file_path, 'wb') as audio_file:
                    audio_file.write(audio_content)
                try:
                    pygame.mixer.init()
                    pygame.mixer.music.load(str(speech_file_path))
                    pygame.mixer.music.play()
                    while pygame.mixer.music.get_busy():
                        pygame.time.Clock().tick(10)
                    pygame.mixer.quit()
                except Exception as e:
                    print(f"Error playing sound: {str(e)}")
                finally:
                    speech_file_path.unlink(missing_ok=True)
            except Exception as e:
                print(f"Error generating speech: {str(e)}")