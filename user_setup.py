import os

def get_user_name(file_path):
    user_name = input("What's your name? ")
    
    try:
        with open(file_path, 'w') as f:
            f.write(user_name)
        print(f"Hello, {user_name}! Your name has been saved.")
    except PermissionError:
        print(f"Error: Insufficient permissions to create the file '{file_path}'.")
    except FileNotFoundError:
        print(f"Error: The directory for the file '{file_path}' does not exist.")
    except Exception as e:
        print(f"Error: An unexpected error occurred - {str(e)}")

if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, 'user_name.txt')
    
    print("Script directory:", script_dir)
    print("User name file path:", file_path)
    
    if not os.path.exists(file_path):
        get_user_name(file_path)
    else:
        try:
            with open(file_path, 'r') as f:
                user_name = f.read().strip()
            print(f"Welcome back, {user_name}!")
        except FileNotFoundError:
            print(f"Error: The file '{file_path}' does not exist.")
        except Exception as e:
            print(f"Error: An unexpected error occurred - {str(e)}")
    
    input("Press Enter to exit...")