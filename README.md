# Cards

Свой «инстаграм» для слов: до 1000 самых частых существительных и 1000 глаголов английского, русского и тайского.
Пост = фото (пока пиктограмма OpenMoji, CC BY-SA 4.0) и слово на языке колоды. Тап раскрывает перевод, транскрипцию
и пример фразы (у каждого слова). Сердце = «выучил»: красное 30 дней, потом серое («подзабыл»), тап возвращает красный.
Кнопки: озвучка (mp3 `audio/<язык>/<fnv1a слова>.mp3`, иначе голос браузера), Google Переводчик, «отправить»
(ссылка `#<base>-<колода>-<n|v>-<слово>` прокручивает к карточке и подсвечивает её), копировать. Двойной тап по фото ставит лайк.
Переключатель Все / Существительные / Глаголы (в «Все» части речи перемешаны, каждая по частоте).

Колода идёт от частого к редкому. Синонимы с одним переводом сливаются в одну карточку, поэтому в части колод меньше тысячи.

Статический сайт: `index.html`, `app.js`, `app.css`, `data.js`, `examples.js`, `photos.js`, `icons/sprite.js`.
Открывается и по `file://`, офлайн-кэш общий с семейством *Fast (`sw.js`). Лайки хранятся в localStorage браузера.

## Файлы

```
index.html          разметка, шапка, подвал
app.js              состояние, колода, карточки, события (комментарии в начале разделов)
src.css → app.css   стили: Tailwind 4 (npm run css), компоненты .seg, .corner, .card
data.js             CONCEPTS: слова, транскрипция, частотные ранги, иконка (собирается)
examples.js         EXAMPLES: фраза-пример каждого слова на en, ru, th + транскрипция th (собирается; ключ — слово, у существительных «n:слово»)
photos.js           PHOTOS: понятия, у которых есть фото (пока пусто)
icons/sprite.js     SPRITE: символы OpenMoji одним файлом (собирается)
tools/
  concepts.tsv      авторская трёхъязычная таблица: en, ru, th, n|v; правится руками
  icons.tsv         иконка каждого понятия: en, pos, флаг, hex OpenMoji, имя; правится руками
  examples.txt      фразы глаголов: глагол|English|Русский|ไทย, слово в [скобках]; правится руками
  examples_n.txt    то же для существительных (1159 слов из колод)
  dump_freq.py      частотные списки → freq.json
  build_data.py     concepts + icons + examples + freq → data.js, examples.js, sprite.js (~4 минуты: tltk медленный)
```

## Сборка

```sh
# частотные списки -> tools/freq.json (wordfreq + spaCy en/ru, pythainlp TNC th)
~/.venv/bin/uv run --with wordfreq --with spacy \
  --with https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl \
  --with https://github.com/explosion/spacy-models/releases/download/ru_core_news_sm-3.8.0/ru_core_news_sm-3.8.0-py3-none-any.whl \
  --with pythainlp tools/dump_freq.py

# data.js + examples.js + icons/sprite.js (транскрипция: IPA для английского, RTGS без тонов для тайского)
~/.venv/bin/uv run --with tltk --with 'numpy<2' --with 'pandas<2.3' --with requests --with nltk \
  --with python-crfsuite --with scikit-learn --with eng-to-ipa python -W ignore tools/build_data.py

# стили (app.css из src.css)
npm i && npm run css

# перед коммитом: offline.json + sw.js
python3 ../ThaiFast/tools/offline.py .
```

## Правки

- **Слово или перевод** — строка в `tools/concepts.tsv`, затем `build_data.py`.
- **Иконка** — строка в `tools/icons.tsv`. Флаг `=` подходит по смыслу, `~` приблизительная метафора,
  `-` иконки нет (карточка покажет первую букву слова в круге). Для абстрактных слов иконку лучше
  не придумывать. Новая иконка скачивается из OpenMoji при сборке.
- Порядок карточек определяют частотные ранги (`k` в `data.js`): у слов без ранга порядок как в таблице.
- **Пример** — строка в `tools/examples.txt` (глаголы) или `tools/examples_n.txt` (существительные): `слово|English|Русский|ไทย`. Во всех трёх фразах слово в `[ ]`,
  фразы переводят друг друга, тайские слова разделены пробелами (это видно на карточке). Сборка предупредит,
  если в тайской фразе нет тайского слова из `concepts.tsv`.
