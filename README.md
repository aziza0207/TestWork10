### Запуск приложения (FastAPI) через Docker Compose
* Клонируйте репозиторий и перейдите в его корневую директорию.
* Создайте файл .env в корневой директории со следующим содержимым
  
.env

```shell

SECRET_KEY=197b2c37c391bed93fe80344fe73b806947a65e36206e05a1a23c2fa12702fe3
ALGORITHM=HS256
```

*  Соберите и запустите контейнеры:
```shell
 docker compose up --build
```

* для запуска тестов в контейнере
```shell
 docker compose run --rm web sh -c "pytest"
```


### После разворота

Swagger - http://127.0.0.1:8000/docs
