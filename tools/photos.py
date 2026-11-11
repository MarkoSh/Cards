"""Photos for Cards from Pixabay (Pixabay Content License). Gentle by design: one search per word, cached for good,
about one request every 1.5 s, thumbnails are 150 px, and only the chosen photo is downloaded in full.

  photos.py scan            search every word of the decks (resumable), pick a default candidate, fetch its thumbnail
  photos.py review [N]      contact sheets of the default picks (40 words each) -> tools/photo-cache/review-NN.png
  photos.py alts word ...   sheet with all candidates of the given words (numbers 1-8)
  photos.py set word=N ...  choose candidate N for a word; N=0 means no photo
  photos.py fetch           download the chosen photos in full, crop to a square, grade, save photos/<pos>-<word>.webp
  photos.py index           write photos.js (key -> author, page, source) from sources.tsv and the files in photos/

Key: PIXABAY_KEY in tools/.keys (gitignored). Overrides of the search term: tools/pilot.tsv (pos, word, query).
Run: ~/.venv/bin/uv run --quiet --no-project --with pillow python tools/photos.py ...
"""
import io, json, os, re, sys, time, urllib.parse, urllib.request
from PIL import Image, ImageDraw, ImageEnhance, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PHOTOS = os.path.join(ROOT, 'photos')
CACHE = os.path.join(HERE, 'photo-cache')            # search results + thumbnails (gitignored)
SOURCES = os.path.join(HERE, 'sources.tsv')
PICKS = os.path.join(HERE, 'photo-picks.json')       # {"n-dog": 1, ...}
SIZE = 800                                           # px, square; the card shows it at most ~450 css px
PAUSE = 1.5                                          # seconds between requests to Pixabay
CELL, COLS, ROWS = 160, 8, 5

def key():
    for line in open(os.path.join(HERE, '.keys'), encoding='utf8'):
        if line.startswith('PIXABAY_KEY='):
            return line.split('=', 1)[1].strip()
    sys.exit('PIXABAY_KEY is missing in tools/.keys')

def slug(word):
    return re.sub(r'\W+', '-', word)

def words():
    """(pos, word) of every noun and verb that has an example sentence, i.e. every word of the decks."""
    data = open(os.path.join(ROOT, 'examples.js'), encoding='utf8').read()
    ex = json.loads(data[data.index('=') + 1:].rstrip().rstrip(';'))
    return [('n', k[2:]) if k.startswith('n:') else ('v', k) for k in ex if not k.startswith(('p:', 'c:'))]

def overrides():
    out = {}
    for line in open(os.path.join(HERE, 'pilot.tsv'), encoding='utf8'):
        if line.strip() and not line.startswith('#'):
            pos, word, query = line.rstrip('\n').split('\t')
            out[pos, word] = query
    return out

def get(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'cards-learning-site (non-commercial; contact via pixabay account)'})
    for attempt in range(4):
        try:
            return urllib.request.urlopen(req, timeout=40).read()
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(65)
            else:
                raise
    raise RuntimeError('rate limited')

def picks():
    return json.load(open(PICKS)) if os.path.exists(PICKS) else {}

def save_picks(p):
    json.dump(p, open(PICKS, 'w'), indent=0, sort_keys=True)

def cand_path(pos, word):
    return os.path.join(CACHE, 'c', f'{pos}-{slug(word)}.json')

def thumb_path(hit):
    return os.path.join(CACHE, 't', f'{hit["id"]}.jpg')

def search(pos, word, query):
    path = cand_path(pos, word)
    if os.path.exists(path):
        return json.load(open(path))
    url = 'https://pixabay.com/api/?' + urllib.parse.urlencode({
        'key': key(), 'q': query, 'image_type': 'photo', 'safesearch': 'true', 'per_page': 8,
        'min_width': 1000, 'min_height': 1000})
    hits = json.loads(get(url))['hits']
    keep = [{k: h.get(k) for k in ('id', 'pageURL', 'user', 'user_id', 'previewURL', 'tags', 'largeImageURL')} for h in hits]
    json.dump(keep, open(path, 'w'), ensure_ascii=False)
    time.sleep(PAUSE)
    return keep

def default_pick(word, hits):
    """First candidate whose tags contain the word itself; else the first one."""
    for i, h in enumerate(hits, 1):
        if word.lower() in [t.strip().lower() for t in h['tags'].split(',')]:
            return i
    return 1 if hits else 0

