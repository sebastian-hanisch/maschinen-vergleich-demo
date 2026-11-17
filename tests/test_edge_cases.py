"""Randfälle: n = 1, n = 2, leere und ungültige Eingaben, zwei gleiche Maschinen, Permalink-Begrenzung, Preset ohne Effekt, n = 10 mit der Umkehrfolge."""

import time

import pytest

import mvg_constants as C
import mvg_evaluation as ev
import mvg_machines as M
import mvg_presets as P
import mvg_sets as S
import mvg_patterns as PT


def test_n1_alle_zehn_sortieren_und_tabelle_hat_keinen_verlust():
    assert all(S.zahl(k, 1) == 1 for k in M.KEYS)
    assert all(z["zahl"] == 1 and z["anteil"] == 100.0 for z in ev.tabelle_zeilen(1))
    assert ev.verdict_tabelle(1)[0] == "info"


def test_n2_nur_eine_warteschlange_verliert():
    zeilen = {z["kuerzel"]: z for z in ev.tabelle_zeilen(2)}
    assert zeilen["Q"]["zahl"] == 1 and all(z["zahl"] == 2 for k, z in zeilen.items() if k != "Q")
    assert zeilen["Q"]["erstes_n_verlust"] == 2 and zeilen["S"]["erstes_n_verlust"] == 3 and zeilen["SSs"]["erstes_n_verlust"] == 7


def test_erstes_n_mit_verlust_fuer_pop_stack_und_spq():
    z = {r["kuerzel"]: r["erstes_n_verlust"] for r in ev.tabelle_zeilen(5)}
    assert z["P"] == 3 and z["SpQ"] == 5 and z["3Q"] == 4 and z["SSp"] == 4 and z["SSs"] == 7


def test_tabelle_n9_laeuft_und_gruppiert_gleiche_zahlen():
    zeilen = ev.tabelle_zeilen(9)
    gruppe = {z["kuerzel"]: z["gruppe"] for z in zeilen}
    assert gruppe["S"] == gruppe["2Q"] == gruppe["SQ"] == gruppe["QS"] and gruppe["3Q"] != gruppe["SSp"]


def test_leere_und_ungueltige_eingaben_geben_meldungen_statt_rechnung():
    for text in ("", " ", "abc", "1 1 2", "0 1 2", "2 3 4", "12345678901"):
        folge, fehler = ev.parse_folge(text)
        assert folge is None and fehler, text


def test_zwei_gleiche_maschinen_sind_eine_warnung_in_beiden_experimenten():
    for k in M.KEYS:
        assert ev.verdict_paar(k, k, 5)[0] == "warning" and ev.verdict_ordnung_paar(k, k, 5)[0] == "warning"


def test_ein_vergleich_ohne_unterschied_meldet_keinen_unterschied():
    # Preset ohne Effekt: Maschinen mit gleicher Menge dürfen keine Zeugen oder „unvergleichbar“ melden
    for a, b in (("S", "SQ"), ("S", "QS"), ("SQ", "QS")):
        for n in range(3, 9):
            kind, text = ev.verdict_paar(a, b, n)
            assert kind == "info" and "dieselbe Menge" in text and "Zeugen" not in text
            kind, text = ev.verdict_ordnung_paar(a, b, n)
            assert "dieselbe Menge" in text and "unvergleichbar" not in text


def test_umkehrfolge_n10_bei_zwei_stapeln_in_serie_in_unter_zwei_sekunden():
    folge = tuple(range(10, 0, -1))
    t = time.time()
    r = M.pruefe("SSs", folge, spur=True)
    assert r.sortierbar and time.time() - t < 2.0
    assert r.zustaende <= 2 * (2 ** 11)  # die Zustandszahl bleibt klein (bis 2047 je Ebene)


def test_alle_zehn_maschinen_fuer_n10_umkehrfolge_in_unter_fuenf_sekunden():
    t = time.time()
    ergebnisse = ev.pruefe_alle(tuple(range(10, 0, -1)))
    assert time.time() - t < 5.0
    assert [k for k in M.KEYS if ergebnisse[k].sortierbar] == ["S", "SSs", "SSp", "SQ", "QS", "SpQ", "P"]


def test_identitaet_n10_sortiert_jede_maschine():
    ergebnisse = ev.pruefe_alle(tuple(range(1, 11)))
    assert all(r.sortierbar for r in ergebnisse.values())


def test_grund_fuer_nein_nennt_muster_oder_zyklus_und_stimmt_mit_der_maschine():
    assert PT.grund_nein("S", (2, 3, 4, 1))[0] == "muster" and "231" in PT.grund_nein("S", (2, 3, 4, 1))[1]
    assert PT.grund_nein("2Q", (3, 2, 1, 4))[0] == "muster" and PT.grund_nein("3Q", (4, 3, 2, 1))[0] == "muster"
    assert PT.grund_nein("Q", (2, 1))[0] == "muster" and PT.grund_nein("P", (2, 3, 1))[0] == "muster"
    art, text = PT.grund_nein("SSp", (2, 3, 4, 1))
    assert art == "zyklus" and "ungerader Länge 3" in text
    assert PT.grund_nein("SSs", (2, 4, 3, 5, 7, 6, 1)) == (None, None)  # kein einfaches Muster


def test_ungerader_zyklus_ist_ein_echter_zyklus_im_konfliktgraphen():
    gefunden = 0
    for p in [(2, 3, 4, 1), (3, 4, 5, 1, 2), (2, 3, 5, 4, 1)]:
        z = PT.ungerader_zyklus(p)
        if z is None:
            continue
        gefunden += 1
        kanten = set(PT.konfliktkanten(p))
        assert len(z) % 2 == 1
        for i in range(len(z)):
            a, b = z[i], z[(i + 1) % len(z)]
            assert (min(a, b), max(a, b)) in kanten
    assert gefunden >= 1


def test_permalink_begrenzt_und_filtert_ungueltige_werte():
    spec_n = P.SETTING_SPECS["e1_n"]
    assert P._begrenze(spec_n, "99") == 9 and P._begrenze(spec_n, "-3") == 1 and P._begrenze(spec_n, "x") is None
    assert P._begrenze(P.SETTING_SPECS["e2_a"], "SSp") == "SSp" and P._begrenze(P.SETTING_SPECS["e2_a"], "XX") is None
    assert P._begrenze(P.SETTING_SPECS["e3_d"], "4") == "4" and P._begrenze(P.SETTING_SPECS["e3_d"], "5") is None
    assert P._begrenze(P.SETTING_SPECS["e3_folge"], "23<script>41") == "2341" and len(P._begrenze(P.SETTING_SPECS["e3_folge"], "1" * 100)) == 40


def test_jedes_preset_aendert_etwas_gegenueber_dem_standard():
    standard = C.PRESETS[C.STANDARD]
    for name, preset in C.PRESETS.items():
        if name != C.STANDARD:
            assert any(preset.get(k, P.SETTING_SPECS[k].default) != standard.get(k, P.SETTING_SPECS[k].default) for k in P.SETTING_SPECS), name
