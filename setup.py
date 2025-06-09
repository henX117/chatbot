import subprocess
import sys
import os
import importlib

def is_package_installed(package):
    try:
        importlib.import_module(package)
        return True
    except ImportError:
        return False

def install_package(package):
    if not is_package_installed(package):
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            print(f'{package} installed successfully!')
        except subprocess.CalledProcessError as e:
            print(f'Error installing {package}: {e}')
    else:
        print(f'{package} ---is already installed!---')

def getspacy():
    install_package('pip')
    install_package('setuptools')
    install_package('wheel')
    install_package('spacy')
    if not is_package_installed('en_core_web_sm'):
        subprocess.check_call([sys.executable, '-m', 'spacy', 'download', 'en_core_web_sm'])
    print('Small language model installed...')
    if not is_package_installed('en_core_web_lg'):
        subprocess.check_call([sys.executable, '-m', 'spacy', 'download', 'en_core_web_lg'])
    print("Large language model installed...")
    install_package('spacy-lookups-data')
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
    install_package('pygame')

def getPDF():
    install_package('PyPDF4')

def getpyttsx3():
    install_package('pyttsx3')

def getsympy():
    install_package('sympy')

def getimg2pdf():
    install_package('img2pdf')

def getpymupdf():
    install_package('PyMuPDF')

def getpdfkit():
    install_package('pdfkit')

def getdocx():
    install_package('python-docx')

def getreportlab():
    install_package('reportlab')

def training():
    script_directory = os.path.dirname(os.path.abspath(__file__))
    spacy_training_file = os.path.join(script_directory, "logic","SpaCy","SpaCy_Training.py")
    subprocess.Popen([sys.executable, spacy_training_file])

print("Hello, User!\nThis file will install/check if you have all the necessary libraries to run the chatbot!")
print("--------------------------------------------------------------------------------------------------------------------------")
wantallornah = input("Would you like to install/validate all the libraries? (Type '1' for yes, 2 for no): ")
if wantallornah == '1':
    print("You have chosen to install all libraries.")
    getspacy()
    getopenai()
    getrequests()
    getwiki()
    getinflect()
    getApp()
    gettts()
    getplaysound()
    getPDF()
    getpyttsx3()
    getsympy()
    getimg2pdf()
    getpymupdf()
    getpymupdf()
    getpdfkit()
    getdocx()
    getreportlab()
    install_package('aiohttp')
    install_package('openpyxl')
    install_package('matplotlib')
    print("All libraries have been installed.")
    print("-------------------------------------------------------------------------")
    print("Please type '1' to begin training the SpaCy model.")
    iwantspacytraining = input()
    if iwantspacytraining == '1':
        try:
            training()
            print("--training has started. Please wait for it to finish.--")
        except Exception as e:
            print(f"An error occurred --> {e}")
        print("-------------------------------------------------------------------------")
        adios = input("Once Epochs are finished, type anything to exit...")
        quit()
    else:
        print("all finished! type anything to exit...")
        x = input("")
        quit()
elif wantallornah == 2:
    quit()

