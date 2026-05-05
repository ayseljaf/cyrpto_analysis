CREATE TABLE IF NOT EXISTS raw_events (
    id BIGSERIAL PRIMARY KEY,
    event_id TEXT NOT NULL UNIQUE,
    source TEXT NOT NULL,
    stream TEXT NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    event_time TIMESTAMPTZ NOT NULL,
    price NUMERIC(30, 8) NOT NULL,
    quantity NUMERIC(30, 8) NOT NULL,
    trade_id BIGINT,
    is_buyer_maker BOOLEAN,
    payload_json JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_raw_events_symbol_event_time
    ON raw_events(symbol, event_time DESC);
CREATE INDEX IF NOT EXISTS idx_raw_events_created_at
    ON raw_events(created_at DESC);

SELECT create_hypertable('raw_events', 'event_time', if_not_exists => TRUE, migrate_data => TRUE);

CREATE TABLE IF NOT EXISTS latest_prices (
    symbol VARCHAR(20) PRIMARY KEY,
    last_price NUMERIC(30, 8) NOT NULL,
    last_quantity NUMERIC(30, 8) NOT NULL,
    last_event_time TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_latest_prices_updated_at
    ON latest_prices(updated_at DESC);

CREATE TABLE IF NOT EXISTS price_1m_rollup (
    symbol VARCHAR(20) NOT NULL,
    bucket_time TIMESTAMPTZ NOT NULL,
    open NUMERIC(30, 8) NOT NULL,
    high NUMERIC(30, 8) NOT NULL,
    low NUMERIC(30, 8) NOT NULL,
    close NUMERIC(30, 8) NOT NULL,
    volume NUMERIC(30, 8) NOT NULL,
    trade_count INTEGER NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (symbol, bucket_time)
);

SELECT create_hypertable('price_1m_rollup', 'bucket_time', if_not_exists => TRUE, migrate_data => TRUE);
