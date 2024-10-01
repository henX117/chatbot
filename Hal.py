import os
os.environ['PYTHONIOENCODING'] = 'utf-8'
import logging
from logging.handlers import RotatingFileHandler
import asyncio
from collections import deque, OrderedDict
import requests
from datetime import datetime, timedelta
from openai import OpenAI
from logic.intents import logical
from logic.utils.speaking import Speaker
from logic.api_keys import OPENAI_API_KEY, WEATHER_API_KEY, JOKES_API_KEY
import aiohttp
import json
import sys

def setup_logging(log_file='Hal.log', max_log_size=5*1024*1024, backup_count=3):
    try:
        log_dir = os.path.join(os.path.dirname(__file__), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        log_path = os.path.join(log_dir, log_file)
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        
        # Remove existing handlers
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
            
        # File handler
        file_handler = RotatingFileHandler(log_path, maxBytes=max_log_size, backupCount=backup_count, encoding = 'utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(filename)s - %(lineno)d - %(message)s')
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        null_handler = logging.NullHandler()
        logger.addHandler(null_handler)
        
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
        
        logging.getLogger('gtts').setLevel(logging.ERROR)
        
        logger.debug(f"Logging has been set up successfully.")
        return logger
    except Exception as e:
        print(f"Error setting up logging: {e}", file=sys.stderr)
        raise

class OllamaAPI:
    def __init__(self, base_url="http://localhost:11434"):
        self.base_url = base_url
        self.logger = logging.getLogger(__name__)

    async def generate_response(self, prompt, model="llama3.1:latest"):
        self.logger.debug(f"Generating response for prompt: {prompt[:50]}...")
        url = f"{self.base_url}/api/generate"
        data = {
            "model": model,
            "prompt": prompt,
            "stream": True,        
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data, timeout=30) as response:
                    response.raise_for_status()
                    full_response = ""
                    async for line in response.content:
                        if line:
                            chunk = json.loads(line)
                            if 'response' in chunk:
                                full_response += chunk['response']
                    self.logger.debug(f"Received response from Ollama API: {full_response[:50]}...")
                    return full_response
        except aiohttp.ClientError as http_err:
            self.logger.error(f"HTTP error occurred in generate_response: {http_err}")
        except ValueError as val_err:
            self.logger.error(f"Value error occurred in generate_response: {val_err}")
        except Exception as e:
            self.logger.error(f"An unexpected error occurred in generate_response: {e}")
        return None     

class Chatbot(logical):
    def __init__(self, api_key, client=None, enable_tts=True):
        super().__init__(api_key, client=client, enable_tts=enable_tts)
        self.logger = logging.getLogger(__name__)
        self.logger.debug("Initializing Chatbot...")
        self.ENABLE_TTS = enable_tts
        self.conversation_history = deque(maxlen=10)
        self.HIGH_CONFIDENCE_THRESHOLD = 0.7
        self.ollama_api = OllamaAPI()
        self.cache = OrderedDict()
        self.cache_max_size = 1000
        self.cache_expiration = timedelta(hours=1)
        self.llm_available = self.check_llm_availability()
        self.intent_handlers = self.setup_intent_handlers()
        self.name = self.get_user_name()
        self.memory = {}
        self.speaker = Speaker(client=self.client, enable_tts = self.ENABLE_TTS)
    
    async def speak_and_return(self, message):
        if self.ENABLE_TTS:
            await self.speaker.speak(message)
        return message

    async def enable_tts(self, user_input=None, filled_slots=None):
        self.ENABLE_TTS = True
        self.speaker.enable_tts = True
        self.logger.info("TTS enabled")
        response = "TTS enabled"
        return await self.speak_and_return(response)

    async def disable_tts(self, user_input=None, filled_slots=None):
        self.ENABLE_TTS = False
        self.speaker.enable_tts = False
        self.logger.info("TTS disabled")
        response = "TTS disabled"
        return await self.speak_and_return(response)

    async def quitter(self, user_input, filled_slots):
        command = input(f"Are you sure you want to quit, {self.name}? Any progress will NOT be saved.\nType 'quit' to quit. Type anything else to stay: ")
        if command.lower() == 'quit':
            await self.speak_and_return("Goodbye!")
            self.logger.info("User initiated quit. Exiting program.")
            await self.cleanup()
            sys.exit(0)
        else:
            return await self.speak_and_return(f'Alright. What do you want to do now, {self.name}?')

    async def main(self):
        self.logger.info("Starting main chatbot loop...")
        try:
            intro = await self.introduction()
            print(await self.speak_and_return(intro))
            while True:
                command = await asyncio.get_event_loop().run_in_executor(None, input, "")
                command = command.strip().lower()
                self.logger.debug(f"Received command: {command}")
                if command == "":
                    response = await self.typeSomething()
                else:
                    intent = self.find_intent(command)
                    if intent in ["huh", "conversation", "greetings", "how_are_you", "thanks"]:
                        response = await self.handle_conversation(command)
                    elif intent in self.intents:
                        intent_info = self.intents[intent]
                        if isinstance(intent_info, tuple):
                            _, handler = intent_info
                            response = await handler(command, {})
                        elif isinstance(intent_info, dict):
                            slot_values = await self.extract_slot_values(command, intent)
                            filled_slots = await self.fill_slots(intent, slot_values)
                            response = await intent_info["handler"](command, filled_slots)
                        else:
                            response = "I'm not sure how to handle that request."
                    else:
                        if self.llm_available:
                            response = await self.handle_conversation(command)
                        else:
                            response = "I'm not sure how to respond to that."
                print(response)
                await self.check_reminders()
        except KeyboardInterrupt:
            await self.speak_and_return("\nExiting the chatbot. Goodbye!")
        finally:
            self.logger.info("Chatbot shutting down...")
            await self.cleanup()

    async def cleanup(self):
        try:
            await self.speaker.stop()
        except Exception as e:
            self.logger.error(f"error during cleanup: {e}")
        self.logger.debug("Cleanup complete")
    
    def get_user_name(self):
        user_name_file = os.path.join(os.path.dirname(__file__), 'user_name.txt')
        if os.path.exists(user_name_file):
            with open(user_name_file, 'r') as f:
                return f.read().strip()
        return "User"
    
    def check_llm_availability(self):
        self.logger.debug("Checking LLM availability...")
        try:
            response = requests.get(f"{self.ollama_api.base_url}/api/tags", timeout=5)
            response.raise_for_status()
            data = response.json()
            
            if not isinstance(data, dict) or 'models' not in data:
                self.logger.error("Unexpected response format from Ollama API")
                return False
            
            models = data['models']
            self.logger.info(f"Available models: {[model['name'] for model in models]}")
            
            desired_model = "llama2:latest"
            
            for model in models:
                if model['name'] == desired_model:
                    self.logger.info(f"Model '{desired_model}' is available.")
                    return True
            
            self.logger.warning(f"Model '{desired_model}' is not available.")
            return False
        except requests.RequestException as e:
            self.logger.error(f"Error checking model availability: {e}")
            return False
        except (KeyError, TypeError) as e:
            self.logger.error(f"Error parsing response from Ollama API: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error checking model availability: {e}")
            return False

    def setup_intent_handlers(self):
        if not self.llm_available:
            return {
                "greetings": self.handle_greeting,
                "how_are_you": self.howareyou,
                "thanks": self.thanks,
            }
        else:
            return {}
        
    def format_conversation_history(self):
        return "\n".join([f"{self.name if speaker == self.name else speaker}: {message}" for speaker, message in self.conversation_history])

    async def query_llm(self, prompt):
        self.logger.debug(f"Querying LLM with prompt: {prompt[:50]}...")
        cache_key = prompt
        if cache_key in self.cache:
            cached_response, timestamp = self.cache[cache_key]
            if datetime.now() - timestamp < self.cache_expiration:
                return cached_response

        response = await self.ollama_api.generate_response(prompt)
        
        if response:
            self.logger.debug("Caching new response")
            self.cache[cache_key] = (response, datetime.now())
            if len(self.cache) > self.cache_max_size:
                self.logger.debug("Cache full, removing oldest item")
                self.cache.popitem(last=False)
        
        return response

    def format_memory(self):
        return "\n".join([f"{key}: {value}" for key, value in self.memory.items()])

    def update_memory(self, key, value):
        self.memory[key] = value

    async def handle_conversation(self, user_input):
        memory_prompt = self.format_memory()
        prompt = f"""
        You are Hal, an AI assistant. Respond to {self.name}'s input in a very short, yet helpful and friendly manner. Always refer to the user as {self.name}.
        Recent conversation history:
        {self.format_conversation_history()}
        {memory_prompt}
        
        User's latest input: {user_input}
        
        Your response:
        """
        response = await self.query_llm(prompt)
        if response is None:
            return await self.speak_and_return("I'm unable to speak at this time.")
        self.conversation_history.append((self.name, user_input))
        self.conversation_history.append(("Hal", response))
        return await self.speak_and_return(response)

async def main():
    logger = setup_logging()
    logger.info("Starting chatbot...")
    
    try:
        enable_tts = True  # Set to False if you want to disable text-to-speech
        script_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(script_dir)
        logger.info(f"Current working directory: {script_dir}")
        
        user_name_file = os.path.join(script_dir, 'user_name.txt')
        
        if not os.path.exists(user_name_file):
            logger.info("Username file not found. Creating a new one.")
            name = input("Enter your name: ")
            with open(user_name_file, 'w') as f:
                f.write(name)
        else:
            with open(user_name_file, 'r') as f:
                name = f.read().strip()
            logger.info(f"Welcome back, {name}!")
        
        api_key = OPENAI_API_KEY
        if not api_key:
            logger.warning("OpenAI API key not found. Some features may be limited.")
        
        client = OpenAI(api_key=api_key) if api_key else None
        logger.info("Initializing chatbot...")
        chatbot = Chatbot(api_key, client=client, enable_tts=enable_tts)
        
        os.system('cls' if os.name == 'nt' else 'clear')
        logger.info("Chatbot initialized. Starting main loop.")
        await chatbot.main()
    except SystemExit:
        logger.info("Chatbot terminated by user.")
    except KeyboardInterrupt:
        logger.info("Chatbot terminated by user.")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}", exc_info=True)
    finally:
        if 'chatbot' in locals():
            await chatbot.cleanup()
        logger.info("Chatbot shutting down...")

if __name__ == "__main__":
    asyncio.run(main())