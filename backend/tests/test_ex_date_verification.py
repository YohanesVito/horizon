import json

import pytest

from work import verify_ex_date_2026 as verification


def test_lppf_2026_temporal_check_fails_release_gate():
    result = verification.report()
    assert result['status'] == 'partial_verification_research_only'
    assert result['model']['training_events'] == 44
    assert result['model']['training_latest_ex_date'] < result['official']['cum_regular']
    assert all(source['retrieved_at'][:10] > result['official']['ex_regular']
               for source in result['snapshot_sources'])
    assert result['observed']['gross_ex_date_pnl_per_share_idr'] == -40
    assert result['observed']['observed_pdr'] == pytest.approx(1.16)
    assert len(result['historical_lppf_crosscheck']) == 4
    assert all(row['issuer_archive_announcement_date'] < row['cum_date']
               for row in result['historical_lppf_crosscheck'])
    assert result['test']['absolute_error_pct_of_cum']['full_dps'] < result['test']['absolute_error_pct_of_cum']['pooled_pdr']
    assert not result['checks']['price_dividend_adjustment_basis_verified']


def test_provider_schedule_conflict_stops_valuation(tmp_path, monkeypatch):
    snapshot = json.loads(verification.CALENDAR.read_text())
    for row in snapshot['result']['dividend']:
        if row['symbol'] == 'LPPF.JK' and row['ex_date'] == '2026-04-24':
            row['dividend_amount'] = 999
    altered = tmp_path / 'calendar.json'
    altered.write_text(json.dumps(snapshot))
    monkeypatch.setattr(verification, 'CALENDAR', altered)
    with pytest.raises(ValueError, match='tidak cocok'):
        verification.report()


def test_issuer_history_conflict_stops_valuation(monkeypatch):
    altered = {date: dict(reference) for date, reference in verification.HISTORICAL_ISSUER_REFERENCE.items()}
    altered['2025-04-22']['dps_idr'] = 1
    monkeypatch.setattr(verification, 'HISTORICAL_ISSUER_REFERENCE', altered)
    with pytest.raises(ValueError, match='historis tidak cocok'):
        verification.report()
