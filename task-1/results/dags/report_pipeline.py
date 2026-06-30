import csv
import logging
from datetime import datetime, timedelta
from decimal import Decimal

from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.standard.operators.empty import EmptyOperator
from airflow.providers.standard.operators.python import get_current_context
from airflow.sdk import dag, task
from airflow.utils.email import send_email_smtp

default_args = {
    "depends_on_past": False,
    "start_date": datetime(2025, 11, 11),
    "retries": 3,
    "retry_delay": timedelta(minutes=2),
    "retry_exponential_backoff": True,
    "max_retry_delay": timedelta(minutes=10),
}


def success_callback(_):
    addressee = "demo@example.com"
    subject = "Отчет успешно сформирован"
    html_content = """
        <h3>Отчет успешно сформирован</h3>
        <p>Все задачи выполнены успешно.</p>
    """
    send_email_smtp(to=addressee, subject=subject, html_content=html_content)


def failure_callback(_):
    addressee = "demo@example.com"
    subject = "Формирование отчета завершилось с ошибкой"
    html_content = """
        <h3>Формирование отчета завершилось с ошибкой</h3>
        <p>Проверьте логи для получения дополнительной информации.</p>
    """
    send_email_smtp(to=addressee, subject=subject, html_content=html_content)


@dag(
    dag_id="report_pipeline",
    default_args=default_args,
    description="Формирование отчета",
    schedule="0 6 * * *",
    catchup=False,
    on_success_callback=success_callback,
    on_failure_callback=failure_callback,
)
def report_pipeline():
    @task
    def read_order_data():
        hook = PostgresHook(postgres_conn_id="postgres-work")
        sql = """
            select order_id, client_id, client_name, order_date, amount
            from order_
            join client using (client_id)
            where status = 'completed'
        """
        records = hook.get_records(sql)
        columns = ["order_id", "client_id", "client_name", "order_date", "amount"]
        data = [dict(zip(columns, row)) for row in records]
        return data

    @task
    def read_delivery_data():
        data = []
        with open("/opt/airflow/data/delivery.csv") as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(
                    {
                        "delivery_id": int(row["delivery_id"]),
                        "order_id": int(row["order_id"]),
                        "address": row["address"],
                        "status": row["status"],
                    }
                )
        return data

    @task
    def analyze_data(order_data, delivery_data):
        # Успешно доставленные заказы
        delivered_orders = set(
            {x["order_id"] for x in delivery_data if x["status"] == "delivered"}
        )
        # Сумма доставленных заказов
        delivered_amount = sum(
            x["amount"] for x in order_data if x["order_id"] in delivered_orders
        )
        return {
            "delivered_amount": delivered_amount,
        }

    @task.branch
    def decide_processing_branch(analysis_result):
        delivered_amount = analysis_result["delivered_amount"]

        if delivered_amount >= Decimal("20000"):
            return "process_high_amount"
        else:
            return "process_low_amount"

    @task
    def process_high_amount():
        context = get_current_context()
        analysis_result = context["ti"].xcom_pull(task_ids="analyze_data")
        delivered_amount = analysis_result["delivered_amount"]
        logging.info("Сложная обработка случая high")
        return {
            "processing_type": "high",
            "delivered_amount": delivered_amount,
        }

    @task
    def process_low_amount():
        context = get_current_context()
        analysis_result = context["ti"].xcom_pull(task_ids="analyze_data")
        delivered_amount = analysis_result["delivered_amount"]
        logging.info("Простая обработка случая low")
        return {
            "processing_type": "low",
            "delivered_amount": delivered_amount,
        }

    @task(trigger_rule="none_failed_min_one_success")
    def join_branches(high_result, low_result):
        return high_result if high_result else low_result

    @task(retries=5, retry_delay=timedelta(minutes=1))
    def save_results_to_db(processing_result):
        hook = PostgresHook(postgres_conn_id="postgres-work")
        sql = """
            insert into report (processing_type, delivered_amount)
            values (%s, %s)
        """
        hook.run(
            sql,
            parameters=(
                processing_result["processing_type"],
                processing_result["delivered_amount"],
            ),
        )
        return processing_result

    start = EmptyOperator(task_id="start")
    end = EmptyOperator(task_id="end")

    order_data = read_order_data()
    delivery_data = read_delivery_data()
    analysis_result = analyze_data(order_data, delivery_data)
    branch_decision = decide_processing_branch(analysis_result)
    high_result = process_high_amount()
    low_result = process_low_amount()
    joined = join_branches(high_result, low_result)
    saved = save_results_to_db(joined)

    start >> [order_data, delivery_data] >> analysis_result >> branch_decision
    branch_decision >> [high_result, low_result]
    [high_result, low_result] >> joined >> saved >> end


dag_instance = report_pipeline()
