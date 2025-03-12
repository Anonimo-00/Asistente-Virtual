import json
import os.path
import re

from langcodes import closest_match
from ovos_plugin_manager.templates.solvers import QuestionSolver
from quebra_frases import word_tokenize


class YesNoSolver(QuestionSolver):
    """not meant to be used within persona framework
    this solver only indicates if the user answered "yes" or "no"
    to a yes/no prompt"""
    enable_tx = False
    priority = 100

    def __init__(self, config=None):
        config = config or {}
        self.resources = {}
        super().__init__(config)

    @staticmethod
    def normalize(text: str, lang: str):
        # Remove single characters surrounded by spaces
        text = re.sub(r'\s+[a-zA-Z]\s+', ' ', text)
        # Replace multiple spaces with a single space
        text = re.sub(r'\s+', ' ', text).strip()
        # Convert to lowercase
        text = text.lower()

        # Handle language-specific normalization
        if lang.startswith("en"):
            text = text.replace("don't", "do not")

        stopwords = ["the"]
        if lang.startswith("pt"):
            stopwords = ["esta", "está", "estás", "é", "de", "com", "são"]
        words = [w for w in word_tokenize(text) if w not in stopwords]
        return " ".join(words)

    def match_yes_or_no(self, text: str, lang: str):
        _langs = os.listdir(f"{os.path.dirname(__file__)}/res")
        lang2, lang_distance = closest_match(lang, _langs)
        if lang_distance > 10:  # unsupported lang, use translation and hope for the best
            text = self.translate(text, target_lang="en", source_lang=lang)
            return self.match_yes_or_no(text, "en")

        lang = lang2

        if lang not in self.resources:
            resource_file = f"{os.path.dirname(__file__)}/res/{lang}/yesno.json"
            with open(resource_file) as f:
                words = json.load(f)
                self.resources[lang] = {k: [_.lower() for _ in v] for k, v in words.items()}

        text = self.normalize(text, lang)

        # if user says yes but later says no, he changed his mind mid-sentence
        # the highest index is the last yesno word
        res = None
        best = -1

        # Compile regex patterns
        yes_pattern = re.compile(r'\b(?:' + '|'.join(self.resources[lang]["yes"]) + r')\b')
        no_pattern = re.compile(r'\b(?:' + '|'.join(self.resources[lang]["no"]) + r')\b')
        neutral_yes_pattern = re.compile(r'\b(?:' + '|'.join(self.resources[lang].get("neutral_yes", [])) + r')\b')
        neutral_no_pattern = re.compile(r'\b(?:' + '|'.join(self.resources[lang].get("neutral_no", [])) + r')\b')

        # Match yes words
        for match in yes_pattern.finditer(text):
            idx = match.start()
            if idx >= best:
                best = idx
                res = True

        # Match no words
        for match in no_pattern.finditer(text):
            idx = match.start()
            if idx >= best:
                best = idx

                # Handle double negatives (e.g., "not a lie")
                double_negatives = [
                    f"{match.group()} {neutral}"
                    for neutral in self.resources[lang].get("neutral_no", [])
                ]
                for pattern in double_negatives:
                    if re.search(re.escape(pattern), text):
                        res = True
                        break
                else:
                    res = False

        # Match neutral no (if no "yes" detected before)
        if res is None:
            for match in neutral_no_pattern.finditer(text):
                idx = match.start()
                if idx >= best:
                    best = idx
                    res = False

        # Match neutral yes (if no "no" detected before)
        if res is None:
            for match in neutral_yes_pattern.finditer(text):
                idx = match.start()
                if idx >= best:
                    best = idx
                    res = True

        # None - neutral
        # True - yes
        # False - no
        return res

    # abstract Solver methods
    def get_data(self, query, context=None):
        return {"answer": self.get_spoken_answer(query, context)}

    def get_spoken_answer(self, query, context=None):
        context = context or {}
        lang = context.get("lang", "en-us")
        res = self.match_yes_or_no(query, lang)
        if res is None:
            return None
        return "yes" if res else "no"


if __name__ == "__main__":
    cfg = {}
    bot = YesNoSolver(config=cfg)
    print(bot.get_spoken_answer("disagree"))
