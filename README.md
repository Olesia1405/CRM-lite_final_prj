# CRM-lite

Система автоматизации для малого бизнеса, ИП и самозанятых

## 📌 О проекте

CRM-lite - это инструмент для автоматизации рутинных задач предпринимателей, позволяющий сосредоточиться на важных аспектах бизнеса.

## 🌟 Возможности

- Регистрация и авторизация по JWT
- Управление компанией (создание, редактирование)
- Управление складами компании
- Разделение прав доступа (владелец/сотрудник)

## 🛠 Технологии

- Python 3.10+
- Django 4.2
- Django REST Framework
- SQLite
- JWT аутентификация

## 🚀 Установка

1. Клонировать репозиторий:
```bash
git clone https://github.com/yourusername/crmlite.git
cd crmlite
```

2. Установить зависимости:
```bash
pip install -r requirements.txt
```

3. Настройка базы данных:
```bash
python manage.py migrate
```

4. Создать суперпользователя:
```bash
python manage.py createsuperuser
```

5. Запустить сервер:
```bash
python manage.py runserver
```

## Документация API

После запуска сервера документация доступна по адресам:

- Swagger UI: http://127.0.0.1:8000/swagger/

- ReDoc: http://127.0.0.1:8000/redoc/

## Модели данных

### Пользователь(User)
- username, email, password
- is_company_owner (флаг владельца компании)
- company (связь с компанией)

### Компания(Company)
- INN (ИНН)
- title (название)
- description (описание)

### Склад(Storage)
- address (адрес)
- company (связь с компанией)

## Права доступа:
- Создавать компании могут только авторизованные пользователи
- Редактировать/удалять компанию может только владелец
- Просматривать данные компании могут все сотрудники
