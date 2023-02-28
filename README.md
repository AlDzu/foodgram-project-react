### Foodgram - «Продуктовый помощник»
---
Cервис, где пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.
---
# Сервис доступен по адресу:
```
http://51.250.102.149/
```
# Запуск и работа с проектом
Чтобы развернуть проект, вам потребуется:
1) Клонировать репозиторий GitHub (не забываем создать виртуальное окружение и установить зависимости):
```python
git clone https://github.com/AlDzu/foodgram-project-react
```
2) Создать файл ```.env``` в папке проекта _/infra/_ и заполнить его всеми ключами:
```
    DB_ENGINE=django.db.backends.postgresql  # указываем, что работаем с postgresql 
    DB_NAME=postgres  # имя базы данных 
    POSTGRES_USER=postgres  # логин для подключения к базе данных 
    POSTGRES_PASSWORD=postgres  # пароль для подключения к БД (установите свой)
    DB_HOST=db  # название сервиса (контейнера) 
    DB_PORT=5432  # порт для подключения к БД
    
    ALLOWED_HOSTS=localhost #Ваши хосты
    SECRET_KEY=KEY # ваш ключ
```
3) Собрать контейнеры:
```python
cd foodgram-project-react/infra
docker-compose up -d --build
```
4) Собрать файлы статики, и запустить миграции командами:
```
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py collectstatic --no-input 
```
5) Создать суперпользователя можно командой:
```
docker-compose exec web python manage.py createsuperuser
```
6) Остановить контейнер:
```
docker-compose down -v
```
Вход в админку:
Email: admin@admin.com
Pass: admin123!