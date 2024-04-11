import spacy
from spacy.lang.en.stop_words import STOP_WORDS
from heapq import nlargest

class TextSummarizer:
    def __init__(self, model="en_core_web_sm"):
        self.nlp = spacy.load(model)
    
    def preprocess(self, text):
        doc = self.nlp(text)
        words = [token.text.lower() for token in doc if not token.is_stop and not token.is_punct]
        return words
    
    def calculate_word_freq(self, words):
        word_freq = {}
        for word in words:
            if word not in word_freq.keys():
                word_freq[word] = 1
            else:
                word_freq[word] += 1
        return word_freq
    
    def calculate_sentence_scores(self, doc, word_freq):
        sentence_scores = {}
        for sent in doc.sents:
            for word in sent:
                if word.text.lower() in word_freq.keys():
                    if sent not in sentence_scores.keys():
                        sentence_scores[sent] = word_freq[word.text.lower()]
                    else:
                        sentence_scores[sent] += word_freq[word.text.lower()]
        return sentence_scores
    
    def summarize(self, text, num_sentences):
        doc = self.nlp(text)
        words = self.preprocess(text)
        word_freq = self.calculate_word_freq(words)
        sentence_scores = self.calculate_sentence_scores(doc, word_freq)
        summary_sentences = nlargest(num_sentences, sentence_scores, key=sentence_scores.get)
        summary = " ".join([sent.text.capitalize() for sent in summary_sentences])
        return summary