def thumb(hit):
    path = thumb_path(hit)
    if not os.path.exists(path):
        open(path, 'wb').write(get(hit['previewURL']))
        time.sleep(0.4)
    im = Image.open(path).convert('RGB')
    w, h = im.size
    s = min(w, h)
    return im.crop(((w - s) // 2, (h - s) // 2, (w + s) // 2, (h + s) // 2)).resize((CELL, CELL))

def scan():
    for d in ('c', 't'):
        os.makedirs(os.path.join(CACHE, d), exist_ok=True)
    over, p, todo = overrides(), picks(), words()
    for i, (pos, word) in enumerate(todo, 1):
        k = f'{pos}-{word}'
        if os.path.exists(os.path.join(PHOTOS, f'{pos}-{slug(word)}.webp')):
            continue
        hits = search(pos, word, over.get((pos, word), word))
        if k not in p:
            p[k] = default_pick(word, hits)
        if p[k]:
            thumb(hits[p[k] - 1])
        if i % 25 == 0:
            save_picks(p)
            print(i, len(todo), flush=True)
    save_picks(p)
    print('scan done', len(todo))

def label_font():
    try:
        return ImageFont.load_default(size=13)
    except TypeError:
        return ImageFont.load_default()

def review(start=1):
    p = picks()
    todo = [(k, n) for k, n in sorted(p.items(), key=lambda kv: kv[0]) if n and not os.path.exists(os.path.join(PHOTOS, slug(k) + '.webp'))]
    per = COLS * ROWS
    font = label_font()
    for s in range(start - 1, (len(todo) + per - 1) // per):
        chunk = todo[s * per:(s + 1) * per]
        im = Image.new('RGB', (COLS * (CELL + 4), ROWS * (CELL + 20)), 'black')
        d = ImageDraw.Draw(im)
        for i, (k, n) in enumerate(chunk):
            pos, word = k.split('-', 1)
            hit = search(pos, word, word)[n - 1]
            x, y = (i % COLS) * (CELL + 4), (i // COLS) * (CELL + 20)
            im.paste(thumb(hit), (x, y))
            d.text((x + 2, y + CELL + 2), f'{pos}:{word}'[:24], fill='yellow', font=font)
        path = os.path.join(CACHE, f'review-{s + 1:02d}.png')
        im.save(path)
        print(path)
        if start != 1:
            break

def alts(ws):
    font = label_font()
    rows = [(pos, w) for pos, w in words() if w in ws]
    im = Image.new('RGB', (8 * (CELL + 4) + 110, max(1, len(rows)) * (CELL + 4)), 'black')
    d = ImageDraw.Draw(im)
    for r, (pos, w) in enumerate(rows):
        d.text((2, r * (CELL + 4) + 2), f'{pos}:{w}', fill='yellow', font=font)
        for c, hit in enumerate(search(pos, w, overrides().get((pos, w), w))):
            x = 110 + c * (CELL + 4)
            im.paste(thumb(hit), (x, r * (CELL + 4)))
            d.rectangle((x, r * (CELL + 4), x + 16, r * (CELL + 4) + 16), fill='black')
            d.text((x + 4, r * (CELL + 4) + 1), str(c + 1), fill='white', font=font)
    path = os.path.join(CACHE, 'alts.png')
    im.save(path)
    print(path)

def grade(im):
    """One look for every photo: a touch of contrast and warmth, slightly lifted colour."""
    im = ImageEnhance.Contrast(im).enhance(1.06)
    im = ImageEnhance.Color(im).enhance(1.08)
    r, g, b = im.split()
    return Image.merge('RGB', (r.point(lambda v: min(255, int(v * 1.03))), g, b.point(lambda v: int(v * 0.97))))

def read_sources():
    rows = {}
    if os.path.exists(SOURCES):
        for line in open(SOURCES, encoding='utf8'):
            if line.strip():
                rows[line.split('\t')[0]] = line.rstrip('\n')
    return rows

def fetch():
    os.makedirs(PHOTOS, exist_ok=True)
    p, rows = picks(), read_sources()
    done = 0
    for k, n in sorted(p.items()):
        pos, word = k.split('-', 1)
        out = os.path.join(PHOTOS, f'{pos}-{slug(word)}.webp')
        if not n or os.path.exists(out):
            continue
        hit = search(pos, word, word)[n - 1]
        im = Image.open(io.BytesIO(get(hit['largeImageURL']))).convert('RGB')
        w, h = im.size
        s = min(w, h)
        im = im.crop(((w - s) // 2, (h - s) // 2, (w + s) // 2, (h + s) // 2)).resize((SIZE, SIZE), Image.LANCZOS)
        grade(im).save(out, 'WEBP', quality=80)
        rows[k] = '\t'.join([k, 'Pixabay', hit['user'], hit['pageURL'], 'Pixabay Content License'])
        open(SOURCES, 'w', encoding='utf8').write('\n'.join(rows[x] for x in sorted(rows)) + '\n')
        done += 1
        if done % 25 == 0:
            print('fetched', done, flush=True)
        time.sleep(PAUSE)
    print('fetch done', done)

def index():
    rows, out = read_sources(), {}
    for f in sorted(os.listdir(PHOTOS)):
        m = re.match(r'(\w)-(.*)\.webp$', f)
        if not m:
            continue
        pos, slugged = m.groups()
        src = next((r.split('\t') for k, r in rows.items() if k.split('-', 1)[0] == pos and slug(k.split('-', 1)[1]) == slugged), None)
        word = src[0].split('-', 1)[1] if src else slugged.replace('-', ' ')
        out[pos + word] = [src[2], src[3], src[1]] if src else ['', '', '']
    open(os.path.join(ROOT, 'photos.js'), 'w', encoding='utf8').write(
        '// key (n/v + English word) -> [author, photo page, source]; written by tools/photos.py index\nconst PHOTOS = '
        + json.dumps(out, ensure_ascii=False, separators=(',', ':')) + ';\n')
    print(len(out), 'photos')

if __name__ == '__main__':
    cmd, args = sys.argv[1], sys.argv[2:]
    os.makedirs(CACHE, exist_ok=True)
    if cmd == 'scan':
        scan()
    elif cmd == 'review':
        review(int(args[0]) if args else 1)
    elif cmd == 'alts':
        alts(set(args))
    elif cmd == 'set':
        p = picks()
        for a in args:
            w, n = a.rsplit('=', 1)
            pos = next(x for x, y in words() if y == w)
            p[f'{pos}-{w}'] = int(n)
        save_picks(p)
    elif cmd == 'fetch':
        fetch()
    elif cmd == 'index':
        index()
