"""Task implementation logic for the crypto Airflow pipeline."""

from datetime import datetime, timedelta
from typing import Dict, List
import logging

import pandas as pd
import pytz
from airflow.providers.postgres.hooks.postgres import PostgresHook
from binance.client import Client

from pipeline.config import POSTGRES_CONN_ID, TRADING_PAIRS
from pipeline.sql_queries import (
    MONTHLY_STATS_UPSERT_SQL,
    OVERALL_STATS_DELETE_SQL,
    OVERALL_STATS_UPSERT_SQL,
    PIPELINE_METADATA_UPSERT_SQL,
    WEEKLY_PRICE_CHANGES_UPSERT_SQL,
)

logger = logging.getLogger(__name__)


def get_crypto_pairs() -> List[str]:
    logger.info("Processing %s trading pairs", len(TRADING_PAIRS))
    return TRADING_PAIRS


def extract_crypto_data(symbol: str, dag_run, data_interval_end) -> Dict:
    lookback_days = int(dag_run.conf.get("lookback_days", 2))
    start_time = data_interval_end - timedelta(days=lookback_days)

    logger.info(
        "Extracting %s from %s to %s (%sd lookback)",
        symbol,
        start_time,
        data_interval_end,
        lookback_days,
    )

    client = Client()
    klines = client.get_historical_klines(
        symbol=symbol,
        interval=Client.KLINE_INTERVAL_1DAY,
        start_str=int(start_time.timestamp() * 1000),
        end_str=int(data_interval_end.timestamp() * 1000),
    )

    if not klines:
        logger.warning("No data returned for %s", symbol)
        return {"symbol": symbol, "records": 0, "success": False}

    df = pd.DataFrame(
        klines,
        columns=[
            "open_time",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "close_time",
            "quote_asset_volume",
            "number_of_trades",
            "taker_buy_base_asset_volume",
            "taker_buy_quote_asset_volume",
            "ignore",
        ],
    )

    df["open_time"] = pd.to_datetime(df["open_time"], unit="ms")
    df["close_time"] = pd.to_datetime(df["close_time"], unit="ms")
    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = df[col].astype(float)

    if df.empty:
        logger.warning("No data points for %s", symbol)
        return {"symbol": symbol, "records": 0, "success": False}

    df_to_load = df[
        ["open_time", "open", "high", "low", "close", "volume", "close_time"]
    ].copy()
    df_to_load.columns = [
        "open_time",
        "open_price",
        "high_price",
        "low_price",
        "close_price",
        "volume",
        "close_time",
    ]
    df_to_load["symbol"] = symbol
    df_to_load["extracted_at"] = datetime.now(pytz.UTC)

    hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)
    hook.run(
        "DELETE FROM crypto_prices WHERE symbol = %s AND open_time BETWEEN %s AND %s",
        parameters=(symbol, df_to_load["open_time"].min(), df_to_load["open_time"].max()),
    )
    engine = hook.get_sqlalchemy_engine()
    df_to_load.to_sql("crypto_prices", engine, if_exists="append", index=False)

    records_loaded = len(df_to_load)
    logger.info("Successfully loaded %s records for %s", records_loaded, symbol)

    return {
        "symbol": symbol,
        "records": records_loaded,
        "success": True,
        "start_date": str(df_to_load["open_time"].min()),
        "end_date": str(df_to_load["open_time"].max()),
    }


def calculate_monthly_statistics(dag_run_id: str) -> int:
    hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)
    result = hook.get_records(MONTHLY_STATS_UPSERT_SQL, parameters=(dag_run_id,))
    records_count = len(result)
    logger.info("Calculated monthly statistics: %s records", records_count)
    return records_count


def calculate_weekly_price_changes(dag_run_id: str) -> int:
    hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)
    result = hook.get_records(WEEKLY_PRICE_CHANGES_UPSERT_SQL, parameters=(dag_run_id,))
    records_count = len(result)
    logger.info("Calculated weekly changes: %s records", records_count)
    return records_count


def calculate_overall_statistics(dag_run_id: str, calculation_date) -> int:
    hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)
    hook.run(OVERALL_STATS_DELETE_SQL, parameters=(calculation_date,))
    result = hook.get_records(
        OVERALL_STATS_UPSERT_SQL, parameters=(calculation_date, dag_run_id)
    )
    records_count = len(result)
    logger.info("Calculated overall statistics: %s records", records_count)
    return records_count


def update_pipeline_metadata(
    extraction_results: List[Dict],
    monthly_count: int,
    weekly_count: int,
    overall_count: int,
    dag_run,
) -> Dict:
    total_extracted = sum(r["records"] for r in extraction_results if r["success"])
    successful_symbols = [r["symbol"] for r in extraction_results if r["success"]]

    hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)
    hook.run(
        PIPELINE_METADATA_UPSERT_SQL,
        parameters=(
            dag_run.dag_id,
            dag_run.run_id,
            dag_run.execution_date,
            "success",
            total_extracted,
            monthly_count + weekly_count + overall_count,
            total_extracted,
            dag_run.start_date,
            datetime.now(pytz.UTC),
        ),
    )

    summary = {
        "dag_run_id": dag_run.run_id,
        "symbols_processed": len(successful_symbols),
        "records_extracted": total_extracted,
        "monthly_stats": monthly_count,
        "weekly_changes": weekly_count,
        "overall_stats": overall_count,
        "status": "success",
    }
    logger.info("Pipeline completed: %s", summary)
    return summary

