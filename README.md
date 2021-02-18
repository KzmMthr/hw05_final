**Сообщество в Yatube** — социальная сеть рецензий и обсуждений фильмов, книг и музыки. 


## Index
1. [Описание](#описание)
2. [Пользовательские роли](#пользовательские-роли)
3. [Установка](#установка)
4. [Технологии](#технологии)


## Описание

**API для сервиса YaMDb. Позволяет работать со следующими сущностями:**
Сообщества для публикаций мнений. Дайте возможность опубликовать пост не только у себя в ленте, но и выбрать группу, в которой появится этот пост. Сообщества создаются администрацией сайта, посетители не смогут их добавлять. При публикации записи автор может выбрать одно сообщество и отправить туда свой пост.

  - Title - уникальное название сообщества.
  - Адрес (slug) — уникальный адрес группы, часть URL.
  - Description — текст, который появится на странице сообщества.

   
### Пользовательские роли

- **Аноним** — может просматривать сообщества, читать отзывы и комментарии.
- **Аутентифицированный пользователь** — может, как и Аноним, читать всё, дополнительно он может 
публиковать отзывы и комментарии в обсуждениях 
- **Модератор** — те же права, что и у Аутентифицированного пользователя плюс право удалять любые отзывы и комментарии.
- **Администратор** — полные права на управление проектом и всем его содержимым. 
Может создавать и удалять категории и произведения. Может назначать роли пользователям.
- **Администратор Django** — те же права, что и у роли Администратор.


## Установка
```
python manage.py runserver
```


## Технологии
- [Python](https://www.python.org/)
- [Django](https://www.djangoproject.com/)
