import os
from logic.intents import get_intents, logical
from logic.api_keys import OPENAI_API_KEY
from openai import OpenAI
import asyncio
class Chatbot(logical):
    def __init__(self, api_key, client=None, enable_tts=True):
        super().__init__(api_key, client=client)
        self.ENABLE_TTS = enable_tts

    def main(self):
        self.introduction()
        while True:
            command = input("").strip().lower()
            intent = self.find_intent(command)
            if intent == "huh":
                response = self.huh()
                print(response)
            elif intent =="analyze":
                response = self.analyze_sentence()
                print(response)
            else:
                try:
                    intent_function = self.intents.get(intent, (None, None))[1]
                    if asyncio.iscoroutinefunction(intent_function):
                        response = asyncio.run(intent_function())
                    else:
                        response = intent_function()
                    print(response)
                except Exception as e:
                    print(f"An error occurred: {str(e)}")
            self.check_reminders()

script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)
user_name_file = os.path.join(script_dir, 'user_name.txt')

if __name__ == "__main__":
    try:
        enable_tts = True
        if not os.path.exists('user_name.txt'):
            print("Username file not found...\n this was detected in Hal.py!")
            name = input("Enter your name: ")
            with open('user_name.txt', 'w') as f:
                f.write(name)
    except Exception as L:
        print(f"Exception Error: {L}")
    api_key = OPENAI_API_KEY
    client = OpenAI(api_key=api_key) if api_key else None
    chatbot = Chatbot(api_key, client=client, enable_tts=enable_tts)
    chatbot.main()