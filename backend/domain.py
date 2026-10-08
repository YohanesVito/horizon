from datetime import date
from decimal import Decimal
from typing import Literal
from pydantic import BaseModel, Field, model_validator


class SimulationRequest(BaseModel):
    timing_mode: Literal['payment_plus_2'] = 'payment_plus_2'
    capital: Decimal = Field(default=Decimal('100000000'), gt=0, le=Decimal('1000000000000'))
    event_ids: list[str] = Field(min_length=1, max_length=10)
    allocation: Literal['single'] = 'single'
    entry_sessions_before_cum: int = Field(default=5, ge=0, le=10)
    exit_rule: Literal['ex_close', 'payment_close', 'price_bep', 'holding_period'] = 'price_bep'
    max_holding_sessions: int = Field(default=20, ge=1, le=60)
    end_date: date = date(2025, 5, 20)
    start_date: date | None = None
    compare: Literal[False] = False

    @model_validator(mode='after')
    def validate_unique(self):
        if len(set(self.event_ids)) != len(self.event_ids):
            raise ValueError('Event yang sama tidak boleh dipilih dua kali.')
        if not self.capital.is_finite():
            raise ValueError('Modal harus berupa angka valid.')
        return self


class WatchlistRequest(BaseModel):
    symbol: str = Field(pattern=r'^[A-Z]{4}$')


class ScreenRules(BaseModel):
    name: str = Field(default='Logika dividen saya', min_length=1, max_length=80)
    minimum_yield: float = Field(default=0, ge=0, le=100)
    minimum_frequency: int = Field(default=0, ge=0, le=12)
    require_replay: bool = False
    sort_by: Literal['yield', 'frequency', 'symbol'] = 'yield'


class FinancialLogic(BaseModel):
    name: str = Field(default='Return dan risiko tim', min_length=1, max_length=80)
    entry_offset: Literal[0, 5, 10] = 5
    horizon: Literal[5, 10, 20] = 20
    objective: Literal['return', 'worst_return', 'risk', 'recovery'] = 'return'
    minimum_samples: int = Field(default=3, ge=1, le=100)
    maximum_loss_upper_pct: float = Field(default=100, ge=0, le=100)
    minimum_median_return_pct: float = Field(default=-100, ge=-100, le=1000)


class ScenarioRequest(BaseModel):
    symbol: str = Field(pattern=r'^[A-Z]{4}$')
    capital: Decimal = Field(default=Decimal('100000000'), gt=0, le=Decimal('1000000000000'))
    entry_price: Decimal = Field(gt=0, le=Decimal('10000000'))
    dps: Decimal = Field(ge=0, le=Decimal('10000000'))
    entry_date: date
    cum_date: date
    ex_date: date
    recording_date: date
    payment_date: date
    valuation_date: date
    entry_offset: Literal[0, 5, 10] = 5
    horizon: Literal[5, 10, 20] = 20

    @model_validator(mode='after')
    def validate_dates(self):
        if not self.entry_date <= self.cum_date < self.ex_date <= self.recording_date <= self.payment_date:
            raise ValueError('Urutan tanggal harus entry ≤ cum < ex ≤ recording ≤ payment.')
        if self.valuation_date < self.ex_date:
            raise ValueError('Tanggal valuasi harus pada/setelah ex-date.')
        if not all(v.is_finite() for v in (self.capital, self.entry_price, self.dps)):
            raise ValueError('Input nominal harus finite.')
        return self


class RotationRequest(BaseModel):
    capital: Decimal = Field(default=Decimal('100000000'), gt=0, le=Decimal('1000000000000'))
    start_date: date = date(2025, 3, 1)
    end_date: date = date(2025, 6, 30)
    symbols: list[str] = Field(default_factory=lambda: ['BBCA', 'BBRI', 'BMRI', 'BBNI', 'DMAS', 'LPPF', 'ADRO', 'CFIN', 'RALS'], min_length=1, max_length=9)
    rules: FinancialLogic = Field(default_factory=FinancialLogic)
    exit_rule: Literal['ex_close', 'payment_close', 'price_bep', 'holding_period'] = 'price_bep'
    max_holding_sessions: int = Field(default=20, ge=1, le=60)
    max_events: int = Field(default=5, ge=1, le=10)
    allow_calendar_assumption: bool = True

    @model_validator(mode='after')
    def validate_period(self):
        if not date(2025, 1, 1) <= self.start_date < self.end_date <= date(2025, 12, 31):
            raise ValueError('Rencana historis mendukung awal < akhir dalam tahun 2025.')
        if len(set(self.symbols)) != len(self.symbols):
            raise ValueError('Emiten tidak boleh duplikat.')
        return self
