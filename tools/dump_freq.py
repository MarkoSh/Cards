"""Dump the most frequent nouns and verbs of en/ru/th into freq.json.

en/ru: wordfreq top list lemmatised and POS-tagged with spaCy small models.
th:    Thai National Corpus frequencies, POS-tagged with pythainlp.

Run:
  ~/.venv/bin/uv run --with wordfreq --with spacy \
    --with https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl \
    --with https://github.com/explosion/spacy-models/releases/download/ru_core_news_sm-3.8.0/ru_core_news_sm-3.8.0-py3-none-any.whl \
    --with pythainlp tools/dump_freq.py
"""
import json, os, re

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'freq.json')
TAKE = 1400  # margin over the 1000 needed, joining concepts costs some words

PROF = {  # keep the gallery clean
    'en': {'fuck', 'shit', 'bitch', 'ass', 'cock', 'pussy', 'dick', 'cunt', 'whore', 'slut', 'nigger', 'tits', 'boobs', 'porn', 'sex'},
    'ru': {'хуй', 'пизда', 'ебать', 'сука', 'блядь', 'шлюха', 'шалава', 'секс', 'порно', 'жопа'},
    'th': {'เย็ด', 'หี', 'ควย', 'หำ', 'นม', 'เงี่ยน'},
}

GOOD = {
    'en': re.compile(r"^[a-z][a-z'-]*[a-z]$"),
    'ru': re.compile(r"^[а-яё][а-яё-]*[а-яё]$"),
    'th': re.compile(r"^[\u0e01-\u0e3a\u0e40-\u0e5b]+$"),
}

def clean(lang, words, take=0):
    seen, out = set(), []
    for w in words:
        w = w.strip().lower().replace('ʼ', "'")
        if len(w) < 2 or w in seen or w in PROF[lang] or not GOOD[lang].match(w):
            continue
        seen.add(w)
        out.append(w)
        if take and len(out) >= take:
            break
    return out

def enru(lang):
    from wordfreq import top_n_list
    import spacy
    nlp = spacy.load(f'{lang}_core_{"web" if lang == "en" else "news"}_sm', disable=['parser', 'ner'])
    words = clean(lang, top_n_list(lang, 15000))
    nouns, verbs = [], []
    for doc in nlp.pipe(words, batch_size=200):
        for t in doc:
            tag = 'NOUN' if lang == 'en' else 'NOUN'
            if t.pos_ == tag and t.lemma_ and GOOD[lang].match(t.lemma_):
                nouns.append(t.lemma_)
            elif t.pos_ == 'VERB' and t.lemma_ and GOOD[lang].match(t.lemma_):
                verbs.append(t.lemma_)
    return {'n': clean(lang, nouns, TAKE), 'v': clean(lang, verbs, TAKE)}

def th():
    from pythainlp.corpus import tnc
    from pythainlp import pos_tag
    words = clean('th', [w for w, _ in sorted(tnc.word_freqs(), key=lambda x: -x[1])])[:10000]
    nouns, verbs = [], []
    for w, tags in zip(words, pos_tag(words)):
        if any(t.startswith('NC') for t in tags):      # NCMN common noun, NC…
            nouns.append(w)
        elif any(t.startswith('V') for t in tags):      # VACT/VATT/…
            verbs.append(w)
    return {'n': nouns[:TAKE], 'v': verbs[:TAKE]}

freq = {'en': enru('en'), 'ru': enru('ru'), 'th': th()}
for lang in freq:
    for pos in freq[lang]:
        assert len(freq[lang][pos]) >= 1000, (lang, pos, len(freq[lang][pos]))
json.dump(freq, open(OUT, 'w'), ensure_ascii=False, separators=(',', ':'))
for lang in freq:
    for pos in ('n', 'v'):
        print(lang, pos, len(freq[lang][pos]), freq[lang][pos][:12])
