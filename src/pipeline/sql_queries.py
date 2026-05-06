"""SQL templates used by crypto pipeline transformation tasks."""

MONTHLY_STATS_UPSERT_SQL = """
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

WEEKLY_PRICE_CHANGES_UPSERT_SQL = """
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

OVERALL_STATS_DELETE_SQL = """
    DELETE FROM overall_statistics
    WHERE calculation_date = %s
"""

OVERALL_STATS_UPSERT_SQL = """
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

PIPELINE_METADATA_UPSERT_SQL = """
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

