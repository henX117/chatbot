from logic.intents import get_intents, logical
from logic.api_keys import OPENAI_API_KEY

class Chatbot(logical):
    def __init__(self, api_key, enable_tts=True):
        super().__init__(api_key)
        self.intents = get_intents(self)
        self.ENABLE_TTS = enable_tts

    def main(self):
        self.introduction()
        while True:
            command = input("").strip().lower()
            intent = self.find_intent(command)
            try:
                intent_function = self.intents.get(intent, (None, None))[1]
                if callable(intent_function):
                    response = intent_function()
                    print(response)
                else:
                    print(f"Error: The function associated with the intent {intent} is not callable or doesn't exist.")
                self.check_reminders()
            except Exception as e:
                print(f"An error occurred {e}")

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
        quit()
    api_key = OPENAI_API_KEY
    chatbot = Chatbot(api_key, enable_tts=enable_tts)
    chatbot.name = name
    chatbot.main()  # Call the main() method here