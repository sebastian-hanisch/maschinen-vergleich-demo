"""Orakel-Tests: die Wegsuche und die vorgerechneten Mengen gegen andere Rechenwege.

(A) Zahlen aus der Wegsuche gegen die Reihen der OEIS (Stufe: gelesen, siehe README) und gegen die Catalan-Formel;
(B) Erzeugen aus der Identität mit freien Bewegungen, invertiert (Sortieren und Erzeugen sind invers), gegen die sortierbare Menge;
(C) Mustercharakterisierungen mit eigenem Mustersucher und eigener LDS: S = Av(231), 2Q = lds <= 2, 3Q = lds <= 3, Q = Identität, P = Av(231, 312), SQ = QS = S;
(D) zwei Stapel parallel = zweifärbbarer Konfliktgraph (eigene Union-Find-Rechnung);
(E) eigene Breitensuche gegen die Wegsuche (bis n = 5, alle zehn Maschinen);
(F) die eingefrorene JSON gegen Neu-Rechnung (n <= 7 immer, n = 8 mit MVG_VOLL=1) und gegen die Muster (n = 8).
Alle Prüfungen sind exakte Ganzzahl- und Mengenvergleiche (plattformfest). Orakel vorher an Handbeispielen geprüft (test_machines.py)."""

import sys
from pathlib import Path

import pytest

import mvg_machines as M
import mvg_sets as S
from conftest import ROOT, nur_voll
from ref_maschinen import alle, catalan, hat_muster, konflikt_zweifaerbbar, lds, sortierbar as ref_sortierbar

sys.path.insert(0, str(Path(ROOT) / "tools"))
import mvg_make_sets as MK  # noqa: E402

# Zahlen n = 1..8: A000108 (Catalan), A005802, A216040, A263929, 2^(n-1); die Reihe für SpQ hat keinen OEIS-Treffer (nur Wegsuche, Erzeugen bis n = 5)
OEIS = {
    "Q": [1, 1, 1, 1, 1, 1, 1, 1],
    "S": [1, 2, 5, 14, 42, 132, 429, 1430],
    "2Q": [1, 2, 5, 14, 42, 132, 429, 1430],
    "3Q": [1, 2, 6, 23, 103, 513, 2761, 15767],
    "SSs": [1, 2, 6, 24, 120, 720, 5018, 39374],
    "SSp": [1, 2, 6, 23, 103, 513, 2760, 15741],
    "SQ": [1, 2, 5, 14, 42, 132, 429, 1430],
    "QS": [1, 2, 5, 14, 42, 132, 429, 1430],
    "SpQ": [1, 2, 6, 24, 118, 668, 4150, 27413],
    "P": [1, 2, 4, 8, 16, 32, 64, 128],
}


@pytest.mark.parametrize("key", M.KEYS)
def test_a_zahlen_der_wegsuche_gleich_den_oeis_reihen_bis_n7(key):
    assert [len(M.sortierbare(key, n)) for n in range(1, 8)] == OEIS[key][:7]


def test_a_catalan_formel_und_potenzen_von_zwei():
    assert OEIS["S"] == [catalan(n) for n in range(1, 9)]
    assert OEIS["P"] == [2 ** (n - 1) for n in range(1, 9)]


@pytest.mark.parametrize("key", M.KEYS)
def test_b_erzeugen_invertiert_gleich_sortieren(key):
    grenze = 5 if key in ("SSs", "SSp", "SpQ") else 6
    for n in range(1, grenze + 1):
        assert {M.inverse(o) for o in M.erzeugbare(key, n)} == set(M.sortierbare(key, n)), (key, n)


