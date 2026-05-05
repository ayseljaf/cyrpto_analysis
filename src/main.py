from typing import Annotated

from fastapi import APIRouter, FastAPI, HTTPException, Query
from sqlalchemy import text

from src.database import DBSession
from src.schemas import (
    MonthlyStat,
    MonthlyStatResponse,
    OverallStat,
    OverallStatResponse,
    WeeklyChange,
    WeeklyChangeResponse,
)

app = FastAPI(title="Crypto Analysis API", version="1.0.0")


# --- Routers ---

health_router = APIRouter(tags=["health"])
crypto_router = APIRouter(tags=["cryptocurrencies"])
stats_router = APIRouter(prefix="/api", tags=["statistics"])


@health_router.get("/health")
def health_check() -> dict:
    return {"status": "healthy", "service": "fastapi"}


@crypto_router.get("/cryptocurrencies")
def list_cryptocurrencies(db: DBSession) -> list[str]:
    result = db.execute(text("SELECT DISTINCT symbol FROM crypto_prices ORDER BY symbol"))
    return [row[0] for row in result]


@stats_router.get("/monthly-statistics")
def get_monthly_statistics(
    db: DBSession,
    symbol: Annotated[str | None, Query(description="Filter by trading pair symbol")] = None,
    months: Annotated[int, Query(ge=1, le=60, description="Number of months to return")] = 12,
) -> MonthlyStatResponse:
    query = (
        "SELECT symbol, month, average_price, highest_price, lowest_price, price_range"
        " FROM monthly_statistics"
    )
    params: dict = {"limit": months}
    if symbol:
        query += " WHERE symbol = :symbol"
        params["symbol"] = symbol
    query += " ORDER BY month DESC LIMIT :limit"

    rows = db.execute(text(query), params).fetchall()
    if not rows:
        raise HTTPException(status_code=404, detail="No monthly statistics found")

    data = [
        MonthlyStat(
            symbol=r[0], month=r[1], average_price=r[2],
            highest_price=r[3], lowest_price=r[4], price_range=r[5],
        )
        for r in rows
    ]
    return MonthlyStatResponse(data=data, count=len(data))


@stats_router.get("/weekly-changes")
def get_weekly_changes(
    db: DBSession,
    symbol: Annotated[str | None, Query(description="Filter by trading pair symbol")] = None,
    days: Annotated[int, Query(ge=1, le=365, description="Number of days to return")] = 30,
) -> WeeklyChangeResponse:
    query = (
        "SELECT symbol, date, current_price, price_7_days_ago, price_change_pct"
        " FROM weekly_price_changes"
    )
    params: dict = {"limit": days}
    if symbol:
        query += " WHERE symbol = :symbol"
        params["symbol"] = symbol
    query += " ORDER BY date DESC LIMIT :limit"

    rows = db.execute(text(query), params).fetchall()
    if not rows:
        raise HTTPException(status_code=404, detail="No weekly changes found")

    data = [
        WeeklyChange(
            symbol=r[0], date=r[1], current_price=r[2],
            price_7_days_ago=r[3], price_change_pct=r[4],
        )
        for r in rows
    ]
    return WeeklyChangeResponse(data=data, count=len(data))


@stats_router.get("/overall-statistics")
def get_overall_statistics(
    db: DBSession,
    symbol: Annotated[str | None, Query(description="Filter by trading pair symbol")] = None,
) -> OverallStatResponse:
    query = """
        SELECT symbol, record_count, average_price, volatility,
               lowest_price, highest_price, earliest_date, latest_date, calculation_date
        FROM overall_statistics
        WHERE calculation_date = (SELECT MAX(calculation_date) FROM overall_statistics)
    """
    params: dict = {}
    if symbol:
        query += " AND symbol = :symbol"
        params["symbol"] = symbol

    rows = db.execute(text(query), params).fetchall()
    if not rows:
        raise HTTPException(status_code=404, detail="No overall statistics found")

    data = [
        OverallStat(
            symbol=r[0], record_count=r[1], average_price=r[2], volatility=r[3],
            lowest_price=r[4], highest_price=r[5], earliest_date=r[6],
            latest_date=r[7], calculation_date=r[8],
        )
        for r in rows
    ]
    return OverallStatResponse(data=data, count=len(data))


app.include_router(health_router)
app.include_router(crypto_router)
app.include_router(stats_router)
