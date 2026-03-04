# Markdown Support для Postов и Комментариев

Добавлена поддержка Markdown для всех постов и комментариев на платформе Mathforces!

## Что было добавлено

### 1. **Зависимости** (`requirements.txt`)
- `markdown==3.5.2` - парсер markdown
- `bleach==6.1.0` - очистка HTML от опасного контента

### 2. **Django Template Filter** (`archive/templatetags/markdown_filter.py`)
Создан custom template filter для преобразования markdown в безопасный HTML:
```django
{{ post.content|markdown|safe }}
{{ comment.text|markdown|safe }}
```

Поддерживаемые markdown элементы:
- **Форматирование**: bold, italic, code inline
- **Заголовки**: h1-h6
- **Списки**: упорядоченные и неупорядоченные
- **Код**: блоки кода с подсветкой синтаксиса
- **Таблицы**: markdown таблицы
- **Цитаты**: blockquotes
- **Ссылки и изображения**

### 3. **Обновленные Шаблоны**

#### `create_post.html`
- Добавлена вкладка "Write" и "Preview"
- Live preview markdown контента
- Информация о markdown синтаксе
- Ссылка на полный гайд markdown

#### `edit_post.html`
- Аналогично create_post.html с preview功能

#### `post_detail.html`
- Добавлены CSS стили для markdown контента
- Поддержка списков, таблиц, кода, цитат

#### `comment_node.html`
- Использует markdown filter для отображения комментариев
- Сохраняет иерархию ответов

#### `community.html`
- Preview markdown контента в списке постов
- Обрезает длинный контент для превью

### 4. **Markdown Guide Page** (`markdown_guide.html`)
Новая страница с полной документацией по markdown синтаксису:
- Примеры форматирования
- Таблицы синтаксиса
- Live примеры
- Доступна по URL: `/community/markdown-guide/`

### 5. **CSS Стили**
Добавлены красивые стили для markdown контента:
- Оформление заголовков
- Подсветка кода
- Стильные таблицы
- Красивые цитаты
- Правильное отступление для списков

## Использование

### Форматирование текста
```markdown
**bold** — жирный текст
_italic_ — курсив
`code` — код в строке
```

### Заголовки
```markdown
# H1
## H2
### H3
```

### Списки
```markdown
- Item 1
- Item 2

1. First
2. Second
```

### Блоки кода
```markdown
```python
def hello():
    print("Hello, World!")
```
```

### Таблицы
```markdown
| Column 1 | Column 2 |
|----------|----------|
| Data 1   | Data 2   |
```

### Цитаты
```markdown
> Important quote
> Can span multiple lines
```

## Безопасность

Все HTML генерируется через `bleach` для очистки от опасного контента. Разрешены только безопасные теги:
- Форматирование: `p`, `strong`, `em`, `u`, `code`, `pre`
- Структура: `h1-h6`, `ul`, `ol`, `li`, `hr`, `br`
- Таблицы: `table`, `thead`, `tbody`, `tr`, `th`, `td`
- Ссылки: `a` (с href и title)
- Изображения: `img` (с src, alt, title)

Опасные теги автоматически удаляются!

## Файлы которые были изменены/созданы

### Созданы:
- `archive/templatetags/__init__.py`
- `archive/templatetags/markdown_filter.py`
- `archive/templates/archive/markdown_guide.html`

### Изменены шаблоны:
- `archive/templates/archive/create_post.html`
- `archive/templates/archive/edit_post.html`
- `archive/templates/archive/post_detail.html`
- `archive/templates/archive/comment_node.html`
- `archive/templates/archive/community.html`

### Изменены Python файлы:
- `archive/urls.py` - добавлен URL для гайда
- `archive/views.py` - добавлена функция `markdown_guide`
- `requirements.txt` - добавлены зависимости

## Установка

1. Установите зависимости:
```bash
pip install markdown bleach
```

2. Сервер автоматически подберет новые template filters через templatetags

## Примеры

### Пример поста:
```markdown
# Решение задачи про факториалы

Факториал можно вычислить несколькими способами:

## Рекурсивный способ

```python
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)
```

## Итеративный способ

- Более быстрый
- Нет риска переполнения стека
- Лучше для больших чисел

| Способ | Скорость | Память |
|--------|----------|--------|
| Рекурсия | Медленно | Много |
| Цикл | Быстро | Мало |

> Совет: используйте встроенную функцию math.factorial() для боевого кода!
```

## Заметки разработчика

- Template filter автоматически кешируется Django
- Live preview использует `marked.js` (客户端парсинг)
- Серверная часть использует Python `markdown` для безопасного парсинга
- Экономия памяти: контент хранится в исходном markdown формате, HTML генерируется при отображении
