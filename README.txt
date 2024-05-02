README - Chatbot Project

Description:
This project is a chatbot named Hal (short for Halsey) implemented in Python. The chatbot utilizes natural language processing (NLP) and various APIs to provide a range of functionalities, including:
- Answering questions and providing information
- Opening and closing applications
- Performing text analysis
- Solving math problems
- Telling jokes and providing weather information
- Playing games
- Handling greetings and conversations
- Setting reminders
- Searching Wikipedia
- Generating random numbers
- merging PDF's
- and more!

Prerequisites:
Before running the chatbot, ensure that you have the following libraries installed:
- spacy
- openai
- requests
- wikipedia
- inflect
- AppOpener
- gtts
- pygame
- PyPDF4 
- pyttsx3
- sympy
- img2pdf
- aiohttp
- openpyxl
- matplotlib

You can install these libraries using pip. For example:
1) Spacy
pip install -U pip setuptools wheel
pip install -U spacy
python -m spacy download en_core_web_sm
python -m spacy download en_core_web_lg
pip install spacy-lookups-data

2) OpenAI
pip install --upgrade openai

3) Requests
pip install requests

...

Usage:
1. To start the chatbot for the first time, run the "setup.py file. It will install the required libraries.
2. run the "user_setup.py" file. This will ask you for you name.
3 If you have API keys for 'openai', 'weatherstack.com', 'official-joke-api.appstop.com' --> place them in the 'api_keys.py' file.
4. Run "Hal.py"

The chatbot supports various commands and intents. You can type "help" or "I need help" to see a list of available commands.


Note: Make sure to keep your API keys secure and do not share them publicly.

Acknowledgements:
The chatbot project uses various libraries and APIs, including:
- spacy: For natural language processing
- OpenAI: For language model integration
- weatherstack.com: For retrieving weather information
- official-joke-api.appspot.com: For fetching jokes
- and many other libraries previously mentioned.
These libraries are essential for running the chatbot and could not be done without them. 


If you have any questions, issues, or suggestions please don't hesitate to reach out!

Authors:
- Henry G