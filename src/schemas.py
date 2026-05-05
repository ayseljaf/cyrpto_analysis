from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel


class MonthlyStat(BaseModel):
    symbol: str
    month: date
    average_price: Decimal
    highest_price: Decimal
    lowest_price: Decimal
    price_range: Decimal


class WeeklyChange(BaseModel):
    symbol: str
    date: date
    current_price: Decimal
    price_7_days_ago: Decimal | None
    price_change_pct: Decimal | None


class OverallStat(BaseModel):
    symbol: str
    record_count: int
    average_price: Decimal
    volatility: Decimal | None
    lowest_price: Decimal
    highest_price: Decimal
    earliest_date: datetime | None
    latest_date: datetime | None
    calculation_date: date


class MonthlyStatResponse(BaseModel):
    data: list[MonthlyStat]
    count: int


class WeeklyChangeResponse(BaseModel):
    data: list[WeeklyChange]
    count: int


class OverallStatResponse(BaseModel):
    data: list[OverallStat]
    count: int
