# Реализация Distributed Scheduling с k8s CronJob

## Подготовка

Запуск MiniKube:

```shell
minikube start
```

Добавление репозитория Helm и развертывание Postgres:

```shell
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
helm install postgresql bitnami/postgresql -f postgres-values.yaml
```

Инициализация базы данных:

```shell
kubectl cp init-db.sql default/postgresql-0:/tmp/init-db.sql
kubectl exec -it postgresql-0 -- psql -U postgres -d logistics -f /tmp/init-db.sql
```

Сборка образа программы:

```shell
eval $(minikube docker-env)
docker build -t data-exporter:latest .
```

Создание PVC для хранилища файлов:

```shell
kubectl apply -f k8s-pvc.yaml
```

## Тестовый запуск задания

Создание job:

```shell
kubectl apply -f k8s-job.yaml
kubectl get jobs
```
```
NAME              STATUS     COMPLETIONS   DURATION   AGE
data-export-job   Complete   1/1           4s         2m18s
```

Посмотреть лог программы:

```shell
kubectl logs job/data-export-job
```
```
Exported 3 rows from shipments to /data/exports/shipments-20251115-134752.csv
```

Посмотреть сформированный файл (minikube):

```shell
minikube ssh cat /tmp/hostpath-provisioner/default/export-data-pvc/shipments-20251115-134752.csv
```
```
id,driver_id,origin,destination,amount
1,1,Москва,СПб,50000.00
2,1,СПб,Луга,10000.00
3,1,СПб,Москва,25000.00
```

## Запуск задания по расписанию

Создание CronJob (изменил расписание для пробного запуска)

```shell
kubectl apply -f k8s-cronjob.yaml
kubectl get cronjobs
```
```
NAME                  SCHEDULE      TIMEZONE           SUSPEND   ACTIVE   LAST SCHEDULE   AGE
data-export-cronjob   50 21 * * *   Asia/Krasnoyarsk   False     0        106s            39m
```

Найдем job, созданный для cronjob:

```shell
kubectl get jobs
```
```
NAME                           STATUS     COMPLETIONS   DURATION   AGE
data-export-cronjob-29386970   Complete   1/1           3s         5m11s
data-export-job                Complete   1/1           4s         15m
```

Посмотрим лог программы:

```shell
kubectl logs job/data-export-cronjob-29386970
```
```
Exported 3 rows from shipments to /data/exports/shipments-20251115-145001.csv
```

Посмотрим сформированный файл (minikube):

```shell
minikube ssh cat /tmp/hostpath-provisioner/default/export-data-pvc/shipments-20251115-145001.csv
```
```
id,driver_id,origin,destination,amount
1,1,Москва,СПб,50000.00
2,1,СПб,Луга,10000.00
3,1,СПб,Москва,25000.00
```
