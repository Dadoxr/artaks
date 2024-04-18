# Описание проекта

Этот проект представляет собой систему для работы с контактами. В нем реализованы следующие функции:

- Получение информации о контактах по (API)[opendata.digital.gov.ru]
- Отображение формы для поиска контактов
- Обновление контактов из CSV-файлов
- Вспомогательные функции для работы с контактами

## Установка

1. Склонируйте репозиторий на свой компьютер:

```
git clone https://github.com/Dadoxr/artaks
cd artaks
```
2. Создайте .env
```
mv var/.env.sample var/.env
``` 


3. Запустите приложение

```
docker compose up -d
```

4. Создайте суперюзера

```
docker compose exec -it web python3 manage.py createsuperuser
```

5. Запустите тесты
```
docker compose exec -it web python3 manage.py test
```

6. Наполните базу контактами
```
docker compose exec -it web python3 manage.py renew
```

Далее система сама раз в сутки будет обновлять базу контактов (celery-beat)

## Endpoints
- hostname/ - форма поиска оператора по померу
- hostname/api {'number': ...} - API для получения оператора по номеру
