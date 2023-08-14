# Проект "Foodgram-project-react"

Домен доступен по адресу: https://super-foodgram.sytes.net/

Админ доступен по адресу: https://super-foodgram.sytes.net/admin/

e-mail: admin@admin.ru

password: 1

## Описание проекта:

Проект Foodgram даёт возможность пользователям публиковать рецепты, подписываться на интересных авторов, добавлять рецепты в избранное и список покупок, а перед походом в магазин скачивать список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

## Технологии:

При реализации бекэнда проекта были использованы следующие основные технологии, фреймворки и библиотеки:

Python 3.9
Django 3.2
Django Rest FrameWork 3.14
PostgreSQL 13.10
Gunicorn 20.1.0

## Как запустить проект:

### Клонируйте репозиторий и перейдите в него в командной строке:

git clone https://github.com/LiubovPerchuk/foodgram-project-react

cd foodgram-project-react

### Cоздайте и активируйте виртуальное окружение:

python3 -m venv venv
source venv/bin/activate
python3 -m pip install --upgrade pip

### Установите зависимости из файла requirements.txt:

pip install -r ./backend/foodgram_backend/requirements.txt

### Выполните миграции:

python3 manage.py migrate

### Запустите проект:

python3 manage.py runserver

## Документация, примеры запросов и ответов:

Обратившись к эндпоинту /redoc/, вы можете ознакомиться с документацией сервиса, посмотреть доступные варианты запросов к серверу и его ответов.