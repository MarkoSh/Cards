"""Digits ('d') and the Thai alphabet ('l') for Cards: authored here, appended to data.js by build_data.py
(or alone, without the slow rebuild: python tools/add_sections.py).
d: n = the number as written; e/r/t = the word in English/Russian/Thai; x = Thai romanization.
l: l = the consonant; e/r/t = its textbook word (ก ไก่); x = the letter's name (ko kai). Only shown for the Thai deck."""

DIGITS = [  # n, en, ru, th, roman
    ('0', 'zero', 'ноль', 'ศูนย์', 'sun'), ('1', 'one', 'один', 'หนึ่ง', 'nueng'), ('2', 'two', 'два', 'สอง', 'song'),
    ('3', 'three', 'три', 'สาม', 'sam'), ('4', 'four', 'четыре', 'สี่', 'si'), ('5', 'five', 'пять', 'ห้า', 'ha'),
    ('6', 'six', 'шесть', 'หก', 'hok'), ('7', 'seven', 'семь', 'เจ็ด', 'chet'), ('8', 'eight', 'восемь', 'แปด', 'paet'),
    ('9', 'nine', 'девять', 'เก้า', 'kao'), ('10', 'ten', 'десять', 'สิบ', 'sip'), ('20', 'twenty', 'двадцать', 'ยี่สิบ', 'yi sip'),
    ('100', 'hundred', 'сто', 'ร้อย', 'roi'), ('1000', 'thousand', 'тысяча', 'พัน', 'phan'),
    ('10000', 'ten thousand', 'десять тысяч', 'หมื่น', 'muen'), ('100000', 'hundred thousand', 'сто тысяч', 'แสน', 'saen'),
    ('1000000', 'million', 'миллион', 'ล้าน', 'lan'),
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

def records(ipa=lambda w: ''):
    out = [{'e': e, 'r': r, 't': t, 'p': 'd', 'n': n, 'x': x, **({'i': ipa(e)} if ipa(e) else {})} for n, e, r, t, x in DIGITS]
    out += [{'e': e, 'r': r, 't': t, 'p': 'l', 'l': l, 'x': x} for l, t, e, r, x in LETTERS]
    return out
