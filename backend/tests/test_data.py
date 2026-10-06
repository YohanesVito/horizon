from backend.data import Dataset


def test_replay_eligibility_excludes_incomplete_and_other_windows():
    d = Dataset()
    eligible = [e for e in d.events.values() if e['replay_available']]
    assert len(eligible) == 5
    assert not d.events['BBCA:2025-12-03']['replay_available']
    assert all(e['declaration_date'] is None for e in eligible)
    assert all(e['cum_date'] < e['ex_date'] <= e['payment_date'] for e in eligible)


def test_conflicting_schedule_stays_quarantined_on_reimport():
    d = Dataset()
    old = d.events['BBCA:2025-03-21']
    row = {'symbol': 'BBCA', 'ex_date': old['ex_date'], 'cum_date': old['cum_date'],
           'dividend_amount': old['dps'], 'recording_date': old['recording_date'], 'payment_date': '2025-04-12'}
    d.add_event(row, 'synthetic-conflict-test')
    assert d.events[old['id']]['quality'] == 'conflict'
    row['payment_date'] = old['payment_date']
    d.add_event(row, 'synthetic-conflict-test')
    assert not d.events[old['id']]['replay_available']
