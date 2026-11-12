"""Put a content hash into the asset URLs of index.html (app.js?v=abc123 ...), run before tools/offline.py.
Why: sw.js serves assets cache-first, so a changed app.js under the same URL would never reach a returning visitor
(index.html is network-first, so a new ?v= makes the browser ask for the new file)."""
import hashlib, os, re
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
path = os.path.join(root, 'index.html')
html = open(path, encoding='utf8').read()
def stamp(m):
    f = m.group(2)
    h = hashlib.sha1(open(os.path.join(root, f), 'rb').read()).hexdigest()[:8]
    return f'{m.group(1)}{f}?v={h}"'
html = re.sub(r'((?:src|href)=")((?:app|data|examples|photos)\.(?:js|css))(?:\?v=\w+)?"', stamp, html)
open(path, 'w', encoding='utf8').write(html)
