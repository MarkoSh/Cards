"""Put the digits and the alphabet into the existing data.js (no 4-minute rebuild): 
~/.venv/bin/uv run --quiet --no-project --with eng-to-ipa --with nltk python tools/add_sections.py"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import eng_to_ipa, sections
path = os.path.join(os.path.dirname(HERE), 'data.js')
text = open(path, encoding='utf8').read()
data = [c for c in json.loads(text[text.index('=') + 1:].rstrip().rstrip(';')) if c['p'] not in 'dl']
def ipa(w):
    s = eng_to_ipa.convert(w)
    return '/' + s + '/' if s and '*' not in s else ''
data += sections.records(ipa)
open(path, 'w', encoding='utf8').write('const CONCEPTS=' + json.dumps(data, ensure_ascii=False, separators=(',', ':')) + ';\n')
print('d+l:', sum(c['p'] in 'dl' for c in data), 'of', len(data))
