"""Build data.js + icons/sprite.js for Cards.

Reads tools/concepts.tsv (en<TAB>ru<TAB>th<TAB>n|v), tools/freq.json and tools/icons.tsv.
Adds en IPA (eng_to_ipa), th romanization (tltk, RTGS), per-language frequency ranks and
the icon of each concept. Black OpenMoji SVGs are cached in tools/openmoji-svg and packed
into one recolorable sprite (icons/sprite.js).

Run: ~/.venv/bin/uv run --with tltk --with 'numpy<2' --with 'pandas<2.3' --with requests --with nltk \
  --with python-crfsuite --with scikit-learn --with eng-to-ipa python -W ignore tools/build_data.py
"""
import json, os, re, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SVG_CACHE = os.path.join(HERE, 'openmoji-svg')
OM_URL = 'https://raw.githubusercontent.com/hfg-gmuend/openmoji/master/black/svg/{}.svg'

def load_icons():
    """tools/icons.tsv: en, pos, flag, hex, name. An empty hex means no pictogram: the card shows a letter."""
    out = {}
    for line in open(os.path.join(HERE, 'icons.tsv'), encoding='utf8'):
        if line.startswith('#') or not line.strip():
            continue
        en, pos, _flag, hexcode = line.rstrip('\n').split('\t')[:4]
        out[en, pos] = hexcode or None
    return out

def load_concepts():
    out = []
    for line in open(os.path.join(HERE, 'concepts.tsv'), encoding='utf8'):
        line = line.strip()
        if not line:
            continue
        en, ru, th, pos = line.split('\t')
        out.append({'e': en, 'r': ru, 't': th, 'p': pos})
    return out

def load_ranks():
    freq = json.load(open(os.path.join(HERE, 'freq.json')))
    ranks = {}
    for lang in freq:
        for pos in freq[lang]:
            ranks[lang, pos] = {w: i + 1 for i, w in enumerate(freq[lang][pos])}
    return ranks

def fetch_svg(hexcode):
    os.makedirs(SVG_CACHE, exist_ok=True)
    path = os.path.join(SVG_CACHE, hexcode + '.svg')
    if not os.path.exists(path):
        try:
            urllib.request.urlretrieve(OM_URL.format(hexcode), path)
        except Exception as ex:
            print('SVG FAIL', hexcode, ex)
            return None
    return path

def build_sprite(hexcodes):
    parts = []
    for hc in sorted(set(hexcodes)):
        path = fetch_svg(hc)
        if not path:
            continue
        svg = open(path, encoding='utf8').read()
        inner = re.sub(r'^.*?<svg[^>]*>|</svg>.*$', '', svg, flags=re.S).strip()
        inner = re.sub(r'fill="(?!none)[^"]*"', 'fill="currentColor"', inner)
        inner = re.sub(r'stroke="#[0-9a-fA-F]{3,6}"', 'stroke="currentColor"', inner)
        parts.append(f'<symbol id="i-{hc}" viewBox="0 0 72 72">{inner}</symbol>')
    os.makedirs(os.path.join(ROOT, 'icons'), exist_ok=True)
    # a script, not a fetched .svg: works when index.html is opened from file://
    svg = '<svg xmlns="http://www.w3.org/2000/svg">' + ''.join(parts) + '</svg>'
    with open(os.path.join(ROOT, 'icons', 'sprite.js'), 'w', encoding='utf8') as f:
        f.write('const SPRITE=' + json.dumps(svg) + ';\n')
    print('sprite:', len(parts), 'icons')

def main():
    import eng_to_ipa
    from tltk.nlp import th2roman  # royin (pythainlp) leaks Thai vowel marks into the Latin text
    concepts, ranks, icons = load_concepts(), load_ranks(), load_icons()
    for c in concepts:
        ipa = eng_to_ipa.convert(c['e'])
        if ipa and '*' not in ipa:
            c['i'] = '/' + ipa + '/'
        c['x'] = ' '.join(th2roman(w).replace('<s/>', '').strip() for w in c['t'].split())
        if icons[c['e'], c['p']]:
            c['g'] = icons[c['e'], c['p']]
        k = {}
        for lang, field in (('en', 'e'), ('ru', 'r'), ('th', 't')):
            w = c[field].lower()
            rank = ranks[lang, c['p']].get(w)
            if rank:
                k[lang] = rank
        if k:
            c['k'] = k
    build_sprite([c['g'] for c in concepts if 'g' in c])
    with open(os.path.join(ROOT, 'data.js'), 'w', encoding='utf8') as f:
        f.write('const CONCEPTS=' + json.dumps(concepts, ensure_ascii=False, separators=(',', ':')) + ';\n')
    print('concepts:', len(concepts))
    for lang in ('en', 'ru', 'th'):
        for pos in ('n', 'v'):
            n = sum(1 for c in concepts if c['p'] == pos and c.get('k', {}).get(lang, 9999) <= 1000)
            print(f'{lang}/{pos}: {n} in top-1000')

if __name__ == '__main__':
    main()
