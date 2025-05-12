### Запуск приложения через docker-compose
* Сделайте clone репозитория. Перейдите в корневую директорию. Создайте два файла в корневой директории.
  
.env

```shell

SECRET_KEY=197b2c37c391bed93fe80344fe73b806947a65e36206e05a1a23c2fa12702fe3
ALGORITHM=HS256
```

* Затем наберите команду находясь там же
```shell
 docker compose up --build
```

* для запуска тестов в контейнере
```shell
 docker compose run --rm web sh -c "pytest"
```


### После разворота

Swagger - http://127.0.0.1:8000/docs
