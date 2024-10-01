import logging
import asyncio
from pathlib import Path
import os
import sys
import pygame
from gtts import gTTS
import tempfile

class Speaker:
    def __init__(self, client=None, enable_tts=True):
        self.logger = logging.getLogger(__name__)
        self.logger.debug("Initializing Speaker class")
        self.client = client
        self.enable_tts = enable_tts
        self.speech_queue = asyncio.Queue()
        self.speech_task = None
        pygame.mixer.init()

    async def speak(self, message):
        if not self.enable_tts:
            self.logger.debug("TTS is disabled, skipping speech")
            return
        await self.speech_queue.put(message)
        if self.speech_task is None or self.speech_task.done():
            self.speech_task = asyncio.create_task(self._process_speech_queue())

    async def _process_speech_queue(self):
        while not self.speech_queue.empty():
            message = await self.speech_queue.get()
            await self._speak_pygame(message)

    async def _speak_pygame(self, message):
        self.logger.debug(f"Attempting to speak: {message[:50]}...")
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
                tts = gTTS(text=message, lang='en')
                tts.save(temp_file.name)
                
            pygame.mixer.music.load(temp_file.name)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                await asyncio.sleep(0.1)
            
            os.unlink(temp_file.name)
            self.logger.debug("Speech completed successfully")
        except Exception as e:
            self.logger.error(f"Error in _speak_pygame: {str(e)}")

        await asyncio.sleep(0.1)  # Add a small delay here
        self.logger.info(f"TTS: {message.encode('utf-8', errors='ignore').decode('utf-8')}")

    async def stop(self):
        if self.speech_task:
            self.speech_task.cancel()
            try:
                await self.speech_task
            except asyncio.CancelledError:
                pass
        if pygame.mixer.get_init():
            pygame.mixer.music.stop()
            pygame.mixer.quit()
        self.logger.debug("TTS stopped")