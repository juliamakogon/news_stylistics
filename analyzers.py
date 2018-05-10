import pymorphy2
from tokenize_uk import tokenize_uk
import string

class Morphology():
    _morph = None
    def __init__(self, lang='uk'):
        Morphology.load(lang=lang)

    @staticmethod
    def load(path = None, lang='uk'):
        if (Morphology._morph == None):
            print('Morphology initialized for', lang)
            Morphology._morph = pymorphy2.MorphAnalyzer(lang=lang)

    def getAnalyzer(self):
        return Morphology._morph


class PosAnalyzer:
    @staticmethod
    def tokenize(text):
        pars = tokenize_uk.tokenize_text(text)
        tokens = []
        for par in pars:
            tokens = tokens + ['<P>']*3
            for sent in par:
                tokens = tokens + sent
            tokens = tokens + ['</P>']*3
        return tokens

    @staticmethod
    def analyze_POS(tokens):
        morphy = Morphology()
        UNDEF = 'UNDEF'
        data = []
        for t in tokens:
            d = t
            if d not in ['<P>', '</P>']:
                parsed = morphy.getAnalyzer().parse(t)
                if parsed:
                    p = parsed[0]
                    if p.tag.POS:
                        d = p.tag.POS
                    elif t[0].isdigit():
                        d = 'NUMBER'
                    elif t[0] in string.punctuation:
                        d = p.normal_form
                    else: 
                        d = UNDEF
                else:
                    d = UNDEF
            data.append(d)
        return data

    @staticmethod  
    def analyze(text):
        return PosAnalyzer.analyze_POS(PosAnalyzer.tokenize(text))
