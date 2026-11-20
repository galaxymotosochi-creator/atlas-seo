# atlas-seo

Статический генератор SEO-блога для **atlaspos.ru** — статьи по нишам с точными title/description, JSON-LD (Article + FAQ), sitemap и robots.

**Разработка:** Bokov777

## Структура

```
atlas-seo/
├── generate.py       # сборка dist/ из pages.json
├── pages.json        # массив статей (slug, title, description, h1, sections, faq, related)
├── template.html     # шаблон статьи (JSON-LD, OG, FAQ, related)
├── index.html        # шаблон хаба со списком статей
└── public/
    ├── images/       # coffee.jpg, shop.jpg
    └── style.css
```

## Сборка

```bash
python3 generate.py        # → dist/
```

Результат:

```
dist/
├── index.html
├── style.css
├── sitemap.xml
├── robots.txt
├── images/
└── blog/
    ├── uchet-v-kofeyne/index.html
    └── inventarizaciya-magazina/index.html
```

`dist/` — готовый к деплою статический сайт (корень домена atlaspos.ru).

## Добавить статью

1. Скопируй объект в `pages.json`.
2. Поменяй `slug`, `title`, `description`, `h1`, `category`, `sections`, `faq`, `related`.
3. Положи изображение в `public/images/` и укажи `/images/<file>.jpg`.
4. `python3 generate.py`.
