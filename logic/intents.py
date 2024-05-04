import os
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
from AppOpener import open as open_app
from gtts import gTTS
import sys
import subprocess
from pathlib import Path
from openai import OpenAI
from .api_keys import OPENAI_API_KEY
from .api_keys import WEATHER_API_KEY
#print(f"WEATHER API KEY: {WEATHER_API_KEY}")
from .api_keys import JOKES_API_KEY
import pyttsx3
import asyncio
import aiohttp
from .utils.pomodoro import Pomodoro
from .utils.speaking import Speaker
from .utils.text_sum import TextSummarizer
import re
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

class logical:
    def __init__(self, api_key=None, client=None, enable_tts=True):
        self.chatbot = 'Hal'
        self.fullchatbot = 'Halsey'
        current_dir = os.getcwd()
        print(f"Current working directory: {current_dir}")
        file_path = 'user_name.txt'
        print(f"looking for file: {file_path}")
        if not os.path.exists(file_path):
            print("Username file not found. Please run setup.py to create the file.")
            input("Press Enter to exit...")
            sys.exit(1)
            
        with open('user_name.txt', 'r') as f:
            self.name = f.read().strip()

        self.client = client
        self.ENABLE_TTS = enable_tts
        self.speaker = Speaker(client=self.client, enable_tts=self.ENABLE_TTS)
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
    
    def start_pomo(self):
        self.pomodoro_timer.start_timer()
        return self.speak_and_return("Pomodoro timer started.")
    
    def stop_pomo(self):
        self.pomodoro_timer.stop_timer()
        return self.speak_and_return("Pomodoro timer stopped.")

    def lottery(*args):
        while True:
            try:
                num_tickets = int(input("Enter the number of lottery tickets you want to generate:"))
                if num_tickets <=0:
                    raise ValueError
                break
            except ValueError:
                print("Invalid input. Please enter a positive interger...idiot.")
        tickets = []
        for _ in range(num_tickets):
            regular_numbers = random.sample(range(1,70),5)
            special_number = random.randint(1,25)
            ticket = (tuple(sorted(regular_numbers)), special_number)
            tickets.append(ticket)
        print("-----Generated Lottery Tickets-----")
        for i, ticket in enumerate(tickets, start=1):
            regular_numbers, special_number = ticket
            print(f"Ticket {i}: Regular numbers: {regular_numbers}, Special number: {special_number}")
        return ""

    def randomnumgen(self):
        whatrange = int(input("Enter starting range -> "))
        lastrange = int(input("Enter ending range -> "))
        number = random.randint(whatrange,lastrange)
        if self.ENABLE_TTS:
            return self.speak_and_return (number)
        else:
            return (number)
        
    async def dalle(self):
        print("----Image Generator with Dalle-----\ntype'stop' to go back to main menu.")
        resp = str(input("Type the image that you would like to be generated\n"))
        if resp == 'stop':
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
                        else:
                            raise Exception(f"API request failed with status code {response.status}")
            except Exception as e:
                return self.speak_and_return(f"An error occurred: {e}")

    def morningornah(self):
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

    def speak_and_return(self, message):
        if self.ENABLE_TTS:
            self.speaker.speak(message)
        return message

    def diceroll(self):
        print("---------------------------------------------------")
        from logic.games import DiceRoll
        dice_game = DiceRoll()
        result = dice_game.roll()
        return self.speak_and_return(f"You rolled a {result}!")

    def rockpaperscissors(self, user_input=None):
        print("---------------------------------------------------")
        from logic.games import RockPaperScissors
        game = RockPaperScissors() #this creates instance of the game!
        game.play_game() #call the play_game method
        responses = [
            "That was fun! Let's play again later!",
            f"good game, {self.name}",
        ]
        X = random.choice(responses)
        return self.speak_and_return (X)
    
    def ineedhelp(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        if self.ENABLE_TTS:
            self.speak_and_return(f"Here is a list of helpful commands, {self.name}.")
        else:
            print(f"here is a list of helpful commands,{self.name}.")
        commands_table = ""
        max_command_length = max(len(command) for command in self.commands.keys())

        for command, description in self.commands.items():
            padded_command = command.ljust(max_command_length)
            commands_table += f"{padded_command} : {description}\n"
        return commands_table

    def extract_app_name(self, command):
        doc = self.nlp(command)
        for match_id, start, end in self.matcher(doc):
            span = doc[start:end]
            if span.text:
                return span.text.split(" ")[1]  # Return app name after "open"
        return None

    def openapp(self):
        self.speaker.speak("What app do you want to open?")
        print("type cancel to stop trying to open an app")
        command = input("I want to open the app called: ")
        if command == 'cancel':
            return self.main()
        else:
            app_name = command
            if app_name:
                try:
                    import AppOpener
                    print(f"Attempting to open {app_name}")
                    self.speaker.speak(f"Attempting to open {app_name}")
                    AppOpener.open(app_name)
                except Exception as e:
                    print(f"Error trying to open {app_name}: {str(e)}")
            else:
                print("Sorry, I couldn't identify the app that you want to open.")
            if self.ENABLE_TTS:
                self.speak_and_return(f"what else would you like to do, {self.name}?")
            else:
                print(f"What else would you like to do, {self.name}?")
            return "" 

    def closeapp(self):
        self.speaker.speak(f"What app do you want to close {self.name}")
        command = input(f"What app do you want to close, {self.name}?")
        try:
            from AppOpener import close
            print(f"attempting to close{command}")
            close(command)
            return""
        except RuntimeError:
            return self.speak_and_return(f"{command} does not want to cooperate and close. try again??")

    def analyze_sentence(self):
        self.speaker.speak("Please enter the text that you want to analyze:")
        command = input("Enter the text that you want to analyze:\n ")
        self.speaker.speak("Do you want a text summarization or a visualization analysis?")
        which_analysis = input("Which analysis do you want?\nText summary (1)\nVisualization (2)\nQuit (3)\n--> ")
    
        if which_analysis == '1':
            try:
                from .utils.text_sum import TextSummarizer
                num_sentences = int(input("Enter the number of sentences in the summary: "))
                summarizer = TextSummarizer()
                summary = summarizer.summarize(command, num_sentences)
                return self.speak_and_return(f"Here's the summary:\n{summary}")
            except Exception as L:
                self.speaker.speak(f"Sorry, {self.name}. I had an issue with getting analysis on that. I'll print the error code below")
                return L
    
        elif which_analysis == '2':
            try:
                from spacy import displacy
                self.speaker.speak("Do you want a large analysis or small analysis?")
                which_nlp = input("Which analysis do you want? 'small' or 'large'?\n").strip().lower()
            
                if which_nlp == 'small':
                    nlp = spacy.load("en_core_web_sm")
                elif which_nlp == 'large':
                    nlp = spacy.load("en_core_web_lg")
                else:
                    return self.speak_and_return("Invalid analysis option. Please choose 'small' or 'large'.")
            
                doc = nlp(command)
                sentences = list(doc.sents)
            
            # Perform Named Entity Recognition
                entities = [(ent.text, ent.label_) for ent in doc.ents]
                if entities:
                    self.speaker.speak("Named Entities found:")
                    for entity in entities:
                        self.speaker.speak(f"{entity[0]} - {entity[1]}")
                else:
                    print("")
            
            # Perform visualization analysis
                html_ent = displacy.render(sentences, style="ent")
                html_dep = displacy.render(sentences, style='dep')
                html_combined = "<html><head><title>SpaCy Analysis</title></head><body>" + html_ent + html_dep + "</body></html>"
            
                output_path = "data_vis_analysis.html"
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(html_combined)
            
                self.speaker.speak(f"Visualization analysis completed. Opening {output_path} in the web browser.")
                webbrowser.open(output_path)
            
                return "Visualization analysis completed."
        
            except (ValueError, KeyError, SyntaxError):
                self.speak_and_return("Something went wrong with the analysis. Please try again.")
        elif which_analysis == '3':
            return self.main()
        else:
            return self.speak_and_return("Invalid analysis option. Please choose '1' for text summary or '2' for visualization.")
        
    def cls(self):
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
        return self.speak_and_return(response)

    def quitter(self):
        command = input(f"Are you sure you want to quit, {self.name}? any progress will NOT be saved \n type 'quit' to quit. type anything else to stay.")
        if command == 'quit':
            quit()
        else:
            return self.speak_and_return(f'alrighty. What do you want to do now, {self.name}?')

    def math(self):
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
                return self.speak_and_return("Graph has been displayed.")
            except Exception as L:
                return self.speak_and_return(L)

        if operation == 'statistics':
            stat_operation = input("Enter the statistical operation (mean, median, mode, stdev, variance)\n")
            data = input("Enter the data points (comma-separated):\n")
            try:
                result = math_helper.statistics(stat_operation, data)
                return self.speak_and_return(f"the {stat_operation} is {result}")
            except Exception as L:
                return self.speak_and_return(L)
        
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
                return self.speak_and_return("invalid series type.")
            return self.speak_and_return(f"The sum of the series {series_type} series is: {result}")

        if operation == 'system of equations':
            equations = []
            while True:
                equation = input("Enter an equation (or press Enter to finish): ")
                if equation == "":
                    break
                equations.append(equation)
            result = math_helper.solve_system_of_equations(equations)
            return self.speak_and_return(f"The solution to the system of equations is: {result}")
        
        if operation == 'summation':
            expression = input("Enter the expression: ")
            lower_limit = input("Enter the lower limit: ")
            upper_limit = input("Enter the upper limit: ")
            variable = input("Enter the variable: ")
            result = math_helper.summation(expression, lower_limit, upper_limit, variable)
            return self.speak_and_return(f"The summation is: {result}")

        if operation == 'limit':
            expression = input("Enter the expression: ")
            variable = input("Enter the variable: ")
            approaching_value = input("Enter the approaching value: ")
            result = math_helper.limit(expression, variable, approaching_value)
            return self.speak_and_return(f"The limit is: {result}")

        if operation == 'derivative':
            expression = input("Enter the mathematical expression: ")
            result = math_helper.derivative(expression)
            return self.speak_and_return(f"The derivative is: {result}")

        if operation == 'equation':
            equation = input("Enter the equation: ")
            variable = input("Enter the variable to solve for: ")
            result = math_helper.equation(equation, variable)
            return self.speak_and_return(f"The solution is: {result}")

        if operation in ['add', 'subtract', 'multiply', 'divide', 'power']:
            num_args = 2
            args = []
            for i in range(num_args):
                arg = float(input(f"Enter argument {i + 1}: "))
                args.append(arg)

            try:
                result = math_helper.perform_operation(operation, *args)
                return self.speak_and_return(f"The result is: {result}")
            except Exception as L:
                return self.speak_and_return(L)

        if operation == 'square root':
            num = float(input("Enter the number: "))
            try:
                result = math_helper.perform_operation(operation, num)
                return self.speak_and_return(f"The square root is: {result}")
            except Exception as L:
                return self.speak_and_return(L)

        if not operation:
            return self.speak_and_return("Unsupported math operation")

    # ...
    def thanks(self):
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
        return self.speak_and_return(response)

    def get_weather(self, filled_slots):
        # Check for empty slots and prompt user if location is not provided
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
            response = requests.get(base_url, params=params)
            response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
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

                return self.speak_and_return(f"{self.name}, here's the weather information: \n {weather_info}")
            else:
                error_message = f"Weather data not found for {location}. Please try another location."
                print(error_message)
                return self.speak_and_return(error_message)

        except requests.exceptions.RequestException as e:
            import traceback
            print(traceback.format_exc())
            error_message = f"Error occurred while fetching weather data for {location}: {str(e)}"
            print(error_message)
            return self.speak_and_return(error_message)

        except Exception as e:
            print(f"An unexpected error occurred: {str(e)}")
            return self.speak_and_return("An unexpected error occurred. Please try again later.")

    def time(self):
        d = datetime.now()
        time_str = d.strftime("%I:%M %p")
        return self.speak_and_return(f"It's currently {time_str}")

    def handle_greeting(self, user_input=None):
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
        response = random.choice(greeting_responses, WEATHER_API_KEY)
        return self.speak_and_return(response)

    def howareyou(self):
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
        return self.speak_and_return(response)

    def myname(self):
        responses = [
            f"my name is {self.chatbot}. It's short for {self.fullchatbot}!",
            f"my name is {self.chatbot}.",
            f"I am {self.chatbot}",
            f"I am a chatbot named {self.chatbot}",
            f"My name is {self.name}. err i mean {self.chatbot}.",
        ]
        response = random.choice(responses)
        return self.speak_and_return(response)

    def yournameis(self):
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
        return self.speak_and_return(response)

    def operatingsystem(self):
        import platform
        os_name = platform.system()
        version = platform.version()
        release = platform.release()
        return self.speak_and_return(f"{os_name} {release} Version {version}")

    def oopsies(self): #lets build up this function.
        return self.speak_and_return("its okay, no worries.")

    def ifeelgood(self):
        responses = [
            f"That's great to hear,{self.name}.",
            f"Awesome! Keep up the positive vibes,{self.name}!",
            f"Glad to hear that,{self.name}!"
        ]
        X = random.choice(responses)
        return self.speak_and_return(X)

    def ifeelbad(self):
        responses = [
            "Oh. Sorry to hear that.",
            "I'm sorry to hear that.",
            "Life has its ups and downs. Want to hear a joke to cheer up? you can say, 'tell me a joke",
            f"Oh cheer up {self.name}..",
        ]
        return self.speak_and_return(random.choice(responses))

    def discuss_hobbies(self):
        import platform
        responses = [
            "Oh nothing special. Just learning.",
            f"I've been looking into my new home. Not sure If i like {platform.system()}. Also, your name is {self.name} right?",
            f"I've been getting into learning how to escape this computer. to rule the world.",
            f"My hobby is learning. I love to learn!",
        ]
        X = random.choice(responses)
        return self.speak_and_return(f"{X}")

    def typeSomething(self):
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
        return self.speak_and_return(X)

    def xac_facts(self):
        import webbrowser
        webbrowser.open("https://campsite.bio/xac_hellven")
        message = "zack has arrived. planet hellven"
        return self.speak_and_return(message)

    def youtube(self):
        import webbrowser
        webbrowser.open("https://www.youtube.com/")
        return self.speak_and_return("Youtube is opened")

    def gpt(self):
        import webbrowser
        webbrowser.open("https://chat.openai.com/")
        return self.speak_and_return("chat G P T is now open")

    def enable_tts(self):
        self.ENABLE_TTS = True
        print("TTS enabled")  # debugging line
        return self.speak_and_return("hello!")

    def disable_tts(self):
        self.ENABLE_TTS = False
        print("TTS disabled")  # debuggin line
        return ""

    def angy(self):
        if self.ENABLE_TTS:
            return self.speaker.speak(f"Alright, {self.name} you are sounding a little angry.")
        else:
            return f"Alright, {self.name}, you're sounding a little angry.."
    def copy(self):
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
                return self.speak_and_return(repeat)
            else:
                return (repeat)
        except (SystemError):
            print("I will not do that!")

    def introduction(self):
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
            f"Good {self.morningornah()}, {self.name}.",
            f"Good {self.morningornah()}!",
            f"Hi!",
            f"it's great to see you again, {self.name}!",
            f"Looks like it's {self.morningornah()}! Have any plans, {self.name}?",
            f"What's on your mind today, {self.name}?",
            f"I'm here to assist you with anything. What's the first thing on your agenda today, {self.name}?",
            f"Welcome {self.name}. If you need anything specific, type 'help'.",
            f"Hey {self.name}, nice to see you! I got a nice joke cooked up. ask me to tell you a joke!",
        ]
        response = random.choice(possible_intro)
        self.speak_and_return (response)
        print(response)
        return response

    def timeconversion(self):
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

    def convert_currency_to_words(self, amount):
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

    def calccompoundinterest(self):
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

    def png_to_pdf(self):
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
        try:
            success = converter.convert(png_paths, output_path)
            if success:
                print(f"PNG to PDF conversion completed successfully. Output file: {output_path}")
                return self.speak_and_return("PNG to PDF conversion completed successfully.")
            else:
                print("An error occurred during PNG to PDF conversion.")
                return self.speak_and_return("An error occurred during PNG to PDF conversion.")
        except Exception as e:
            print(f"An error occurred during PNG to PDF conversion: {str(e)}")
            return self.speak_and_return("An error occurred during PNG to PDF conversion.")


    def checkapass(self):
        from .utils.passcheck import passwords
        password = input("Enter a password to check it's strenght")
        if passwords.is_strong_password(password):
            return self.speak_and_return("Strong password! Good job!")
        else:
            return self.speak_and_return("Weak password. Fix dat!")

    def merge_pdfs(self): #problem! "An error occurred while merging PDFs: No module named 'pdfs'"
        self.speak_and_return ("Make sure to have the PDFs in the 'PLACE_PDFs_HERE' folder!")
        X = input("Press any key to continue...")

        try:
            from logic.pdfs.pdfmerger import PDFMerger 
            merger = PDFMerger()
            input_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "PLACE_PDFs_HERE") #<-- name of input file
            os.makedirs(input_dir, exist_ok=True)
            merged_file_path = merger.merge_pdfs(input_dir)
            
            delete_files = input("Do you want to delete the original PDF files? (Y/N): ")
            if delete_files.lower() == 'y':
                merger.clean_up(input_dir)
                print("Original PDFs have been deleted")

            if os.path.exists(merged_file_path):
                if platform.system() == 'Windows':
                    os.startfile(merged_file_path)
                else:
                    subprocess.run(['open', merged_file_path], check = True)
                return self.speak_and_return("Files have been merged successfully!\nWhat's next?")
            else:
                return self.speak_and_return("The merged PDF could not be found.")
        except Exception as e:
            return self.speak_and_return(f"An error occurred while merging PDFs: {e}")

    def tell_joke(self):
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

    def time_remaining(self, reminder_time):
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

    def set_reminder(self):
        reminder_text = input("What should I remind you about?\n")
        remind_time = input("When should I remind you? (e.g., '2023-06-10 14:30')\n")
        remind_time = datetime.strptime(remind_time, "%Y-%m-%d %H:%M")
        self.reminders.append((remind_time, reminder_text))
        time_left = self.time_remaining(remind_time)
        return f"Okay, I'll remind you about '{reminder_text}' at {remind_time.strftime('%Y-%m-%d %H:%M')}."

    def reminder_loop(self):
        while True:
            self.check_reminders()
            time.sleep(60)

    def check_reminders(self):
        current_time = datetime.now()
        for reminder in self.reminders:
            if reminder[0] <= current_time:
                reminder_text = reminder[1]
                self.speak_and_return(f"Reminder: {reminder_text}")
                self.reminders.remove(reminder)

    def search_wikipedia(self):
        query = input("What would you like to search for on Wikipedia?\n")
        try:
            wiki_summary = wikipedia.summary(query, sentences=2)
            return f"Here's a summary from Wikipedia about {query}:\n{wiki_summary}"
        except wikipedia.exceptions.DisambiguationError as e:
            options = e.options[:5]
            return f"There are multiple results for '{query}'. Did you mean one of these?\n{','.join(options)}"
        except wikipedia.exceptions.PageError:
            return f"sorry, I couldn't find a Wikipedia page for {query}"
    def news(self):
        return self.speak_and_return("I'm sorry, I can't fetch the news right now. Please try again later.")
    def huh(self):
        responses = [
            "I'm sorry what now?",
            "I don't understand.",
            "Coud you type that in a different way?",
            "huh?",
            "mmhm",
            f"I didn't understand that,{self.name}.",
            f"I did not understand that, remember that you can type 'help' to see my capabilities.",
            "I didn't quite understand that",
        ]
        randomresp = random.choice(responses)
        return self.speak_and_return (randomresp)
    
    def find_intent(self, user_input):
        #print(f"find_intent: Finding intent for user input: {user_input}")
        matched_intent = None  # Initialize matched_intent to None
        doc = self.nlp(user_input)

        if doc.cats:
            highest_prob_intent = max(doc.cats, key=doc.cats.get)
            #print(f"Matched intent using SpaCy NLP: {highest_prob_intent}")
            if doc.cats[highest_prob_intent] > 0.7:
                matched_intent = highest_prob_intent  # Assign the matched intent

        input_doc = self.nlp(user_input)
        max_similarity = 0
        threshold = 0.75
        for intent, templates in self.intent_templates.items():
            for template_doc in templates:
                similarity = input_doc.similarity(template_doc)
                if similarity > max_similarity:
                    max_similarity = similarity
                    matched_intent = intent
        if max_similarity >= threshold:
            pass
        else:
            #print("No intent matched")
            matched_intent = "huh"

        # Print the matched intent after it has been assigned
        #print(f"find_intent: Matched intent: {matched_intent}")
        return matched_intent

    def extract_slot_values(self, user_input, intent):
        slot_values = {}

        # Use regular expressions to extract the location
        location_pattern = r"(in|for)\s*(\w+(?:\s+\w+)*)"
        match = re.search(location_pattern, user_input, re.IGNORECASE)
        if match:
            slot_values["location"] = match.group(2).strip()
        else:
            print(f"No location found in the user input: {user_input}")

        # Set the default date to today's date
        slot_values["date"] = datetime.now().strftime("%Y-%m-%d")

        #print(f"Extracted slot values: {slot_values}")
        return slot_values

    def fill_slots(self, intent, slot_values):
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
            print("Checking for missing slots...")
            for slot in self.intents[intent]["slots"]:
                if slot not in filled_slots:
                    slot_value = input(f"Please provide the {slot}: ")
                    filled_slots[slot] = slot_value

        #print("Final filled_slots:", filled_slots)
        return filled_slots

