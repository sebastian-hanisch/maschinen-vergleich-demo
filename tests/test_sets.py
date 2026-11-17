"""Mengen als Bitmasken (mvg_sets): Ränge, Vergleich, Paarstatistik, Fingerabdrücke und Ordnung an handgesetzten Werten und gegen die eigene Referenz."""

from math import factorial

import pytest

import mvg_sets as S
from mvg_machines import KEYS
from ref_maschinen import alle, sortierbar as ref_sortierbar


def test_rang_ist_der_index_in_der_lexikographischen_reihenfolge():
    for n in range(1, 6):
        assert [S.rang(p) for p in S.folgen(n)] == list(range(factorial(n)))


def test_mitglieder_liefert_die_kleinsten_folgen_zuerst_und_begrenzt():
    m = S.maske([(2, 1, 3), (1, 3, 2), (3, 2, 1)])
    assert S.mitglieder(m, 3) == [(1, 3, 2), (2, 1, 3), (3, 2, 1)]
    assert S.mitglieder(m, 3, 2) == [(1, 3, 2), (2, 1, 3)]
    assert S.zaehle(m) == 3 and S.mitglieder(0, 3) == []


def test_ist_mitglied_gleich_der_bitverschiebung():
    for key in ("S", "SSp"):
        m = S.menge(key, 5)
        assert all(S.ist_mitglied(key, 5, r) == bool((m >> r) & 1) for r in range(120))


def test_handbeispiel_n3_stapel_gegen_zwei_warteschlangen():
    v = S.vergleich("S", "2Q", 3)
    assert (v["nur_a"], v["beide"], v["nur_b"], v["beziehung"]) == (1, 4, 1, "unvergleichbar")
    assert v["zeugen_a"] == [(3, 2, 1)] and v["zeugen_b"] == [(2, 3, 1)]


@pytest.mark.parametrize("n, erwartet", [(4, (1, 22, 1)), (5, (17, 86, 17)), (6, (171, 342, 171)), (7, (1395, 1365, 1396))])
def test_ssp_gegen_3q_nur_ssp_gemeinsam_nur_3q(n, erwartet):
    v = S.vergleich("SSp", "3Q", n)
    assert (v["nur_a"], v["beide"], v["nur_b"]) == erwartet
    assert S.zahl("SSp", n) == v["nur_a"] + v["beide"] and S.zahl("3Q", n) == v["nur_b"] + v["beide"]


def test_n4_zeugen_ssp_gegen_3q_sind_4321_und_2341():
    v = S.vergleich("SSp", "3Q", 4)
    assert v["zeugen_a"] == [(4, 3, 2, 1)] and v["zeugen_b"] == [(2, 3, 4, 1)]


def test_s_gegen_2q_bei_n8_1302_128_1302():
    v = S.vergleich("S", "2Q", 8)
    assert (v["nur_a"], v["beide"], v["nur_b"]) == (1302, 128, 1302)


@pytest.mark.parametrize("n, erwartet", [(3, (6, 3)), (4, (7, 4)), (5, (7, 4)), (6, (7, 4)), (7, (6, 3)), (8, (6, 3))])
def test_paare_mit_gleicher_zahl_unter_n_fakultaet_und_davon_verschiedene_menge(n, erwartet):
    gl = S.paare_gleiche_zahl(n)
    assert (len(gl), sum(1 for _, _, gleich in gl if not gleich)) == erwartet


def test_paare_bei_n_kleiner_3_alle_zahlen_gleich_n_fakultaet():
    assert S.paare_gleiche_zahl(1) == [] and S.paare_gleiche_zahl(2) == []


@pytest.mark.parametrize("n, erwartet", [(3, (4, 5)), (4, (5, 7)), (5, (6, 8)), (6, (6, 8)), (7, (7, 8)), (8, (7, 8))])
def test_zaehlfolgen_und_mengen(n, erwartet):
    assert S.zaehlfolgen_und_mengen(n) == erwartet


def test_zahl_trennt_s_und_2q_nie_die_menge_ab_n3():
    assert S.erstes_n_zahl_trennt("S", "2Q") is None and S.erstes_n_menge_trennt("S", "2Q") == 3
    assert S.erstes_n_zahl_trennt("3Q", "SSp") == 7 and S.erstes_n_menge_trennt("3Q", "SSp") == 4
    assert S.erstes_n_menge_trennt("S", "SQ") is None


def test_ordnung_bei_n8_acht_klassen_neun_kanten_zehn_unvergleichbare_paare():
    o = S.ordnung(8)
    assert o["klassen"] == [["Q"], ["S", "SQ", "QS"], ["2Q"], ["3Q"], ["SSs"], ["SSp"], ["SpQ"], ["P"]]
    assert o["kanten"] == sorted([("Q", "2Q"), ("Q", "P"), ("P", "S"), ("S", "SSp"), ("S", "SpQ"), ("SSp", "SSs"), ("2Q", "3Q"), ("2Q", "SSs"), ("2Q", "SpQ")])
    assert o["unvergleichbar"] == [("S", "2Q"), ("S", "3Q"), ("2Q", "SSp"), ("2Q", "P"), ("3Q", "SSs"), ("3Q", "SSp"), ("3Q", "SpQ"), ("3Q", "P"),
                                   ("SSs", "SpQ"), ("SSp", "SpQ")]


