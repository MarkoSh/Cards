"""One photo from Wikimedia Commons into Cards: commons.py <pos-word key, e.g. n-god> "File:Title.jpg"
Square crop + the same grade as Pixabay photos; credit (author, page, licence) goes to tools/sources.tsv."""
import io, json, re, sys, urllib.parse, urllib.request
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
import photos as P
from PIL import Image
UA = {'User-Agent': 'cards-learning-site (non-commercial)'}
key, title = sys.argv[1:3]
q = urllib.parse.urlencode({'action': 'query', 'format': 'json', 'titles': title, 'prop': 'imageinfo',
                            'iiprop': 'url|extmetadata', 'iiurlwidth': 1000})
info = list(json.load(urllib.request.urlopen(urllib.request.Request('https://commons.wikimedia.org/w/api.php?' + q, headers=UA)))['query']['pages'].values())[0]['imageinfo'][0]
m = info['extmetadata']
author = re.sub(r'<[^>]+>', '', m.get('Artist', {}).get('value', 'unknown')).strip()
lic = m['LicenseShortName']['value']
im = Image.open(io.BytesIO(urllib.request.urlopen(urllib.request.Request(info['thumburl'], headers=UA)).read())).convert('RGB')
w, h = im.size; s = min(w, h)
im = im.crop(((w - s) // 2, (h - s) // 2, (w + s) // 2, (h + s) // 2)).resize((P.SIZE, P.SIZE), Image.LANCZOS)
pos, word = key.split('-', 1)
P.grade(im).save(f'{P.PHOTOS}/{pos}-{P.slug(word)}.webp', 'WEBP', quality=80)
rows = P.read_sources()
rows[key] = '\t'.join([key, 'Wikimedia Commons', author, info['descriptionurl'], lic])
open(P.SOURCES, 'w', encoding='utf8').write('\n'.join(rows[x] for x in sorted(rows)) + '\n')
print(author, lic)
