# Реализация ETL с использованием Spring Batch

## Описание решения

Реализовано ETL-приложение на базе Spring Batch для пакетной обработки данных о складских остатках компании TradeWare.

[ADR с обоснованием решения](ADR-spring-batch.md)

[C4-диаграмма архитектуры](architecture.png)

[Docker-compose файл](../complete/docker-compose.yml)

[Java-проект приложения](../complete/)

## Запуск решения

Выполнить команды:

```shell
cd task-4/complete

./gradlew build

docker build -t batch-processing .

docker compose up -d
```

Последовательность действий:

1. Поднимается Postgres с инициализацией схемы (schema-all.sql)
2. Загружаются данные из loyality_data.csv в таблицу loyality_data
3. Запускается Spring Batch приложение
4. Приложение обрабатывает product-data.csv:
    - Читает данные по товарам
    - Обогащает данными из loyality_data
    - Сохраняет в таблицу products
5. Приложение завершается с логами результата

Просмотр лога приложения:

```shell
docker compose logs app
```

[Лог приложения](app.log)

В логе приложения видно успешное исполнение приложения.

В результате: данные были прочитаны, обогащены и загружены в базу.

## Проверка результата

Запрос к базе данных:

```shell
docker compose exec postgresdb psql -U postgres -d productsdb -c 'select * from products'
```

Требуемый результат (поле productdata обогащено):

```
 productid | productsku | productname | productamount | productdata
-----------+------------+-------------+---------------+-------------
         1 |      20001 | hammer      |            45 | Loyality_on
         2 |      30001 | sink        |            20 | Loyality_on
         3 |      40001 | roof_shell  |           256 | Loyality_on
         4 |      50001 | priming     |            67 | Loyality_on
         5 |      60001 | clapboard   |           120 | Loyality_on
(5 rows)
```

Метаданные Spring Batch:

```shell
docker compose exec postgresdb psql -U postgres -d productsdb -x -c 'select * from batch_job_execution'
```

Видно успешное выполнение задания:

```
-[ RECORD 1 ]----+---------------------------
job_execution_id | 1
version          | 2
job_instance_id  | 1
create_time      | 2025-11-17 15:07:43.148027
start_time       | 2025-11-17 15:07:43.155209
end_time         | 2025-11-17 15:07:43.207372
status           | COMPLETED
exit_code        | COMPLETED
exit_message     |
last_updated     | 2025-11-17 15:07:43.208703
```
