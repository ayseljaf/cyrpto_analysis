-- Create schema for crypto analysis tables
CREATE TABLE IF NOT EXISTS crypto_prices (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    open_time TIMESTAMP NOT NULL,
    open_price DECIMAL(20, 8) NOT NULL,
    high_price DECIMAL(20, 8) NOT NULL,
    low_price DECIMAL(20, 8) NOT NULL,
    close_price DECIMAL(20, 8) NOT NULL,
    volume DECIMAL(30, 8) NOT NULL,
    close_time TIMESTAMP NOT NULL,
    quote_asset_volume DECIMAL(30, 8),
    number_of_trades INTEGER,
    taker_buy_base_volume DECIMAL(30, 8),
    taker_buy_quote_volume DECIMAL(30, 8),
    extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(symbol, open_time)
);

CREATE TABLE IF NOT EXISTS crypto_statistics (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    period_start TIMESTAMP NOT NULL,
    period_end TIMESTAMP NOT NULL,
    avg_price DECIMAL(20, 8),
    min_price DECIMAL(20, 8),
    max_price DECIMAL(20, 8),
    total_volume DECIMAL(20, 8),
    price_change_pct DECIMAL(10, 4),
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(symbol, period_start, period_end)
);

CREATE TABLE IF NOT EXISTS crypto_weekly_changes (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    week_start TIMESTAMP NOT NULL,
    week_end TIMESTAMP NOT NULL,
    opening_price DECIMAL(20, 8),
    closing_price DECIMAL(20, 8),
    weekly_change_pct DECIMAL(10, 4),
    weekly_volume DECIMAL(20, 8),
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(symbol, week_start)
);

CREATE TABLE IF NOT EXISTS crypto_monthly_analysis (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    month_start TIMESTAMP NOT NULL,
    month_end TIMESTAMP NOT NULL,
    avg_monthly_price DECIMAL(20, 8),
    monthly_high DECIMAL(20, 8),
    monthly_low DECIMAL(20, 8),
    monthly_volume DECIMAL(20, 8),
    monthly_change_pct DECIMAL(10, 4),
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(symbol, month_start)
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_crypto_prices_symbol_time ON crypto_prices(symbol, open_time);
CREATE INDEX IF NOT EXISTS idx_crypto_statistics_symbol_period ON crypto_statistics(symbol, period_start, period_end);
CREATE INDEX IF NOT EXISTS idx_crypto_weekly_symbol_week ON crypto_weekly_changes(symbol, week_start);
CREATE INDEX IF NOT EXISTS idx_crypto_monthly_symbol_month ON crypto_monthly_analysis(symbol, month_start);
