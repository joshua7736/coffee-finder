from coffee_finder import main as cf_main


def test_main_cli_with_latlng(monkeypatch, capsys):
    sample = [{"name": "My Coffee", "lat": 1.0, "lng": 2.0, "distance_m": 123, "address": "123 St", "rating": 4.5}]

    def fake_choose(lat, lng, radius=1000, limit=10, min_rating=None):
        return sample

    monkeypatch.setattr(cf_main, "choose_provider", fake_choose)
    # call main with args
    cf_main.main(["--latlng", "1.0,2.0", "--limit", "1"]) 
    captured = capsys.readouterr()
    assert "Found 1 places" in captured.out or "Found 1 place" in captured.out
    assert "My Coffee" in captured.out
