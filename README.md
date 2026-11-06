# Cards

Галерея карточек: 1000 самых частых существительных и 1000 глаголов английского,
русского и тайского. Иконки OpenMoji (CC BY-SA 4.0), транскрипция, перевод по клику, частотность слова (ранг и шкала), кнопка «копировать».
Без озвучки: карточки для чтения. Карточки идут от частого к редкому слева направо, затем вниз; слова без ранга (их нет в частотном списке) стоят в конце в авторском порядке. Статический сайт: `index.html` + `app.js` + `data.js` + `icons/sprite.svg`.

## Сборка

```sh
# частотные списки -> tools/freq.json (wordfreq + spaCy en/ru, pythainlp TNC th)
~/.venv/bin/uv run --with wordfreq --with spacy \
  --with https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl \
  --with https://github.com/explosion/spacy-models/releases/download/ru_core_news_sm-3.8.0/ru_core_news_sm-3.8.0-py3-none-any.whl \
  --with pythainlp tools/dump_freq.py

# данные и иконки -> data.js + icons/sprite.svg (нужен tools/openmoji.json:
# curl -LO https://raw.githubusercontent.com/hfg-gmuend/openmoji/master/data/openmoji.json)
~/.venv/bin/uv run --with tltk --with 'numpy<2' --with 'pandas<2.3' --with requests --with nltk \
  --with python-crfsuite --with scikit-learn --with eng-to-ipa python -W ignore tools/build_data.py

# стили (app.css из src.css)
npm i && npm run css

# перед коммитом: offline.json + sw.js
python3 ../ThaiFast/tools/offline.py .
```

`tools/concepts.tsv` — авторская трёхъязычная таблица (en, th, n|v),
редактируется руками. Иконки подобраны в `tools/overrides.tsv` и словаре OVERRIDES
в `tools/build_data.py`. В каждой из шести колод по 1000 карточек: сначала идут концепты
по частотному рангу соответствующего языка, затем добивка в авторском порядке из таблицы.

## Иконки

`tools/icons.tsv` — ручная подборка (en, pos, флаг, hex OpenMoji). Флаги: `=` точная иконка,
`~` приблизительная (метафора, одна иконка не чаще 5 раз на колоду), `-` иконки нет: у абстрактных
слов (truth, way, portion…) карточка показывает первую букву слова в круге. Слова, которых в файле нет,
берут иконку по ключевым словам OpenMoji (`find_icon` в `tools/build_data.py`). После правки файла:
запустить `build_data.py` (см. выше).

Транскрипция тайского — RTGS через `tltk` (без тонов); `pythainlp royin` оставлял тайские знаки в латинском тексте.
