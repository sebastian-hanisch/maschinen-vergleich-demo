"""Die Wegsuche (mvg_machines) an Handbeispielen, mit unabhängigem Abspieler für jede Spur und Randfällen."""

import pytest

import mvg_machines as M
from ref_maschinen import SCHLUESSEL, alle, sortierbar as ref_sortierbar, spiele_ab


def test_handbeispiel_n3_stapel_scheitert_nur_an_231_zwei_warteschlangen_nur_an_321(alle3):
    # Von Hand: 231: die 2 und die 3 liegen vor der 1; im Stapel läge die 3 über der 2 und müsste vor ihr heraus. 321: drei fallende Zahlen brauchen drei Warteschlangen.
    assert {p for p in alle3 if not M.ist_sortierbar("S", p)} == {(2, 3, 1)}
    assert {p for p in alle3 if not M.ist_sortierbar("2Q", p)} == {(3, 2, 1)}
    assert sum(M.ist_sortierbar("S", p) for p in alle3) == 5 == sum(M.ist_sortierbar("2Q", p) for p in alle3)


def test_handbeispiel_n4_die_zehn_zahlen_von_hand():
    # Q nur 1234; S Catalan C(8,4)/5 = 14; 2Q 14; 3Q scheitert nur an 4321 (23); SSs alles (24); SSp scheitert nur an 2341 (23); SQ, QS 14; SpQ alles (24); P 2^3 = 8
    erwartet = {"Q": 1, "S": 14, "2Q": 14, "3Q": 23, "SSs": 24, "SSp": 23, "SQ": 14, "QS": 14, "SpQ": 24, "P": 8}
    assert {k: sum(M.ist_sortierbar(k, p) for p in alle(4)) for k in M.KEYS} == erwartet


def test_handbeispiel_2341_und_4321_scheitern_genau_an_den_von_hand_bestimmten_maschinen():
    assert [k for k in M.KEYS if not M.ist_sortierbar(k, (2, 3, 4, 1))] == ["Q", "S", "SSp", "SQ", "QS", "P"]
    assert [k for k in M.KEYS if not M.ist_sortierbar(k, (4, 3, 2, 1))] == ["Q", "2Q", "3Q"]


def test_handbeispiel_zwei_stapel_in_serie_sortieren_2341():
    # Von Hand: 2, 3, 4, 1 in Stapel A; 1 nach B und ausgeben; 4, 3, 2 nach B (B von oben 2, 3, 4), ausgeben: 1, 2, 3, 4.
    r = M.pruefe("SSs", (2, 3, 4, 1), spur=True)
    assert r.sortierbar
    assert spiele_ab("SSs", (2, 3, 4, 1), r.schritte) == (True, "")


def test_handbeispiel_n7_kuerzeste_unsortierbare_folge_fuer_zwei_stapel_in_serie():
    # 2435761 hat die längste fallende Teilfolge 3 (4, 3, 1): drei Warteschlangen sortieren sie; zwei Stapel in Serie nicht (die kürzeste solche Folge).
    # 4321567 hat die längste fallende Teilfolge 4: drei Warteschlangen scheitern, zwei Stapel in Serie nicht.
    assert M.ist_sortierbar("3Q", (2, 4, 3, 5, 7, 6, 1)) and not M.ist_sortierbar("SSs", (2, 4, 3, 5, 7, 6, 1))
    assert M.ist_sortierbar("SSs", (4, 3, 2, 1, 5, 6, 7)) and not M.ist_sortierbar("3Q", (4, 3, 2, 1, 5, 6, 7))


@pytest.mark.parametrize("key", SCHLUESSEL)
def test_jede_spur_wird_vom_unabhaengigen_abspieler_nachvollzogen(key):
    for n in (3, 4, 5):
        for p in alle(n):
            r = M.pruefe(key, p, spur=True)
            if r.sortierbar:
                ok, grund = spiele_ab(key, p, r.schritte)
                assert ok, (key, p, grund)
            else:
                assert r.schritte is None


@pytest.mark.parametrize("key", SCHLUESSEL)
def test_wegsuche_gleich_unabhaengiger_wegsuche_bis_n5(key):
    for n in range(1, 6):
        for p in alle(n):
            assert M.ist_sortierbar(key, p) == ref_sortierbar(key, p), (key, p)


@pytest.mark.parametrize("key", SCHLUESSEL)
def test_abkuerzungen_veraendern_die_menge_nicht_roh_gegen_gierig_n5(key):
    for n in range(1, 6):
        for p in alle(n):
            assert M.pruefe(key, p, gierig=False, senken=False).sortierbar == M.ist_sortierbar(key, p), (key, p)


def test_die_roh_suche_verwirft_nichts_und_untersucht_mehr_zustaende():
    # Zweig-Test: die Abkürzungen greifen wirklich (sonst wären sie toter Code).
    p = (3, 1, 4, 2, 5)
    assert M.pruefe("SSs", p, gierig=False, senken=False).zustaende > M.pruefe("SSs", p).zustaende


def test_zufallsfolgen_n9_n10_spuren_stimmen_und_nein_heisst_nein():
    from mvg_rng import SplitMix64

    rng = SplitMix64(4242)
    for _ in range(12):
        n = 9 + rng.below(2)
        p = list(range(1, n + 1))
        rng.shuffle(p)
        p = tuple(p)
        for key in ("S", "2Q", "3Q", "SSp", "SpQ", "P"):
            r = M.pruefe(key, p, spur=True)
            if r.sortierbar:
                assert spiele_ab(key, p, r.schritte)[0]
            else:
                assert not ref_sortierbar(key, p)


def test_abspielen_lehnt_unzulaessige_schritte_ab():
    with pytest.raises(ValueError):
        M.abspielen("S", [("ein", 2, 0), ("aus", 1, 0)])  # die 1 liegt nicht an der Spitze
    with pytest.raises(ValueError):
        M.abspielen("Q", [("um", 1, 0, 1)])  # Q hat keine Umsetzung
    with pytest.raises(ValueError):
        M.abspielen("S", [("ein", 1, 1)])  # Behälter 1 gibt es nicht im Eingang


# ---------------------------------------------------------------- Randfälle
def test_leere_folge_und_n1_n2():
    assert all(M.ist_sortierbar(k, ()) for k in M.KEYS)
    assert all(M.ist_sortierbar(k, (1,)) for k in M.KEYS)
    assert [k for k in M.KEYS if not M.ist_sortierbar(k, (2, 1))] == ["Q"]  # n = 2: nur eine Warteschlange sortiert 21 nicht


def test_aufzaehlung_n1_n2_n3():
    assert [len(M.sortierbare("Q", n)) for n in (1, 2, 3)] == [1, 1, 1]
    assert [len(M.sortierbare("S", n)) for n in (1, 2, 3)] == [1, 2, 5]
    assert M.sortierbare("2Q", 3) == [p for p in alle(3) if p != (3, 2, 1)]


def test_pop_stack_n_gleich_2_hoch_n_minus_1_und_beispielfolge():
    assert [len(M.sortierbare("P", n)) for n in range(1, 7)] == [1, 2, 4, 8, 16, 32]
    assert M.ist_sortierbar("P", (2, 1, 3)) and not M.ist_sortierbar("P", (2, 3, 1))


def test_inverse_ist_selbstinvers():
    for p in alle(4):
        assert M.inverse(M.inverse(p)) == p
