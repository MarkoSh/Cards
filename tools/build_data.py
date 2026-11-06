"""Build data.js + icons/sprite.js for Cards.

Reads tools/concepts.tsv (en<TAB>ru<TAB>th<TAB>n|v), tools/freq.json,
tools/openmoji.json. Adds en IPA (eng_to_ipa), th romanization (pythainlp royin),
per-language frequency ranks and an OpenMoji icon per concept. Black OpenMoji SVGs
are cached in tools/openmoji-svg and packed into one recolorable sprite.

Run: ~/.venv/bin/uv run --with tltk --with 'numpy<2' --with 'pandas<2.3' --with requests --with nltk \
  --with python-crfsuite --with scikit-learn --with eng-to-ipa python -W ignore tools/build_data.py
"""
import concurrent.futures, json, os, re, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SVG_CACHE = os.path.join(HERE, 'openmoji-svg')
OM_URL = 'https://raw.githubusercontent.com/hfg-gmuend/openmoji/master/black/svg/{}.svg'
FALLBACK = '1F4AC'  # speech balloon

# Hand-picked icons for frequent concepts where keyword matching is poor.
OVERRIDES = {
    'time': '23F0', 'water': '1F4A7', 'fire': '1F525', 'house': '1F3E0', 'home': '1F3E0',
    'car': '1F697', 'book': '1F4D6', 'money': '1F4B0', 'dog': '1F415', 'cat': '1F408',
    'food': '1F35E', 'bread': '1F35E', 'heart': '2764', 'sun': '2600', 'moon': '1F319',
    'star': '2B50', 'tree': '1F333', 'flower': '1F338', 'rain': '1F327', 'snow': '2744',
    'phone': '1F4F1', 'computer': '1F4BB', 'email': '1F4E7', 'mail': '1F4EC',
    'school': '1F3EB', 'work': '1F4BC', 'job': '1F4BC', 'business': '1F4BC',
    'hand': '270B', 'eye': '1F441', 'ear': '1F442', 'mouth': '1F444', 'foot': '1F9B6',
    'man': '1F468', 'woman': '1F469', 'boy': '1F466', 'girl': '1F467', 'baby': '1F476',
    'child': '1F9D2', 'kid': '1F9D2', 'people': '1F465', 'person': '1F9CD',
    'friend': '1F46B', 'family': '1F46A', 'father': '1F468-200D-1F467', 'mother': '1F469-200D-1F467',
    'world': '1F30D', 'earth': '1F30D', 'map': '1F5FA', 'country': '1F5FA',
    'city': '1F3D9', 'town': '1F3D8', 'village': '1F3D8', 'building': '1F3E2',
    'street': '1F6E4', 'road': '1F6E4', 'bridge': '1F309', 'car ': '1F697',
    'bus': '1F68C', 'train': '1F686', 'plane': '1F6EB', 'jet': '1F6EB', 'boat': '26F5',
    'ship': '1F6A2', 'bike': '1F6B2', 'taxi': '1F695', 'truck': '1F69A',
    'eat': '1F374', 'drink': '1F964', 'cook': '1F373', 'cooking': '1F373',
    'breakfast': '1F95E', 'lunch': '1F371', 'dinner': '1F35D', 'meal': '1F35D',
    'coffee': '2615', 'tea': '1F375', 'milk': '1F95B', 'juice': '1F9C3',
    'beer': '1F37A', 'wine': '1F377', 'water ': '1F4A7',
    'apple': '1F34E', 'orange': '1F34A', 'lemon': '1F34B', 'pear': '1F350',
    'fruit': '1F34E', 'vegetable': '1F966', 'potato': '1F954', 'tomato': '1F345',
    'onion': '1F9C5', 'rice': '1F35A', 'egg': '1F95A', 'meat': '1F969',
    'fish': '1F41F', 'chicken': '1F414', 'pig': '1F416', 'cow': '1F404',
    'horse': '1F40E', 'sheep': '1F411', 'goat': '1F410', 'duck': '1F986',
    'bird': '1F426', 'mouse': '1F401', 'rabbit': '1F407', 'snake': '1F40D',
    'tiger': '1F405', 'elephant': '1F418', 'monkey': '1F412', 'wolf': '1F43A',
    'insect': '1F41B', 'mosquito': '1F99F', 'animal': '1F43E',
    'shirt': '1F455', 'pants': '1F456', 'jeans': '1F456', 'dress': '1F457',
    'skirt': '1F457', 'shoe': '1F45E', 'hat': '1F3A9', 'cap': '1F9E2',
    'coat': '1F9E5', 'sock': '1F9E6', 'glove': '1F9E4', 'clothes': '1F455',
    'glasses': '1F453', 'watch': '231A', 'clock': '1F550', 'bag': '1F45C',
    'purse': '1F45B', 'wallet': '1F45B', 'luggage': '1F9F3', 'key': '1F511',
    'lock': '1F512', 'door': '1F6AA', 'window': '1F6AA', 'bed': '1F6CF',
    'chair': '1FA91', 'table': '1F4CB', 'lamp': '1F4A1', 'light': '1F4A1',
    'soap': '1F9FC', 'towel': '1F9FB', 'toilet': '1F6BD', 'shower': '1F6BF',
    'bath': '1F6C1', 'kitchen': '1F373', 'pot': '1F372', 'pan': '1F373',
    'cup': '2615', 'glass': '1F95B', 'bottle': '1F37E', 'plate': '1F37D',
    'dish': '1F37D', 'bowl': '1F963', 'spoon': '1F944', 'fork': '1F374',
    'knife': '1F52A', 'box': '1F4E6', 'package': '1F4E6', 'bag ': '1F45C',
    'pen': '1F58A', 'pencil': '270F', 'paper': '1F4C4', 'page': '1F4C4',
    'letter': '2709', 'document': '1F4C4', 'newspaper': '1F4F0', 'magazine': '1F4D5',
    'music': '1F3B5', 'song': '1F3B6', 'guitar': '1F3B8', 'piano': '1F3B9',
    'drum': '1F941', 'movie': '1F3AC', 'film': '1F39E', 'video': '1F3A5',
    'camera': '1F4F7', 'photo': '1F5BC', 'picture': '1F5BC', 'image': '1F5BC',
    'painting': '1F5BC', 'art': '1F3A8', 'theater': '1F3AD', 'drama': '1F3AD',
    'game': '1F3AE', 'sport': '26BD', 'football': '26BD', 'soccer': '26BD',
    'ball': '26BD', 'tennis': '1F3BE', 'golf': '26F3', 'swim': '1F3CA',
    'run': '1F3C3', 'walk': '1F6B6', 'jump': '1F998', 'dance': '1F483',
    'sing': '1F3A4', 'read': '1F4D6', 'write': '270D', 'draw': '270F',
    'paint': '1F3A8', 'study': '1F4DA', 'learn': '1F4DA', 'teach': '1F468-200D-1F3EB',
    'sleep': '1F634', 'dream': '1F4AD', 'wake': '23F0', 'rest': '1F6CC',
    'think': '1F914', 'idea': '1F4A1', 'thought': '1F4AD', 'mind': '1F9E0',
    'brain': '1F9E0', 'memory': '1F9E0', 'knowledge': '1F4DA', 'question': '2753',
    'answer': '1F4AC', 'talk': '1F4AC', 'speak': '1F5E3', 'say': '1F5E3',
    'tell': '1F5E3', 'voice': '1F5E3', 'sound': '1F50A', 'hear': '1F442',
    'listen': '1F3A7', 'see': '1F441', 'look': '1F440', 'watch': '1F440',
    'smell': '1F443', 'nose': '1F443', 'taste': '1F445', 'tongue': '1F445',
    'touch': '1F446', 'feel': '1F494', 'love': '2764', 'like': '1F44D',
    'hate': '1F44E', 'dislike': '1F44E', 'smile': '1F60A', 'laugh': '1F602',
    'cry': '1F62D', 'sad': '1F622', 'happy': '1F60A', 'fear': '1F628',
    'anger': '1F620', 'surprise': '1F632', 'worry': '1F61F', 'hope': '1F64F',
    'wish': '1F320', 'pray': '1F64F', 'prayer': '1F64F', 'god': '1F64F',
    'health': '1F49A', 'hospital': '1F3E5', 'doctor': '1F468-200D-2695-FE0F',
    'nurse': '1F469-200D-2695-FE0F', 'medicine': '1F48A', 'drug': '1F48A',
    'pill': '1F48A', 'pain': '1F915', 'disease': '1F9A0', 'virus': '1F9A0',
    'death': '1F480', 'die': '1F480', 'kill': '1F52A', 'blood': '1FA78',
    'war': '2694', 'fight': '1F94A', 'peace': '262E', 'weapon': '1F52B',
    'gun': '1F52B', 'police': '1F46E', 'cop': '1F46E', 'law': '2696',
    'court': '2696', 'judge': '2696', 'prison': '26D3', 'jail': '26D3',
    'money ': '1F4B0', 'bank': '1F3E6', 'cash': '1F4B5', 'dollar': '1F4B2',
    'coin': '1FA99', 'credit': '1F4B3', 'card': '1F4B3', 'price': '1F3F7',
    'cost': '1F4B2', 'pay': '1F4B5', 'buy': '1F6D2', 'shop': '1F6CD',
    'shopping': '1F6D2', 'store': '1F3EA', 'market': '1F3EA', 'sell': '1F3F7',
    'sale': '1F3F7', 'gift': '1F381', 'present': '1F381', 'party': '1F389',
    'holiday': '1F334', 'vacation': '1F334', 'travel': '2708', 'trip': '1F9F3',
    'tour': '1F9F3', 'tourist': '1F9F3', 'hotel': '1F3E8', 'beach': '1F3D6',
    'sea': '1F30A', 'ocean': '1F30A', 'wave': '1F30A', 'island': '1F3DD',
    'mountain': '26F0', 'hill': '26F0', 'valley': '1F3DE', 'forest': '1F332',
    'jungle': '1F334', 'park': '1F3DE', 'garden': '1F33F', 'plant': '1F331',
    'seed': '1F331', 'leaf': '1F343', 'wood': '1FAB5', 'log': '1FAB5',
    'stone': '1FAA8', 'rock': '1FAA8', 'sand': '1F3D6', 'desert': '1F3DC',
    'fire ': '1F525', 'flame': '1F525', 'heat': '1F525', 'ice': '1F9CA',
    'snow ': '2744', 'wind': '1F4A8', 'air': '1F4A8', 'cloud': '2601',
    'fog': '1F32B', 'storm': '26C8', 'lightning': '26A1', 'thunder': '26A1',
    'weather': '1F324', 'sky': '1F324', 'rainbow': '1F308', 'star ': '2B50',
    'night': '1F303', 'evening': '1F306', 'morning': '1F305', 'dawn': '1F305',
    'day': '1F31E', 'week': '1F4C5', 'month': '1F4C5', 'year': '1F4C5',
    'date': '1F4C5', 'calendar': '1F4C5', 'schedule': '1F4C5', 'hour': '231B',
    'minute': '23F1', 'second': '23F1', 'moment': '23F1', 'future': '1F52E',
    'past': '1F4DC', 'history': '1F4DC', 'beginning': '1F530', 'start': '25B6',
    'end': '1F51A', 'finish': '1F3C1', 'stop': '1F6D1', 'pause': '23F8',
    'play ': '25B6', 'go': '27A1', 'come': '2B05', 'enter': '1F6AA',
    'exit': '1F6AA', 'leave': '1F6AA', 'arrive': '1F6EC', 'depart': '1F6EB',
    'return': '21A9', 'turn': '21AA', 'move': '1F504', 'follow': '1F463',
    'lead': '1F9ED', 'guide': '1F9ED', 'direction': '1F9ED', 'north': '2B06',
    'south': '2B07', 'east': '27A1', 'west': '2B05', 'up': '2B06',
    'down': '2B07', 'left': '2B05', 'right': '27A1', 'top': '1F53D',
    'bottom': '1F53D', 'middle': '2194', 'center': '1F3AF', 'target': '1F3AF',
    'goal': '1F945', 'aim': '1F3AF', 'point': '1F449', 'line': '2796',
    'circle': '26AA', 'square': '2B1B', 'triangle': '1F53A', 'shape': '1F536',
    'color': '1F3A8', 'paint ': '1F3A8', 'red': '1F534', 'blue': '1F535',
    'green': '1F7E2', 'yellow': '1F7E1', 'black': '26AB', 'white': '26AA',
    'new': '1F195', 'old': '1F474', 'young': '1F9D2', 'big': '1F418',
    'small': '1F401', 'long': '1F4CF', 'short': '1F4CF', 'high': '2B06',
    'low': '2B07', 'size': '1F4CF', 'weight': '1F3CB', 'heavy': '1F3CB',
    'speed': '1F406', 'fast': '1F40C', 'slow': '1F40C', 'quick': '23F3',
}

