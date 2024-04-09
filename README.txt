README - Chatbot Project

Description:
This project is a chatbot named Hal (short for Halsey) implemented in Python. The chatbot utilizes natural language processing (NLP) and various APIs to provide a range of functionalities, including:
- Answering questions and providing information
- Opening and closing applications
- Performing text analysis
- Solving math problems
- Telling jokes and providing weather information
- Playing games like Rock Paper Scissors
- Handling greetings and conversations
- Setting reminders
- Searching Wikipedia
- Generating random numbers
- And more!

Prerequisites:
Before running the chatbot, ensure that you have the following libraries installed:
- spacy
webbrowser
- openai
- requests
- wikipedia
- inflect
- AppOpener
- gtts
- playsound

You can install these libraries using pip. For example:
1) Spacy
pip install -U pip setuptools wheel
pip install -U spacy
python -m spacy download en_core_web_sm
python -m spacy download en_core_web_lg

2) OpenAI
pip install --upgrade openai

3) Requests
pip install requests

4) Wikipedia
pip install wikipedia

5) Inflect
pip install inflect

6) AppOpener
pip install appopener

7) gTTS
pip install gTTS

8) playsound
pip install playsound


Additionally, make sure you have the necessary language models downloaded for spacy. You can download them by running:
python -m spacy download en_core_web_sm
python -m spacy download en_core_web_lg

Configuration:
Before running the chatbot, you need to provide your API keys in the `api_keys.py` file. Replace the placeholders with your actual API keys:
- OPENAI_API_KEY: Your OpenAI API key
- WEATHER_API_KEY: Your weather API key (from weatherstack.com)
- JOKE_API_KEY: Your joke API key (from official-joke-api.appspot.com)

Usage:
To start the chatbot, run the `#Hal.py` file. You will be prompted to enter your name. After providing your name, you can interact with the chatbot by typing your messages or commands.

The chatbot supports various commands and intents. You can type "help" or "I need help" to see a list of available commands.

Some key functionalities include:
- Saying "open [application_name]" to open a specific application
- Asking for the current time or weather information
- Requesting jokes or playing Rock Paper Scissors
- Performing math calculations
- Analyzing text using spacy
- Setting reminders
- Searching Wikipedia

You can explore the different commands and intents to discover more functionalities of the chatbot.

Files:
- `#Hal.py`: The main chatbot file that initializes the chatbot and handles user interactions.
- `intents.py`: Contains the implementation of the chatbot's intents and logical processing.
- `api_keys.py`: Stores the API keys used by the chatbot (you need to provide your own keys).

Note: Make sure to keep your API keys secure and do not share them publicly.

Acknowledgements:
The chatbot project uses various libraries and APIs, including:
- spacy: For natural language processing
- OpenAI: For language model integration
- weatherstack.com: For retrieving weather information
- official-joke-api.appspot.com: For fetching jokes

Feel free to customize and extend the chatbot based on your requirements. If you have any questions or issues, please don't hesitate to reach out.

Enjoy chatting with Hal!