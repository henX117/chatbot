import random

class RockPaperScissors:
    def __init__(self):
        self.choices = ['rock', 'paper', 'scissors']
        self.user_wins = 0
        self.robot_wins = 0

    def get_user_choice(self):
        while True:
            my_choice = input("Type either 'rock', 'paper', or 'scissors': ").lower()
            if my_choice in self.choices or my_choice == 'quit':
                return my_choice
            else:
                print("Invalid choice. Please try again.")

    def determine_winner(self, my_choice, robo_choice):
        if my_choice == robo_choice:
            return "It's a tie!"
        elif (my_choice == 'rock' and robo_choice == 'scissors') or \
             (my_choice == 'paper' and robo_choice == 'rock') or \
             (my_choice == 'scissors' and robo_choice == 'paper'):
            self.user_wins += 1
            return "You win!"
        else:
            self.robot_wins += 1
            return "I win!"

    def play_game(self):
        print("Welcome to Rock-Paper-Scissors!")
        while True:
            my_choice = self.get_user_choice()
            if my_choice == 'quit':
                print("Thanks for playing!")
                break

            robo_choice = random.choice(self.choices)
            print(f"Robot chose: {robo_choice}")
            result = self.determine_winner(my_choice, robo_choice)
            print(result)
            print(f"Score: You {self.user_wins} - {self.robot_wins} Robot")

class DiceRoll:
    def __init__(self):
        self.sides = 6

    def roll(self):
        return random.randint(1, self.sides)

if __name__ == "__main__":
    dice_game = DiceRoll()
    print(f"You rolled a {dice_game.roll()}!")