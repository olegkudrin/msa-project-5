# Выбор и реализация решения для пакетной обработки данных

## Обоснование выбора технологического решения

Предлагается использовать Apache Airflow.

Это платформа для программного создания, планирования и мониторинга рабочих процессов.
Оптимальный выбор для задач пакетной обработки данных объемом порядка миллиона записей за запуск.
Предоставляет возможность гибкой настройки пайплайнов и интеграцию с различными системами.

Преимущества Airflow:

- Зрелость и популярность
- Масштабируемость
- Гибкость
- Встроенный мониторинг
- Надежность

Airflow предоставляет готовые официальные провайдеры для всех требуемых систем:

- BigQuery: создание таблиц, запись и чтение данных.
- Redshift: выполнение SQL, выгрузка и загрузка из/в S3.
- Kafka: чтение и запись из/в топиков.
- Spark: запуск приложений, выполнение SQL.

Airflow поддерживает в полной мере:

- Ветвление: динамический выбор пути выполнения на основе условий
- Условные операторы: прерывание выполнения downstream-задач при невыполнении условия
- Event-триггеры: sensors, dataset-aware scheduling, trigger rules.

Airflow реализовано из коробки:

- Fallback-logic (обработка ошибок)
- Retry (повторные попытки с гибкой настройкой)
- Email-уведомления (произвольные тексты)

Airflow имеет отличную поддержку облачных платформ:

- Google Cloud Platform (GCP)
- Amazon Web Services (AWS)
- Microsoft Azure
- Kubernetes (любое облако)
- Docker Compose (для разработки/тестирования)

## Пример простого проекта как POC

Используем docker composer.

- Файл конфигурации: [docker-compose.yaml](docker-compose.yaml)
- DAG: [dags/report_pipeline.py](dags/report_pipeline.py)
- Инициализация рабочей базы: [init-db.sql](init-db.sql)
- Файл с данными (CSV): [data/delivery.csv](data/delivery.csv)

Запуск проекта:
```shell
docker compose up -d
```
Вывод:
```
[+] Running 13/13
 ✔ Network work_default                    Created                                                                                   0.0s
 ✔ Volume "work_postgres-work-volume"      Created                                                                                   0.0s
 ✔ Volume "work_postgres-db-volume"        Created                                                                                   0.0s
 ✔ Container work-mailpit-1                Started                                                                                   0.2s
 ✔ Container work-redis-1                  Healthy                                                                                  21.5s
 ✔ Container work-postgres-work-1          Started                                                                                   0.2s
 ✔ Container work-postgres-1               Healthy                                                                                  21.5s
 ✔ Container work-airflow-init-1           Exited                                                                                   21.5s
 ✔ Container work-airflow-dag-processor-1  Started                                                                                  20.9s
 ✔ Container work-airflow-triggerer-1      Started                                                                                  20.9s
 ✔ Container work-airflow-scheduler-1      Started                                                                                  20.9s
 ✔ Container work-airflow-apiserver-1      Healthy                                                                                  31.4s
 ✔ Container work-airflow-worker-1         Started                                                                                  31.5s
```