def test_c_muster_charakterisierungen_bis_n7():
    for n in range(1, 8):
        a = alle(n)
        sortiert = {k: set(M.sortierbare(k, n)) for k in ("Q", "S", "2Q", "3Q", "SQ", "QS", "P")}
        assert sortiert["S"] == {p for p in a if not hat_muster(p, (2, 3, 1))}
        assert sortiert["SQ"] == sortiert["QS"] == sortiert["S"]
        assert sortiert["2Q"] == {p for p in a if lds(p) <= 2}
        assert sortiert["3Q"] == {p for p in a if lds(p) <= 3}
        assert sortiert["Q"] == {tuple(range(1, n + 1))}
        assert sortiert["P"] == {p for p in a if not hat_muster(p, (2, 3, 1)) and not hat_muster(p, (3, 1, 2))}


def test_c_lds_zaehlt_wie_von_hand():
    assert lds((4, 3, 2, 1)) == 4 and lds((2, 3, 4, 1)) == 2 and lds((2, 4, 3, 5, 7, 6, 1)) == 3


@pytest.mark.parametrize("n", range(1, 8))
def test_d_zwei_stapel_parallel_gleich_zweifaerbbarer_konfliktgraph(n):
    assert set(M.sortierbare("SSp", n)) == {p for p in alle(n) if konflikt_zweifaerbbar(p)}


def test_d_der_konfliktgraph_von_2341_ist_ein_dreieck():
    assert not konflikt_zweifaerbbar((2, 3, 4, 1)) and konflikt_zweifaerbbar((4, 3, 2, 1))


@pytest.mark.parametrize("key", M.KEYS)
def test_e_eigene_breitensuche_gleich_wegsuche_menge_bis_n5(key):
    for n in range(1, 6):
        assert {p for p in alle(n) if ref_sortierbar(key, p)} == set(M.sortierbare(key, n)), (key, n)


def test_f_eingefrorene_mengen_gleich_neu_rechnung_bis_n7():
    assert MK.pruefe(7, log=lambda *_: None) == []


@nur_voll
def test_f_eingefrorene_mengen_gleich_neu_rechnung_n8():
    assert MK.pruefe(8, log=lambda *_: None) == []


def test_f_eingefrorene_mengen_gleich_den_mustern_n8():
    n = 8
    a = S.folgen(n)
    assert {a[i] for i in range(len(a)) if (S.menge("S", n) >> i) & 1} == {p for p in a if not hat_muster(p, (2, 3, 1))}
    assert S.menge("SQ", n) == S.menge("QS", n) == S.menge("S", n)
    assert {a[i] for i in range(len(a)) if (S.menge("2Q", n) >> i) & 1} == {p for p in a if lds(p) <= 2}
    assert {a[i] for i in range(len(a)) if (S.menge("3Q", n) >> i) & 1} == {p for p in a if lds(p) <= 3}
    assert {a[i] for i in range(len(a)) if (S.menge("SSp", n) >> i) & 1} == {p for p in a if konflikt_zweifaerbbar(p)}
    assert S.mitglieder(S.menge("Q", n), n) == [tuple(range(1, 9))]
    assert {a[i] for i in range(len(a)) if (S.menge("P", n) >> i) & 1} == {p for p in a if not hat_muster(p, (2, 3, 1)) and not hat_muster(p, (3, 1, 2))}


def test_f_zahlen_der_eingefrorenen_mengen_gleich_den_oeis_reihen_bis_n8():
    for key in M.KEYS:
        assert [S.zahl(key, n) for n in range(1, 9)] == OEIS[key], key


def test_f_zwei_durchlauf_regeln_gleich_den_bekannten_zahlen():
    # A000139 (West-2): 2(3n)!/((n+1)!(2n+1)!), n = 1..8 (Bóna 2003, Satz 3.2); Pop-2: Zahlen einer früheren Messung, nicht aus einer Quelle
    from math import factorial

    for n in range(1, 9):
        assert S.zahl("W2", n) == 2 * factorial(3 * n) // (factorial(n + 1) * factorial(2 * n + 1)), n
    assert [S.zahl("P2", n) for n in range(1, 9)] == [1, 2, 6, 16, 42, 112, 298, 792]
