# Выбор инструментов

## Мониторинг: Prometheus + Grafana

- Prometheus собирает метрики
- Grafana визуализирует метрики
- Алерты настраиваются в Grafana

## Логирование: ELK Stack

- Logback  - структурированные логи в JSON формате
- Filebeat - сбор логов из Docker контейнеров
- Logstash - обработка и передача в Elasticsearch
- Kibana   - просмотр и анализ логов

## Дашборд Grafana

Создан дашборд с 7 панелями:

- Batch Job Duration         - среднее время выполнения job'ов (timeseries)
- Batch Job Executions Rate  - частота запуска job'ов (timeseries)
- Batch Step Duration        - время выполнения step'ов (timeseries)
- Item Processing Throughput - скорость обработки записей: read/process/write (timeseries)
- JVM Heap Memory            - использование памяти (stat)
- DB Connection Pool         - активные/idle соединения (stat)
- GC Pause Rate              - частота GC (stat)
