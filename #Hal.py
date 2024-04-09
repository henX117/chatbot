from intents import get_intents, logical
import api_keys
class Chatbot(logical):
    def __init__(self, api_key):
        super().__init__(api_key)
        self.intents = get_intents(self)

    def main(self):
        self.introduction()
        while True:
            command = input("").strip().lower()
            intent = self.find_intent(command)
            try:
                intent_function = self.intents.get(intent, (None, None))[1]
                if callable(intent_function):
                    response = intent_function()
                else:
                    print(f"Error: The function associated with the intent {intent} is not callable or doesn't exist.")
                print(response)
                self.check_reminders()
            except Exception as e:
                print(f"An error occurred {e}")
if __name__ == "__main__":
    try:
        name = input("Welcome! Please state your name to continue\n-->")
    except KeyboardInterrupt:
        print("You done fucked up the whole thing.")
        quit()
    api_key = api_keys.OPENAI_API_KEY
    chatbot = Chatbot(api_key)
    chatbot.name = name
    chatbot.main()  # Call the main() method here
    