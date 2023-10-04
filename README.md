### Описание проекта FOODGRAM:

«Фудграм» — сайт, на котором пользователи могут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Пользователям сайта также доступен сервис «Список покупок». Он позволит скачать список продуктов, которые нужно купить для приготовления выбранных блюд.


### Как запустить проект:

* Клонировать репозиторий и перейти в него в командной строке:

    ```
    git@github.com:Evgenmater/foodgram-project-react.git
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

* Запустите Docker Compose с этой конфигурацией на своём компьютере, далее команды, чтобы собрать статику:

    ```
    docker compose -f docker-compose.production.yml up
    docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
    docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /backend_static/static/
    ```

* Распаковка ингредиентов:

    ```
    docker compose -f docker-compose.production.yml exec backend python manage.py unpack_ingredients
    ```

* Выполнить миграции:

    ```
    docker compose -f docker-compose.production.yml exec backend python manage.py migrate
    ```

* Создайте суперпользователя:

    ```
    docker compose -f docker-compose.production.yml exec backend python manage.py createsuperuser
    ```

### Примеры запросов к API.

* Получить список всех рецептов:

    ```
    https://foodgram.myftp.biz/recipes
    ```

* Админ-панель для суперпользователя:

    ```
   https://foodgram.myftp.biz/admin/
    ```

* Пример запрос к API:

    ```
    https://foodgram.myftp.biz/api/

    https://foodgram.myftp.biz/api/recipes/
    ```

### Автор:  
Хлебнев Евгений Юрьевич<br>
**email**: hlebnev@yandex.ru<br>
**telegram** @Evgen0991