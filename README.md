
## Описание проекта Foodgram
«Продуктовый помощник»: приложение, на котором пользователи публикуют рецепты, 
подписываться на публикации других авторов и добавлять рецепты в избранное. 
Сервис «Список покупок» позволит пользователю создавать список продуктов, 
которые нужно купить для приготовления выбранных блюд. 

## Запуск проекта в dev-режиме

- Клонируйте репозиторий с проектом на свой компьютер. В терминале из рабочей директории выполните команду:
```bash
git clone git@github.com:Evgenmater/foodgram-project-react.git
```

- Установить и активировать виртуальное окружение

```bash
source /venv/bin/activate
```

- Установить зависимости из файла requirements.txt

```bash
python -m pip install --upgrade pip
```
```bash
pip install -r requirements.txt
```
- Создать файл .env в папке проекта:
```.env
DB_ENGINE=django.db.backends.postgresql # указываем, что работаем с postgresql
DB_NAME=postgres # имя базы данных
POSTGRES_USER=postgres # логин для подключения к базе данных
POSTGRES_PASSWORD=postgres # пароль для подключения к БД (установите свой)
DB_HOST=db # название сервиса (контейнера)
DB_PORT=5432 # порт для подключения к БД
```

### Выполните миграции:
```bash
python manage.py migrate
```

- В папке с файлом manage.py выполнить команду:
```bash
python manage.py runserver
```

- Создание нового супер пользователя 
```bash
python manage.py createsuperuser
```

### Загрузите статику:
```bash
python manage.py collectstatic --no-input
```
### Заполните базу данных ингредиентами: 
```bash
python manage.py push_ingredients
```


## Запуск проекта через Docker

Установите Docker, используя инструкции с официального сайта:
- для [Windows и MacOS](https://www.docker.com/products/docker-desktop)
- для [Linux](https://docs.docker.com/engine/install/ubuntu/). Отдельно потребуется установть [Docker Compose](https://docs.docker.com/compose/install/)

Клонируйте репозиторий с проектом на свой компьютер.
В терминале из рабочей директории выполните команду:
```bash
git clone git@github.com:Evgenmater/foodgram-project-react.git
```

* Перейти в директорию проекта:

    ```
    cd foodgram-project-react
    ```

* Cобираем образы, замените "usernmae" на ваш логин на Docker Hub:

    ```
    cd frontend
    docker build -t username/foodgram_frontend .
    cd ../backend
    docker build -t username/foodgram_backend .
    cd ../nginx
    docker build -t username/foodgram_gateway .
    ```

* Загружаем образы на Docker Hub, замените "usernmae" на ваш логин на Docker Hub:

    ```
    docker push username/foodgram_frontend
    docker push username/foodgram_backend
    docker push username/foodgram_gateway
    ```

* В конфиге docker-compose.production.yml, замените "evgenmater" на ваш логин на Docker Hub:

    ```
    image: evgenmater/foodgram_backend
    ```

* Запустите Docker Compose с этой конфигурацией на своём компьютере/сервере, далее команды, чтобы собрать статику:

    ```
    docker compose -f docker-compose.production.yml up
    docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
    docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /backend_static/static/
    ```

* Для запуска Docker Compose в режиме демона команду docker compose up нужно запустить с флагом -d:

    ```
    sudo docker compose -f docker-compose.production.yml up -d
    ```

- В результате должны быть собрано три контейнера, при введении следующей команды получаем список запущенных контейнеров:  
```bash
sudo docker compose -f docker-compose.production.yml ps
```
Назначение контейнеров(frontend котейнер у нас нужен для сбора статики, далее он прекращает свою работу):  

|          IMAGES                  | NAMES                |        DESCRIPTIONS         |
|:--------------------------------:|:---------------------|:---------------------------:|
| evgenmater/foodgram_gateway      | foodgram-gateway-1   |   контейнер HTTP-сервера    |
|       postgres:13.11             | foodgram-db-1        |    контейнер базы данных    |
| evgenmater/foodgram_backend      | foodgram-backend-1   | контейнер приложения Django |


* Распаковка ингредиентов:

    ```
    docker compose -f docker-compose.production.yml exec backend python manage.py push_ingredients
    ```

### Выполните миграции:
```bash
docker compose -f docker-compose.production.yml exec backend python manage.py migrate
```
### Создайте суперпользователя:
```bash
docker compose -f docker-compose.production.yml exec backend python manage.py createsuperuser
```

### Загрузите статику:
```bash
docker-compose exec backend python manage.py collectstatic --no-input
```

### Заполните базу ингредиентами:
```bash
docker compose -f docker-compose.production.yml exec backend python manage.py push_ingredients
```


### Основные адреса: 

| Адреса проекта:

| https://foodgram.myftp.biz/recipes 
| https://foodgram.myftp.biz/admin/ 
| https://foodgram.myftp.biz/recipes/api/ 

### Автор:  
_Хлебнев Евгений_<br>
**email**: _hlebnev@yandex.ru_<br>
**telegram** _@Evgen0991_ 