def test_ordnung_zeugen_ssp_nicht_in_spq_und_3q_gegen_sss():
    v = S.vergleich("SSp", "SpQ", 8)
    assert v["beziehung"] == "unvergleichbar" and (v["nur_a"], v["beide"], v["nur_b"]) == (3758, 11983, 15430)
    v = S.vergleich("3Q", "SSs", 8)
    assert (v["nur_a"], v["beide"], v["nur_b"]) == (406, 15361, 24013)


def test_ordnung_inklusionen_gelten_fuer_alle_n_von_1_bis_8():
    for a, b in (("Q", "S"), ("Q", "2Q"), ("2Q", "3Q"), ("S", "SSp"), ("S", "SSs"), ("S", "SpQ"), ("P", "S"), ("SSp", "SSs"), ("2Q", "SSs"), ("2Q", "SpQ")):
        assert all(S.menge(a, n) & ~S.menge(b, n) == 0 for n in range(1, 9)), (a, b)


def test_fingerabdruck_von_2341_und_4321():
    assert S.fingerabdruck((2, 3, 4, 1)) == ("2Q", "3Q", "SSs", "SpQ")
    assert S.fingerabdruck((4, 3, 2, 1)) == ("S", "SSs", "SSp", "SQ", "QS", "SpQ", "P")
    assert S.fingerabdruck((1, 2, 3, 4)) == KEYS


def test_haeufigkeit_des_fingerabdrucks_gegen_eigene_zaehlung_n4():
    fp = S.fingerabdruck((2, 3, 4, 1))
    eigene = sum(1 for p in alle(4) if tuple(k for k in KEYS if ref_sortierbar(k, p)) == fp)
    assert S.haeufigkeit_fingerabdruck(fp, 4) == eigene


@pytest.mark.parametrize("n, erwartet", [(3, 5), (4, 9), (5, 13), (6, 16), (7, 20), (8, 21)])
def test_zahl_verschiedener_fingerabdruecke(n, erwartet):
    assert S.zahl_verschiedener_fingerabdruecke(n) == erwartet


def test_verteilung_n8_508_folgen_von_keiner_maschine_sortiert_und_mittel():
    v = S.verteilung_zahl_maschinen(8)
    assert v[0] == 508 and v[10] == 1 and sum(v.values()) == 40320
    # 1 + 1430 + 1430 + 15767 + 39374 + 15741 + 1430 + 1430 + 27413 + 128 = 104 144 (Zahlen der zehn Maschinen bei n = 8)
    assert abs(S.mittlere_zahl_maschinen(8) - 104144 / 40320) < 1e-12
    assert sum(z * c for z, c in v.items()) == 104144  # zweite Rechnung: Folgen mal Zahl der sortierenden Maschinen


def test_tabelle_n9_stammt_aus_der_wegsuche_ausser_zwei_stapel_in_serie():
    assert S.zahl("S", 9) == S.zahl("2Q", 9) == S.zahl("SQ", 9) == S.zahl("QS", 9) == 4862
    assert (S.zahl("3Q", 9), S.zahl("SSp", 9), S.zahl("SpQ", 9), S.zahl("P", 9), S.zahl("Q", 9)) == (94359, 93944, 188785, 256, 1)
    assert S.zahl("SSs", 9) == 337816 and "nicht nachgerechnet" in S.quelle_n9("SSs")
    assert S.lade()["n9"]["SSs"]["nachgerechnet"] is False and S.lade()["n9"]["S"]["nachgerechnet"] is True


def test_n9_hat_keine_mengen():
    with pytest.raises(ValueError):
        S.menge("S", 9)


def test_zwei_stapel_in_serie_n7_22_unsortierbare_und_n4_vier_maschinen():
    assert factorial(7) - S.zahl("SSs", 7) == 22
    assert S.vier_zwei_stapel(4) == {"SSs": 24, "SSp": 23, "W2": 22, "P2": 16, "n!": 24}

    def fehlt(k):
        return set(alle(4)) - set(S.mitglieder(S.menge(k, 4), 4))

    assert fehlt("SSp") == {(2, 3, 4, 1)} and fehlt("W2") == {(2, 3, 4, 1), (3, 2, 4, 1)}
    assert fehlt("P2") == {(2, 3, 4, 1), (3, 2, 4, 1), (3, 4, 1, 2), (3, 4, 2, 1), (4, 1, 2, 3), (4, 1, 3, 2), (4, 2, 3, 1), (4, 3, 1, 2)}


def test_west2_und_pop2_unvergleichbar_bei_n5_und_west2_nicht_in_ssp_bei_n8():
    assert S.mitglieder(S.menge("P2", 5) & ~S.menge("W2", 5), 5) == [(4, 1, 3, 5, 2)]
    assert S.menge("W2", 5) & ~S.menge("P2", 5) != 0
    assert all(S.menge("W2", n) & ~S.menge("SSp", n) == 0 for n in range(1, 8))
    assert S.mitglieder(S.menge("W2", 8) & ~S.menge("SSp", 8), 8) == [(5, 8, 2, 7, 4, 1, 6, 3)]
