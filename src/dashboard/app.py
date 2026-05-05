import dash
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import dcc, html
from dash.dependencies import Input, Output

from db import get_engine

app = dash.Dash(__name__)


def load_all_data_from_db():
    engine = get_engine()
    with engine.connect() as conn:
        monthly_stats = pd.read_sql(
            """
            SELECT symbol, month, average_price, highest_price, lowest_price, price_range
            FROM monthly_statistics
            ORDER BY symbol, month DESC
            """,
            conn,
        )
        monthly_stats["month"] = pd.to_datetime(monthly_stats["month"])

        overall_stats = pd.read_sql(
            """
            SELECT symbol, record_count AS count, average_price,
                   volatility, lowest_price, highest_price
            FROM overall_statistics
            WHERE calculation_date = (SELECT MAX(calculation_date) FROM overall_statistics)
            """,
            conn,
        )

        weekly_changes = pd.read_sql(
            """
            SELECT symbol, date, current_price, price_7_days_ago, price_change_pct
            FROM weekly_price_changes
            ORDER BY symbol, date DESC
            """,
            conn,
        )
        weekly_changes["date"] = pd.to_datetime(weekly_changes["date"])

        latest_prices = pd.read_sql(
            """
            SELECT symbol, last_price, last_event_time, updated_at
            FROM latest_prices
            ORDER BY symbol
            """,
            conn,
        )

    return monthly_stats, overall_stats, weekly_changes, latest_prices


CRYPTO_OPTIONS = [
    {"label": "Bitcoin (BTC)", "value": "BTCUSDT"},
    {"label": "Ethereum (ETH)", "value": "ETHUSDT"},
    {"label": "Solana (SOL)", "value": "SOLUSDT"},
    {"label": "Cardano (ADA)", "value": "ADAUSDT"},
    {"label": "Dogecoin (DOGE)", "value": "DOGEUSDT"},
    {"label": "Shiba Inu (SHIB)", "value": "SHIBUSDT"},
    {"label": "USDC", "value": "USDCUSDT"},
]

app.layout = html.Div(
    [
        dcc.Interval(
            id="interval-component",
            interval=5 * 1000,
            n_intervals=0,
        ),
        html.H1(
            "Cryptocurrency Analysis Dashboard",
            style={"textAlign": "center", "color": "#2c3e50", "marginBottom": 30},
        ),
        html.Div(
            [
                html.H2("Real-Time Latest Prices", style={"color": "#34495e", "marginBottom": 20}),
                dcc.Graph(id="latest-prices-table"),
            ]
        ),
        html.Div(
            [
                html.H2("Monthly Price Statistics", style={"color": "#34495e", "marginBottom": 20}),
                dcc.Dropdown(
                    id="crypto-selector",
                    options=CRYPTO_OPTIONS,
                    value="BTCUSDT",
                    style={"marginBottom": 20},
                ),
                dcc.Graph(id="monthly-price-trends"),
            ]
        ),
        html.Div(
            [
                html.H2("Overall Statistics", style={"color": "#34495e", "marginBottom": 20}),
                dcc.Graph(id="overall-stats-table"),
            ]
        ),
        html.Div(
            [
                html.H2("Weekly Price Changes", style={"color": "#34495e", "marginBottom": 20}),
                dcc.Graph(id="weekly-changes-chart"),
            ]
        ),
        html.Div(
            [
                html.H2("Monthly Price Ranges", style={"color": "#34495e", "marginBottom": 20}),
                dcc.Graph(id="price-range-chart"),
            ]
        ),
    ],
    style={"padding": "20px"},
)


@app.callback(
    [
        Output("monthly-price-trends", "figure"),
        Output("overall-stats-table", "figure"),
        Output("weekly-changes-chart", "figure"),
        Output("price-range-chart", "figure"),
        Output("latest-prices-table", "figure"),
    ],
    [
        Input("crypto-selector", "value"),
        Input("interval-component", "n_intervals"),
    ],
)
def update_graphs(selected_crypto, n_intervals):
    monthly_stats, overall_stats, weekly_changes, latest_prices = load_all_data_from_db()

    monthly_fig = px.line(
        monthly_stats[monthly_stats["symbol"] == selected_crypto],
        x="month",
        y=["average_price", "highest_price", "lowest_price"],
        title=f"Monthly Price Trends for {selected_crypto}",
        labels={"value": "Price (USDT)", "month": "Month"},
        template="plotly_white",
    )

    stats_fig = go.Figure(
        data=[
            go.Table(
                header=dict(
                    values=list(overall_stats.columns),
                    fill_color="#34495e",
                    align="left",
                    font=dict(color="white", size=12),
                ),
                cells=dict(
                    values=[overall_stats[col] for col in overall_stats.columns],
                    fill_color="lavender",
                    align="left",
                ),
            )
        ]
    )
    stats_fig.update_layout(title="Overall Statistics for All Cryptocurrencies")

    weekly_fig = px.line(
        weekly_changes[weekly_changes["symbol"] == selected_crypto].head(12),
        x="date",
        y="price_change_pct",
        title=f"Weekly Price Changes for {selected_crypto}",
        labels={"price_change_pct": "Price Change (%)", "date": "Date"},
        template="plotly_white",
    )
    weekly_fig.add_hline(y=0, line_dash="dash", line_color="gray")

    range_data = monthly_stats[monthly_stats["symbol"] == selected_crypto].head(12)
    range_fig = go.Figure()
    range_fig.add_trace(
        go.Bar(x=range_data["month"], y=range_data["price_range"], marker_color="#3498db")
    )
    range_fig.update_layout(
        title=f"Monthly Price Ranges for {selected_crypto}",
        xaxis_title="Month",
        yaxis_title="Price Range (USDT)",
        template="plotly_white",
    )

    if latest_prices.empty:
        latest_fig = go.Figure()
        latest_fig.update_layout(
            title="Real-Time Latest Prices (waiting for stream data)",
            template="plotly_white",
        )
    else:
        latest_fig = go.Figure(
            data=[
                go.Table(
                    header=dict(
                        values=["symbol", "last_price", "last_event_time", "updated_at"],
                        fill_color="#34495e",
                        align="left",
                        font=dict(color="white", size=12),
                    ),
                    cells=dict(
                        values=[
                            latest_prices["symbol"],
                            latest_prices["last_price"],
                            latest_prices["last_event_time"],
                            latest_prices["updated_at"],
                        ],
                        fill_color="lavender",
                        align="left",
                    ),
                )
            ]
        )
        latest_fig.update_layout(title="Real-Time Latest Prices")

    return monthly_fig, stats_fig, weekly_fig, range_fig, latest_fig


if __name__ == "__main__":
    app.run_server(debug=False, host="0.0.0.0", port=8050)
