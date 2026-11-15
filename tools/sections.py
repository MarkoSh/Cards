"""Digits ('d') and the Thai alphabet ('l') for Cards: authored here, appended to data.js by build_data.py
(or alone, without the slow rebuild: python tools/add_sections.py).
d: n = the number as written; e/r/t = the word in English/Russian/Thai; x = Thai romanization.
l: l = the consonant; e/r/t = its textbook word (ก ไก่); x = the letter's name (ko kai). Only shown for the Thai deck."""

EN1 = 'zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen'.split()
EN10 = 'x x twenty thirty forty fifty sixty seventy eighty ninety'.split()
RU1 = 'ноль один два три четыре пять шесть семь восемь девять десять одиннадцать двенадцать тринадцать четырнадцать пятнадцать шестнадцать семнадцать восемнадцать девятнадцать'.split()
RU10 = 'x x двадцать тридцать сорок пятьдесят шестьдесят семьдесят восемьдесят девяносто'.split()
TH1 = 'ศูนย์ หนึ่ง สอง สาม สี่ ห้า หก เจ็ด แปด เก้า'.split()
RO1 = 'sun nueng song sam si ha hok chet paet kao'.split()

def number(n):
    """(en, ru, th, roman, note_ru, note_en) of 0..99. Thai: 10 is สิบ (no หนึ่ง), 20 is ยี่สิบ (not สองสิบ), a final 1 after tens is เอ็ด (not หนึ่ง)."""
    if n < 10:
        return EN1[n], RU1[n], TH1[n], RO1[n], '', ''
    t, u = divmod(n, 10)
    en = EN1[n] if n < 20 else EN10[t] + (f'-{EN1[u]}' if u else '')
    ru = RU1[n] if n < 20 else RU10[t] + (f' {RU1[u]}' if u else '')
    th, ro, notes = ('สิบ', 'sip') if t == 1 else (('ยี่สิบ', 'yi sip') if t == 2 else (TH1[t] + 'สิบ', RO1[t] + ' sip')), '', []
    th, ro = (th[0], th[1]) if isinstance(th, tuple) else (th, ro)
    if t == 1 and u == 0:
        notes.append(('десять — просто สิบ, без «один» (не หนึ่งสิบ)', 'ten is just สิบ, no "one" in front (not หนึ่งสิบ)'))
    if t == 2 and u == 0:
        notes.append(('двадцать — ยี่สิบ: вместо สอง стоит ยี่ (не สองสิบ)', 'twenty is ยี่สิบ: ยี่ instead of สอง (not สองสิบ)'))
    if u:
        th += 'เอ็ด' if u == 1 else TH1[u]; ro += ' et' if u == 1 else ' ' + RO1[u]
        if u == 1:
            notes.append(('в конце «один» читается เอ็ด, а не หนึ่ง', 'a final "one" is เอ็ด, not หนึ่ง'))
        if t == 2:
            notes.append(('двадцать — ยี่สิบ, не สองสิบ', 'twenty is ยี่สิบ, not สองสิบ'))
        if t == 1:
            notes.append(('десять — просто สิบ, без «один»', 'ten is just สิบ, no "one" in front'))
    return en, ru, th, ro, '. '.join(x[0] for x in notes), '. '.join(x[1] for x in notes)

BIG = [  # n, en, ru, th, roman, note_ru, note_en
    (100, 'one hundred', 'сто', 'หนึ่งร้อย', 'nueng roi', 'можно сказать и просто ร้อย; 101 — หนึ่งร้อยเอ็ด', 'plain ร้อย works too; 101 is หนึ่งร้อยเอ็ด'),
    (200, 'two hundred', 'двести', 'สองร้อย', 'song roi', 'здесь «два» — обычное สอง (ยี่ только перед สิบ)', 'here "two" is the plain สอง (ยี่ only comes before สิบ)'),
    (1000, 'one thousand', 'тысяча', 'หนึ่งพัน', 'nueng phan', 'можно просто พัน; 1001 — หนึ่งพันเอ็ด', 'plain พัน works too; 1001 is หนึ่งพันเอ็ด'),
    (2000, 'two thousand', 'две тысячи', 'สองพัน', 'song phan', 'สอง, не ยี่', 'สอง, not ยี่'),
    (10000, 'ten thousand', 'десять тысяч', 'หนึ่งหมื่น', 'nueng muen', 'отдельное слово หมื่น = 10 000', 'a word of its own: หมื่น = 10,000'),
    (100000, 'hundred thousand', 'сто тысяч', 'หนึ่งแสน', 'nueng saen', 'отдельное слово แสน = 100 000', 'a word of its own: แสน = 100,000'),
    (1000000, 'million', 'миллион', 'หนึ่งล้าน', 'nueng lan', 'ล้าน = 1 000 000', 'ล้าน = 1,000,000'),
]

