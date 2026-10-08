from copy import deepcopy

import pytest

from backend.ex_date_forecast import observations
from backend.intelligence import IntelligenceDataset
from work import audit_ex_date_f02c as audit


def test_frozen_cohort_gates_and_source_revision_are_explicit():
    result = audit.report()
    assert result['dataset_version'] == audit.EXPECTED_DATASET
    assert (result['source_events'], result['eligible_events']) == (48, 44)
    assert result['official_dividend_gate_counts'] == {
        'pass_notice_before_cum': 3, 'revision_unresolved': 1, 'unknown': 44,
    }
    by_id = {row['event_id']: row for row in result['event_audit']}
    initial = by_id['LPPF:2022-04-14']
    assert initial['gates']['official_dividend'] == 'revision_unresolved'
    assert initial['official_reference']['payment'] == '2022-05-06'
    assert initial['payment_date'] == '2022-04-28'
    assert all(row['gates']['price_basis'] == 'unknown' for row in result['event_audit'])
    assert all(row['gates']['point_in_time'] == 'unknown' for row in result['event_audit'])
    assert not result['lppf_2026']['external_close_display']['provider_lineage_known']
    assert len({row['event_id'] for row in result['event_audit']}) == 48


def test_issuer_comparison_uses_only_prior_year_labels():
    result = audit.report()
    evaluated = result['comparison']['evaluated']
    assert len(evaluated) == 36
    assert [fold['training_n'] for fold in result['comparison']['folds']] == [8, 20, 32]
    assert all(row['training_latest_ex_date'] < row['cum_date'] for row in evaluated)
    assert all(row['issuer_training_n'] <= row['training_n'] for row in evaluated)
    assert sum(result['comparison']['metrics']['wins_vs_full_dps']['issuer_shrunk'].values()) == 36
    lppf = result['lppf_2026']
    assert lppf['training_n'] == 44
    assert lppf['training_latest_ex_date'] < lppf['cum_date']
    assert lppf['issuer_training_n'] == 4
    assert lppf['absolute_error_pct_of_cum']['full_dps'] < lppf['absolute_error_pct_of_cum']['issuer_shrunk']


def test_issuer_shrinkage_does_not_read_future_labels():
    rows, _ = observations(IntelligenceDataset().events)
    target = next(row for row in rows if row['event_id'] == 'LPPF:2024-04-22')
    earlier = [row for row in rows if row['ex_date'] < '2024-01-01']
    later = [row for row in rows if row['ex_date'] >= '2025-01-01']
    baseline = audit._predictions(target, earlier)
    assert baseline is not None
    mutated = deepcopy(later)
    for row in mutated:
        row['observed_pdr'] = 10000
    assert audit._predictions(target, earlier + mutated) == baseline


def test_primary_notice_conflict_fails_official_gate(monkeypatch):
    refs = deepcopy(audit.PRIMARY_LPPF)
    refs['LPPF:2024-04-22']['dps'] = 999
    monkeypatch.setattr(audit, 'PRIMARY_LPPF', refs)
    rows, _ = observations(IntelligenceDataset().events)
    audited = audit.audit_events(IntelligenceDataset(), rows)
    by_id = {row['event_id']: row for row in audited}
    assert by_id['LPPF:2024-04-22']['gates']['official_dividend'] == 'conflict'


def test_frozen_dataset_digest_detects_mutation(monkeypatch):
    monkeypatch.setattr(audit, 'EXPECTED_DATASET', 'invalid')
    with pytest.raises(ValueError, match='Digest kohort berubah'):
        audit.report()


def test_external_display_mismatch_is_not_recorded_as_match(monkeypatch):
    altered = {**audit.EXTERNAL_LPPF_2026, 'ex_close': 999}
    monkeypatch.setattr(audit, 'EXTERNAL_LPPF_2026', altered)
    assert audit.report()['lppf_2026']['external_close_display']['status'] == 'conflict'
