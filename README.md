# atlas-seo

Статический генератор SEO-страниц для **atlaspos.ru** — на каждую нишу отдельный лендинг с точным title/description/canonical.

**Разработка:** Bokov777

## Структура

```
atlas-seo/
├── generate.py       # рендер страниц из pages.json по template.html
├── pages.json        # контент: site + список страниц
├── template.html     # HTML-шаблон с {{плейсхолдерами}}
└── public/
    ├── images/       # исходные изображения (coffee.jpg, shop.jpg)
    ├── style.css     # общий CSS
    └── generated/    # результат сборки (по папке на slug)
```

## Запуск

```bash
python3 generate.py --clean
```

Результат: `public/generated/<slug>/index.html`.

## Добавить страницу

1. Скопируй объект в `pages.json → pages`, поменяй `slug`, `title`, `description`, `keywords`, `hero`, `features`.
2. Положи картинку в `public/images/`.
3. Запусти генератор.
