# Проект "Foodgram-project-react"
Доступный домен: http://super-foodgram.sytes.net

## Описание проекта:

Проект Foodgram даёт возможность пользователям публиковать рецепты, подписываться на интересных авторов, добавлять рецепты в избранное и список покупок.

## Технологии:

При реализации бекэнда проекта были использованы следующие основные технологии, фреймворки и библиотеки:

Python 3.9
Django 4.2
Django Rest FrameWork 3.14

## Как запустить проект:

### Клонируйте репозиторий и перейдите в него в командной строке:

git clone https://github.com/LiubovPerchuk/foodgram-project-react
cd foodgram-project-react
### Cоздайте и активируйте виртуальное окружение:

python3 -m venv venv
source venv/bin/activate
python3 -m pip install --upgrade pip
### Установите зависимости из файла requirements.txt:

pip install -r requirements.txt
### Выполните миграции:

python3 manage.py migrate
### Запустите проект:

python3 manage.py runserver

## Документация, примеры запросов и ответов:

Обратившись к эндпоинту /redoc/, вы можете ознакомиться с документацией сервиса, посмотреть доступные варианты запросов к серверу и его ответов.