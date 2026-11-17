"""Ankunftsmodell V/U (mvg_model): Rang-Abbildung von Hand, Orakel gegen eine frühere Messreihe und exakte Gleichverteilung, eingefrorene Tabelle."""

from math import sqrt

import pytest

import mvg_model as MO
import mvg_sets as S
from mvg_machines import KEYS
from mvg_patterns import west_durchlauf
from mvg_rng import SplitMix64


def ident(n):
    return tuple(range(1, n + 1))


def test_rang_abbildung_von_hand_mit_festen_verweilzeiten():
    # Verweilzeiten 2,5 / 0,1 / 0,2 bei Ankunft 1, 2, 3: Abfahrt 3,5 / 2,1 / 3,2 -> Ränge 3, 1, 2
    class Fest:
        def __init__(self, werte):
            self.w = iter(werte)

        def expovariate(self, mean):
            return next(self.w) * mean

    assert MO.folge(Fest([2.5, 0.1, 0.2]), 3, 1.0) == (3, 1, 2)


def test_folge_ist_immer_eine_permutation_und_reproduzierbar():
    for d in MO.D_WERTE:
        a = MO.stichprobe(7, d, 30, 99)
        assert a == MO.stichprobe(7, d, 30, 99)
        assert all(sorted(p) == list(range(1, 8)) for p in a)
    assert MO.stichprobe(7, 2.0, 5, 1) != MO.stichprobe(7, 2.0, 5, 2)


def test_winzige_verweilzeit_gibt_die_identitaet_und_riesige_ist_wie_gleichverteilt():
    assert all(p == ident(8) for p in MO.stichprobe(8, 1e-9, 50, 5))
    assert sum(p == ident(6) for p in MO.stichprobe(6, 1e6, 3000, 5)) / 3000 < 0.01  # gleichverteilt: 1/720 = 0,14 %


def test_modell_u_anteile_gleich_exakt_aus_den_mengen_im_band():
    n, anzahl = 8, 6000
    z = MO.zaehle_maschinen(MO.stichprobe(n, None, anzahl, 321), n)
    for k in KEYS:
        ex = S.anteil(k, n)
        assert abs(z[k] / anzahl - ex) <= MO.band(ex, anzahl) + 1e-9, k


# Früher gemessene Anteile eines Stapels bei n = 10 (2000 Folgen je D, Prozent): ein Orakel für die Rang-Abbildung des Modells
FRUEH_S_N10 = {0.5: 99.4, 1.0: 90.8, 2.0: 58.7, 4.0: 20.3, 8.0: 6.7, 16.0: 2.2, None: 0.55}


def test_orakel_ein_stapel_bei_n10_gegen_fruehere_messreihe_im_band():
    anzahl = 1500
    for j, (d, ref) in enumerate(FRUEH_S_N10.items()):
        folgen = MO.stichprobe(10, d, anzahl, 777 + j)
        mein = 100 * sum(west_durchlauf(p) == ident(10) for p in folgen) / anzahl
        se_ref = 100 * sqrt(max(ref / 100 * (1 - ref / 100), 1e-4) / 2000)
        se_mein = 100 * sqrt(max(mein / 100 * (1 - mein / 100), 1e-4) / anzahl)
        assert abs(mein - ref) <= 4 * sqrt(se_ref**2 + se_mein**2) + 0.3, (d, mein, ref)


def test_stapel_anteil_faellt_mit_wachsender_verweilzeit():
    anteile = [MO.anteile(8, d, 2000, 50 + j)[0]["S"] for j, d in enumerate(MO.D_WERTE)]
    assert anteile == sorted(anteile, reverse=True)


def test_band_und_differenz_von_hand():
    assert MO.band(0.5, 10000) == pytest.approx(4 * 0.005)
    d, se = MO.differenz_und_fehler(30, 10, 1000)  # (0,03 - 0,01); Var = (30 + 10 - 400 / 1000) / 1e6 = 39,6e-6
    assert d == pytest.approx(0.02) and se == pytest.approx(sqrt(39.6e-6))
    assert MO.differenz_und_fehler(5, 5, 100)[0] == 0


def test_zaehle_paare_zerlegt_in_nur_a_nur_b_beide():
    n = 8
    folgen = MO.stichprobe(n, 4.0, 1500, 11)
    z = MO.zaehle_maschinen(folgen, n)
    p = MO.zaehle_paare(folgen, n)
    nur_s, nur_2q, beide = p["S|2Q"]
    assert nur_s + beide == z["S"] and nur_2q + beide == z["2Q"]
    nur_3q, nur_ssp, beide2 = p["3Q|SSp"]
    assert nur_3q + beide2 == z["3Q"] and nur_ssp + beide2 == z["SSp"]


def test_eingefrorene_tabelle_erster_block_je_d_wird_exakt_neu_gerechnet():
    daten = MO.lade()
    assert [z["d"] for z in daten["zeilen"]] == list(MO.D_WERTE) and daten["n"] == 8
    z = daten["zeilen"][3]  # D = 4
    folgen = MO.stichprobe(8, z["d"], z["block"], z["seed"])
    assert MO.zaehle_maschinen(folgen, 8) == z["zaehler_block"]
    assert MO.zaehle_paare(folgen, 8) == z["paare_block"]


def test_eingefrorene_tabelle_ist_in_sich_stimmig():
    daten = MO.lade()
    for z in daten["zeilen"]:
        c = z["zaehler"]
        assert z["anzahl"] == 20000 == MO.ANZAHL_FROZEN
        assert c["S"] == c["SQ"] == c["QS"]  # dieselbe Menge bei n = 8
        assert all(z["zaehler_block"][k] <= c[k] for k in KEYS)
        na, nb, be = z["paare"]["S|2Q"]
        assert na + be == c["S"] and nb + be == c["2Q"]
        na, nb, be = z["paare"]["3Q|SSp"]
        assert na + be == c["3Q"] and nb + be == c["SSp"]
    ys = [z["zaehler"]["S"] for z in daten["zeilen"]]
    assert ys == sorted(ys, reverse=True)
    letzte = daten["zeilen"][-1]  # D = ∞: gleichverteilt, exakt aus den Mengen im Band
    for k in KEYS:
        ex = S.anteil(k, 8)
        assert abs(letzte["zaehler"][k] / 20000 - ex) <= MO.band(ex, 20000) + 1e-9, k


def test_zufall_kommt_nur_aus_splitmix64():
    quelle = open(MO.__file__, encoding="utf-8").read()
    assert "import random" not in quelle and "numpy" not in quelle
    assert SplitMix64(1).next_u64() == SplitMix64(1).next_u64()
