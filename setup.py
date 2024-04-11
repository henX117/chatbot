#inital setup
import subprocess
import sys
import os

def install_package(package):
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
        print(f'{package} installed successfully!')
    except subprocess.CalledProcessError as e:
        print(f'Error installing {package}: {e}')

def getspacy():
    install_package('pip')
    install_package('setuptools')
    install_package('wheel')
    install_package('spacy')
    subprocess.check_call([sys.executable, '-m', 'spacy', 'download', 'en_core_web_sm'])
    print('Small language model installed...')
    subprocess.check_call([sys.executable, '-m', 'spacy', 'download', 'en_core_web_lg'])
    print("Large language model installed...")
    print("All of spacy has finished installing!")
    print("-------------------------------------------------------------------------")

def getopenai():
    install_package('openai')

def getrequests():
    install_package('requests')

def getwiki():
    install_package('wikipedia')

def getinflect():
    install_package('inflect')

def getApp():
    install_package('AppOpener')

def gettts():
    install_package('gtts')

def getplaysound():
    install_package('playsound')

def getPDF():
    install_package('PyPDF4')

def getpyttsx3():
    install_package('pyttsx3')

print("Hello, User!\nThis file will install all the necessary libraries to run the chatbot!\nYou can also do this process manually if you would like to! Check the README for more information!")

try:
    wantspacy = input("Please type 1 if you would like to install spacy automatically. Else, please type anything to continue... ")
    if wantspacy == '1':
        getspacy()
    else:
        print("Spacy not installed.")

    wantopenai = input("Type 1 if you want OpenAI: ")
    if wantopenai == '1':
        getopenai()
    else:
        print("OpenAI not installed.")

    wantreq = input("Type 1 if you want Requests: ")
    if wantreq == '1':
        getrequests()
    else:
        print("Requests not installed.")

    wantwiki = input("Type 1 if you want Wikipedia: ")
    if wantwiki == '1':
        getwiki()
    else:
        print("Wikipedia library not installed.")

    wantinflect = input("Type 1 if you want Inflect: ")
    if wantinflect == '1':
        getinflect()
    else:
        print("Inflect library not installed.")

    wantgetapp = input("Type 1 if you want AppOpener: ")
    if wantgetapp == '1':
        getApp()
    else:
        print("AppOpener not installed.")

    wanttts = input("Type 1 if you want Text-to-Speech (gTTS): ")
    if wanttts == '1':
        gettts()
    else:
        print("gTTS not installed.")

    wantsound = input("Type 1 if you want Playsound: ")
    if wantsound == '1':
        getplaysound()
    else:
        print("Playsound not installed.")

    wantPDF = input("Type 1 if you want PyDF4 ")
    if wantPDF == '1':
        getPDF()
    else:
        print("Not installing.")
    
    wantpyttsx3 = input("Type 1 to install pyttsx3 ")
    if wantpyttsx3 == '1':
        getpyttsx3()
    else:
        print("Not installing")

except Exception as e:
    print(f"An error occurred --> {e}")

print("All done! This file can now be safely closed.")
print("-------------------------")
print("READ ME and CHATBOT will be automatically opened. Type anything to now close this file...")
print("-------------------------")
try:
    script_directory = os.path.dirname(os.path.abspath(__file__))
    readme_file = os.path.join(script_directory, "README.txt")
    os.startfile(readme_file)
except Exception as e:
    print(f"An error occurred --> {e}")
x = input("")
quit()