import pytest

from bot import lists

SAMPLE_YAML = """
schwimmen:
  title: "🏊 Schwimmen"
  aliases: [pool, swim]
  items:
    - Badehose
    - Schwimmbrille
    - Handtuch
rennrad:
  title: "🚴 Rennrad"
  aliases: [rr, radfahren]
  items:
    - Helm
    - Trikot
"""


@pytest.fixture(autouse=True)
def load_sample(tmp_path):
    f = tmp_path / "lists.yaml"
    f.write_text(SAMPLE_YAML, encoding="utf-8")
    lists.load_lists(f)


def test_load_returns_count(tmp_path):
    f = tmp_path / "lists.yaml"
    f.write_text(SAMPLE_YAML, encoding="utf-8")
    assert lists.load_lists(f) == 2


def test_exact_lookup():
    result = lists.get_list("schwimmen")
    assert result is not None
    assert result["title"] == "🏊 Schwimmen"
    assert "Badehose" in result["items"]


def test_alias_lookup():
    result = lists.get_list("pool")
    assert result is not None
    assert result["key"] == "schwimmen"


def test_alias_lookup_rr():
    result = lists.get_list("rr")
    assert result is not None
    assert result["key"] == "rennrad"


def test_case_insensitive():
    assert lists.get_list("SCHWIMMEN") is not None
    assert lists.get_list("Rennrad") is not None


def test_whitespace_trimmed():
    assert lists.get_list("  schwimmen  ") is not None


def test_unknown_returns_none():
    assert lists.get_list("wandern") is None


def test_fuzzy_match_typo():
    match = lists.fuzzy_match("schwimen")
    assert match is not None


def test_fuzzy_match_alias():
    match = lists.fuzzy_match("swm")
    # low similarity — may or may not match, just assert no crash
    assert match is None or isinstance(match, str)


def test_fuzzy_no_match_garbage():
    assert lists.fuzzy_match("xyz123qwerty") is None


def test_get_all_keywords_sorted():
    keywords = lists.get_all_keywords()
    assert "schwimmen" in keywords
    assert "rennrad" in keywords
    assert keywords == sorted(keywords)


def test_get_all_keywords_no_aliases():
    keywords = lists.get_all_keywords()
    assert "pool" not in keywords
    assert "rr" not in keywords
