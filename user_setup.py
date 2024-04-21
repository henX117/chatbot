import os

def get_user_name():
    user_name = input("What's your name? ")
    with open('user_name.txt', 'w') as f:
        f.write(user_name)
    print(f"Hello, {user_name}! Your name has been saved.")

if __name__ == '__main__':
    if not os.path.exists('user_name.txt'):
        get_user_name()
    else:
        with open('user_name.txt', 'r') as f:
            user_name = f.read().strip()
        print(f"Welcome back, {user_name}!")