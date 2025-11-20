# Выбор метрик и алертов

Концентрируем внимание на основной задаче - пакетной обработке.
Для комплекта собираем базовые системные метрики.

Метрики автоматически экспортируются через Spring Boot Actuator + Micrometer в формате Prometheus.

## Spring Batch метрики (основные)

- Job Duration (spring_batch_job_seconds_*) - время выполнения заданий
- Job Execution Rate (spring_batch_job_seconds_count) - частота запуска заданий
- Step Duration (spring_batch_step_seconds_*) - время выполнения каждого шага заданий
- Item Throughput (spring_batch_item_read/process/write_seconds_count) - скорость обработки записей

## Системные метрики (дополнительные)

- JVM Heap Memory (jvm_memory_used_bytes) - использование памяти
- DB Connection Pool (hikaricp_connections_active/idle) - пул соединений
- GC Pause Rate (jvm_gc_pause_seconds_count) - частота сборки мусора

## Алерты в Grafana

Используем Grafana, для примера смотрим высокую нагрузку.

### 1. High CPU Usage

- Условие: CPU > 80% в течение 2 минут
- Метрика: process_cpu_usage{job="batch-processing"} * 100
- Обоснование: Высокая загрузка CPU указывает на проблемы производительности

### 2. High Memory Usage

- Условие: Heap memory > 80% от максимума
- Метрика: jvm_memory_used_bytes / jvm_memory_max_bytes > 0.8
- Обоснование: Предотвращение OutOfMemoryError
