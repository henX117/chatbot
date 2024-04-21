import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton
from PyQt6.QtWidgets import QInputDialog
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from logic.intents import logical  # Or import your specific subclass
from logic.api_keys import OPENAI_API_KEY
import os
from user_setup import get_user_name
class ChatbotGUI(QWidget):
    def __init__(self, chatbot):
        super().__init__()
        self.chatbot = chatbot
        self.initUI()
        self.chatbot.chat_history = self.chat_history

    def initUI(self):
        self.setGeometry(100, 100, 400, 600)  # x, y, width, height
        self.setWindowTitle("Hal v1.1.2")
        layout = QVBoxLayout()
        layout.setSpacing(10)

        # Chat history text area
        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        self.chat_history.setFont(QFont('Arial', 12))
        layout.addWidget(self.chat_history)

        # User input field
        self.user_input = QLineEdit()
        self.user_input.setFont(QFont('Arial', 12))
        self.user_input.returnPressed.connect(self.send_message)
        layout.addWidget(self.user_input)

        # Send button
        self.send_button = QPushButton("Send")
        self.send_button.setFont(QFont('Arial', 12))
        self.send_button.clicked.connect(self.send_message)
        layout.addWidget(self.send_button)

        self.setLayout(layout)
        self.setWindowTitle("Hal v1.1.2")

        # Styling
        self.setStyleSheet("""
            QWidget {
                background-color: #34495e;
            }
            QTextEdit {
                background-color: #ecf0f1;
                border: 1px solid #bdc3c7;
                color: #2c3e50;
                padding: 5px;
            }
            QLineEdit {
                background-color: #ecf0f1;
                border: 1px solid #bdc3c7;
                color: #2c3e50;
                padding: 5px;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 10px;
                border-radius: 5px;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #3498db;
                border: 1px solid #2980b9;
            }
        """)

    def send_message(self):
        user_message = self.user_input.text()
        self.user_input.clear()
        self.chat_history.append(f"You: {user_message}")
        print(f"User message: {user_message}") #debug line
        response = self.chatbot.find_intent(user_message)
        print(f"Chatbot response: {response}") #debug line
        if response['type'] == 'input_request':
            if response['message'] == "What app do you want to open? (Type 'cancel' to stop trying to open an app)":
                self.chatbot.active_intent = "open app"
            elif response['message'] == "What app do you want to close?":
                self.chatbot.active_intent = "close app"
            elif response['message'] == "Enter a location:":
                self.chatbot.active_intent = "weather"
            elif response['message'] == "What should I remind you about?":
                self.chatbot.active_intent = "remind"
            elif response['message'] == "What would you like to search for on Wikipedia?":
                self.chatbot.active_intent = "wiki"
            elif response['message'] == "Type the image that you would like to be generated (or type 'stop' to go back to the main menu):":
                self.chatbot.active_intent = "image generator"
            self.request_user_input(response['message'], self.handle_user_input)
        else:
            if response['message'] == "cls":
                response = self.chatbot.cls()
            self.chat_history.append(f"Chatbot: {response['message']}")
            if self.chatbot.active_intent in ["open app", "close app", "weather", "remind", "wiki", "image generator"]:
                self.chatbot.active_intent = None

    def handle_user_input(self, user_input):
        print(f"User input from input request window: {user_input}")  # debug line
        response = self.chatbot.process_user_input(user_input)
        print(f"Response from process_user_input: {response}")  # debug line
        if response['type'] == 'input_request':
            if response['message'].startswith("Enter the "):
                self.request_user_input(response['message'], self.handle_user_input)
            elif response['message'].startswith("Which analysis do you want?"):
                self.request_user_input(response['message'], self.handle_user_input)
            else:
                self.chat_history.append(f"Chatbot: {response['message']}")
        else:
            self.chat_history.append(f"Chatbot: {response['message']}")
            if self.chatbot.active_intent in ["analyze", "analyze_summary", "analyze_visualization", "open app", "close app", "weather", "remind", "wiki", "image generator", "math"]:
                self.chatbot.active_intent = None

    def request_user_input(self, message, callback):
        text, ok = QInputDialog.getText(self, 'Input Request', message)
        if ok:
            callback(text)

def main():
    app = QApplication(sys.argv)
    # Here we pass the API key to the logical class
    if not os.path.exists('user_name.txt'):
        print("Username file not found. run setup.py first.")
        return
    chatbot = logical(api_key=OPENAI_API_KEY)
    gui = ChatbotGUI(chatbot)
    gui.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()