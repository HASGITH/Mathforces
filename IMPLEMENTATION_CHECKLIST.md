# Чек-лист внедрения Markdown поддержки

## Завершено

### 1. Установка зависимостей
- [x] Добавлены пакеты `markdown` и `bleach` в requirements.txt
- [x] Пакеты успешно установлены

### 2. Backend разработка
- [x] Создана директория `archive/templatetags`
- [x] Создан файл `archive/templatetags/__init__.py`
- [x] Создан файл `archive/templatetags/markdown_filter.py` с:
  - Django template filter `|markdown`
  - Поддержка markdown extensions: tables, fenced_code, codehilite
  - Очистка HTML через bleach для безопасности
  - Whitelist разрешенных HTML тегов

### 3. Frontend - Шаблоны
- [x] Обновлен `create_post.html`:
  - Добавлены вкладки "Write" и "Preview"
  - Live preview usando marked.js
  - Информация о markdown синтаксисе
  - Ссылка на полный гайд

- [x] Обновлен `edit_post.html`:
  - Аналогично create_post.html
  - Сохранение функциональности редактирования

- [x] Обновлен `post_detail.html`:
  - Добавлен {% load markdown_filter %}
  - Применен фильтр к post.content
  - Добавлены CSS стили для markdown контента:
    - Заголовки с правильными размерами
    - Форматирование кода и цитат
    - Стили для таблиц и списков

- [x] Обновлен `comment_node.html`:
  - Добавлен {% load markdown_filter %}
  - Применен фильтр к comment.text
  - Наследует CSS стили от post_detail.html

- [x] Обновлен `community.html`:
  - Добавлен {% load markdown_filter %}
  - Preview markdown контента в списке постов
  - Обрезание длинного контента для превью

- [x] Создан `markdown_guide.html`:
  - Полная документация по markdown
  - Примеры всех форматирований
  - Live примеры с результатами
  - Таблицы синтаксиса

### 4. URL и Views
- [x] Добавлен URL маршрут для markdown guide:
  ```python
  path('community/markdown-guide/', views.markdown_guide, name='markdown_guide'),
  ```
- [x] Создана view функция `markdown_guide()` в views.py

### 5. CSS Стили
- [x] Добавлены стили для markdown элементов:
  - Заголовки: h1, h2, h3, h4, h5, h6
  - Параграфы с правильным line-height
  - Inline код с подсветкой
  - Блоки кода с темным фоном
  - Цитаты с левой границей
  - Списки упорядоченные и неупорядоченные
  - Таблицы с стилем

### 6. JavaScript
- [x] Добавлен marked.js для live preview
- [x] Функции переключения между "Write" и "Preview"
- [x] Функции обновления preview при вводе

### 7. Безопасность
- [x] Все HTML очищается через bleach
- [x] Whitelist разрешенных тегов:
  - Текст: p, br, strong, em, u, code, pre
  - Структура: h1-h6, ul, ol, li, hr
  - Таблицы: table, thead, tbody, tr, th, td
  - Ссылки: a (с href и title)
  - Изображения: img (с src, alt, title)
  - Прочее: blockquote, sup, sub

## Функциональность

### Поддерживаемый markdown синтаксис
- [x] **Жирный текст**: `**text**` → <strong>text</strong>
- [x] _Курсив_: `_text_` или `*text*` → <em>text</em>
- [x] Код: `` `code` `` → <code>code</code>
- [x] Блоки кода: ` ```code``` `
- [x] Заголовки: `# H1`, `## H2`, etc.
- [x] Списки: `- item` и `1. item`
- [x] Цитаты: `> quote`
- [x] Таблицы: markdown таблицы
- [x] Ссылки: `[text](url)`
- [x] Изображения: `![alt](url)`
- [x] Горизонтальная линия: `---`

## Документация

- [x] Создан файл `MARKDOWN_SUPPORT.md` с:
  - Описанием добавленных изменений
  - Инструкциями по использованию
  - Примерами markdown контента
  - Информацией о безопасности
  - Списком измененных файлов

## Тестирование

- [x] `python manage.py check` - прошла без ошибок
- [x] Markdown парсинг - работает корректно
- [x] Bleach очистка HTML - работает корректно
- [x] Template filter - работает корректно

## Использование

### Для пользователей:
1. При создании/редактировании поста видят информацию о markdown
2. Могут переключаться между "Write" и "Preview"
3. Могут открыть полный гайд markdown по кнопке
4. Посты и комментарии отображаются с красивым форматированием

### Для разработчиков:
1. В шаблонах используется `{{ content|markdown|safe }}`
2. Контент хранится в исходном markdown формате
3. HTML генерируется при каждом отображении (Django кеширует)

## Файлы которые были изменены

### Созданы:
- `archive/templatetags/__init__.py`
- `archive/templatetags/markdown_filter.py`
- `archive/templates/archive/markdown_guide.html`
- `MARKDOWN_SUPPORT.md`

### Изменены:
- `requirements.txt` - добавлены markdown, bleach
- `archive/urls.py` - добавлен URL для гайда
- `archive/views.py` - добавлена функция markdown_guide
- `archive/templates/archive/create_post.html` - preview, guide
- `archive/templates/archive/edit_post.html` - preview, guide
- `archive/templates/archive/post_detail.html` - markdown filter, CSS
- `archive/templates/archive/comment_node.html` - markdown filter
- `archive/templates/archive/community.html` - markdown filter, preview

## Результат

Посты и комментарии теперь:
- Поддерживают красивое markdown форматирование
- Имеют live preview при создании/редактировании
- Отображаются с профессиональным стилем
- Защищены от XSS атак через bleach
- Имеют полную документацию в гайде
