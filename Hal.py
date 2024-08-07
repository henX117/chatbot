import os
from logic.intents import get_intents, logical
from logic.api_keys import OPENAI_API_KEY
from openai import OpenAI
import asyncio
import subprocess

class Chatbot(logical):
    def __init__(self, api_key, client=None, enable_tts=True):
        super().__init__(api_key, client=client)
        self.ENABLE_TTS = enable_tts

    def main(self):
        try:
            self.introduction()
            while True:
                command = input("").strip().lower()
                if command == "":
                    response = self.typeSomething()
                    print(response)
                else:
                    intent = self.find_intent(command)
                    if intent == "huh":
                        response = self.huh()
                        print(response)
                    elif intent == "analyze":
                        response = self.analyze_sentence()
                        print(response)
                    elif intent == "weather":
                        slot_values = self.extract_slot_values(command, intent)
                        filled_slots = self.fill_slots(intent, slot_values)
                        response = self.get_weather(filled_slots)
                        print(response)
                    elif intent == "pass_check":
                        try:
                            response = self.checkapass(command)
                            print(response)
                        except Exception as e:
                            print(f"An error occurred while checking password: {str(e)}")
                    elif intent == "lottery":
                        slot_values = self.extract_slot_values(command, intent)
                        filled_slots = self.fill_slots(intent, slot_values)
                        response = self.lottery(filled_slots.get("num_tickets", 1))
                        print(response)
                    else:
                        try:
                            intent_function = self.intents.get(intent, (None, None))[1]
                            if asyncio.iscoroutinefunction(intent_function):
                                response = asyncio.run(intent_function())
                            else:
                                response = intent_function()
                            print(response)
                        except AttributeError:
                            print(f"Error: The intent '{intent}' is not implemented/recognized.")
                        except asyncio.TimeoutError:
                            print("The operation timed out.")
                        except subprocess.CalledProcessError as e:
                            if e.returncode == 305:
                                print("--An error occurred, but everything is fine.--")
                            else:
                                print(f"subprocess error: {str(e)}")
                        except Exception as e:
                            print(f"An error occurred: {str(e)}")
                            print("If this error persists, please post your log file on the GitHub page.\n https://github.com/henX117/chatbot")
                    self.check_reminders()
        except KeyboardInterrupt:
            print("\nExiting the chatbot. Goodbye!")

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
    os.system('cls' if os.name == 'nt' else 'clear')

    chatbot.main()