"""Photos for Cards from Pixabay (free licence, no attribution needed; we still keep sources.tsv).

  photos.py search [word ...]   candidates of the pilot words (all of tools/pilot.tsv if none) -> contact sheets
  photos.py pick word=N ...     download candidate N (1-6) of a word, crop to a square, grade, save photos/<pos>-<word>.webp
  photos.py index               write photos.js from the files in photos/

Key: PIXABAY_KEY in tools/.keys (gitignored). Pixabay allows 100 requests a minute; files are downloaded, never hot-linked.
Run: ~/.venv/bin/uv run --quiet --no-project --with pillow python tools/photos.py ...
"""
import io, json, os, re, sys, time, urllib.parse, urllib.request
from PIL import Image, ImageDraw, ImageEnhance

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PHOTOS = os.path.join(ROOT, 'photos')
CACHE = os.path.join(HERE, 'photo-cache')          # candidates + thumbnails (gitignored)
SOURCES = os.path.join(HERE, 'sources.tsv')
SIZE = 800                                         # px, square; the card shows it at most ~450 css px
PER_SHEET, CANDIDATES, THUMB = 6, 6, 210

def key():
    for line in open(os.path.join(HERE, '.keys'), encoding='utf8'):
        if line.startswith('PIXABAY_KEY='):
            return line.split('=', 1)[1].strip()
    sys.exit('PIXABAY_KEY is missing in tools/.keys')

def pilot():
    out = []
    for line in open(os.path.join(HERE, 'pilot.tsv'), encoding='utf8'):
        if line.strip() and not line.startswith('#'):
            pos, word, query = line.rstrip('\n').split('\t')
            out.append((pos, word, query))
    return out

def get(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'cards-photo-picker'})
    return urllib.request.urlopen(req, timeout=30).read()

def slug(word):
    return re.sub(r'\W+', '-', word)

def candidates(pos, word, query):
    path = os.path.join(CACHE, f'{pos}-{slug(word)}.json')
    if not os.path.exists(path):
        url = 'https://pixabay.com/api/?' + urllib.parse.urlencode({
            'key': key(), 'q': query, 'image_type': 'photo', 'safesearch': 'true', 'order': 'popular',
            'per_page': 12, 'min_width': 1000, 'min_height': 1000})
        hits = json.loads(get(url))['hits']
        keep = [{k: h[k] for k in ('id', 'pageURL', 'user', 'webformatURL', 'largeImageURL', 'tags')} for h in hits[:CANDIDATES]]
        json.dump(keep, open(path, 'w'), ensure_ascii=False)
        time.sleep(0.7)
    return json.load(open(path))

def thumb(hit):
    path = os.path.join(CACHE, f'{hit["id"]}.jpg')
    if not os.path.exists(path):
        open(path, 'wb').write(get(hit['webformatURL']))
        time.sleep(0.2)
    im = Image.open(path).convert('RGB')
    w, h = im.size
    s = min(w, h)
    return im.crop(((w - s) // 2, (h - s) // 2, (w + s) // 2, (h + s) // 2)).resize((THUMB, THUMB))

def sheet(rows, n):
    im = Image.new('RGB', (CANDIDATES * (THUMB + 6) + 90, len(rows) * (THUMB + 6)), 'black')
    d = ImageDraw.Draw(im)
    for r, (pos, word, query) in enumerate(rows):
        d.text((4, r * (THUMB + 6) + 4), f'{word}', fill='yellow')
        for c, hit in enumerate(candidates(pos, word, query)):
            x = 90 + c * (THUMB + 6)
            im.paste(thumb(hit), (x, r * (THUMB + 6)))
            d.rectangle((x, r * (THUMB + 6), x + 18, r * (THUMB + 6) + 16), fill='black')
            d.text((x + 4, r * (THUMB + 6) + 2), str(c + 1), fill='white')
    path = os.path.join(CACHE, f'sheet-{n:02d}.png')
    im.save(path)
    print(path)

def grade(im):
    """One look for every photo: a touch of contrast and warmth, slightly lifted colour."""
    im = ImageEnhance.Contrast(im).enhance(1.06)
    im = ImageEnhance.Color(im).enhance(1.08)
    r, g, b = im.split()
    r = r.point(lambda v: min(255, int(v * 1.03)))
    b = b.point(lambda v: int(v * 0.97))
    return Image.merge('RGB', (r, g, b))

def pick(word, n):
    pos, _, query = next(x for x in pilot() if x[1] == word)
    hit = candidates(pos, word, query)[n - 1]
    im = Image.open(io.BytesIO(get(hit['largeImageURL']))).convert('RGB')
    w, h = im.size
    s = min(w, h)
    im = im.crop(((w - s) // 2, (h - s) // 2, (w + s) // 2, (h + s) // 2)).resize((SIZE, SIZE), Image.LANCZOS)
    os.makedirs(PHOTOS, exist_ok=True)
    grade(im).save(os.path.join(PHOTOS, f'{pos}-{slug(word)}.webp'), 'WEBP', quality=80)
    rows = {}
    if os.path.exists(SOURCES):
        for line in open(SOURCES, encoding='utf8'):
            rows[line.split('\t')[0]] = line.rstrip('\n')
    rows[f'{pos}-{word}'] = '\t'.join([f'{pos}-{word}', 'Pixabay', hit['user'], hit['pageURL'], 'Pixabay Content License'])
    open(SOURCES, 'w', encoding='utf8').write('\n'.join(rows[k] for k in sorted(rows)) + '\n')
    print('ok', word, hit['pageURL'])
    time.sleep(0.3)

def index():
    keys = sorted(re.match(r'(\w)-(.*)\.webp$', f).expand(r'\1\2').replace('-', ' ') for f in os.listdir(PHOTOS) if f.endswith('.webp'))
    open(os.path.join(ROOT, 'photos.js'), 'w', encoding='utf8').write(
        '// Keys (n/v/p + English word) that have photos/<p>-<word>.webp; written by tools/photos.py index\nconst PHOTOS = new Set(' + json.dumps(keys, ensure_ascii=False) + ');\n')
    print(len(keys), 'photos')

if __name__ == '__main__':
    cmd, args = sys.argv[1], sys.argv[2:]
    os.makedirs(CACHE, exist_ok=True)
    if cmd == 'search':
        rows = [x for x in pilot() if not args or x[1] in args]
        for i in range(0, len(rows), PER_SHEET):
            sheet(rows[i:i + PER_SHEET], i // PER_SHEET + 1)
    elif cmd == 'pick':
        for a in args:
            w, n = a.rsplit('=', 1)
            pick(w, int(n))
    elif cmd == 'index':
        index()
