import tkinter as tk
from tkinter import scrolledtext
from Hal import Chatbot
import api_keys

class ChatbotGUI:
    def __init__(self, master):
        self.master = master
        master.title("Chatbot")
        
        self.chatbot = Chatbot(api_keys.OPENAI_API_KEY)
        
        self.name_frame = tk.Frame(master)
        self.name_frame.pack(pady=10)
        
        tk.Label(self.name_frame, text="Welcome! Please enter your name:").pack()
        self.name_entry = tk.Entry(self.name_frame)
        self.name_entry.pack(pady=5)
        self.name_entry.bind("<Return>", self.set_name)
        
        tk.Button(self.name_frame, text="Start", command=self.set_name).pack()
        
        self.chat_frame = tk.Frame(master)
        
        self.chat_history = scrolledtext.ScrolledText(self.chat_frame, wrap=tk.WORD, width=50, height=20)
        self.chat_history.pack(pady=10)

        self.user_input = tk.Entry(self.chat_frame, width=50)
        self.user_input.pack(pady=5)
        self.user_input.bind("<Return>", self.send_message)

        self.send_button = tk.Button(self.chat_frame, text="Send", command=self.send_message)
        self.send_button.pack()
        
        self.user_input_dialog = None
        self.user_input_entry = None
        self.user_input_callback = None
    
    def set_name(self, event=None):
        name = self.name_entry.get()
        if name:
            self.chatbot.name = name
            self.name_frame.pack_forget()
            self.chat_frame.pack()
            
            # Speak the introduction
            introduction = self.chatbot.introduction()
            self.chat_history.insert(tk.END, "Chatbot: " + introduction + "\n")
        else:
            tk.messagebox.showwarning("Name Required", "Please enter your name to start the chatbot.")
    
    def send_message(self, event=None):
        user_message = self.user_input.get()
        self.chat_history.insert(tk.END, "You: " + user_message + "\n")
        self.user_input.delete(0, tk.END)

        intent = self.chatbot.find_intent(user_message)
        self.process_intent(intent)
    
    def process_intent(self, intent):
        intent_function = self.chatbot.intents.get(intent, (None, None))[1]

        if callable(intent_function):
            if intent == "lottery":
                self.open_user_input_dialog("Enter the number of lottery tickets you want to generate:")
            else:
                self.user_input_callback = intent_function
                self.open_user_input_dialog("Please provide the required input:")
        else:
            self.chat_history.insert(tk.END, "Chatbot: Sorry, I didn't understand that.\n")
    
    def open_user_input_dialog(self, message):
        if self.user_input_dialog is None:
            self.user_input_dialog = tk.Toplevel(self.master)
            self.user_input_dialog.title("User Input")
            
            tk.Label(self.user_input_dialog, text=message).pack()
            self.user_input_entry = tk.Entry(self.user_input_dialog)
            self.user_input_entry.pack()
            self.user_input_entry.bind("<Return>", self.process_user_input)
            
            tk.Button(self.user_input_dialog, text="Submit", command=self.process_user_input).pack()
        else:
            self.user_input_dialog.deiconify()
    
    def process_user_input(self, event=None):
        user_input = self.user_input_entry.get()
        self.user_input_dialog.withdraw()
        
        if self.user_input_callback:
            try:
                response = self.user_input_callback(user_input)
                if isinstance(response, str):
                    self.chat_history.insert(tk.END, "Chatbot: " + response + "\n")
                elif isinstance(response, dict):
                    response_text = "\n".join([f"{key}: {value}" for key, value in response.items()])
                    self.chat_history.insert(tk.END, "Chatbot: " + response_text + "\n")
                else:
                    self.chat_history.insert(tk.END, "Chatbot: Sorry, I couldn't process the response.\n")
            except ValueError:
                self.chat_history.insert(tk.END, "Chatbot: Invalid input. Please try again.\n")
            
            self.user_input_callback = None

root = tk.Tk()
chatbot_gui = ChatbotGUI(root)
root.mainloop()