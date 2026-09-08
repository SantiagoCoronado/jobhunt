"""config/geo.yaml + src/geo.py: where a location string points, relative to a scope of regions.

The first table is the calibrated behaviour the tailor build carried when the relocation scope
was hardcoded to the US, Mexico and Canada (docs/spec-open-source.md decision 7 moved the
tables into geo.yaml and the scope into the profile); it must not regress.
"""
from __future__ import annotations

import pytest

from src import geo

TN = {"united states", "canada", "mexico"}


@pytest.mark.parametrize("location,expected", [
    ("Berlin", True), ("London, GB", True), ("Singapore", True), ("Remote, EU", True), ("Bangalore, India", True),
    ("Bengaluru, Karnataka, in", True), ("Berlin, DE", True), ("Tel Aviv, IL", True), ("Berlin, Germany", True),
    ("Indianapolis, IN, USA", False), ("Ukiah, CA", False), ("Paris, TX", False), ("New Madrid, MO", False),
    ("London, KY", False), ("London, UK; San Francisco, CA", False), ("Remote (US) or London", False),
    ("Santa Clara, CA", False), ("Mexico City", False), ("Toronto, Canada", False), ("Remote", False), ("", False),
    (None, False), ("US remote", False),
    # A US option anywhere in a multi-region string keeps the row inside, including the
    # spelled-out state names and the bare "US".
    ("Austin, Texas; London, England, United Kingdom; New York, New York", False),
    ("NY / SF / EMEA", False), ("Remote (US/EU)", False), ("Remote - US or Europe", False),
    ("Remote, APAC; Remote, EMEA; Remote, US", False), ("US, UK, Singapore, Remote", False),
    ("Europe + San Francisco", False), ("Hybrid - San Francisco, New York City, London", False),
    # LATAM contains Mexico, so it is inside a scope that holds Mexico, not "outside".
    ("LATAM remote-first", False), ("Remote LATAM", False), ("LATAM (remote)", False),
    # ... but a foreign-only multi-part string is still outside.
    ("Berlin; Munich", True), ("London; Dublin; Amsterdam", True),
    # a bare US state code is the US unless geo.yaml lists it as meaning a country (DE, IN ...)
    ("London / CA", False), ("Remote / CO / AR", False), ("Berlin / DE", True),
])
def test_outside_the_tn_scope_matches_the_calibrated_table(location, expected):
    assert geo.outside(location, TN) is expected


@pytest.mark.parametrize("location,expected", [
    ("Berlin", False), ("London", False), ("Zurich", False), ("Remote (EU)", False), ("Lisbon, PT", False),
    ("Remote", False), ("San Francisco, CA", True), ("Dubai", True), ("Singapore", True), ("Mexico City", True),
    ("Remote, EMEA", False),                 # EMEA contains Europe: reachable
    ("Berlin; New York, NY", False),         # a European option exists
])
def test_outside_a_european_scope(location, expected):
    assert geo.outside(location, {"europe"}) is expected


@pytest.mark.parametrize("location,regions", [
    ("Tijuana, Baja California", {"mexico"}), ("Baja California", {"mexico"}),
    ("La Paz, Baja California Sur", {"mexico"}), ("Mexicali, Baja California", {"mexico"}),
    ("San Francisco del Rincon, Guanajuato", {"mexico"}),
    ("Memphis, Tennessee", {"united states"}), ("Washington, DC", {"united states"}),
    ("Bogota, CO", {"colombia"}), ("Arvada, CO", {"united states"}), ("Toronto, CA", {"canada"}),
    ("Ukiah, CA", {"united states"}), ("Buenos Aires, AR", {"argentina"}), ("Montevideo (Hybrid)", {"uruguay"}),
    # the other direction (second review): an explicit US state code or a longer US state name
    # outranks a Mexican state name
    ("Santa Fe, New Mexico", {"united states"}), ("Durango, CO", {"united states"}),
    ("Sonora, CA", {"united states"}), ("Hidalgo, TX", {"united states"}), ("Durango", {"mexico"}),
    ("Colima, Mexico", {"mexico"}),
])
def test_state_names_and_americas_codes(location, regions):
    """PR #22 review: a US state name decides only when no region word does ("Baja
    California" is Mexico), and the Americas carry country codes like Europe does."""
    assert geo.hits(location) == regions
    assert geo.outside(location, TN) is (regions == {"colombia"} or regions == {"argentina"} or regions == {"uruguay"})


def test_hits_name_the_regions_a_part_resolves_to():
    assert geo.hits("Bengaluru, Karnataka, in") == {"india"}
    assert geo.hits("Paris, TX") == {"united states"}
    assert geo.hits("Europe + San Francisco") == {"europe", "united states"}
    assert geo.hits("Remote") == set() and geo.hits("") == set()
    assert geo.hits("NY") == {"united states"}
    assert geo.hits("CA") == {"united states"} and geo.hits("CO") == {"united states"}
    assert geo.hits("DE") == set()            # a bare code geo.yaml lists as meaning a country decides nothing
    assert "_bare_country_codes" not in geo.regions()


def test_empty_scope_never_marks_anything_outside():
    assert geo.outside("Berlin", set()) is False
    assert geo.outside("Berlin", []) is False


def test_closure_and_containment():
    assert geo.closure("mexico") == {"mexico", "latam", "north america", "americas"}
    assert "portugal" in geo.contained("eu") and "united kingdom" not in geo.contained("eu")
    assert "united kingdom" in geo.contained("europe")
    with pytest.raises(ValueError, match="no region 'narnia'"):
        geo.closure("narnia")


def test_home_from_header_location_then_locations():
    assert geo.home({"header_location": "Mexico City, Mexico"}) == {"mexico"}
    assert geo.home({"header_location": "Lisbon, Portugal"}) == {"portugal"}
    assert geo.home({"header_location": "", "locations": ["Remote (worldwide)", "Hybrid Lisbon"]}) == {"portugal"}
    assert geo.home({"header_location": "Remote"}) == set()


def test_home_and_locked_out_words_split_the_world():
    home = {"portugal"}
    ok = set(geo.home_words(home))
    locked = set(geo.locked_out_words(home))
    assert {"portugal", "lisbon", "eu", "europe", "emea", "remote", "anywhere"} <= ok
    assert {"san francisco", "united states", "berlin", "india", "mexico", "california"} <= locked
    assert not ok & locked
    assert "berlin" in geo.locked_out_words({"portugal"})      # a sibling country's city is locked
    assert "germany" in geo.locked_out_words({"portugal"})


def test_every_within_points_at_a_known_region_and_the_us_carries_states():
    t = geo.table()
    for name, block in t.items():
        for parent in block["within"]:
            assert parent in t, f"{name} within {parent}"
    assert "tx" in t["united states"]["state_codes"] and "texas" in t["united states"]["state_names"]


def test_cli_prints_hits_and_scope_verdict(capsys):
    assert geo.main(["London, UK; San Francisco, CA", "--scope", "Europe"]) == 0   # case-insensitive
    out = capsys.readouterr().out
    assert "'london, uk': united kingdom" in out and "'san francisco, ca': united states" in out
    assert "outside ['europe']: False" in out
    assert geo.main(["Berlin", "--scope", "Europ"]) == 1
    assert "unknown region(s): europ" in capsys.readouterr().out


def test_us_home_keeps_santa_fe_and_locks_out_mexican_states():
    assert geo.outside("Santa Fe, New Mexico", {"united states"}) is False
    ok = set(geo.home_words({"united states"}))
    assert "new mexico" in ok and "baja california" in set(geo.locked_out_words({"united states"}))
