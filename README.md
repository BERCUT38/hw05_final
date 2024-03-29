# Социальная сеть Yatube

## 1. [Описание](#1)
## 2. [Команды для запуска](#2)
## 3. [Техническая информация](#3)
## 4. [Об авторе](#4)

---
## 1. Описание <a id=1></a>

Проект cоциальной сети Yatube разработан по MVT архитектуре.  
Написаны тесты для проверки работы сервиса (pytest).

В проекте реализованы следующие возможности:
- регистрация, авторизация с верификацией
- публикация статей (текст, картинка)
- комментирование записей других пользователей
- подписка на авторов статей
- смена и восстановление пароля через почту
- пагинация
- кеширование страниц

---
## 2. Команды для запуска <a id=2></a>

Перед запуском необходимо склонировать проект:
```bash
HTTPS: git clone https://github.com/Bercut38/hw05_final.git
SSH: git clone git@github.com:Bercut38/hw05_final.git
```

Cоздать и активировать виртуальное окружение:
```bash
python -m venv venv
```
```bash
Linux: source venv/bin/activate
Windows: source venv/Scripts/activate
```

И установить зависимости из файла requirements.txt:
```bash
python3 -m pip install --upgrade pip
```
```bash
pip install -r requirements.txt
```

Выполнить миграции:
```bash
python3 manage.py migrate
```

Запустить проект:
```bash
python3 manage.py runserver
```

Теперь доступность проекта можно проверить по адресу [http://localhost/admin/](http://localhost/admin/)

---
## 3. Техническая информация <a id=3></a>

Стек технологий: Python 3, Django, pytest.

---
## 4. Об авторе <a id=4></a>

Будник Сергей Александрович  
Python-разработчик (Backend)  
Россия, г. Краснодар  
E-mail: bercut38877@yandex.ru  
Telegram: @Bercut38