LETTERS = [  # letter, Thai word, en, ru, letter name
    ('ก', 'ไก่', 'chicken', 'курица', 'ko kai'), ('ข', 'ไข่', 'egg', 'яйцо', 'kho khai'), ('ฃ', 'ขวด', 'bottle', 'бутылка', 'kho khuat'),
    ('ค', 'ควาย', 'buffalo', 'буйвол', 'kho khwai'), ('ฅ', 'คน', 'person', 'человек', 'kho khon'), ('ฆ', 'ระฆัง', 'bell', 'колокол', 'kho rakhang'),
    ('ง', 'งู', 'snake', 'змея', 'ngo ngu'), ('จ', 'จาน', 'plate', 'тарелка', 'cho chan'), ('ฉ', 'ฉิ่ง', 'cymbals', 'тарелки (цимбалы)', 'cho ching'),
    ('ช', 'ช้าง', 'elephant', 'слон', 'cho chang'), ('ซ', 'โซ่', 'chain', 'цепь', 'so so'), ('ฌ', 'เฌอ', 'tree', 'дерево', 'cho choe'),
    ('ญ', 'หญิง', 'woman', 'женщина', 'yo ying'), ('ฎ', 'ชฎา', 'headdress', 'головной убор', 'do chada'), ('ฏ', 'ปฏัก', 'goad', 'стрекало', 'to patak'),
    ('ฐ', 'ฐาน', 'base', 'основание', 'tho than'), ('ฑ', 'มณโฑ', 'Montho', 'Монто', 'tho montho'), ('ฒ', 'ผู้เฒ่า', 'elder', 'старец', 'tho phu thao'),
    ('ณ', 'เณร', 'novice monk', 'послушник', 'no nen'), ('ด', 'เด็ก', 'child', 'ребёнок', 'do dek'), ('ต', 'เต่า', 'turtle', 'черепаха', 'to tao'),
    ('ถ', 'ถุง', 'bag', 'мешок', 'tho thung'), ('ท', 'ทหาร', 'soldier', 'солдат', 'tho thahan'), ('ธ', 'ธง', 'flag', 'флаг', 'tho thong'),
    ('น', 'หนู', 'mouse', 'мышь', 'no nu'), ('บ', 'ใบไม้', 'leaf', 'лист', 'bo baimai'), ('ป', 'ปลา', 'fish', 'рыба', 'po pla'),
    ('ผ', 'ผึ้ง', 'bee', 'пчела', 'pho phueng'), ('ฝ', 'ฝา', 'lid', 'крышка', 'fo fa'), ('พ', 'พาน', 'tray', 'поднос', 'pho phan'),
    ('ฟ', 'ฟัน', 'tooth', 'зуб', 'fo fan'), ('ภ', 'สำเภา', 'junk ship', 'джонка', 'pho samphao'), ('ม', 'ม้า', 'horse', 'лошадь', 'mo ma'),
    ('ย', 'ยักษ์', 'giant', 'великан', 'yo yak'), ('ร', 'เรือ', 'boat', 'лодка', 'ro ruea'), ('ล', 'ลิง', 'monkey', 'обезьяна', 'lo ling'),
    ('ว', 'แหวน', 'ring', 'кольцо', 'wo waen'), ('ศ', 'ศาลา', 'pavilion', 'павильон', 'so sala'), ('ษ', 'ฤๅษี', 'hermit', 'отшельник', 'so ruesi'),
    ('ส', 'เสือ', 'tiger', 'тигр', 'so suea'), ('ห', 'หีบ', 'chest', 'сундук', 'ho hip'), ('ฬ', 'จุฬา', 'kite', 'воздушный змей', 'lo chula'),
    ('อ', 'อ่าง', 'basin', 'таз', 'o ang'), ('ฮ', 'นกฮูก', 'owl', 'сова', 'ho nokhuk'),
]

def rec(n, e, r, t, x, nr, ne, ipa):
    c = {'e': e, 'r': r, 't': t, 'p': 'd', 'n': str(n), 'x': x}
    if nr:
        c['o'] = {'ru': nr, 'en': ne}
    if ipa(e):
        c['i'] = ipa(e)
    return c

def records(ipa=lambda w: ''):
    out = []
    for n in range(100):
        e, r, t, x, nr, ne = number(n)
        out.append(rec(n, e, r, t, x, nr, ne, ipa))
    out += [rec(n, e, r, t, x, nr, ne, ipa) for n, e, r, t, x, nr, ne in BIG]
    out += [{'e': e, 'r': r, 't': t, 'p': 'l', 'l': l, 'x': x} for l, t, e, r, x in LETTERS]
    return out
