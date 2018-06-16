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
    def tokenize(text, ngram_delta = 3):
        pars = tokenize_uk.tokenize_text(text)
        tokens = []
        for par in pars:
            tokens = tokens + ['<P>']*ngram_delta
            for sent in par:
                tokens = tokens + sent
            tokens = tokens + ['</P>']*ngram_delta
        return tokens

    @staticmethod
    def analyze_token(t, morph):
        UNDEF = 'UNDEF'
        d = t
        if d not in ['<P>', '</P>']:
            parsed = morph.parse(t)
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
        return d     

    @staticmethod
    def analyze_POS(tokens):
        morph = Morphology().getAnalyzer()
        data = []
        for t in tokens:
            data.append(PosAnalyzer.analyze_token(t, morph))
        return data

    @staticmethod  
    def analyze(text):
        return PosAnalyzer.analyze_POS(PosAnalyzer.tokenize(text))

class PosFreqWordsAnalyzer:
    def __init__(self, morph, freq_words = None, lemmatize_freq = False, 
        lemma_exceptions = {'за':1, 'до':14, 'про':7, 'мені':4, 'бути':4, 'того':8, 'собі':1, 'кому':1, 'доки':4, 'піти':1, 'мати':7, 
             'тому':4, 'була':2, 'зараз':1, 'чому':1, 'голові':2, 'серед':1, 'році':1, 'при':1, 'три':1, 'справ':1, 'боку':2,
             'їм':1, 'стала':2, 'може':1, 'щоб':1  }):
        self.morph = morph
        self.lemma_exceptions = lemma_exceptions
        self.lemmatize_freq = lemmatize_freq
        self.freq_words = set()
        if not freq_words is None:
            for w in freq_words:
                self.freq_words.add(self.get_lemma(w))


    def parse(self, word):
        p = self.morph.parse(word) # hack pymorphy2: if voct has 0 index, try index 1
        k = self.lemma_exceptions.get(word.lower(), 0)
        if k == 0:
            try:
                if 'voct' in p[0].tag or p[0].tag.POS is None:
                    k = 1 if len(p) > 1 else 0
            except:
                k = 0
        return p[k]

    def get_lemma(self, word):
        if self.lemmatize_freq:
            return self.parse(word).normal_form  
        else:
             return word.lower()       


    def analyze_tokens(self, tokens):
        data = []
        for t in tokens:
            d = PosAnalyzer.analyze_token(t, self.morph)
            if self.freq_words is not None:
                tform = self.get_lemma(t)
                if tform in self.freq_words:
                    d = tform
            data.append(d)
        return data

    def analyze(self, text):
        return self.analyze_tokens(PosAnalyzer.tokenize(text))        


class PosLexAnalyzer:
    # only for bigrams
    def __init__(self, pwf_analyzer, lexngrams, ngramsize = 2):
        self.pwf_analyzer = pwf_analyzer
        self.process_lexngrams(lexngrams)
        
    def process_lexngrams(self, lexngrams):
        self.lexngrams = {}
        for ng in lexngrams:
            ar = self.lexngrams.get(ng[0].lower(), set())
            ar.add(ng[1].lower())
            self.lexngrams[ng[0]] = ar
                

    def parse(self, word):
        return self.pwf_analyzer.parse(word)

    def get_lemma(self, word):
        return self.pwf_analyzer.get_lemma(word)

    def analyze_tokens(self, tokens):
        data = []
        i = 0
        while i < len(tokens):
            t = tokens[i]
            d = PosAnalyzer.analyze_token(t, self.pwf_analyzer.morph)
            tform = self.get_lemma(t)
            if tform in self.lexngrams:
                if i + 1 < len(tokens):
                    tt = self.get_lemma(tokens[i + 1])
                    if tt in self.lexngrams[tform]:
                        data.append(d if tform[0] in string.punctuation else tform)
                        data.append(tt)
                        i += 2
                        continue
            if self.pwf_analyzer.freq_words is not None:
                if tform in self.pwf_analyzer.freq_words:
                    d = tform
            data.append(d)
            i += 1
        return data

    def analyze(self, text):
        return self.analyze_tokens(PosAnalyzer.tokenize(text)) 