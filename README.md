# Cards

Галерея карточек для чтения: до 1000 самых частых существительных и до 1000 глаголов английского,
русского и тайского. На карточке иконка (OpenMoji, CC BY-SA 4.0), слово, транскрипция, перевод по клику,
шкала частотности слова, кнопки «копировать» и «Google Переводчик». У каждого глагола ещё кнопка «пример»:
короткая фраза с этим глаголом (на языке колоды, с транскрипцией для тайского и переводом). Без озвучки.

Колода идёт от частого к редкому: слева направо, затем вниз. Слова, которых нет в частотном списке,
стоят в конце в авторском порядке. Синонимы с одним переводом сливаются в одну карточку, поэтому
в части колод меньше тысячи.

Статический сайт, без сборки на сервере: `index.html`, `app.js`, `app.css`, `data.js`, `icons/sprite.js`.
Открывается и по `file://`, офлайн-кэш общий с семейством *Fast (`sw.js`).

## Файлы

```
index.html          разметка, шапка, подвал
app.js              состояние, колода, карточки, события (комментарии в начале разделов)
src.css → app.css   стили: Tailwind 4 (npm run css), компоненты .seg, .corner, .card
data.js             CONCEPTS: слова, транскрипция, частотные ранги, иконка (собирается)
examples.js         EXAMPLES: фраза-пример каждого глагола на en, ru, th + транскрипция th (собирается)
icons/sprite.js     SPRITE: символы OpenMoji одним файлом (собирается)
tools/
  concepts.tsv      авторская трёхъязычная таблица: en, ru, th, n|v; правится руками
  icons.tsv         иконка каждого понятия: en, pos, флаг, hex OpenMoji, имя; правится руками
  examples.txt      фразы-примеры: глагол|English|Русский|ไทย, глагол в [скобках]; правится руками
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
- **Пример глагола** — строка в `tools/examples.txt`: `глагол|English|Русский|ไทย`. Во всех трёх фразах глагол в `[ ]`,
  фразы переводят друг друга, тайские слова разделены пробелами (это видно на карточке). Сборка предупредит,
  если в тайской фразе нет слова глагола из `concepts.tsv`.
