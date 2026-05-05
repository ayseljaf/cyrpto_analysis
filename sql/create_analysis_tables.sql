-- Monthly Statistics Table
CREATE TABLE IF NOT EXISTS monthly_statistics (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    month DATE NOT NULL,
    average_price DECIMAL(20, 8) NOT NULL,
    highest_price DECIMAL(20, 8) NOT NULL,
    lowest_price DECIMAL(20, 8) NOT NULL,
    price_range DECIMAL(20, 8) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    dag_run_id VARCHAR(250),
    CONSTRAINT uq_monthly_symbol_month UNIQUE (symbol, month)
);

CREATE INDEX IF NOT EXISTS idx_monthly_stats_symbol ON monthly_statistics(symbol);
CREATE INDEX IF NOT EXISTS idx_monthly_stats_month ON monthly_statistics(month DESC);

-- Weekly Price Changes Table
CREATE TABLE IF NOT EXISTS weekly_price_changes (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    date DATE NOT NULL,
    current_price DECIMAL(20, 8) NOT NULL,
    price_7_days_ago DECIMAL(20, 8),
    price_change_pct DECIMAL(10, 4),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    dag_run_id VARCHAR(250),
    CONSTRAINT uq_weekly_symbol_date UNIQUE (symbol, date)
);

CREATE INDEX IF NOT EXISTS idx_weekly_changes_symbol ON weekly_price_changes(symbol);
CREATE INDEX IF NOT EXISTS idx_weekly_changes_date ON weekly_price_changes(date DESC);

-- Overall Statistics Table
CREATE TABLE IF NOT EXISTS overall_statistics (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    record_count INTEGER NOT NULL,
    average_price DECIMAL(20, 8) NOT NULL,
    volatility DECIMAL(20, 8),
    lowest_price DECIMAL(20, 8) NOT NULL,
    highest_price DECIMAL(20, 8) NOT NULL,
    earliest_date TIMESTAMP WITH TIME ZONE,
    latest_date TIMESTAMP WITH TIME ZONE,
    calculation_date DATE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    dag_run_id VARCHAR(250),
    CONSTRAINT uq_overall_symbol_calc_date UNIQUE (symbol, calculation_date)
);

CREATE INDEX IF NOT EXISTS idx_overall_stats_symbol ON overall_statistics(symbol);

-- Pipeline Metadata Table
CREATE TABLE IF NOT EXISTS pipeline_metadata (
    id SERIAL PRIMARY KEY,
    dag_id VARCHAR(250) NOT NULL,
    dag_run_id VARCHAR(250) NOT NULL,
    execution_date TIMESTAMP WITH TIME ZONE NOT NULL,
    status VARCHAR(50) NOT NULL,
    records_extracted INTEGER DEFAULT 0,
    records_transformed INTEGER DEFAULT 0,
    records_loaded INTEGER DEFAULT 0,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    error_message TEXT,
    CONSTRAINT uq_pipeline_dag_run UNIQUE (dag_id, dag_run_id)
);

-- Modify Existing crypto_prices Table
ALTER TABLE crypto_prices
    ADD COLUMN IF NOT EXISTS dag_run_id VARCHAR(250),
    ADD COLUMN IF NOT EXISTS extracted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;

CREATE INDEX IF NOT EXISTS idx_crypto_prices_dag_run ON crypto_prices(dag_run_id);