Список сервисов:
```shell
docker compose ps
```
Вывод:
```
NAME                           IMAGE                    COMMAND                  SERVICE                 CREATED         STATUS                   PORTS
work-airflow-apiserver-1       apache/airflow:3.1.2     "/usr/bin/dumb-init …"   airflow-apiserver       4 minutes ago   Up 4 minutes (healthy)   0.0.0.0:8080->8080/tcp, [::]:8080->8080/tcp
work-airflow-dag-processor-1   apache/airflow:3.1.2     "/usr/bin/dumb-init …"   airflow-dag-processor   4 minutes ago   Up 4 minutes (healthy)   8080/tcp
work-airflow-scheduler-1       apache/airflow:3.1.2     "/usr/bin/dumb-init …"   airflow-scheduler       4 minutes ago   Up 4 minutes (healthy)   8080/tcp
work-airflow-triggerer-1       apache/airflow:3.1.2     "/usr/bin/dumb-init …"   airflow-triggerer       4 minutes ago   Up 4 minutes (healthy)   8080/tcp
work-airflow-worker-1          apache/airflow:3.1.2     "/usr/bin/dumb-init …"   airflow-worker          4 minutes ago   Up 3 minutes (healthy)   8080/tcp
work-mailpit-1                 axllent/mailpit:latest   "/mailpit"               mailpit                 4 minutes ago   Up 4 minutes (healthy)   0.0.0.0:1025->1025/tcp, [::]:1025->1025/tcp, 0.0.0.0:8025->8025/tcp, [::]:8025->8025/tcp, 1110/tcp
work-postgres-1                postgres:16              "docker-entrypoint.s…"   postgres                4 minutes ago   Up 4 minutes (healthy)   5432/tcp
work-postgres-work-1           postgres:16              "docker-entrypoint.s…"   postgres-work           4 minutes ago   Up 4 minutes (healthy)   5432/tcp
work-redis-1                   redis:7.2-bookworm       "docker-entrypoint.s…"   redis                   4 minutes ago   Up 4 minutes (healthy)   6379/tcp
```

Создание подключения к рабочей базе данных:
```shell
docker compose run --rm airflow-cli \
airflow connections add postgres-work \
--conn-type postgres \
--conn-host postgres-work \
--conn-login demo \
--conn-password secret \
--conn-schema demo \
--conn-port 5432
```
Вывод:
```
Successfully added `conn_id`=postgres-work : postgres://demo:******@postgres-work:5432/demo
```
Первые три запуска DAG (один автоматический + два вручную):

![Изображение Airflow UI](airflow-ui.png)

Графическое представление DAG:

![Изображение DAG](dag-graph.png)

Список DAG:
```shell
docker compose run --rm airflow-cli \
airflow dags list
```
Вывод:
```
dag_id          | fileloc                              | owners  | is_paused | bundle_name | bundle_version
================+======================================+=========+===========+=============+===============
report_pipeline | /opt/airflow/dags/report_pipeline.py | airflow | False     | dags-folder | None
```

Список запусков:
```shell
docker compose run --rm airflow-cli \
airflow dags list-runs report_pipeline
```
Вывод:
```
dag_id          | run_id                               | state   | run_after                 | logical_date              | start_date                       | end_date
================+======================================+=========+===========================+===========================+==================================+=================================
report_pipeline | manual__2025-11-11T14:21:28+00:00    | success | 2025-11-11T14:21:28+00:00 | 2025-11-11T14:21:28+00:00 | 2025-11-11T14:21:29.804598+00:00 | 2025-11-11T14:21:38.306129+00:00
report_pipeline | manual__2025-11-11T14:20:12+00:00    | success | 2025-11-11T14:20:12+00:00 | 2025-11-11T14:20:12+00:00 | 2025-11-11T14:20:19.744385+00:00 | 2025-11-11T14:20:29.373687+00:00
report_pipeline | scheduled__2025-11-11T06:00:00+00:00 | success | 2025-11-11T06:00:00+00:00 | 2025-11-11T06:00:00+00:00 | 2025-11-11T14:20:19.743436+00:00 | 2025-11-11T14:20:29.360609+00:00
```

Отчеты в рабочей базе данных:
```shell
docker compose exec postgres-work \
psql -U demo -c 'select * from report order by report_id'
```
Вывод:
```
 report_id | processing_type | delivered_amount |          created_at
-----------+-----------------+------------------+-------------------------------
         1 | high            |         22400.00 | 2025-11-11 14:20:27.272664+00
         2 | high            |         22400.00 | 2025-11-11 14:20:27.272795+00
         3 | high            |         22400.00 | 2025-11-11 14:21:36.226019+00
(3 rows)
```

Письма уведомлений в Mailpit UI (другой запуск системы):

![Изображение Mailpit UI](mailpit.png)
