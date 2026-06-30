# Проектирование и реализация выбранных решений для мониторинга, оповещения и логирования

## Проектные решения

- [Архитектурная диаграмма](architecture-mon-log.png)
- [Выбор метрик и алертов](metrics-selection.md)
- [Выбор инструментов и дашбоард](tools-selection.md)

## Доработанное приложение

- [Docker-compose файл](../complete/docker-compose.yml)
- [Java-проект приложения](../complete/)

Изменения относительно задания 4:

- Программа превращена в демона, который висит постоянно.
- Отключен автозапуска batch job и последующее завершение программы.
- Добавлен REST контроллер, который ждет команды на запуск batch job.
- В docker compose добавлен restart как положено для демона.
- Добавлены зависимости для REST API и метрик.
- Метрики доступны через REST для prometheus.
- Настроено логирование для logback.
- Добавлена очистка таблиц (для повторных запусков).

## Мониторинг (Prometheus + Grafana)

- Spring Boot Actuator экспортирует метрики
- Prometheus собирает метрики
- Grafana настроен дашборд
- Настроены алерты в Grafana

## Логирование (ELK Stack)

- Logback с JSON форматом логов
- Filebeat собирает логи из Docker контейнеров
- Logstash обрабатывает и передает в Elasticsearch
- Kibana для просмотра логов

## Доступ к компонентам

- Приложение API: http://localhost:8080
- Grafana:        http://localhost:3000 (admin/admin)
- Prometheus:     http://localhost:9090
- Kibana:         http://localhost:5601
- Elasticsearch:  http://localhost:9200

## Запуск Batch Job через REST API

```shell
curl -X POST http://localhost:8080/api/batch/run
```
Ответ при успешном запуске:
```
{
  "message": "Batch job started successfully",
  "status": "success",
  "timestamp": "1763524722519"
}
```

## Проверка метрик

Метрики приложения
```shell
curl http://localhost:8080/actuator/prometheus
```
Health check
```shell
curl http://localhost:8080/actuator/health
```
Метрики в Prometheus
```shell
curl http://localhost:9090/api/v1/query?query=process_cpu_usage
```
Spring Batch метрики
```shell
curl http://localhost:9090/api/v1/query?query=spring_batch_job_seconds_sum
```
