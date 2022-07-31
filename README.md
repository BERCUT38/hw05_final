1. Описание
Проект cоциальной сети Yatube разработан по MVT архитектуре.
Написаны тесты для проверки работы сервиса (pytest).

В проекте реализованы следующие возможности:

регистрация, авторизация с верификацией
публикация статей (текст, картинка)
комментирование записей других пользователей
подписка на авторов статей
смена и восстановление пароля через почту
пагинация
кеширование страниц
2. Команды для запуска
Перед запуском необходимо склонировать проект:

HTTPS: git clone https://github.com/BERCUT38/hw05_final.git
SSH: git clone git@github.com:BERCUT38/hw05_final.git
Cоздать и активировать виртуальное окружение:

python -m venv venv
Linux: source venv/bin/activate
Windows: source venv/Scripts/activate
И установить зависимости из файла requirements.txt:

python3 -m pip install --upgrade pip
pip install -r requirements.txt
Выполнить миграции:

python3 manage.py migrate
Запустить проект:

python3 manage.py runserver
Теперь доступность проекта можно проверить по адресу http://localhost/admin/

3. Техническая информация
Стек технологий: Python 3, Django, pytest.

4. Об авторе
Будник Сергей Александрович
Python-разработчик (Backend)
Россия, г. Краснодар
E-mail: bercut38877@yandex.ru.ru
Telegram: @Bercut38