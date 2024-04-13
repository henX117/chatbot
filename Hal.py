from logic.intents import get_intents, logical
from logic.api_keys import OPENAI_API_KEY

class Chatbot(logical):
    def __init__(self, api_key, enable_tts=True):
        super().__init__(api_key)
        self.ENABLE_TTS = enable_tts

    def main(self):
        self.introduction()
        while True:
            command = input("").strip().lower()
            intent = self.find_intent(command)
            if intent == "huh":
                response = self.huh()
                print(response)
            else:
                try:
                    intent_function = self.intents.get(intent, (None, None))[1]
                    if callable(intent_function):
                        response = intent_function()
                        print(response)
                    else:
                        print(f"Error: The function associated with the intent {intent} is not callable or doesn't exist.")
                except Exception as e:
                    print(f"An error occurred {e}")
            self.check_reminders

if __name__ == "__main__":
    try:
        name = input("Welcome! Please state your name to continue\n-->")
        enable_tts = True
        if name.lower() == 'notts':
            enable_tts = False
            print("tts disabled")
            name = input("name:")
    except KeyboardInterrupt:
        print("You done fucked up the whole thing.")
        x = input("press any key to quit")
    except Exception as L:
        print(f"Exception Error: {L}")
    api_key = OPENAI_API_KEY
    chatbot = Chatbot(api_key, enable_tts=enable_tts)
    chatbot.name = name
    chatbot.main()  # Call the main() method here