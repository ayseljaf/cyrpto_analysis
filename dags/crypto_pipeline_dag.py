"""
Crypto Analysis Pipeline DAG
Modern Airflow 2.x implementation using TaskFlow API

This DAG orchestrates daily cryptocurrency data extraction from Binance,
performs analysis calculations, and stores results in PostgreSQL.

Features:
- TaskFlow API with @task decorators
- Dynamic task mapping for parallel crypto pair processing
- Data interval-aware queries
- Idempotent transformations (delete-before-insert)
- Data quality checks with SQLColumnCheckOperator
- Optimized sensors with mode='reschedule'
"""

from datetime import datetime, timedelta
from typing import List, Dict
import logging

from airflow.decorators import dag, task
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.common.sql.operators.sql import SQLColumnCheckOperator
from airflow.providers.common.sql.sensors.sql import SqlSensor
from binance.client import Client
import pandas as pd
import pytz

# Constants
TRADING_PAIRS = [
    'BTCUSDT', 'ETHUSDT', 'SOLUSDT',
    'ADAUSDT', 'DOGEUSDT', 'SHIBUSDT', 'USDCUSDT'
]

POSTGRES_CONN_ID = 'crypto_postgres'

logger = logging.getLogger(__name__)

# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'retry_exponential_backoff': True,
    'max_retry_delay': timedelta(minutes=30),
}


