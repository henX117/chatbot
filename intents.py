#intents.py
import os
import math
import spacy
import webbrowser
from spacy.matcher import Matcher
import warnings
import requests
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
import api_keys

class logical:
    def __init__(self, api_key):
        self.chatbot = 'Hal'
        self.fullchatbot = 'Halsey'
        self.name = ''
        self.client = OpenAI(api_key=api_key)
        self.ENABLE_TTS = True
        self.reminders = []
        self.nlp = spacy.load("en_core_web_lg")
        self.matcher = Matcher(self.nlp.vocab)
        pattern = [{"LOWER": "open"}, {"IS_ALPHA": True}]
        self.matcher.add("OPEN_APP", [pattern])
        self.known_apps = ['spotify', 'chrome', 'word', 'excel']
        self.reminder_thread = threading.Thread(target=self.reminder_loop)
        self.reminder_thread.daemon = True
        self.reminder_thread.start()
        self.commands = {
            "app": "Opens an app",
            "cls": "clears the screen",
            "math": "to do mathematics!",
            "quit": "to leave the program",
            'analyze': "to analyze",
            "time": "tells the current time",
            "joke": "tells a joke",
            "news": "see whats on the headlines",
            "weather": "get weather information",
            "rock paper scissors": "play the rock paper scissors game",
            "windows": "shows what version of windows OS is using",
            "remind": "set a reminder",
            "wiki": "search Wikipedia" }


    def randomnumgen(self):
        whatrange = int(input("Enter starting range -> "))
        lastrange = int(input("Enter ending range -> "))
        

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

    def speak(self, message):
        if not self.ENABLE_TTS:
            return ""
        import playsound
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
            playsound.playsound(str(speech_file_path), True)
        except Exception as e:
            print(f"An error occurred: {e}")

    def speak_and_return(self, message):
        self.speak(message)
        return message

    def rockpaperscissors(self):
        print("---------------------------------------------------")
        print("Welcome to rock paper scissors!")
        choices = ['rock', 'paper', 'scissors']
        while True:
            my_choice = input("Type either 'rock','paper',scissors'")
            robo_choice = random.choice(choices)
            if my_choice == robo_choice:
                print(f"we picked the same thing! Lets try again?")
            elif my_choice == 'rock' and robo_choice == 'scissors':
                print("you win! type quit to go to the main menu!")
            elif my_choice == 'rock' and robo_choice == 'paper':
                print("I WIN HAHAHAHAHA\n type quit to exit!")
            elif my_choice == 'paper' and robo_choice == 'scissors':
                print("I WIN HAHAHAHAHA")
            elif my_choice == 'paper' and robo_choice == 'rock':
                print("you win!")
            elif my_choice == 'scissors' and robo_choice == 'paper':
                print("you cut me up! YOU WIN!!")
            elif my_choice == 'scissors' and robo_choice == 'rock':
                self.speak_and_return("this rock messed you up!")
            elif my_choice == 'quit':
                self.speak_and_return("Well, that was fun playing rock paper scissors. lets play next time!")
                break
            else:
                print("a problem just happened! restarting")
                print("--------------------------------")
        return ""

    def ineedhelp(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        self.speak_and_return(f"here is a list of helpful commands,{self.name}.")
        return self.commands

    def extract_app_name(self, command):
        doc = self.nlp(command)
        for match_id, start, end in self.matcher(doc):
            span = doc[start:end]
            if span.text:
                return span.text.split(" ")[1]  # Return app name after "open"
        return None

    def openapp(self):
        self.speak("What app do you want to open?")
        command = input("What app do you want to open: ")
        app_name = command
        if app_name:
            try:
                import AppOpener
                print(f"Attempting to open {app_name}")
                self.speak(f"Attempting to open {app_name}")
                AppOpener.open(app_name)
            except Exception as e:
                print(f"Error trying to open {app_name}: {str(e)}")
        else:
            print("Sorry, I couldn't identify the app that you want to open.")
        print(self.matcher)
        return self.speak_and_return(f"what else would you like to do, {self.name}?")

    def closeapp(self):
        self.speak(f"What app do you want to close {self.name}")
        command = input(f"What app do you want to close, {self.name}?")
        try:
            from AppOpener import close
            (f"attempting to close{command}")
            close(command)
        except RuntimeError:
            return self.speak_and_return(f"{command} does not want to cooperate and close. try again??")

    def analyze_sentence(self, command):
        try:
            from spacy import displacy
            self.speak("Do you want a large analysis or small analysis?")
            which_nlp = input("Which analysis do you want?'small' or 'large'?\n").strip().lower()
            if which_nlp == 'small':
                nlp = spacy.load("en_core_web_sm")
                doc = nlp(command)
                sentences = list(doc.sents)
                html_ent1 = displacy.render(sentences, style="ent")
                html_dep1 = displacy.render(sentences, style="dep")
                self.speak("Small analysis, got it.")
                html_combined1 = "<html><head><title><SpaCy Analysis</title></head><body>" + html_ent1 + html_dep1 + "</body></html>"
                with open("data_visC.html", "w", encoding="utf-8") as f:
                    f.write(html_combined1)
                try:
                    if os.path.exists("data_visC.html") and os.access("data_visCG.html", os.R_OK):
                        webbrowser.open("data_visC.html")
                except (LookupError):
                    print("couldn't open the HTML. Try and find it in your files!")
            # ------------------------------------------------------------------------
            elif which_nlp == 'large':
                nlp = spacy.load("en_core_web_lg")
                print("large language model loaded")
                doc = nlp(command)
                print("sentence converted into doc")
                sentences = list(doc.sents)
                print("sentence converted to list")
                self.speak("large analysis, got it.")
                html_ent = displacy.render(sentences, style="ent")
                html_dep = displacy.render(sentences, style='dep')
                html_combined = "<html><head><title><SpaCy Analysis</title></head><body>" + html_ent + html_dep + "</body></html>"
                print("HTML has been rendered")

                with open("data_visCG.html", "w", encoding="utf-8") as f:
                    f.write(html_combined)
                try:
                    if os.path.exists("data_visCG.html") and os.access("data_visCG.html", os.R_OK):
                        webbrowser.open("data_visCG.html")
                        self.speak(f"okay, I'm finished analyzing the file. I'll display the contents to your screen {self.name}")
                except (LookupError):
                    print("couldn't open the HTML. Try and find it in your files!")
        except (ValueError, KeyError, SyntaxError):
            self.speak_and_return("something went so wrong with that. wtf did you do?")

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
            f"this is as empty as my back account!",
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
        from ast import literal_eval
        x = input("input a math equation")
        return self.speak_and_return(f"Heres your answer: {eval(x)}")

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

    def get_weather(self, city):
        api_key = api_keys.WEATHER_API_KEY
        base_url = "http://api.weatherstack.com/current"
        params = {
            "access_key": api_key,
            "query": city,
            "units": "f"  # Requesting weather data in Fahrenheit directly from the API
        }
        response = requests.get(base_url, params=params)

        if response.status_code == 200:
            data = response.json()
            # Check if the API response contains the expected data
            if 'current' in data:
                current = data['current']
                weather_descriptions = current.get('weather_descriptions', ['Not Available'])[0]
                temperature = current.get('temperature', 'Not Available')  # Already in Fahrenheit
                feelslike = current.get('feelslike', 'Not Available')  # Already in Fahrenheit

                weather_info = (f"Weather in {city.title()}: {weather_descriptions}, "
                                f"Temperature: {temperature} degrees, "
                                f"Feels like: {feelslike} degrees.")
                return self.speak_and_return(f"{self.name}, here's the weather information: \n {weather_info}")
            else:
                return "Weather data not found. Please try another location."
        else:
            return "Failed to retrieve weather data. Please try again later."

    def time(self):
        d = datetime.now()
        time_str = d.strftime("%I:%M %p")
        print(time_str)
        return self.speak(f"It's currently {time_str}")

    def handle_greeting(self):
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

    def oopsies(self):
        return self.speak_and_return("its okay, no worries.")

    def ifeelgood(self):
        responses = [
            f"That's great to hear,{self.name}.",
            f"Awesome! Keep up the positive vibes,{self.name}!",
            f"Glad to hear that,{self.name}!"
        ]
        X = random.choice(responses)
        return self.speak_and_return(X)

    def ifeelbad(self):  # add isaacs thing. get lottery numbers
        lotto = random.randint(1000000, 99999099)
        responses = [
            "Oh. Sorry to hear that.",
            "I'm sorry to hear that.",
            "Life has its ups and downs. Want to hear a joke to cheer up? you can say, 'tell me a joke",
            f"Oh cheer up {self.name}.. Here's some lottery numbers. Go have some fun! \n The numbers are {lotto}",
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
        return self.speak(f"Alright, {self.name} you are sounding a little angry.")

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
            self.speak_and_return(repeat)
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
            f"Good {self.morningornah}, {self.name}."
            f"Good {self.morningornah}!"
            f"Hi!"
            f"it's great to see you again, {self.name}!"
            f"Looks like it's {self.morningornah}! Have any plans, {self.name}?"
            f"What's on your mind today, {self.name}?"
            f"I'm here to assist you with anything. What's the first thing on your agenda today, {self.name}?"
            f"Welcome {self.name}. If you need anything specific, type 'help'."
            f"Hey {self.name}, nice to see you! I got a nice joke cooked up. ask me to tell you a joke!"
            f"{self.name}. I didn't know this until now but... Did you know that {self.time}?"
        ]
        X = random.choice(possible_intro)
        return self.speak_and_return(f"{X}")

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

    def tell_joke(self):
        response = requests.get("https://official-joke-api.appspot.com/random_joke")
        if response.status_code == 200:
            joke = response.json()
            setup = joke['setup']
            punchline = joke['punchline']
            print(f"{setup}\n{punchline}")
            alltogether = setup + punchline
            self.speak(f"{alltogether}.")
            return ""
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
    def find_intent(self, user_input):
    # Process the user input
        input_doc = self.nlp(user_input)
        scores = {}

    # Compare the user input to each command template in the intents dictionary
        for command, (templates, _) in self.intents.items():
        # Ensure there's at least one element (the template phrase or phrases) in the tuple
            if len(templates) > 0:
            # If there are multiple templates, iterate through them
                template_scores = [input_doc.similarity(self.nlp(template)) for template in templates]
            # Use the highest score among the template phrases for this command
                scores[command] = max(template_scores)

    # Identify the command with the highest similarity score
        intent = max(scores, key=scores.get)
        return intent

def get_intents(logical_instance):
    intents = {
        "cls": (["cls", "clear the screen"], logical_instance.cls),
        "help": (["i need help", "can you assist me", "how does this work", "show me the available commands"], logical_instance.ineedhelp),
        "time": (["what time is it", "tell me the time now", "could you give me the time", "time check"], logical_instance.time),
        "open app": (["open an app", "I want to fucking open an app", "I want to open an app", "i want to open an application", "launch an app for me", "start Spotify", "open Chrome"], logical_instance.openapp),
        "close app": (["close an application", "shut down an app", "close Chrome", "shut Spotify"], logical_instance.closeapp),
        "analyze": (["analyze a paper for me", "analyze this sentence", "analise this sentence", "do text analysis", "check this text"], lambda: logical_instance.analyze_sentence(input("Enter a sentence to analyze\n"))),
        "math": (["i need to calculate something", "can you help me with maths?", "i want to solve a math problem", "do some math"], logical_instance.math),
        "thanks": (["thanks for the", "thank you", "thanks", "i give you my thanks", "i appreciate it", "respect", "thats whats up", "I owe you one"], logical_instance.thanks),
        "quit": (["i quit", "i want to quit", "I want to leave", "exit", "im finished", "can i quit"], logical_instance.quitter),
        "joke": (["joke", "tell me another joke", "tell me a joke", "make me laugh", "I want to laugh", "are you funny", "tell me a funny joke"], logical_instance.tell_joke),
        "weather": (["whats the weather like in", "tell me the weather in", "weather", "whats the weather", "show me the weather report", "weather report", "hows the weather", "whats the weather going to be like","give me the weather forecast", "whats the weather going to be like"], lambda: logical_instance.get_weather(input("Enter a location:\n"))),
        "rock paper scissors": (["lets play RPS", "rock paper scissors", "can we play rock paper scissors"], logical_instance.rockpaperscissors),
        "greetings": (["hello", "hi", "good afternoon", "good morning", "whats up", "sup", "hey"], logical_instance.handle_greeting),
        "how are you": (["how are you", "how are you doing", "how are you feeling"], logical_instance.howareyou),
        "what is your name": (["what is your name", "whats your name", "do you have a name", "who are you"], logical_instance.myname),
        "my name": (["say my name", "what is my name", "who am i", "whats my name", "my name", "i am who", "do you even know who i am"], logical_instance.yournameis),
        "windows": (["windows version", "windows", "what operating system is this", "operating system details", "what version of windows am i using"], logical_instance.operatingsystem),
        "sorry": (["im sorry", "my apologies", "oops", "oopsies", "whoops", "my bad"], logical_instance.oopsies),
        "i feel good": (["Im good", "good", "i feel great", "i am fantastic", "im okay", "im alright", "good and you"], logical_instance.ifeelgood),
        "i feel bad": (["im doing bad", "im not so good", "im sad", "im not happy", "im not okay", "eh", " i am sad", "i feel bad", "you make me sad"], logical_instance.ifeelbad),
        "discuss hobbies": (["what are your hobbies", "do you have hobbys", "got any hobbies", "hobby", "hobbies"], logical_instance.discuss_hobbies),
        " ": ([" ", ""], logical_instance.typeSomething),
        "xac hellven": (["who is xac", "who is xac hellven", "xac has arrived planet hellven", "whos xac", "who the fuck is xac hellven", "tell me about xac hellven"], logical_instance.xac_facts),
        "youtube": (["open youtube", "youtube", "YT", "open YT"], logical_instance.youtube),
        "GPT": (["open chat gpt", "GPT", "launch GPT", "open gpt"], logical_instance.gpt),
        "enable tts": (["enable text to speech", "enable tts"], logical_instance.enable_tts),
        "disable tts": (["disable text to speech", "disable tts", "turn off tts"], logical_instance.disable_tts),
        "angry": (["im mad", "i am mad", "i am angry", "you are pissing me off", "i am pissed off", "i am so mad", "I am so mad right now", "angry", "im angry", "im so angry"], logical_instance.angy),
        "copy": (["copy", "copy me", "copy what im saying", "duplicate this", "copy this", "Say this"], logical_instance.copy),
        "time conversion": (["time conversion", "hours to minutes", "minutes to hours", "what is this in minutes", "what is this in hours"], logical_instance.timeconversion),
        "calculate compound interest": (["calculate compound interest", "compound interest calculator", "interest"], logical_instance.calccompoundinterest),
        "remind": (["remind me", "set a reminder", "add a reminder"], logical_instance.set_reminder),
        "wiki": (["search wikipedia", "look up on wikipedia", "wikipedia"], logical_instance.search_wikipedia),
        "random number": (["random number", "random num", "random number generator", "generate a random number", "random num generator"], logical_instance.randomnumgen),
        }
    return intents