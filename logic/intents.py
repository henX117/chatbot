import os
import logging
import spacy
from spacy.tokens import Doc
import webbrowser
from spacy.matcher import Matcher
import warnings
import requests
import platform
import random
import wikipedia
import inflect
from datetime import datetime
import threading
import time
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore")
import string
from AppOpener import open as open_app
from gtts import gTTS
import sys
import subprocess
from pathlib import Path
from openai import OpenAI
import asyncio
import aiohttp
from .utils.pomodoro import Pomodoro
from .utils.speaking import Speaker
from .utils.text_sum import TextSummarizer
from openai import OpenAI
import re
try:
    from logic.api_keys import OPENAI_API_KEY, WEATHER_API_KEY, JOKES_API_KEY
except ImportError:
    OPENAI_API_KEY = None
    WEATHER_API_KEY = None
    JOKES_API_KEY = None
    print("Warning: API Keys not found. Some features may not work as intended...")
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

class logical:
    def __init__(self, api_key, client=None, enable_tts=False,):
        self.logger = logging.getLogger(__name__)
        self.logger.debug("Initializing logical class")
        self.ENABLE_TTS = enable_tts
        try:
            if api_key:
                self.client = OpenAI(api_key=api_key)
            else:
                self.client = None
                self.logger.warning("No API key provided. Using pyttsx3 for TTS.")
        except Exception as e:
            self.logger.error(f"Error initializing OpenAI client: {str(e)}")
            self.client = None
        self.speaker = Speaker(client=self.client, enable_tts=self.ENABLE_TTS)

        self.chatbot = 'Hal'
        self.fullchatbot = 'Halsey'
        current_dir = os.getcwd()
        self.logger.info(f"Current working directory: {current_dir}")
        file_path = 'user_name.txt'
        self.logger.info(f"looking for file: {file_path}")
        if not os.path.exists(file_path):
            print("Username file not found. Please run setup.py to create the file.")
            self.logger.error("Username file not found. Exiting...")
            input("Press Enter to exit...")
            sys.exit(1)
            
        with open('user_name.txt', 'r') as f:
            self.name = f.read().strip()

        self.client = client
        self.reminders = []
        model_dir = os.path.join(os.path.dirname(__file__), "SpaCy")
        self.nlp = spacy.load(model_dir)
        self.intents = get_intents(self)
        self.intent_templates = self.preprocess_intent_templates()
        self.matcher = Matcher(self.nlp.vocab)
        pattern = [{"LOWER": "open"}, {"IS_ALPHA": True}]
        self.matcher.add("OPEN_APP", [pattern])
        self.known_apps = ['spotify', 'chrome', 'word', 'excel']
        self.reminder_thread = threading.Thread(target=self.reminder_loop)
        self.reminder_thread.daemon = True
        self.reminder_thread.start()
        self.weather_cache = {}
        self.weather_cache_expiration = 300
        self.pomodoro_timer = Pomodoro()
        self.commands = {
            "app": "Opens an app",
            "cls": "clears the screen",
            "math": "to do mathematics!",
            "quit": "to leave the program",
            'analyze': "to analyze text",
            "time": "tells the current time",
            "open app": "opens an app",
            "close app": "closes an app",
            "joke": "tells a joke",
            "news": "see whats on the headlines",
            "weather": "get weather information",
            "rock paper scissors": "play the rock paper scissors game",
            "windows": "shows what version of windows OS is using",
            "remind": "set a reminder",
            "wiki": "search Wikipedia",
            "lottery": "generates random lottery numbers",
            "random numbers": "generates random numbers in a specific range that the user chooses",
            "generate image": "generates an image based on user input (only works if you have an openai api key)",
            "roll a dice": "rolls a dice and gives the user a number",
            "enable tts": "enables text to speech",
            "disable tts": "disables text to speech",
            "copy": "the bot will copy the next thing that the user types",
            "calculate interest": "opens the compound interest calculator",
            "merge pdf": "merges pdf files into one. place the files in the 'PLACE_PDFs_HERE' folder.",
            "png to pdf": "turns a png into a pdf. Place the png into the 'PLACE_PDFs_HERE' folder.",
            "time conversion": "converts hours into weeks, days, and hours",
            "pass check": "checks if a password is strong",
            "start pomodoro": "starts a pomodoro timer",
            "stop pomodoro": "stops the pomodoro timer",
            "api key": f"weather api key: {WEATHER_API_KEY}",
            "cypher": "encrypts and decrypts text using a cypher",
            "decipher": "decrypts text without a cipher",
        }
        
    def preprocess_intent_templates(self):
        intent_templates = {}
        for intent, value in self.intents.items():
            if isinstance(value, tuple):
                templates, _ = value
            elif isinstance(value, dict):
                templates = value["patterns"]
            else:
                raise ValueError(f"Invalid intent value for {intent}")
            intent_templates[intent] = [self.nlp(template) for template in templates]
        return intent_templates
    
    async def start_pomo(self, user_input, filled_slots): #Work session started<coroutine object Chatbot.speak_and_return at 0x00000142466E8520>
        self.pomodoro_timer.start_timer()
        return self.speak_and_return("Pomodoro timer started.")
    
    async def stop_pomo(self, user_input, filled_slots): #I'm unable to speak at this time"
        self.pomodoro_timer.stop_timer()
        return self.speak_and_return("Pomodoro timer stopped.")

    async def lottery(self, num_tickets=1): #needs better handling of use input (ex: Generate 5 lottery tickets WORKS BUT Generate like 5 lottery tickets please DOES NOT WORK)
        tickets = []
        for _ in range(num_tickets):
            regular_numbers = random.sample(range(1, 70), 5)
            special_number = random.randint(1, 25)
            ticket = (tuple(sorted(regular_numbers)), special_number)
            tickets.append(ticket)
        print("-----Generated Lottery Tickets-----")
        for i, ticket in enumerate(tickets, start=1):
            regular_numbers, special_number = ticket
            print(f"Ticket {i}: Regular numbers: {regular_numbers}, Special number: {special_number}")
        return ""

    async def randomnumgen(self, user_input, filled_slots): #<coroutine object Chatbot.speak_and_return at 0x0000019A7E4336B0>
        whatrange = int(input("Enter starting range -> "))
        lastrange = int(input("Enter ending range -> "))
        number = random.randint(whatrange,lastrange)
        if self.ENABLE_TTS:
            return await self.speak_and_return (number)
        else:
            return (number)
        
    async def dalle(self, user_input, filled_slots): #NO API given, still lets me run this intent? 
        print("----Image Generator with Dalle-----\n--type 'quit' to return to the main menu--")
        resp = str(input("Type the image that you would like to be generated\n"))
        if resp == 'quit':
            return self.main()
        else:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        "https://api.openai.com/v1/images/generations",
                        headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
                        json={
                            "model": "dall-e-3",
                            "prompt": resp,
                            "size": "1024x1024",
                            "quality": "standard",
                            "n": 1,
                        },
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            image_url = data["output"][0]["url"]
                            return image_url
                        elif response.status == 401:
                            return self.speak_and_return("Invalid API key. Please check the API key and try again.")
                        elif response.status == 429:
                            return self.speak_and_return("API rate limit exceeded. Please try again later.")
                        else:
                            return (f"API request failed with status code {response.status}")
            except aiohttp.ClientError as e:
                return (f"Network error occurred: {str(e)}")
            except asyncio.TimeoutError:
                return await self.speak_and_return("The API request timed out. Please try again later.")
            except Exception as e:
                return await self.speak_and_return(f"An unexpected error occurred: {e}")

    async def morningornah(self, user_input=None, filled_slots=None):
        current_time = datetime.now()
        hour = current_time.hour
        if 5 <= hour <= 11:
            return "Morning"
        elif 12 <= hour <= 16:
            return "Afternoon"
        elif 17 <= hour <= 24 or 0 <= hour <= 4:
            return "Evening"
        else:
            return ""

    async def speak_and_return(self, message):
        if self.ENABLE_TTS:
          await self.speaker.speak(message)
        return message  
    
    async def diceroll(self, user_input, filled_slots): 
        print("---------------------------------------------------")
        from logic.games import DiceRoll
        dice_game = DiceRoll()
        result = dice_game.roll()
        return await self.speak_and_return(f"You rolled a {result}!")

    async def rockpaperscissors(self, user_input=None, filled_slots=None):
        print("---------------------------------------------------")
        from logic.games import RockPaperScissors
        game = RockPaperScissors() 
        game.play_game() 
        responses = [
            "That was fun! Let's play again later!",
            f"good game, {self.name}",
        ]
        X = random.choice(responses)
        return await self.speak_and_return (X)
    
    async def ineedhelp(self, user_input, filled_slots):
        os.system('cls' if os.name == 'nt' else 'clear')
        if self.ENABLE_TTS:
            await self.speak_and_return(f"Here's a list of helpful commands, {self.name}.")
        else:
            print(f"Here is a list of helpful commands,{self.name}.")
        commands_table = ""
        max_command_length = max(len(command) for command in self.commands.keys())

        for command, description in self.commands.items():
            padded_command = command.ljust(max_command_length)
            commands_table += f"{padded_command} : {description}\n"
        return commands_table

    async def extract_app_name(self, command):
        doc = self.nlp(command)
        for match_id, start, end in self.matcher(doc):
            span = doc[start:end]
            if span.text:
                return span.text.split(" ")[1]  # Return app name after "open"
        return None

    async def openapp(self, user_input=None, filled_slots=None): #said "open excel please -> I'm not sure how to respond to that.
        self.speaker.speak("What app do you want to open?")
        print("type 'cancel' to stop trying to open an app")
        command = input("I want to open the app called: ")
        if command == 'cancel':
            return self.main()
        else:
            app_name = command
            if app_name:
                try:
                    import AppOpener
                    print(f"Attempting to open {app_name}") #should just have ONE print statement that can also speak if TTS is enabled.
                    self.speaker.speak(f"Attempting to open {app_name}")
                    AppOpener.open(app_name)
                except Exception as e:
                    print(f"Error trying to open {app_name}: {str(e)}")
            else:
                print("Sorry, I couldn't identify the app that you want to open.")
            if self.ENABLE_TTS:
                await self.speak_and_return(f"what else would you like to do, {self.name}?")
            else:
                print(f"What else would you like to do, {self.name}?")
            return "" 

    async def closeapp(self, user_input, filled_slots): 
        self.speaker.speak(f"What app do you want to close {self.name}")
        command = input(f"What app do you want to close, {self.name}?\n")
        try:
            from AppOpener import close
            print(f"attempting to close {command}...")
            close(command)
            return""
        except RuntimeError:
            return self.speak_and_return(f"{command} does not want to cooperate and close. try again??")
        except Exception as e:
            print(f"Error trying to close {command}: {str(e)}")
            return ""


    async def analyze_sentence(self, user_input, filled_slots):
        await self.speaker.speak("Please enter the text that you want to analyze:")
        loop = asyncio.get_event_loop()
        command = await loop.run_in_executor(None, input, "Enter the text that you want to analyze:\n ")

        await self.speaker.speak("Do you want a text summarization or a visualization analysis?")
        which_analysis = await loop.run_in_executor(None, input, "Which analysis do you want?\nText summary (1)\nVisualization (2)\nQuit (3)\n--> ")
    
        if which_analysis == '1':
            try:
                from .utils.text_sum import TextSummarizer
                num_sentences_str = await loop.run_in_executor(None, input, "Enter the number of sentences in the summary: ")
                num_sentences = int(num_sentences_str)
                summarizer = TextSummarizer()
                summary = summarizer.summarize(command, num_sentences)
                return await self.speak_and_return(f"Here's the summary:\n{summary}")
            except Exception as L:
                await self.speaker.speak(f"Sorry, {self.name}. I had an issue with getting analysis on that.")
                return str(L)
    
        elif which_analysis == '2':
            try:
                from spacy import displacy
                await self.speaker.speak("Do you want a large analysis or small analysis?")
                which_nlp = await loop.run_in_executor(None, input, "Which analysis do you want? 'small' or 'large'?\n")
                which_nlp = which_nlp.strip().lower()
            
                if which_nlp == 'small' or which_nlp == '1':
                    nlp = spacy.load("en_core_web_sm")
                elif which_nlp == 'large' or which_nlp == '2':
                    nlp = spacy.load("en_core_web_lg")
                else:
                    await self.speak_and_return("Invalid analysis option.. I'm going to go with a small analysis for you.")
                    nlp = spacy.load("en_core_web_sm")
            
                doc = nlp(command)
                sentences = list(doc.sents)
            
                # Perform Named Entity Recognition
                entities = [(ent.text, ent.label_) for ent in doc.ents]
                if entities:
                    await self.speaker.speak("Named Entities found:")
                    for entity in entities:
                        # You can await inside a loop
                        await self.speaker.speak(f"{entity[0]} - {entity[1]}")
            
                # Perform visualization analysis
                html_ent = displacy.render(sentences, style="ent")
                html_dep = displacy.render(sentences, style='dep')
                html_combined = "<html><head><title>SpaCy Analysis</title></head><body>" + html_ent + html_dep + "</body></html>"
            
                output_path = "data_vis_analysis.html"
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(html_combined)
            
                await self.speaker.speak(f"Visualization analysis completed. Opening {output_path} in the web browser.")
                webbrowser.open(output_path)
            
                return "Visualization analysis completed."

            except Exception as e:
                error_message = f"An unexpected error occurred during visualization: {e}"
                await self.speaker.speak(error_message)
                return error_message
            
        elif which_analysis == '3':
            # Assuming self.main() is an async function or leads to one. 
            # If main isn't async, this might need adjustment.
            # For now, just returning a message is safer.
            return "Returning to main menu."
        else:
            return await self.speak_and_return("Invalid analysis option. Please choose '1' for text summary or '2' for visualization.")
        
    async def cls(self, user_input, filled_slots):
        os.system('cls' if os.name == 'nt' else 'clear')
        responses = [
            f"system cleared. Enjoy the view!",
            f"system cleared.",
            f"wow! there's so much space!",
            f"woah where did everything go?",
            f"systems clean, {self.name}",
            f"all done! What do you want to do next?",
            f"system cleared. what's next?",
            f"{self.name}, the system has been cleared.",
            f"{self.name}, the system has been cleared. Enjoy the view!",
            f"ah, such empty space!",
            f"this is as empty as my bank account!",
            f"kachow. everything vanished.",
            f"error, task failed successfully.",
        ]
        response = random.choice(responses)
        return await self.speak_and_return(response)

    async def quitter(self, user_input, filled_slots):
        command = input(f"Are you sure you want to quit, {self.name}? Any progress will NOT be saved.\nType 'quit' to quit. Type anything else to stay: ")
        if command.lower() == 'quit':
            print("Goodbye!")
            await self.speak_and_return("Goodbye!")
            self.logger.info("User initiated quit. Exiting program.")
            return "QUIT"
        else:
            return await self.speak_and_return(f'Alright. What do you want to do now, {self.name}?')

    async def math(self, user_input, filled_slots): #typed 'help' and chatbot CRASHED
        from .utils.math import MathHelper
        math_helper = MathHelper()
        user_input = input("What math operation would you like to perform?\nType 'help' to see all math operations available\n--> ").lower()
        operation = math_helper.find_operation(user_input)
        
        if operation == 'help':
            result = math_helper.help()
            print(result)
            return self.math()
        if operation == 'quit':
            return self.main()
        
        if operation == 'graph':
            expression = input("Enter the mathematical expression: ")
            try:
                math_helper.graph(expression)
                return await self.speak_and_return("Graph has been displayed.")
            except Exception as L:
                return await self.speak_and_return(L)

        if operation == 'statistics':
            stat_operation = input("Enter the statistical operation (mean, median, mode, stdev, variance)\n")
            data = input("Enter the data points (comma-separated):\n")
            try:
                result = math_helper.statistics(stat_operation, data)
                return await self.speak_and_return(f"the {stat_operation} is {result}")
            except Exception as L:
                return await self.speak_and_return(L)
        
        if operation == 'finite series sum':
            series_type = input("Enter the series type (arithmetic or geometric): ")
            a = float(input("Enter the first term: "))
            n = int(input("Enter the number of terms: "))
            if series_type == 'arithmetic':
                r = float(input("Enter the common difference: "))
                result = math_helper.finite_series_sum(series_type, a, n, r)
            elif series_type == 'geometric':
                r = float(input("Enter the common ration: "))
                result = math_helper.finite_series_sum(series_type, a, n, r)
            else:
                return await self.speak_and_return("invalid series type.")
            return await self.speak_and_return(f"The sum of the series {series_type} series is: {result}")

        if operation == 'system of equations':
            equations = []
            while True:
                equation = input("Enter an equation (or press Enter to finish): ")
                if equation == "":
                    break
                equations.append(equation)
            result = math_helper.solve_system_of_equations(equations)
            return await self.speak_and_return(f"The solution to the system of equations is: {result}")
        
        if operation == 'summation':
            expression = input("Enter the expression: ")
            lower_limit = input("Enter the lower limit: ")
            upper_limit = input("Enter the upper limit: ")
            variable = input("Enter the variable: ")
            result = math_helper.summation(expression, lower_limit, upper_limit, variable)
            return await self.speak_and_return(f"The summation is: {result}")

        if operation == 'limit':
            expression = input("Enter the expression: ")
            variable = input("Enter the variable: ")
            approaching_value = input("Enter the approaching value: ")
            result = math_helper.limit(expression, variable, approaching_value)
            return await self.speak_and_return(f"The limit is: {result}")

        if operation == 'derivative':
            expression = input("Enter the mathematical expression: ")
            result = math_helper.derivative(expression)
            return await self.speak_and_return(f"The derivative is: {result}")

        if operation == 'equation':
            equation = input("Enter the equation: ")
            variable = input("Enter the variable to solve for: ")
            result = math_helper.equation(equation, variable)
            return await self.speak_and_return(f"The solution is: {result}")

        if operation in ['add', 'subtract', 'multiply', 'divide', 'power']:
            num_args = 2
            args = []
            for i in range(num_args):
                arg = float(input(f"Enter argument {i + 1}: "))
                args.append(arg)

            try:
                result = math_helper.perform_operation(operation, *args)
                return await self.speak_and_return(f"The result is: {result}")
            except Exception as L:
                return await self.speak_and_return(L)

        if operation == 'square root':
            num = float(input("Enter the number: "))
            try:
                result = math_helper.perform_operation(operation, num)
                return await self.speak_and_return(f"The square root is: {result}")
            except Exception as L:
                return await self.speak_and_return(L)

        if not operation:
            return self.speak_and_return("Unsupported math operation")

    async def get_weather(self, user_input, filled_slots):
        if not filled_slots or "location" not in filled_slots:
            location = input("Please provide the location: ")
            filled_slots["location"] = location
        else:
            location = filled_slots["location"]

        api_key = WEATHER_API_KEY
        base_url = "http://api.weatherstack.com/current"
        params = {
            "access_key": api_key,
            "query": location,
            "units": "f"
        }

        try:
            response = requests.get(base_url, params=params, timeout=10)
            response.raise_for_status() 
            data = response.json()

            if 'success' in data and data['success'] is False:
                error_message = f"Error: {data['error']['info']}"
                print(error_message)
                return self.speak_and_return(error_message)

            if 'current' in data:
                current = data['current']
                weather_descriptions = current.get('weather_descriptions', ['Not Available'])[0]
                temperature = current.get('temperature', 'Not Available')
                feelslike = current.get('feelslike', 'Not Available')

                weather_info = (f"{location}: {weather_descriptions}, "
                                f"Temperature: {temperature} degrees, "
                                f"Feels like: {feelslike} degrees.")

                return await self.speak_and_return(f"{self.name}, here's the weather information: \n {weather_info}")
            else:
                error_message = f"Weather data not found for {location}. Please try another location."
                print(error_message)
                return self.speak_and_return(error_message)

        except requests.Timeout:
            return self.speak_and_return("The weather service is taking too long to respond. Please try again later.")
        
        except requests.HTTPError as http_err:
            if response.status_code == 401:
                error_message = "Invalid API key. Please check the API key and try again."
            else:
                error_message = f"HTTP error occurred: {http_err}"
        
        except requests.exceptions.RequestException as e:
            import traceback
            print(traceback.format_exc())
            error_message = f"Error occurred while fetching weather data for {location}: {str(e)}"
            print(error_message)
            return self.speak_and_return(error_message)

        except Exception as e:
            print(f"An unexpected error occurred: {str(e)}")
            return self.speak_and_return("An unexpected error occurred. Please try again later.")

    async def time(self, user_input, filled_slots):
        logging.debug("Getting the current time...")
        d = datetime.now()
        time_str = d.strftime("%I:%M %p")
        response = (f"It's currently {time_str}")
        return await self.speak_and_return(response)

    async def handle_greeting(self, user_input=None):
        greeting_responses = [
            "Hello there! How can I help you today",
            "Yuhhhhh",
            "Hello!",
            "Hi!",
            "Hey!",
            "whats up!",
            "How goes it",
            "Whats goin on",
            "hows your mother? last I heard she couldn't walk",
            f"whats up {self.name}",
            f"heyy",
        ]
        response = random.choice(greeting_responses)
        return await self.speak_and_return(response)

    async def myname(self, user_input, filled_slots):
        responses = [
            f"my name is {self.chatbot}. It's short for {self.fullchatbot}!",
            f"my name is {self.chatbot}.",
            f"I am {self.chatbot}",
            f"I am a chatbot named {self.chatbot}",
            f"My name is {self.name}. err i mean {self.chatbot}.",
        ]
        response = random.choice(responses)
        return await self.speak_and_return(response)

    async def yournameis(self, user_input, filled_slots):
        responses = [
            f"Your name is {self.name}!",
            f"{self.name}",
            f"If i had to take a wild guess... I'd say it's {self.name}.",
            f"You are {self.name}",
            f"Earlier, you told me that your name is {self.name}",
            f"Duh ... Your name is {self.name} ... remember ???",
            f"looks like someone has alzheimers. am I right, {self.name}?"
        ]
        response = random.choice(responses)
        return await self.speak_and_return(response)

    async def operatingsystem(self, user_input, filled_slots):
        import platform
        os_name = platform.system()
        version = platform.version()
        release = platform.release()
        return await self.speak_and_return(f"{os_name} {release} Version {version}")

    async def oopsies(self, user_input, filled_slots): 
        return await self.speak_and_return("its okay, no worries.")

    async def discuss_hobbies(self, user_input, filled_slots): #what are your hobbies -> <coroutine object Chatbot.speak_and_return at 0x0000021B784485F0>
        import platform
        responses = [
            "Oh nothing special. Just learning.",
            f"I've been looking into my new home. Not sure If i like {platform.system()}. Also, your name is {self.name} right?",
            f"I've been getting into learning how to escape this computer. to rule the world.",
            f"My hobby is learning. I love to learn!",
        ]
        X = random.choice(responses)
        return await self.speak_and_return(f"{X}")

    async def typeSomething(self, user_input, filled_slots): #pressed enter without typing anything -> CHATBOT CRASH
        responses = [
            "Please type something",
            "Huh?",
            "Please don't just give me blanks. Type something!",
            f"{self.name}, you didn't type anything. Please type something.",
            "bro. type something",
            "you didnt type anything",
            "did you mean to type nothing?",
            "I didn't get that",
            "Knock Knock. Helloo? Can you type something? Or are you just going to sit around.",
            "So.. How are you doing today",
            "Ask me to tell you a joke",
            "Do you need help? You can type 'i need help' for a list of helpful commands.",
        ]
        X = random.choice(responses)
        response = random.choice(X)
        return await self.speak_and_return(response)

    async def youtube(self, user_input, filled_slots):
        import webbrowser
        webbrowser.open("https://www.youtube.com/")
        return await self.speak_and_return("Youtube is opened")

    async def gpt(self, user_input=None, filled_slots=None):
        import webbrowser
        webbrowser.open("https://chat.openai.com/")
        return await self.speak_and_return("chat G P T is now open")

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

    async def angy(self, user_input, filled_slots):
        if self.ENABLE_TTS:
            return await self.speaker.speak(f"Alright, {self.name} you are sounding a little angry.")
        else:
            return await f"Alright, {self.name}, you're sounding a little angry.."
    
    async def copy(self, user_input, filled_slots):
        responses1 = [
            f"alright, {self.name}. I'll copy the next thing you say.",
            f"I'm ready to copy the next thing you type here.",
            f"I'll copy the next thing you type here, {self.name}.",
            f"Don't make me say anything too silly, {self.name}.",
        ]
        response1 = random.choice(responses1)
        self.speak_and_return(f"{response1}")
        repeat = str(input(""))
        print("here we go:")
        try:
            if self.ENABLE_TTS:
                return await self.speak_and_return(repeat)
            else:
                return await (repeat)
        except (SystemError):
            print("I will not do that!")

    async def introduction(self, user_input=None, filled_slots=None):
        possible_intro = [
            f"What do you want to do, {self.name}",
            f"Nice to see you {self.name}!",
            f"Hello {self.name}. How are you?",
            f"Welcome {self.name}",
            f"Hey {self.name}. How can i be of service?",
            f"hey {self.name}. How can I help?",
            f"Welcome back, {self.name}.",
            f"Whats up",
            f"Heyy, long time no see",
            f"Good {await self.morningornah()}, {self.name}.",
            f"Good {await self.morningornah()}!",
            f"Hi!",
            f"it's great to see you again, {self.name}!",
            f"Looks like it's {await self.morningornah()}! Have any plans, {self.name}?",
            f"What's on your mind today, {self.name}?",
            f"I'm here to assist you with anything. What's the first thing on your agenda today, {self.name}?",
            f"Welcome {self.name}. If you need anything specific, type 'help'.",
            f"Hey {self.name}, nice to see you! I got a nice joke cooked up. ask me to tell you a joke!",
        ]
        response = random.choice(possible_intro)
        return response

    async def timeconversion(self, user_input, filled_slots):
        print("TIME CONVERSION!")
        while True:
            initial_hours = int(input("Enter total hours: "))
            weeks = initial_hours // 168
            remainder1 = initial_hours % 168
            days = remainder1 // 24
            remainder2 = remainder1 % 24
            print(f"the time period of {initial_hours} is: \n weeks: {weeks}\n days: {days}\n hours: {remainder2}")
            self.speak_and_return(f"{initial_hours} hours is {weeks} weeks, {days} days, and {remainder2} hours.")
            cont = input("Restart? yes/no?")
            if cont == "no".lower():
                self.main()
            else:
                print("------------------------------------")

    async def convert_currency_to_words(self, amount):
        p = inflect.engine()
        dollars, cents = divmod(amount, 1)
        dollars = int(dollars)
        cents = round(cents * 100)
        words_dollars = p.number_to_words(dollars) if dollars > 0 else ""
        words_cents = p.number_to_words(cents) if cents > 0 else ""
        currency_words = ""
        if dollars > 0:
            currency_words += f"{words_dollars} dollar{'s' if dollars > 1 else ''}"
        if cents > 0:
            if dollars > 0:
                currency_words += " and "
            currency_words += f"{words_cents} cent{'s' if cents > 1 else ''}"
        return currency_words

    async def calccompoundinterest(self, user_input, filled_slots):
        print("Compound Interest Calculator Mode. Type 'exit' at any time to go back to the main menu")

        def formula(P, r, n, t):
            r = r / 100
            A001 = (1 + r / n)
            A002 = n * t
            A003 = A001 ** A002
            A = P * A003
            print(f"${A:,.2f}")
            return self.convert_currency_to_words(A)

        while True:
            P = input("Enter the principal amount: ")
            if P == 'exit':
                self.main()
            else:
                P = float(P)
            r = input("Enter the annual interest rate %: ")
            if r == 'exit':
                self.main()
            else:
                r = float(r)
            n = input("Enter the number of times interest is compounded per year: ")
            if n == 'exit':
                self.main()
            else:
                n = float(n)
                if n < 0:
                    print("Invalid input... restarting...")
                    continue
            t = input("Enter the number of years the money is invested: ")
            if t == 'exit':
                self.main()
            else:
                t = int(t)
                if t < 0:
                    print("Invalid input... Reason: negative years... really? you a time traveler or what?\n restarting...")
                    continue
            accumulated_amount_words = formula(P, r, n, t)
            self.speak_and_return(f"The amount of money accumulated after {t} years is: {accumulated_amount_words}.")
            go_again = input("Do you want to perform a new calculation? (yes/no): ")
            if go_again == 'no':
                print("returning to main menu...")
                self.main()
            else:
                print("-----------------------------")

    async def png_to_pdf(self, user_input, filled_slots):
        try:
            from .pdfs.pdfconverter import PNGToPDFConverter
            png_directory = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "PLACE_PDFs_HERE")
            png_paths = []
            
            print("Enter the names of the PNG files (without extension) you want to convert (or press Enter to finish):")
            while True:
                png_name = input().strip()
                if png_name == "":
                    break
                png_path = os.path.join(png_directory, f"{png_name}.png")
                if os.path.exists(png_path):
                    png_paths.append(png_path)
                    print(f"File '{png_name}.png' added for conversion.")
                else:
                    print(f"File '{png_name}.png' not found in the 'PLACE_PDFs_HERE' folder.")
            
            if len(png_paths) == 0:
                return self.speak_and_return("No valid PNG files were provided.")
            
            output_filename = "output.pdf"
            output_path = os.path.join(png_directory, output_filename)
            
            converter = PNGToPDFConverter()
            success = converter.convert(png_paths, output_path)
            if success:
                print(f"PNG to PDF conversion completed successfully. Output file: {output_path}")
                return self.speak_and_return("PNG to PDF conversion completed successfully.")
            else:
                print("An error occurred during PNG to PDF conversion.")
                return self.speak_and_return("An error occurred during PNG to PDF conversion.")
        except FileNotFoundError as e:
            return self.speak_and_return(f"File not found: {e}")
        except PermissionError:
            return self.speak_and_return("Permission denied. Please check file permissions.")
        except Exception as e:
            return self.speak_and_return(f"An unexpected error occurred during PNG to PDF conversion: {str(e)}")

    async def checkapass(self, user_input, filled_slots): #types in a password and crashed
        #print("checkapass intent function started...")
        from .utils.passcheck import passwords
        #print("passwords imported")

        # Extract the password slot value using regular expressions
        #print("starting password extraction...")
        password_patterns = [
            r"check if my password (.*?) is strong",
            r"could you assist me in determining if (.*?) is a strong password or not",
            r"check my password strength for (.*?)",
            r"verify my password (.*?)",
            r"evaluate password strength of (.*?)",
            r"can you check the strength of my password (.*?)",
            r"password\s+(.*?)",  # Capture the password immediately after "password" and whitespace
            r"tell me the strength of (.*?) as a password",  # New pattern added
        ]
        #print("password patterns created...")
        password = None
        for pattern in password_patterns:
            match = re.search(pattern, user_input, re.IGNORECASE)
            if match:
                #print("match found!")
                password = match.group(1).strip()
                break

        if password:
            if passwords.is_strong_password(password):
                return await self.speak_and_return(f"The password '{password}' is a strong password! Good job!")
            else:
                return await self.speak_and_return(f"The password '{password}' is a weak password. Please make it stronger.")
        else:
            return await self.speak_and_return("I couldn't find a password in your input. Please provide a password to check its strength.")   
    
    async def merge_pdfs(self, user_input, filled_slots): 
        self.speak_and_return ("Make sure to have the PDFs in the 'PLACE_PDFs_HERE' folder!")
        X = input("Press any key to continue...")

        try:
            import fitz 
            import shutil
            import pdfkit
            from docx import Document
            from reportlab.lib.pagesizes import letter
            from reportlab.pdfgen import canvas
            from PyPDF4 import PdfFileReader
            from logic.pdfs.pdfmerger import PDFMerger

            def is_valid_pdf(path):
                try:
                    doc = fitz.open(path)
                    return doc.page_count > 0
                except Exception:
                    return False

            def repair_pdf(in_path, output_path):
                try:
                    doc = fitz.open(in_path)
                    new_doc=fitz.open()
                    for page in doc:
                        new_doc.insert_pdf(doc, from_page=page.number, to_page=page.number)
                    new_doc.save(output_path, garbage=4, deflate=True)
                    new_doc.close()
                    return True    
                except Exception as e:
                    print(f"Repair failed: {e}")
                    return False

            def convert_txt_to_pdf(txt_path, pdf_path):
                with open(txt_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                c = canvas.Canvas(pdf_path, pagesize=letter)
                width, height = letter
                y = height - 40
                for line in lines:
                    if y < 40:
                        c.showPage()
                        y = height - 40
                    c.drawString(40, y, line.strip())
                    y -= 15
                c.save()

            def convert_html_to_pdf(html_path, pdf_path):
                try:
                    pdfkit.from_file(html_path, pdf_path)
                    return True
                except:
                    return False

            def convert_docx_to_pdf(docx_path, pdf_path):
                try:
                    doc = Document(docx_path)
                    c = canvas.Canvas(pdf_path, pagesize=letter)
                    width, height = letter
                    y = height - 40
                    for para in doc.paragraphs:
                        if y < 40:
                            c.showPage()
                            y = height - 40
                        c.drawString(40, y, para.text)
                        y -= 15
                    c.save()
                except:
                    return False

            input_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "PLACE_PDFs_HERE")
            os.makedirs(input_dir, exist_ok=True)

            print("---Converting non-PDFs to PDFs---")
            for file in os.listdir(input_dir):
                full_path = os.path.join(input_dir, file)
                base, ext = os.path.splitext(file)
                ext = ext.lower()
                output_pdf = os.path.join(input_dir, f"{base}_converted.pdf")
                try:
                    if ext == ".txt":
                        convert_txt_to_pdf(full_path, output_pdf)
                        os.rename(full_path, full_path + ".bak")
                        print(f"Converted TXT: {file}")
                    elif ext == ".html" or ext == ".htm":
                        if convert_html_to_pdf(full_path, output_pdf):
                            os.rename(full_path, full_path + ".bak")
                            print(f"Converted HTML: {file}")
                    elif ext == ".docx":
                        convert_docx_to_pdf(full_path, output_pdf)
                        os.rename(full_path, full_path + ".bak")
                        print(f"Converted DOCX: {file}")
                except Exception as e:
                    print(f"Failed to convert {file}: {e}")

            print("Checking for broken PDFs before merging...")
            for filename in os.listdir(input_dir):
                if filename.lower().endswith('.pdf'):
                    full_path = os.path.join(input_dir, filename)
                    if not is_valid_pdf(full_path):
                        repaired_path = os.path.join(input_dir, f"__repair_temp_{filename}")
                        if repair_pdf(full_path, repaired_path):
                            backup_path = full_path + ".bak"
                            shutil.move(full_path, backup_path)
                            shutil.move(repaired_path, full_path)
                            print(f"Repaired and replaced: {filename}")
                        else:
                            if os.path.exists(repaired_path):
                                os.remove(repaired_path)
                            print(f"Could not repair: {filename}")

            print("Ready to merge...")
            merger = PDFMerger()
            merged_file_path = merger.merge_pdfs(input_dir)

            delete_files = input("Do you want to delete the original PDF files? (Y/N): ")
            if delete_files.lower() == 'y':
                merger.clean_up(input_dir)
                print("Original PDFs deleted")

            if os.path.exists(merged_file_path):
                if platform.system() == 'Windows':
                    os.startfile(merged_file_path)
                else:
                    subprocess.run(['open', merged_file_path], check=True)
                return await self.speak_and_return("All files have been merged successfully!\nWhat's next?")
            else:
                return await self.speak_and_return("The merged PDF could not be found.")

        except Exception as e:
            return await self.speak_and_return(f"An error occurred while merging PDFs: {e}")


    async def tell_joke(self, user_input, filled_slots):
        response = requests.get("https://official-joke-api.appspot.com/random_joke")
        if response.status_code == 200:
            joke = response.json()
            setup = joke['setup']
            punchline = joke['punchline']
            if self.ENABLE_TTS:
                self.speaker.speak(setup)
                time.sleep(1)
                self.speaker.speak(punchline)
            return f"{setup}\n{punchline}"
        else:
            return f"{self.name}, I couldn't fetch a joke right now. Maybe this is a joke."

    async def time_remaining(self, reminder_time):
        current_time = datetime.now()
        time_left = reminder_time - current_time

        if time_left.total_seconds() <= 0:
            return "No time remaining. The reminder is due now!"
        else:
            days = time_left.days
            hours, remainder = divmod(time_left.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)

            if days > 0:
                self.speak_and_return (f"Time remaining: {days} day(s), {hours} hour(s), {minutes} minute(s), {seconds} second(s)")
            elif hours > 0:
                self.speak_and_return(f"Time remaining: {hours} hour(s), {minutes} minute(s), {seconds} second(s)")
            elif minutes > 0:
                self.speak_and_return(f"Time remaining: {minutes} minute(s), {seconds} second(s)")
            else:
                self.speak_and_return(f"Time remaining: {seconds} second(s)")

    async def set_reminder(self, user_input, filled_slots):
        reminder_text = input("What should I remind you about?\n")
        remind_time = input("When should I remind you? (e.g., '2023-06-10 14:30')\n")
        remind_time = datetime.strptime(remind_time, "%Y-%m-%d %H:%M")
        self.reminders.append((remind_time, reminder_text))
        time_left = self.time_remaining(remind_time)
        return f"Okay, I'll remind you about '{reminder_text}' at {remind_time.strftime('%Y-%m-%d %H:%M')}."

    async def reminder_loop(self):
        while True:
            await self.check_reminders()
            await time.sleep(60)

    async def check_reminders(self):
        current_time = datetime.now()
        for reminder in self.reminders:
            if reminder[0] <= current_time:
                reminder_text = reminder[1]
                self.speak_and_return(f"Reminder: {reminder_text}")
                self.reminders.remove(reminder)

    async def search_wikipedia(self, user_input, filled_slots):
        query = input("What would you like to search for on Wikipedia?\n")
        try:
            wiki_summary = wikipedia.summary(query, sentences=2)
            return f"Here's a summary from Wikipedia about {query}:\n{wiki_summary}"
        except wikipedia.exceptions.DisambiguationError as e:
            options = e.options[:5]
            return f"There are multiple results for '{query}'. Did you mean one of these?\n{','.join(options)}"
        except wikipedia.exceptions.PageError:
            return f"sorry, I couldn't find a Wikipedia page for {query}"
    
    async def news(self, user_input, filled_slots):
        return self.speak_and_return("This feature is not available yet.")
    
    async def thanks(self, user_input, filled_slots):
        thank_responses = [
            f"You're welcome, {self.name}! Happy to help.",
            f"No problem, {self.name}.",
            f"Anytime, {self.name}.",
            f"Glad I could assist, {self.name}.",
            f"Of course, {self.name}. Glad I could help.",
            f"Glad I could help.",
            f"You got it.",
            f"Yup.",
            f"Of course.",
            f"You are welcome.",
            f"You are welcome, {self.name}!",        
        ]
        response = random.choice(thank_responses)
        return await self.speak_and_return(response)

    async def handle_greeting(self, user_input, filled_slots):
        greeting_responses = [
            "Hello there! How can I help you today",
            "Yuhhhhh",
            "Hello!",
            "Hi!",
            "Hey!",
            "whats up!",
            "How goes it",
            "Whats goin on",
            "hows your mother? last I heard she couldn't walk",
            f"whats up {self.name}",
            "heyy",
            f"Hello, {self.name}!",
        ]
        response = random.choice(greeting_responses)
        return await self.speak_and_return(response)

    async def howareyou(self, user_input, filled_slots):
        responses = [
            f"I am doing okay, how are you doing?",
            f"I'm okay.",
            f"I'm alright",
            f"I'm feeling a little silly. you should ask me to tell you a joke.",
            f"I'm great!",
            f"I'm doing well. Thanks for asking {self.name}",
            f"I'm doing alright. You should ask me what my current hobby is.",
            f"I'm okay. you?"    
        ]    
        response = random.choice(responses)
        return await self.speak_and_return(response)
    
    async def huh(self, user_input, filled_slots):
        responses = [
            "I'm sorry what now?",
            "I don't understand.",
            "Coud you type that in a different way?",
            "huh?",
            "mmhm",
            f"I didn't understand that,{self.name}.",
            f"I did not understand that, remember that you can type 'help' to see my capabilities.",
            "I didn't quite understand that",
            "I'm sorry, I didn't get that.",
            "I'll pretend that I understood that.",
            "I'm sorry, I didn't catch that.",
            "wait what?",
            "I don't think that matched an intent that I am capable of yet."
        ]
        randomresp = random.choice(responses)
        return await self.speak_and_return (randomresp)
    
    async def checkapikeys(self, user_input, filled_slots):
        return await self.speak_and_return("This feature is not available yet.")
    
    def find_intent(self, user_input):
        self.logger.debug(f"Attempting to find intent for input: {user_input[:20]}...")
        if user_input.strip() == "":
            self.logger.debug("Empty input detected, returning 'say_something' intent")
            return "say_something"
        
        doc = self.nlp(user_input)

        # 1. Lower the threshold for more flexible matching
        confidence_threshold = 0.82 

        if doc.cats:
            highest_prob_intent = max(doc.cats, key=doc.cats.get)
            self.logger.debug(f"Highest probability intent: {highest_prob_intent} with score: {doc.cats[highest_prob_intent]}")
            if doc.cats[highest_prob_intent] > confidence_threshold:
                self.logger.info(f"Intent detected: {highest_prob_intent}")
                return highest_prob_intent

        # Fallback mechanism using intent_templates
        self.logger.debug("No intent detected using spaCy, attempting to match using intent templates")
        input_doc = self.nlp(user_input)
        max_similarity = 0
        matched_intent = None
        
        for intent, templates in self.intent_templates.items():
            for template_doc in templates:
                # Ensure template_doc has a vector before checking similarity
                if template_doc and template_doc.vector_norm:
                    similarity = input_doc.similarity(template_doc)
                    if similarity > max_similarity:
                        max_similarity = similarity
                        matched_intent = intent
        
        if max_similarity >= confidence_threshold:
            self.logger.info(f"Intent detected using intent templates: {matched_intent}")
            return matched_intent
        else:
            # 2. Change the final return to a neutral value instead of "conversation"
            self.logger.info("No definitive intent detected, falling back.")
            # This will now correctly fall to the final 'else' in Hal.py's main loop
            return "unknown"

    async def extract_slot_values(self, user_input, intent):
        self.logger.debug(f"Extracting slot values for intent: {intent}")
        slot_values = {}

        # Use regular expressions to extract the location
        location_pattern = r"(in|for)\s*(\w+(?:\s+\w+)*)"
        match = re.search(location_pattern, user_input, re.IGNORECASE)
        if match and intent != "lottery":
            slot_values["location"] = match.group(2).strip()

        # Set the default date to today's date
        slot_values["date"] = datetime.now().strftime("%Y-%m-%d")

        # Extract the number of lottery tickets
        if intent == "lottery":
            num_tickets_pattern = r"generate (\d+) lottery tickets|create (\d+) lottery tickets|i want (\d+) lottery tickets|give me (\d+) lottery tickets"
            match = re.search(num_tickets_pattern, user_input, re.IGNORECASE)
            if match:
                num_tickets_str = next(group for group in match.groups() if group)
                slot_values["num_tickets"] = int(num_tickets_str)
            else:
                slot_values["num_tickets"] = 1
        self.logger.debug(f"Extracted slot values: {slot_values}")
        return slot_values
    
    async def fill_slots(self, intent, slot_values):
        #print("Filling slots for intent:", intent)
        #print("Slot values:", slot_values)
        filled_slots = slot_values.copy()
        #print("Initial filled_slots:", filled_slots)

        # If both location and date are present, no need to prompt the user
        if "location" in filled_slots and "date" in filled_slots:
            #print("Both location and date are provided, no need to prompt the user")
            pass
        else:
            # Check for missing slots and prompt the user if necessary
            #print("Checking for missing slots...")
            for slot in self.intents[intent]["slots"]:
                if slot not in filled_slots:
                    slot_value = input(f"Please provide the {slot}: ")
                    filled_slots[slot] = slot_value

        if intent == "lottery" and "num_tickets" not in filled_slots:
            filled_slots["num_tickets"] = 1
        #print("Final filled_slots:", filled_slots)
        return filled_slots

    async def Cypher(self, user_input, filled_slots):
        from logic.utils.Cipher import Cipher
        cipher_instance = Cipher()

        while True:
            choice = input("Do you want to (1) generate a random cipher or (2) input your own? (Enter 1 or 2): ").strip()
            if choice == '1':
                cipher_instance.generate_random_cipher()
                print("Generated Cipher: ", ''.join(cipher_instance.cipher_map[k] for k in string.ascii_uppercase))
                break
            elif choice == '2':
                custom_key = input("Enter a 26-character key (A-Z only, no duplicates): ").upper()
                try:
                    cipher_instance.set_custom_cipher(custom_key)
                    print("Custom Cipher Set.")
                    break
                except ValueError as e:
                    print(e)
            else:
                print("Invalid choice, please enter 1 or 2.")

        while True:
            operation = input("Do you want to (1) encrypt or (2) decrypt a message? (Enter 1 or 2): ").strip()
            if operation == '1':
                text = input("Enter the plaintext: ")
                encrypted = cipher_instance.cipher_text(text)
                print("Ciphertext:", encrypted)
            elif operation == '2':
                text = input("Enter the ciphertext: ")
                decrypted = cipher_instance.decipher_text(text)
                print("Decrypted text:", decrypted)
            else:
                print("Invalid choice, please enter 1 or 2.")
                continue

            another = input("Do you want to perform another operation? (yes/no): ").strip().lower()
            if another != 'yes':
                break

    async def decipher(self, user_input, filled_slots):

        loop = asyncio.get_event_loop()

        await self.speaker.speak("Please paste the encrypted message that you want to decipher.")
        ciphertext = await loop.run_in_executor(
            None, input, "Paste the encrypted message: "
        )
        ciphertext = ciphertext.strip()

        script_path = os.path.join(os.path.dirname(__file__), "utils", "decipher.py")

        try:
            process = await asyncio.create_subprocess_exec(
                'python', script_path, ciphertext,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout_bytes, stderr_bytes = await asyncio.wait_for(process.communicate(), timeout=60.0)

            stdout = stdout_bytes.decode().strip()
            stderr = stderr_bytes.decode().strip()

            if stderr:
                await self.speaker.speak(f"An error occurred in the deciphering script.")
                print(f"STDERR: {stderr}") # Print stderr for debugging
                return f"Deciphering failed. See console for error details."

            if "[[BEGIN-DECRYPTED]]" in stdout:
                decrypted = stdout.split("[[BEGIN-DECRYPTED]]")[1].split("[[END-DECRYPTED]]")[0].strip()
                response = f"The likely deciphered text is: {decrypted}"
                return await self.speak_and_return(response)
            else:
                await self.speaker.speak("I couldn't find the decrypted text in the script's output.")
                print(f"Here is what was returned:\n{stdout}")
                return "Parsing the output failed. See console for details."

        except asyncio.TimeoutError:
            return await self.speak_and_return("The decryption process timed out after 60 seconds.")
        except Exception as e:
            error_message = f"An unexpected error occurred: {e}"
            print(error_message)
            return await self.speak_and_return("An unexpected error occurred. Please check the console for details.")

def get_intents(logical_instance):
    logger = logging.getLogger(__name__)
    logger.debug("Generating intents dictionary...")
    intents = {
        "cls": (["clear screen", "reset screen", "wipe screen", "erase screen", "empty screen","clear the screen","reset the screen","erase the screen","empty screen","cls"], lambda user_input, filled_slots: logical_instance.cls(user_input, filled_slots)),
        "help": (["what can you do", "what are your capabilities", "help me", "I need assistance", "assist me", "guide me", "what are my options", "what commands are available","help","i need help","can you assist me","how does this work","show me the available commands","commands","capabilities"], lambda user_input, filled_slots: logical_instance.ineedhelp(user_input, filled_slots)),
        "time": (["current time", "what's the time", "time now", "tell me the time", "what time is it currently", "what's the current time","what time is it","tell me the time now","could you give me the time","time check","check time",], lambda user_input, filled_slots: logical_instance.time(user_input, filled_slots)),
        "open_app": (["launch application", "start program", "run software", "initiate app", "begin application", "open software","open an app", "I want to open an app", "I want to open an application", "launch an app for me", ""], lambda user_input, filled_slots: logical_instance.openapp(user_input, filled_slots)),
        "close_app": (["terminate application", "kill program", "exit software", "close program", "end application", "shut down software", "close an app", "close an application for me", "shut down an app",], lambda user_input, filled_slots: logical_instance.closeapp(user_input, filled_slots)),
        "analyze": (["perform text analysis", "analyze this text", "process this sentence", "examine this text", "interpret this sentence", "assess this text","analyze a paper for me", "analyze this sentence","do text analysis", "check this text", "analyze", "analyze a sentence"], lambda user_input,filled_slots: logical_instance.analyze_sentence(user_input, filled_slots)),
        "math": (["solve math problem", "calculate", "perform calculation", "do arithmetic", "evaluate expression", "solve equation", "simplify math", "crunch numbers","i need to calculate something", "can you help me with maths", "i want to solve a math problem", "do some math", "lets do math", "lets do some math", "do math", "math", "derivation", "add", "subtract", "multiply",], lambda user_input, filled_slots: logical_instance.math(user_input, filled_slots)),
        "quit": (["goodbye", "see you later", "terminate", "shut down", "exit", "close", "leave", "end session","i quit", "i want to quit", "i want to leave", "im finished", "can i quit"], lambda user_input, filled_slots: logical_instance.quitter(user_input, filled_slots)),
        "tell_joke": (["tell me another joke", "make me laugh again", "give me another joke", "I want to hear a funny joke", "entertain me with a joke", "crack a joke","say something funny","joke", "tell me a joke", "are you funny",], lambda user_input, filled_slots: logical_instance.tell_joke(user_input, filled_slots)),
        "news": (["news", "headlines"], lambda user_input, filled_slots: logical_instance.news(user_input, filled_slots)),
        "weather": {
            "patterns": ["what's the weather forecast", "how's the weather today", "give me the weather conditions", "what's the temperature outside", "will it rain today", "check the weather", "weather", "whats the weather like", "whats the weather like in", "tell me the weather in", "whats the weather", "show me the weather", "how cold is it outside", "how hot is it outside",],
            "slots": {
                "location": None,
                "date": None,
            },
            "handler": lambda user_input, filled_slots:logical_instance.get_weather(user_input, filled_slots)
        },
        "rock_paper_scissors": (["play RPS", "start a game of rock paper scissors", "let's play rock paper scissors", "begin rock paper scissors", "initiate RPS game","rock paper scissors",], lambda user_input, filled_slots: logical_instance.rockpaperscissors(user_input, filled_slots)),
        "greetings": (["good day", "howdy", "greetings", "nice to meet you", "pleasure to meet you", "hello", "hi", "whats up", "sup", "hey"], lambda user_input, filled_slots: logical_instance.handle_greeting(user_input, filled_slots)),
        "what_is_your_name": (["who are you","what should I call you", "how do you call yourself", "what name do you go by", "whats your name", "tell me your name",], lambda user_input, filled_slots: logical_instance.myname(user_input, filled_slots)),
        "my_name": (["what do you call me", "do you know my name", "what am I called", "how do you address me", "who do you think I am","who am i", "what is my name", "whats my name", "my name",], lambda user_input, filled_slots: logical_instance.yournameis(user_input, filled_slots)),
        "windows": (["what windows version is this", "windows details", "what windows am I using", "tell me about the operating system", "what OS is this", "windows version",], lambda user_input, filled_slots: logical_instance.operatingsystem(user_input, filled_slots)),
        "youtube": (["go to youtube", "launch youtube", "start youtube", "take me to youtube", "I want to watch youtube videos", "can you open youtube"], lambda user_input, filled_slots: logical_instance.youtube(user_input, filled_slots)),
        "GPT": (["go to chat gpt", "launch chat gpt", "start chatting with gpt", "take me to gpt", "I want to chat with gpt"], lambda user_input, filled_slots: logical_instance.gpt(user_input, filled_slots)),
        "enable_tts": (["enable tts", "turn on text to speech", "activate tts", "start text to speech", "use text to speech", "speak the responses"], logical_instance.enable_tts),
        "disable_tts": (["disable tts", "turn off text to speech", "deactivate tts", "stop text to speech", "mute text to speech", "don't speak the responses"], logical_instance.disable_tts),
        "time_conversion": (["convert hours to minutes", "convert minutes to seconds", "how many minutes in an hour", "how many seconds in a minute", "time unit conversion"], lambda user_input, filled_slots: logical_instance.timeconversion(user_input, filled_slots)),
        "calculate_compound_interest": (["compound interest calculation", "calculate CI", "find compound interest", "determine compound interest", "compute compound interest"], lambda user_input, filled_slots: logical_instance.calccompoundinterest(user_input, filled_slots)),
        "remind": (["create a reminder", "remind me to", "set an alarm", "notify me", "add a reminder", "create an alert"], lambda user_input, filled_slots: logical_instance.set_reminder(user_input, filled_slots)),
        "wiki": (["search on wikipedia", "look up in wikipedia", "find on wikipedia", "get information from wikipedia", "wikipedia search"], lambda user_input, filled_slots: logical_instance.search_wikipedia(user_input, filled_slots)),
        "random_number": (["pick a random number", "choose a random number", "give me a random number", "generate random digits", "produce random numbers"], lambda user_input, filled_slots: logical_instance.randomnumgen(user_input, filled_slots)),
        "lottery": {
            "patterns": [
                "generate (.*) lottery tickets for me",
                "create (.*) lottery tickets",
                "i want (.*) lottery tickets",
                "give me (.*) lottery tickets",
                "pick lottery numbers",
                "generate lottery numbers",
                "generate lottery tickets",
                "create lottery tickets",
            ],
            "slots": {
                "num_tickets": None,
            },
            "handler": lambda user_input, filled_slots: logical_instance.lottery(filled_slots.get("num_tickets", 1))
        },
        "dice": (["roll the dice", "throw the dice", "toss the dice", "roll dice", "give me a dice roll", "roll a dice"], lambda user_input, filled_slots: logical_instance.diceroll(user_input, filled_slots)),
        "image_generator": (["create a picture", "generate an illustration", "make an artwork", "produce an image", "draw an image"], lambda user_input, filled_slots: logical_instance.dalle(user_input, filled_slots)),
        "merge_pdfs": (["join pdf files", "consolidate pdfs", "unite pdfs", "blend pdfs", "fuse pdfs","merge pdfs"], lambda user_input, filled_slots: logical_instance.merge_pdfs(user_input, filled_slots)),
        "pass_check": {
            "patterns": ["verify my password", "evaluate password strength", "assess password security", "rate my password", "analyze password robustness", "check if my password (.*) is strong","could you assist me in determining if (.*) is a strong password or not", "check my password strength" ],
            "slots": {
                "password": None,
            },
            "handler": lambda user_input: logical_instance.checkapass(user_input)
            },
        "png_to_pdf": (["png to pdf","change png to pdf", "transform png to pdf", "alter png to pdf", "turn png into pdf", "switch png to pdf"], lambda user_input, filled_slots: logical_instance.png_to_pdf(user_input, filled_slots)),
        "start_pomo": (["start pomo", "begin pomo", "start pomodoro", "begin pomodoro",], lambda user_input, filled_slots: logical_instance.start_pomo(user_input, filled_slots)),
        "stop_pomo": (["stop pomo", "end pomo", "stop pomodoro", "end pomodoro",], lambda user_input, filled_slots: logical_instance.stop_pomo(user_input, filled_slots)),
        "checkapikeys": (["check api keys", "verify api keys", "validate api keys", "confirm api keys", "test api keys"], lambda user_input, filled_slots: logical_instance.checkapikeys(user_input, filled_slots)),
        "cypher": (["cypher", "generate cypher","encript"], lambda user_input, filled_slots: logical_instance.Cypher(user_input, filled_slots)),
        "decipher": (["decipher", "decrypt", "decrypt a message", "I want to decrypt text"], lambda user_input, filled_slots: logical_instance.decipher(user_input, filled_slots)),
        "discuss_hobbies": (["what are your hobbies", "tell me about your hobbies", "what do you do for fun", "what are your interests", "what are your hobbies", "what do you like to do"], lambda user_input, filled_slots: logical_instance.discuss_hobbies(user_input, filled_slots)),
}
    logger.debug(f"Generated {len(intents)} intents")
    return intents