"""Eigenschaftstests (ORACLE-PLAYBOOK §5.2): belegte Aussagen über die Maschinen, geprüft an Zufallsfolgen mit n = 9 und 10 (jenseits der vorgerechneten Mengen).

Die Zufallsfolgen kommen aus dem ausgedachten Ankunftsmodell (feste Zufalls-Seeds; kleine D liefern oft sortierbare Folgen, damit beide Antworten vorkommen)
und aus der Gleichverteilung. Jede Eigenschaft ist ein Satz der Literatur oder eine Folge der Bauart, nicht das bloße Verhalten des Codes:
  - Klasse: Streichen einer Zahl (mit Neunummerieren) einer sortierbaren Folge liefert eine sortierbare Folge (jedes Teilmuster bleibt in der Klasse);
  - mehr Wege, mehr Folgen: ein Behälter mehr oder ein zusätzlicher Weg verliert nie eine Folge (Inklusionen aus der Konstruktion);
  - Charakterisierungen: S = Av(231), mQ = lds <= m (Tarjan 1971, Lemma 2, Vorfassung), P = Av(231, 312) (Bóna 2003);
  - Spuren gültig, Bestimmtheit: dasselbe Ergebnis bei erneuter Suche."""

import pytest

import mvg_machines as M
import mvg_model as MO
import mvg_patterns as P
from mvg_rng import SplitMix64
from ref_maschinen import hat_muster, lds, spiele_ab, sortierbar as ref_sortierbar


def zufallsfolgen(anzahl, seed):
    """Gemischt: Modell V mit kleinem und mittlerem D, n = 9 und 10, dazu gleichverteilte Folgen."""
    res = []
    for n in (9, 10):
        for d in (0.5, 1.0, 2.0):
            res += MO.stichprobe(n, d, anzahl // 6, seed + n * 10 + int(d * 10))
    rng = SplitMix64(seed)
    for _ in range(anzahl // 6):
        p = list(range(1, 11))
        rng.shuffle(p)
        res.append(tuple(p))
    return res


FOLGEN = zufallsfolgen(48, 2026)


def streichen(p, i):
    """Streicht die Stelle i und nummeriert neu (Werte über p[i] rücken um eins nach unten)."""
    return tuple(x - 1 if x > p[i] else x for j, x in enumerate(p) if j != i)


def test_die_testfolgen_enthalten_sortierbare_und_unsortierbare_fuer_jede_maschine():
    # Gegen leere Tests: für jede der zehn Maschinen kommen beide Antworten vor (Q ausgenommen: nur die Identität ist sortierbar)
    for k in M.KEYS:
        antworten = {M.ist_sortierbar(k, p) for p in FOLGEN}
        if k != "Q":
            assert antworten == {True, False}, k


@pytest.mark.parametrize("key", M.KEYS)
def test_klasse_streichen_einer_zahl_bleibt_sortierbar(key):
    geprueft = 0
    for p in FOLGEN:
        if M.ist_sortierbar(key, p):
            for i in range(0, len(p), 3):
                assert M.ist_sortierbar(key, streichen(p, i)), (key, p, i)
                geprueft += 1
    assert geprueft >= 3 or key == "Q"


def test_mehr_wege_mehr_folgen_inklusionen_aus_der_konstruktion():
    folgen_je_maschine = {k: [M.ist_sortierbar(k, p) for p in FOLGEN] for k in M.KEYS}
    ein = lambda a, b: all((not x) or y for x, y in zip(folgen_je_maschine[a], folgen_je_maschine[b]))  # noqa: E731
    for a, b in (("Q", "2Q"), ("2Q", "3Q"), ("Q", "S"), ("P", "S"), ("S", "SSp"), ("S", "SSs"), ("S", "SpQ"), ("S", "SQ"), ("S", "QS"), ("2Q", "SSs"), ("2Q", "SpQ"), ("SSp", "SSs")):
        assert ein(a, b), (a, b)


def test_stapel_ist_231_vermeidend_warteschlangen_sind_fallende_teilfolgen_pop_stack_ist_geschichtet():
    for p in FOLGEN:
        assert M.ist_sortierbar("S", p) == (not hat_muster(p, (2, 3, 1)))
        assert M.ist_sortierbar("2Q", p) == (lds(p) <= 2)
        assert M.ist_sortierbar("3Q", p) == (lds(p) <= 3)
        assert M.ist_sortierbar("P", p) == (not hat_muster(p, (2, 3, 1)) and not hat_muster(p, (3, 1, 2)))
        assert M.ist_sortierbar("Q", p) == (p == tuple(range(1, len(p) + 1)))


def test_zwei_stapel_parallel_ist_der_zweifaerbbare_konfliktgraph_auch_bei_n9_und_n10():
    for p in FOLGEN:
        assert M.ist_sortierbar("SSp", p) == P.konflikt_zweifaerbbar(p), p


def test_spuren_sind_gueltig_und_die_suche_ist_bestimmt():
    for p in FOLGEN[:24]:
        for k in ("S", "3Q", "SSs", "SSp", "SpQ", "P"):
            a = M.pruefe(k, p, spur=True)
            b = M.pruefe(k, p, spur=True)
            assert (a.sortierbar, a.schritte) == (b.sortierbar, b.schritte)
            if a.sortierbar:
                assert spiele_ab(k, p, a.schritte)[0]
            else:
                assert not ref_sortierbar(k, p)


def test_verkettung_nie_schlechter_als_die_erste_stufe_allein():
    # Eine Warteschlange oder ein Stapel am Ausgang kann nur helfen, wenn die erste Stufe schon sortiert: S -> Q sortiert jede Folge, die S allein sortiert
    for p in FOLGEN:
        if M.ist_sortierbar("S", p):
            assert M.ist_sortierbar("SQ", p) and M.ist_sortierbar("QS", p)