@dag(
    dag_id='crypto_analysis_pipeline',
    default_args=default_args,
    description='Daily cryptocurrency data extraction and analysis pipeline',
    schedule='0 18 * * *',  # Daily at 18:00 UTC
    start_date=datetime(2024, 1, 1),
    catchup=False,
    max_active_runs=1,
    tags=['crypto', 'etl', 'daily', 'production'],
    doc_md=__doc__,
)
def crypto_analysis_pipeline():
    """
    Main DAG function defining the crypto analysis pipeline workflow.
    """

    @task
    def get_crypto_pairs() -> List[str]:
        """
        Returns the list of cryptocurrency trading pairs to process.
        
        Returns:
            List of trading pair symbols (e.g., ['BTCUSDT', 'ETHUSDT'])
        """
        logger.info(f"Processing {len(TRADING_PAIRS)} trading pairs")
        return TRADING_PAIRS

    @task
    def extract_crypto_data(symbol: str, **context) -> Dict:
        """
        Extract historical price data for a single cryptocurrency from Binance API.
        
        Uses data intervals to ensure idempotent, time-aware data extraction.
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT')
            context: Airflow context with data_interval_start and data_interval_end
            
        Returns:
            Dictionary with extraction results and metadata
        """
        dag_run_id = context['dag_run'].run_id
        data_interval_end = context['data_interval_end']

        # lookback_days=365 for historical backfill, default 2 for daily incremental
        lookback_days = int(context['dag_run'].conf.get('lookback_days', 2))
        start_time = data_interval_end - timedelta(days=lookback_days)

        logger.info(f"Extracting {symbol} from {start_time} to {data_interval_end} ({lookback_days}d lookback)")

        try:
            client = Client()
            
            # Fetch daily klines from Binance (1 day interval)
            klines = client.get_historical_klines(
                symbol=symbol,
                interval=Client.KLINE_INTERVAL_1DAY,
                start_str=int(start_time.timestamp() * 1000),
                end_str=int(data_interval_end.timestamp() * 1000)
            )
            
            if not klines:
                logger.warning(f"No data returned for {symbol}")
                return {'symbol': symbol, 'records': 0, 'success': False}
            
            # Convert to DataFrame with proper column mapping
            df = pd.DataFrame(klines, columns=[
                'open_time', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_asset_volume', 'number_of_trades',
                'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
            ])
            
            # Convert timestamps and prices to proper types
            df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
            df['close_time'] = pd.to_datetime(df['close_time'], unit='ms')
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = df[col].astype(float)
            
            if df.empty:
                logger.warning(f"No data points for {symbol}")
                return {'symbol': symbol, 'records': 0, 'success': False}
            
            # Prepare data for database insertion matching actual table schema
            df_to_load = df[['open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time']].copy()
            df_to_load.columns = ['open_time', 'open_price', 'high_price', 'low_price', 'close_price', 'volume', 'close_time']
            df_to_load['symbol'] = symbol
            df_to_load['extracted_at'] = datetime.now(pytz.UTC)
            
            # Load to database (delete-before-insert for idempotency)
            hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)
            hook.run(
                "DELETE FROM crypto_prices WHERE symbol = %s AND open_time BETWEEN %s AND %s",
                parameters=(symbol, df_to_load['open_time'].min(), df_to_load['open_time'].max())
            )
            engine = hook.get_sqlalchemy_engine()
            df_to_load.to_sql('crypto_prices', engine, if_exists='append', index=False)
            
            records_loaded = len(df_to_load)
            logger.info(f"Successfully loaded {records_loaded} records for {symbol}")
            
            return {
                'symbol': symbol,
                'records': records_loaded,
                'success': True,
                'start_date': str(df_to_load['open_time'].min()),
                'end_date': str(df_to_load['open_time'].max())
            }
            
        except Exception as e:
            logger.error(f"Error extracting {symbol}: {str(e)}")
            raise

    @task
    def calculate_monthly_statistics(**context) -> int:
        """
        Calculate monthly statistics for all cryptocurrencies.
        
        Uses idempotent delete-before-insert pattern to ensure data consistency.
        
        Returns:
            Number of records processed
        """
        dag_run_id = context['dag_run'].run_id

        logger.info("Calculating monthly statistics")

        hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)

        # Aggregate ALL data in crypto_prices (not just current month)
        insert_query = """
            INSERT INTO monthly_statistics (
                symbol, month, average_price, highest_price,
                lowest_price, price_range, created_at, updated_at, dag_run_id
            )
            SELECT
                symbol,
                DATE_TRUNC('month', open_time)::date as month,
                AVG(close_price) as average_price,
                MAX(high_price) as highest_price,
                MIN(low_price) as lowest_price,
                MAX(high_price) - MIN(low_price) as price_range,
                CURRENT_TIMESTAMP as created_at,
                CURRENT_TIMESTAMP as updated_at,
                %s as dag_run_id
            FROM crypto_prices
            GROUP BY symbol, DATE_TRUNC('month', open_time)
            ON CONFLICT (symbol, month)
            DO UPDATE SET
                average_price = EXCLUDED.average_price,
                highest_price = EXCLUDED.highest_price,
                lowest_price = EXCLUDED.lowest_price,
                price_range = EXCLUDED.price_range,
                updated_at = EXCLUDED.updated_at,
                dag_run_id = EXCLUDED.dag_run_id
            RETURNING id
        """

        result = hook.get_records(
            insert_query,
            parameters=(dag_run_id,)
        )
        
        records_count = len(result)
        logger.info(f"Calculated monthly statistics: {records_count} records")
        
        return records_count

    @task
    def calculate_weekly_price_changes(**context) -> int:
        """
        Calculate weekly price changes for all cryptocurrencies.
        
        Uses idempotent delete-before-insert pattern.
        
        Returns:
            Number of records processed
        """
        dag_run_id = context['dag_run'].run_id

        logger.info("Calculating weekly price changes")

        hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)

        # Compute weekly changes for ALL dates across full history
        insert_query = """
            INSERT INTO weekly_price_changes (
                symbol, date, current_price, price_7_days_ago,
                price_change_pct, created_at, dag_run_id
            )
            WITH price_changes AS (
                SELECT
                    symbol,
                    open_time::date as date,
                    close_price as current_price,
                    LAG(close_price, 7) OVER (PARTITION BY symbol ORDER BY open_time) as price_7_days_ago
                FROM crypto_prices
            )
            SELECT
                symbol,
                date,
                current_price,
                price_7_days_ago,
                CASE
                    WHEN price_7_days_ago IS NOT NULL AND price_7_days_ago > 0
                    THEN ((current_price - price_7_days_ago) / price_7_days_ago * 100)
                    ELSE NULL
                END as price_change_pct,
                CURRENT_TIMESTAMP as created_at,
                %s as dag_run_id
            FROM price_changes
            WHERE price_7_days_ago IS NOT NULL
            ON CONFLICT (symbol, date)
            DO UPDATE SET
                current_price = EXCLUDED.current_price,
                price_7_days_ago = EXCLUDED.price_7_days_ago,
                price_change_pct = EXCLUDED.price_change_pct,
                dag_run_id = EXCLUDED.dag_run_id
            RETURNING id
        """

        result = hook.get_records(
            insert_query,
            parameters=(dag_run_id,)
        )
        
        records_count = len(result)
        logger.info(f"Calculated weekly changes: {records_count} records")
        
        return records_count

    @task
    def calculate_overall_statistics(**context) -> int:
        """
        Calculate overall statistics for all cryptocurrencies.
        
        Uses idempotent delete-before-insert pattern.
        
        Returns:
            Number of records processed
        """
        dag_run_id = context['dag_run'].run_id
        calculation_date = context['data_interval_start'].date()
        
        logger.info("Calculating overall statistics")
        
        hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)
        
        # Delete existing records for this calculation date (idempotency)
        delete_query = """
            DELETE FROM overall_statistics 
            WHERE calculation_date = %s
        """
        hook.run(delete_query, parameters=(calculation_date,))
        
        # Calculate and insert overall statistics
        insert_query = """
            INSERT INTO overall_statistics (
                symbol, record_count, average_price, volatility,
                lowest_price, highest_price, earliest_date, latest_date,
                calculation_date, created_at, dag_run_id
            )
            SELECT
                symbol,
                COUNT(*) as record_count,
                AVG(close_price) as average_price,
                STDDEV(close_price) as volatility,
                MIN(low_price) as lowest_price,
                MAX(high_price) as highest_price,
                MIN(open_time) as earliest_date,
                MAX(close_time) as latest_date,
                %s::date as calculation_date,
                CURRENT_TIMESTAMP as created_at,
                %s as dag_run_id
            FROM crypto_prices
            GROUP BY symbol
            ON CONFLICT (symbol, calculation_date)
            DO UPDATE SET
                record_count = EXCLUDED.record_count,
                average_price = EXCLUDED.average_price,
                volatility = EXCLUDED.volatility,
                lowest_price = EXCLUDED.lowest_price,
                highest_price = EXCLUDED.highest_price,
                earliest_date = EXCLUDED.earliest_date,
                latest_date = EXCLUDED.latest_date,
                dag_run_id = EXCLUDED.dag_run_id
            RETURNING id
        """
        
        result = hook.get_records(
            insert_query,
            parameters=(calculation_date, dag_run_id)
        )
        
        records_count = len(result)
        logger.info(f"Calculated overall statistics: {records_count} records")
        
        return records_count

    @task
    def update_pipeline_metadata(
        extraction_results: List[Dict],
        monthly_count: int,
        weekly_count: int,
        overall_count: int,
        **context
    ) -> Dict:
        """
        Update pipeline metadata table with run information.
        
        Args:
            extraction_results: Results from extraction tasks
            monthly_count: Number of monthly statistics records
            weekly_count: Number of weekly change records
            overall_count: Number of overall statistics records
            
        Returns:
            Summary of pipeline execution
        """
        dag_run = context['dag_run']
        
        logger.info("Updating pipeline metadata")
        
        # Calculate totals
        total_extracted = sum(r['records'] for r in extraction_results if r['success'])
        successful_symbols = [r['symbol'] for r in extraction_results if r['success']]
        
        hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)
        
        insert_query = """
            INSERT INTO pipeline_metadata (
                dag_id, dag_run_id, execution_date, status,
                records_extracted, records_transformed, records_loaded,
                started_at, completed_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (dag_id, dag_run_id)
            DO UPDATE SET
                status = EXCLUDED.status,
                records_extracted = EXCLUDED.records_extracted,
                records_transformed = EXCLUDED.records_transformed,
                records_loaded = EXCLUDED.records_loaded,
                completed_at = EXCLUDED.completed_at
        """
        
        hook.run(
            insert_query,
            parameters=(
                dag_run.dag_id,
                dag_run.run_id,
                dag_run.execution_date,
                'success',
                total_extracted,
                monthly_count + weekly_count + overall_count,
                total_extracted,
                dag_run.start_date,
                datetime.now(pytz.UTC)
            )
        )
        
        summary = {
            'dag_run_id': dag_run.run_id,
            'symbols_processed': len(successful_symbols),
            'records_extracted': total_extracted,
            'monthly_stats': monthly_count,
            'weekly_changes': weekly_count,
            'overall_stats': overall_count,
            'status': 'success'
        }
        
        logger.info(f"Pipeline completed: {summary}")
        
        return summary

    # Define task dependencies using TaskFlow API
    
    # Get list of crypto pairs
    crypto_pairs = get_crypto_pairs()
    
    # Extract data for each pair in parallel using dynamic task mapping
    extraction_results = extract_crypto_data.expand(symbol=crypto_pairs)
    
    # Data quality check: Verify extracted data
    check_extracted_data = SQLColumnCheckOperator(
        task_id='check_extracted_data',
        conn_id=POSTGRES_CONN_ID,
        table='crypto_prices',
        column_mapping={
            'close_price': {
                'min': {'greater_than': 0},
                'null_check': {'equal_to': 0}
            },
            'symbol': {
                'null_check': {'equal_to': 0}
            }
        }
    )
    
    # Sensor: Wait for data to be loaded
    verify_data_loaded = SqlSensor(
        task_id='verify_data_loaded',
        conn_id=POSTGRES_CONN_ID,
        sql="""
            SELECT COUNT(*) > 0
            FROM crypto_prices
            WHERE open_time >= CURRENT_DATE - INTERVAL '1 day'
        """,
        poke_interval=30,
        timeout=600,
        mode='reschedule',  # Optimized sensor mode
    )
    
    # Transform tasks (run in parallel)
    monthly_stats = calculate_monthly_statistics()
    weekly_changes = calculate_weekly_price_changes()
    overall_stats = calculate_overall_statistics()
    
    # Data quality check: Validate monthly statistics
    validate_monthly_stats = SQLColumnCheckOperator(
        task_id='validate_monthly_stats',
        conn_id=POSTGRES_CONN_ID,
        table='monthly_statistics',
        column_mapping={
            'average_price': {
                'min': {'greater_than': 0},
                'null_check': {'equal_to': 0}
            },
            'highest_price': {
                'min': {'greater_than': 0}
            },
            'lowest_price': {
                'min': {'greater_than': 0}
            }
        }
    )
    
    # Update metadata with all results
    pipeline_summary = update_pipeline_metadata(
        extraction_results,
        monthly_stats,
        weekly_changes,
        overall_stats
    )
    
    # Define task flow
    extraction_results >> check_extracted_data >> verify_data_loaded
    verify_data_loaded >> [monthly_stats, weekly_changes, overall_stats]
    [monthly_stats, weekly_changes, overall_stats] >> validate_monthly_stats
    validate_monthly_stats >> pipeline_summary


# Instantiate the DAG
crypto_dag = crypto_analysis_pipeline()