with open(os.path.join(HERE, 'overrides.tsv'), encoding='utf8') as f:
    for line in f:
        word, hexcode = line.rstrip('\n').split('\t')
        OVERRIDES[word] = hexcode

def load_curated():
    """tools/icons.tsv: en, pos, flag (= exact, ~ approximate, - none), hex. Missing rows keep the keyword pick."""
    out = {}
    for line in open(os.path.join(HERE, 'icons.tsv'), encoding='utf8'):
        if line.startswith('#') or not line.strip():
            continue
        en, pos, flag, hexcode = line.rstrip('\n').split('\t')
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

def load_openmoji():
    data = json.load(open(os.path.join(HERE, 'openmoji.json')))
    entries = [e for e in data if not e.get('skintone')]
    index = {}  # keyword -> [hexcode]
    for e in entries:
        words = set(re.findall(r"[a-z']+", ' '.join([
            e['annotation'], e.get('tags', ''), e.get('openmoji_tags', '')]).lower()))
        for w in words:
            index.setdefault(w, []).append(e['hexcode'])
    return index

def find_icon(word, index):
    if word in OVERRIDES:
        return OVERRIDES[word]
    cands = [word]
    if word.endswith('e'):
        cands.append(word[:-1] + 'ing')
    else:
        cands += [word + 'ing', word + 's', word + 'ed']
    if word.endswith('y'):
        cands.append(word[:-1] + 'ies')
    for w in cands:
        if w in index:
            return index[w][0]
    for w in cands:  # substring match on longer keywords
        if len(w) < 4:
            continue
        for key in index:
            if w in key:
                return index[key][0]
    return FALLBACK

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
    concepts, ranks, index = load_concepts(), load_ranks(), load_openmoji()
    curated = load_curated()
    for c in concepts:
        ipa = eng_to_ipa.convert(c['e'])
        if ipa and '*' not in ipa:
            c['i'] = '/' + ipa + '/'
        c['x'] = ' '.join(th2roman(w).replace('<s/>', '').strip() for w in c['t'].split())
        g = curated[c['e'], c['p']] if (c['e'], c['p']) in curated else find_icon(c['e'], index)
        if g:
            c['g'] = g  # no icon: the card shows a letter badge
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
