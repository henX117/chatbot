import os
import spacy
from spacy.util import minibatch, compounding
from spacy.training import Example
import openpyxl
import warnings
import matplotlib.pyplot as plt

warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore")

nlp = spacy.load("en_core_web_lg")

if 'textcat' not in nlp.pipe_names:
    nlp.add_pipe("textcat", last=True)

textcat = nlp.get_pipe("textcat")

def load_training_data(file_path):
    workbook = openpyxl.load_workbook(file_path)
    sheet = workbook.active
    training_data = []
    
    intents = [cell.value for cell in sheet[1] if cell.value]
    
    for row in sheet.iter_rows(min_row=2, values_only=True):
        for intent, phrase in zip(intents, row):
            if phrase:
                training_data.append((phrase, intent))
    
    return training_data, intents

def calculate_accuracy(model, data):
    correct = 0
    total = 0
    for text, true_label in data:
        doc = model.make_doc(text)
        predicted_label = max(model(doc).cats, key=model(doc).cats.get)
        if predicted_label == true_label:
            correct += 1
        total += 1
    accuracy = correct / total
    return accuracy

# Get the path to the training data file relative to the current script
current_dir = os.path.dirname(os.path.abspath(__file__))
training_file = os.path.join(current_dir, "training_data.xlsx")

# Load training data from Excel file
train_data, labels = load_training_data(training_file)

for label in labels:
    textcat.add_label(label)

accuracies = []
losses = []

optimizer = nlp.begin_training()
for i in range(10):
    epoch_losses = {}
    batches = minibatch(train_data, size=compounding(32.0, 128.0, 1.001))
    for batch in batches:
        examples = []
        for text, annotation in batch:
            doc = nlp.make_doc(text)
            example = Example.from_dict(doc, {"cats": {label: label == annotation for label in labels}})
            examples.append(example)
        nlp.update(examples, sgd=optimizer, losses=epoch_losses)
    
    accuracy = calculate_accuracy(nlp, train_data)
    accuracies.append(accuracy)
    losses.append(epoch_losses['textcat'])
    
    print(f"Epoch {i+1}: Loss = {epoch_losses['textcat']:.3f}, Accuracy = {accuracy:.3f}")

plt.figure(figsize=(12, 6))

plt.subplot(1, 2, 1)
plt.plot(range(1, len(accuracies) + 1), accuracies)
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.title('Training Accuracy')

plt.subplot(1, 2, 2)
plt.plot(range(1, len(losses) + 1), losses)
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.title('Training Loss')

plt.tight_layout()
plt.show()

# Save the trained model relative to the current script's directory
model_dir = os.path.join(current_dir, "SpaCy")
nlp.to_disk(model_dir)
print("Officially trained the model!")