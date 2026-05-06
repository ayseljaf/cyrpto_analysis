"""
Crypto Analysis Pipeline DAG.

The DAG file stays thin and orchestration-focused; heavy logic lives in src/pipeline.
"""

from airflow.decorators import dag, task
from airflow.providers.common.sql.operators.sql import SQLColumnCheckOperator
from airflow.providers.common.sql.sensors.sql import SqlSensor
import pendulum

from pipeline.config import DEFAULT_ARGS, POSTGRES_CONN_ID
from pipeline import task_logic


@dag(
    dag_id="crypto_analysis_pipeline",
    default_args=DEFAULT_ARGS,
    description="Daily cryptocurrency data extraction and analysis pipeline",
    schedule="0 18 * * *",
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    catchup=False,
    max_active_runs=1,
    tags=["crypto", "etl", "daily", "production"],
    doc_md=__doc__,
)
def crypto_analysis_pipeline():
    @task
    def get_crypto_pairs():
        return task_logic.get_crypto_pairs()

    @task
    def extract_crypto_data(symbol: str, **context):
        return task_logic.extract_crypto_data(
            symbol=symbol,
            dag_run=context["dag_run"],
            data_interval_end=context["data_interval_end"],
        )

    @task
    def calculate_monthly_statistics(**context) -> int:
        return task_logic.calculate_monthly_statistics(
            dag_run_id=context["dag_run"].run_id
        )

    @task
    def calculate_weekly_price_changes(**context) -> int:
        return task_logic.calculate_weekly_price_changes(
            dag_run_id=context["dag_run"].run_id
        )

    @task
    def calculate_overall_statistics(**context) -> int:
        return task_logic.calculate_overall_statistics(
            dag_run_id=context["dag_run"].run_id,
            calculation_date=context["data_interval_start"].date(),
        )

    @task
    def update_pipeline_metadata(
        extraction_results, monthly_count: int, weekly_count: int, overall_count: int, **context
    ):
        return task_logic.update_pipeline_metadata(
            extraction_results=extraction_results,
            monthly_count=monthly_count,
            weekly_count=weekly_count,
            overall_count=overall_count,
            dag_run=context["dag_run"],
        )

    crypto_pairs = get_crypto_pairs()
    extraction_results = extract_crypto_data.expand(symbol=crypto_pairs)

    check_extracted_data = SQLColumnCheckOperator(
        task_id="check_extracted_data",
        conn_id=POSTGRES_CONN_ID,
        table="crypto_prices",
        column_mapping={
            "close_price": {"min": {"greater_than": 0}, "null_check": {"equal_to": 0}},
            "symbol": {"null_check": {"equal_to": 0}},
        },
    )

    verify_data_loaded = SqlSensor(
        task_id="verify_data_loaded",
        conn_id=POSTGRES_CONN_ID,
        sql="""
            SELECT COUNT(*) > 0
            FROM crypto_prices
            WHERE open_time >= CURRENT_DATE - INTERVAL '1 day'
        """,
        poke_interval=30,
        timeout=600,
        mode="reschedule",
    )

    monthly_stats = calculate_monthly_statistics()
    weekly_changes = calculate_weekly_price_changes()
    overall_stats = calculate_overall_statistics()

    validate_monthly_stats = SQLColumnCheckOperator(
        task_id="validate_monthly_stats",
        conn_id=POSTGRES_CONN_ID,
        table="monthly_statistics",
        column_mapping={
            "average_price": {"min": {"greater_than": 0}, "null_check": {"equal_to": 0}},
            "highest_price": {"min": {"greater_than": 0}},
            "lowest_price": {"min": {"greater_than": 0}},
        },
    )

    pipeline_summary = update_pipeline_metadata(
        extraction_results, monthly_stats, weekly_changes, overall_stats
    )

    extraction_results >> check_extracted_data >> verify_data_loaded
    verify_data_loaded >> [monthly_stats, weekly_changes, overall_stats]
    [monthly_stats, weekly_changes, overall_stats] >> validate_monthly_stats
    validate_monthly_stats >> pipeline_summary


crypto_dag = crypto_analysis_pipeline()