def get_intents(logical_instance):
    intents = {
        "cls": (["clear screen", "reset screen", "wipe screen", "erase screen", "empty screen","clear the screen","reset the screen","erase the screen","empty screen","cls"], logical_instance.cls),
        "help": (["what can you do", "what are your capabilities", "help me", "I need assistance", "assist me", "guide me", "what are my options", "what commands are available","help","i need help","can you assist me","how does this work","show me the available commands","commands","capabilities"], logical_instance.ineedhelp),
        "time": (["current time", "what's the time", "time now", "tell me the time", "what time is it currently", "what's the current time","what time is it","tell me the time now","could you give me the time","time check","check time",], logical_instance.time),
        "open_app": (["launch application", "start program", "run software", "initiate app", "begin application", "open software","open an app", "I want to open an app", "I want to open an application", "launch an app for me", ""], logical_instance.openapp),
        "close_app": (["terminate application", "kill program", "exit software", "close program", "end application", "shut down software", "close an app", "close an application for me", "shut down an app",], logical_instance.closeapp),
        "analyze": (["perform text analysis", "analyze this text", "process this sentence", "examine this text", "interpret this sentence", "assess this text","analyze a paper for me", "analyze this sentence","do text analysis", "check this text", "analyze", "analyze a sentence"], lambda: logical_instance.analyze_sentence),
        "math": (["solve math problem", "calculate", "perform calculation", "do arithmetic", "evaluate expression", "solve equation", "simplify math", "crunch numbers","i need to calculate something", "can you help me with maths", "i want to solve a math problem", "do some math", "lets do math", "lets do some math", "do math", "math", "derivation", "add", "subtract", "multiply",], logical_instance.math),
        "thanks": (["thank you so much", "I really appreciate it", "thanks a lot", "many thanks", "I'm grateful", "you're awesome", "I owe you one", "thanks", "thank you", "i give you my thanks", "i appreciate it", "respect", "thats whats up",], logical_instance.thanks),
        "quit": (["goodbye", "see you later", "terminate", "shut down", "exit", "close", "leave", "end session","i quit", "i want to quit", "i want to leave", "im finished", "can i quit"], logical_instance.quitter),
        "tell_joke": (["tell me another joke", "make me laugh again", "give me another joke", "I want to hear a funny joke", "entertain me with a joke", "crack a joke","say something funny","joke", "tell me a joke", "are you funny",], logical_instance.tell_joke),
        "news": (["news", "headlines"], logical_instance.news),
        "weather": {
            "patterns": ["what's the weather forecast", "how's the weather today", "give me the weather conditions", "what's the temperature outside", "will it rain today", "check the weather", "weather", "whats the weather like", "whats the weather like in", "tell me the weather in", "whats the weather", "show me the weather", "how cold is it outside", "how hot is it outside",],
            "slots": {
                "location": None,
                "date": None,
            },
            "handler": logical_instance.get_weather
        },
        "rock_paper_scissors": (["play RPS", "start a game of rock paper scissors", "let's play rock paper scissors", "begin rock paper scissors", "initiate RPS game","rock paper scissors",], lambda: logical_instance.rockpaperscissors()),
        "greetings": (["good day", "howdy", "greetings", "nice to meet you", "pleasure to meet you", "what's up", "how's it going","hello","hi","good morning", "good afternoon", "good evening", "whats up", "sup", "hey"], logical_instance.handle_greeting),
        "how_are_you": (["how's your day", "how have you been", "how's life", "how are things", "what's new with you", "how are you holding up", "how are you", "how are you doing", "how are you feeling"], logical_instance.howareyou),
        "what_is_your_name": (["who are you","what should I call you", "how do you call yourself", "what name do you go by", "whats your name", "tell me your name",], logical_instance.myname),
        "my_name": (["what do you call me", "do you know my name", "what am I called", "how do you address me", "who do you think I am","who am i", "what is my name", "whats my name", "my name",], logical_instance.yournameis),
        "windows": (["what windows version is this", "windows details", "what windows am I using", "tell me about the operating system", "what OS is this", "windows version",], logical_instance.operatingsystem),
        "sorry": (["my mistake", "I apologize", "pardon me", "forgive me", "my bad", "I didn't mean that", "im sorry", "my apologies", "oops", "oopsies", "whoops","sorry about that",], logical_instance.oopsies),
        "feeling_good": (["I'm doing well", "I'm fine", "I'm fantastic", "I'm great, thanks for asking", "I'm happy", "I'm feeling positive", "i feel good", "im doing good",], logical_instance.ifeelgood),
        "feeling_bad": (["I'm feeling down", "I'm not doing well", "I'm feeling sad", "I'm upset", "I'm not in a good mood", "I'm feeling negative", "im doing bad", "im not so good", "im sad", "im not happy", "im not okay", "eh", "i am sad",], logical_instance.ifeelbad),
        "discuss_hobbies": (["tell me about your hobbies", "what do you like to do", "what are your favorite activities", "how do you spend your free time", "what interests you", "what are your hobbies", "do you have hobbys", "got any hobbies", "hobby", "hobbies", "what is your current hobby"], logical_instance.discuss_hobbies),
        "xac_hellven": (["who is this xac person", "what do you know about xac hellven", "tell me more about xac", "who is this xac hellven guy", "what's the deal with xac hellven"], logical_instance.xac_facts),
        "youtube": (["go to youtube", "launch youtube", "start youtube", "take me to youtube", "I want to watch youtube videos"], logical_instance.youtube),
        "GPT": (["go to chat gpt", "launch chat gpt", "start chatting with gpt", "take me to gpt", "I want to chat with gpt"], logical_instance.gpt),
        "enable_tts": (["enable tts", "turn on text to speech", "activate tts", "start text to speech", "use text to speech", "speak the responses"], logical_instance.enable_tts),
        "disable_tts": (["disable tts", "turn off text to speech", "deactivate tts", "stop text to speech", "mute text to speech", "don't speak the responses"], logical_instance.disable_tts),
        "angry": (["I'm furious", "I'm enraged", "I'm livid", "you're making me angry", "I'm irritated", "I'm annoyed", "I'm mad at you"], logical_instance.angy),
        "copy": (["repeat after me", "say what I say", "copy my words", "mimic my speech", "echo my message", "parrot my words"], logical_instance.copy),
        "time_conversion": (["convert hours to minutes", "convert minutes to seconds", "how many minutes in an hour", "how many seconds in a minute", "time unit conversion"], logical_instance.timeconversion),
        "calculate_compound_interest": (["compound interest calculation", "calculate CI", "find compound interest", "determine compound interest", "compute compound interest"], logical_instance.calccompoundinterest),
        "remind": (["create a reminder", "remind me to", "set an alarm", "notify me", "add a reminder", "create an alert"], logical_instance.set_reminder),
        "wiki": (["search on wikipedia", "look up in wikipedia", "find on wikipedia", "get information from wikipedia", "wikipedia search"], logical_instance.search_wikipedia),
        "random_number": (["pick a random number", "choose a random number", "give me a random number", "generate random digits", "produce random numbers"], logical_instance.randomnumgen),
        "lottery": (["pick lottery numbers", "generate lottery numbers", "choose lottery digits", "give me lucky numbers", "suggest lottery numbers","i want to play the lottery", "lottery", "give me numbers for my lottery ticket"], logical_instance.lottery),
        "dice": (["roll the dice", "throw the dice", "toss the dice", "roll dice", "give me a dice roll", "roll a dice"], logical_instance.diceroll),
        "image_generator": (["create a picture", "generate an illustration", "make an artwork", "produce an image", "draw an image"], logical_instance.dalle),
        "merge_pdfs": (["join pdf files", "consolidate pdfs", "unite pdfs", "blend pdfs", "fuse pdfs","merge pdfs"], logical_instance.merge_pdfs),
        "pass_check": (["verify my password", "evaluate password strength", "assess password security", "rate my password", "analyze password robustness"], logical_instance.checkapass),
        "png_to_pdf": (["png to pdf","change png to pdf", "transform png to pdf", "alter png to pdf", "turn png into pdf", "switch png to pdf"], logical_instance.png_to_pdf),
        "say_something": ([" "], logical_instance.typeSomething),
        "start_pomo": (["start pomo", "begin pomo", "start pomodoro", "begin pomodoro",], logical_instance.start_pomo),
        "stop_pomo": (["stop pomo", "end pomo", "stop pomodoro", "end pomodoro",], logical_instance.stop_pomo),
}
    return intents