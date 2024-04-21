# text_sum.py
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer as Summarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words

class TextSummarizer:
    def __init__(self):
        self.language = 'english'
        self.stemmer = Stemmer(self.language)
        self.summarizer = Summarizer(self.stemmer)
        self.summarizer.stop_words = get_stop_words(self.language)

    def summarize(self, text, num_sentences):
        parser = PlaintextParser.from_string(text, Tokenizer(self.language))
        summary = self.summarizer(parser.document, num_sentences)
        return ' '.join(str(sentence) for sentence in summary)