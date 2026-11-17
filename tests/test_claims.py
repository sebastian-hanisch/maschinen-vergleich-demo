"""Claims: jede Zahl und jeder Befundsatz der README wird hier nachgerechnet (DEMO-PLAYBOOK §4, §11a) und steht als Satz in der README.

Jeder Test nennt die Bedingung (n, Zähleinheit). Messungen der README, die nicht im Test stehen, heißen in der README ausdrücklich so; hier nicht: die Seitenlänge der Seite."""

import re
import subprocess
import sys
from math import factorial, sqrt
from pathlib import Path

import pytest

import mvg_evaluation as ev
import mvg_machines as M
import mvg_model as MO
import mvg_sets as S
from mvg_machines import KEYS

ROOT = Path(__file__).resolve().parent.parent
README = (ROOT / "README.md").read_text(encoding="utf-8")


def readme_hat(*saetze):
    flach = re.sub(r"\s+", " ", README)
    for satz in saetze:
        assert re.sub(r"\s+", " ", satz) in flach, f"nicht in der README: {satz}"


def test_tabelle_der_readme_gleich_den_zahlen_der_mengen():
    zeilen = [z for z in README.splitlines() if re.match(r"\| [3-9] \| [\d ]+ \|", z)]
    assert len(zeilen) == 7
    for z in zeilen:
        zellen = [c.strip().replace(" †", "").replace(" ", "") for c in z.strip("|").split("|")]
        n = int(zellen[0])
        assert int(zellen[1]) == factorial(n)
        assert [int(c) for c in zellen[2:]] == [S.zahl(k, n) for k in KEYS], n


def test_anteile_bei_n8_und_9_zahlen():
    readme_hat("S, 2Q, SQ, QS 3,55 %", "3Q 39,10 %", "SSp 39,04 %", "SpQ 67,99 %", "SSs 97,65 %", "P 0,32 %")
    got = {k: round(100 * S.anteil(k, 8), 2) for k in KEYS}
    assert got["S"] == 3.55 and got["3Q"] == 39.10 and got["SSp"] == 39.04 and got["SpQ"] == 67.99 and got["SSs"] == 97.65 and got["P"] == 0.32
    assert S.zahl("SSs", 9) == 337816 and S.zahl("SQ", 9) == 4862


def test_kleinster_fall_n3_und_s_gegen_2q():
    v = S.vergleich("S", "2Q", 3)
    assert (v["nur_a"], v["beide"], v["nur_b"], v["zeugen_a"], v["zeugen_b"]) == (1, 4, 1, [(3, 2, 1)], [(2, 3, 1)])
    assert all(S.zahl("S", n) == S.zahl("2Q", n) for n in range(1, 9)) and all(S.menge("S", n) != S.menge("2Q", n) for n in range(3, 9))
    assert S.vergleich("S", "2Q", 8)["nur_a"] == 1302
    readme_hat("n = 3: S gegen 2Q, je 5 von 6; nur S sortiert 321, nur 2Q sortiert 231", "bei n = 8 nur S 1302, nur 2Q 1302, gemeinsam 128")


def test_3q_gegen_ssp():
    ergebnis = {n: S.vergleich("SSp", "3Q", n) for n in range(4, 8)}
    assert [(ergebnis[n]["nur_a"], ergebnis[n]["nur_b"]) for n in (4, 5, 6)] == [(1, 1), (17, 17), (171, 171)]
    assert [S.zahl("SSp", n) for n in (4, 5, 6)] == [S.zahl("3Q", n) for n in (4, 5, 6)] == [23, 103, 513]
    assert ergebnis[5]["beide"] == 86 and (S.zahl("SSp", 7), S.zahl("3Q", 7)) == (2760, 2761)
    assert (ergebnis[7]["nur_a"], ergebnis[7]["nur_b"], ergebnis[7]["beide"]) == (1395, 1396, 1365)
    assert ergebnis[4]["zeugen_a"] == [(4, 3, 2, 1)] and ergebnis[4]["zeugen_b"] == [(2, 3, 4, 1)]
    readme_hat("je 23, 103, 513 bei n = 4, 5, 6", "nur SSp 1, 17, 171 und nur 3Q 1, 17, 171", "n = 7: 2760 gegen 2761 (nur SSp 1395, nur 3Q 1396, gemeinsam 1365)")


def test_paare_und_zaehlfolgen():
    paare = {n: S.paare_gleiche_zahl(n) for n in range(3, 9)}
    assert {n: (len(p), sum(1 for _, _, g in p if not g)) for n, p in paare.items()} == {3: (6, 3), 4: (7, 4), 5: (7, 4), 6: (7, 4), 7: (6, 3), 8: (6, 3)}
    assert {n: S.zaehlfolgen_und_mengen(n) for n in range(3, 9)} == {3: (4, 5), 4: (5, 7), 5: (6, 8), 6: (6, 8), 7: (7, 8), 8: (7, 8)}
    readme_hat("n = 3: 6 und 3; n = 4, 5, 6: 7 und 4; n = 7, 8: 6 und 3 (von 45 Paaren)", "n = 3: 4 gegen 5; n = 4: 5 gegen 7; n = 5 und 6: 6 gegen 8; n = 7 und 8: 7 gegen 8")
    assert len(KEYS) * (len(KEYS) - 1) // 2 == 45


def test_gleiche_menge_nur_s_sq_qs():
    gleich = [(a, b) for i, a in enumerate(KEYS) for b in KEYS[i + 1:] if all(S.menge(a, n) == S.menge(b, n) for n in range(1, 9))]
    assert gleich == [("S", "SQ"), ("S", "QS"), ("SQ", "QS")]
    readme_hat("S = SQ = QS für n ≤ 8 (gemessen, nicht bewiesen)")


def test_ordnung_bei_n8_und_unvergleichbare_beispiele():
    o = S.ordnung(8)
    assert (len(o["klassen"]), len(o["kanten"]), len(o["unvergleichbar"])) == (8, 9, 10)
    v = S.vergleich("SSp", "SpQ", 8)
    assert (v["nur_a"], v["nur_b"]) == (3758, 15430) and S.menge("SSp", 8) & ~S.menge("SSs", 8) == 0
    v = S.vergleich("3Q", "SSs", 8)
    assert (v["nur_a"], v["beide"], v["nur_b"]) == (406, 15361, 24013)
    assert M.ist_sortierbar("3Q", (2, 4, 3, 5, 7, 6, 1)) and not M.ist_sortierbar("SSs", (2, 4, 3, 5, 7, 6, 1))
    assert M.ist_sortierbar("SSs", (4, 3, 2, 1, 5, 6, 7)) and not M.ist_sortierbar("3Q", (4, 3, 2, 1, 5, 6, 7))
    readme_hat("8 verschiedene Mengen, 9 echte Teilmengenkanten ohne Zwischenglied, 10 unvergleichbare Paare", "nur SSp 3758, nur SpQ 15 430",
               "nur 3Q 406, nur SSs 24 013, gemeinsam 15 361", "2435761: 3Q ja, SSs nein; 4321567: SSs ja, 3Q nein")


def test_fingerabdruecke_und_keine_maschine():
    assert [S.zahl_verschiedener_fingerabdruecke(n) for n in range(3, 9)] == [5, 9, 13, 16, 20, 21]
    assert len(S.fingerabdruck((2, 3, 4, 1))) == 4 and len(S.fingerabdruck((4, 3, 2, 1))) == 7
    v = S.verteilung_zahl_maschinen(8)
    assert v[0] == 508 and round(100 * v[0] / 40320, 2) == 1.26 and round(S.mittlere_zahl_maschinen(8), 2) == 2.58 and round(S.mittlere_zahl_maschinen(8), 3) == 2.583
    readme_hat("5, 9, 13, 16, 20, 21", "508 von 40 320 (1,26 %)", "im Mittel sortieren 2,58 Maschinen eine gleichverteilte Folge", "im Mittel 2,583 Maschinen")


def test_vier_zwei_stapel_und_serie_n7():
    assert S.vier_zwei_stapel(4) == {"SSs": 24, "SSp": 23, "W2": 22, "P2": 16, "n!": 24}
    assert S.mitglieder(S.menge("P2", 5) & ~S.menge("W2", 5), 5) == [(4, 1, 3, 5, 2)]
    assert S.mitglieder(S.menge("W2", 8) & ~S.menge("SSp", 8), 8) == [(5, 8, 2, 7, 4, 1, 6, 3)]
    assert all(S.menge("W2", n) & ~S.menge("SSp", n) == 0 for n in range(1, 8)) and factorial(7) - S.zahl("SSs", 7) == 22
    readme_hat("n = 4: SSs 24, SSp 23, West-2 22, Pop-2 16 von 24", "(n = 5: 41352)", "bei n = 8 nicht mehr (eine Folge, 58274163)", "22 von 5040 Folgen unsortierbar")


def test_zwei_parallele_stapel_ohne_zwischenausgabe_nur_132_bei_n6():
    # „erst alles hinein, dann alles hinaus“: zwei parallele Stapel sortieren genau die Folgen mit längster wachsender Teilfolge <= 2 (Tarjan 1971, Lemma 3, Vorfassung)
    from mvg_patterns import laengste_wachsende

    assert sum(1 for p in S.folgen(6) if laengste_wachsende(p) <= 2) == 132 and S.zahl("SSp", 6) == 513
    readme_hat("zwei parallele Stapel sortieren so bei n = 6 nur 132 statt 513 Folgen")


# ---------------------------------------------------------------- Ankunftsmodell V
def _tabelle_der_readme():
    zeilen = [z for z in README.splitlines() if re.match(r"\| (0,5|1|2|4|8|16|∞) \| \d+,\d\d \| \d+,\d\d \|", z)]
    assert len(zeilen) == 7
    res = {}
    for z in zeilen:
        c = [x.strip() for x in z.strip("|").split("|")]
        res[c[0]] = c
    return res


def test_tabelle_modell_v_der_readme_gleich_der_json():
    tab = _tabelle_der_readme()
    for zeile in ev.frozen_zeilen():
        c = tab[MO.d_text(zeile["d"])]
        for k, text in zip(KEYS, c[1:11]):
            assert text == f"{100 * zeile['anteile'][k]:.2f}".replace(".", ","), (zeile["d"], k)
        assert c[11] == f"{zeile['mittel']:.3f}".replace(".", ",")
        for spalte, paar in ((12, "S|2Q"), (13, "3Q|SSp")):
            d, se = zeile["paare"][paar]
            erwartet = f"{100 * d:+.2f} ({100 * se:.2f})".replace(".", ",").replace("-", "−")
            assert c[spalte] == erwartet, (zeile["d"], paar, c[spalte], erwartet)


def test_modell_v_differenzen_und_sieben_von_sieben():
    zs = ev.frozen_zeilen()
    d1 = [100 * z["paare"]["S|2Q"][0] for z in zs]
    d2 = [100 * z["paare"]["3Q|SSp"][0] for z in zs]
    assert (round(min(d1), 2), round(max(d1), 2)) == (-0.36, 0.43) and (round(min(d2), 2), round(max(d2), 2)) == (-0.33, 0.78)
    assert all(abs(z["paare"]["S|2Q"][0]) <= 4 * z["paare"]["S|2Q"][1] for z in zs) and all(abs(z["paare"]["3Q|SSp"][0]) <= 4 * z["paare"]["3Q|SSp"][1] for z in zs)
    se1 = [100 * z["paare"]["S|2Q"][1] for z in zs]
    assert round(4 * min(se1), 1) == 0.2 and round(4 * max(se1), 1) == 1.8
    readme_hat("Differenz der Anteile −0,36 bis +0,43 Punkte, in 7 von 7 Zeilen innerhalb von vier Standardfehlern der Differenz",
               "−0,33 bis +0,78 Punkte, ebenfalls 7 von 7", "das sind je nach Zeile 0,2 bis 1,8 Punkte")


def test_exakte_anteile_der_readme_und_gleichverteilte_zeile():
    letzte = ev.frozen_zeilen()[-1]
    assert letzte["d"] is None
    for k in KEYS:
        assert abs(letzte["anteile"][k] - S.anteil(k, 8)) <= MO.band(S.anteil(k, 8), 20000) + 1e-9


FRUEH = {  # früher gemessen (anderer Zufallsgenerator), n = 8, 20 000 Folgen je D, Prozent; Spalten wie KEYS
    0.5: [58.78, 99.70, 99.69, 100.00, 100.00, 100.00, 99.70, 99.70, 100.00, 94.61],
    1.0: [18.79, 93.14, 93.31, 99.92, 100.00, 99.93, 93.14, 93.14, 100.00, 66.62],
    2.0: [2.83, 66.29, 66.41, 97.44, 100.00, 97.60, 66.29, 66.29, 99.91, 27.59],
    4.0: [0.31, 34.04, 33.90, 86.79, 99.99, 86.70, 34.04, 34.04, 97.83, 7.89],
    8.0: [0.04, 16.07, 15.78, 69.87, 99.88, 70.18, 16.07, 16.07, 91.39, 2.46],
    16.0: [0.01, 8.65, 8.52, 56.68, 99.36, 56.02, 8.65, 8.65, 83.22, 1.04],
    None: [0.00, 3.55, 3.55, 39.10, 97.65, 39.04, 3.55, 3.55, 67.99, 0.32],
}


def test_alle_70_anteile_innerhalb_von_vier_standardfehlern_der_fruehen_messung():
    zs = {z["d"]: z for z in ev.frozen_zeilen()}
    groesste = 0.0
    for d, reihe in FRUEH.items():
        for k, frueh in zip(KEYS, reihe):
            mein = 100 * zs[d]["anteile"][k]
            se1 = 100 * sqrt(max(frueh / 100 * (1 - frueh / 100), 1e-6) / 20000)
            se2 = 100 * sqrt(max(mein / 100 * (1 - mein / 100), 1e-6) / 20000)
            assert abs(mein - frueh) <= 4 * sqrt(se1**2 + se2**2) + 0.01, (d, k, mein, frueh)
            groesste = max(groesste, abs(mein - frueh))
    assert round(groesste, 2) == 0.68
    readme_hat("Alle 70 Anteile (zehn Maschinen, sieben Werte von D) liegen innerhalb von vier Standardfehlern der Differenz beider Messungen",
               "die größte Abweichung beträgt 0,68 Punkte (3Q bei D = 16: 56,00 % statt 56,68 %)")
    assert round(100 * zs[16.0]["anteile"]["3Q"], 2) == 56.00


def test_standardfehler_der_live_stichprobe_hoechstens_1_12_punkte():
    assert round(100 * sqrt(0.25 / MO.ANZAHL_LIVE), 2) == 1.12
    readme_hat("höchstens 1,12 Punkte (bei 50 %)")


def test_wegsuche_n10_hoechstens_2047_konfigurationen_je_maschine():
    from test_eigenschaften_maschinen_vergleich import FOLGEN

    assert len(FOLGEN) == 56
    groesste = 0
    for p in list(FOLGEN) + [tuple(range(10, 0, -1))]:
        for k in KEYS:
            groesste = max(groesste, M.pruefe(k, p).zustaende)
    assert groesste == 2047
    readme_hat("56 Zufallsfolgen mit n = 9 und 10", "je Maschine höchstens 2 047 Konfigurationen")


def test_zahl_der_tests_in_der_readme_gibt_es_nicht_als_feste_zahl_hier():
    assert "tests/test_claims.py" in README  # die Testzahl prüft tools/readme_test_counts.py im Website-Repo


# ---------------------------------------------------------------- Planungswörter und Zufall
VERBOTEN = ("Stück", "Linie", "Vormessung", "Plan Z", "V1", "sm_v", "Phase 0", "geplant", "Saatwert", "trägt", "tragen", "läuft lokal")


def _text_dateien():
    dateien = [ROOT / "README.md", ROOT / "app.py"] + sorted(ROOT.glob("mvg_*.py")) + sorted((ROOT / "tools").glob("*.py"))
    return [p for p in dateien if p.name != "mvg_rng.py"]


def test_keine_planungswoerter_in_readme_app_und_quelltext():
    gefunden = []
    for p in _text_dateien():
        for nr, zeile in enumerate(p.read_text(encoding="utf-8").splitlines(), start=1):
            if "Mehr zur Reihe" in zeile:  # vom Footer-Werkzeug erzeugt
                continue
            for wort in VERBOTEN:
                if re.search(r"" + re.escape(wort) + r"", zeile):  # ganze Wörter: „beträgt“ enthält „trägt“, ist aber erlaubt
                    gefunden.append(f"{p.name}:{nr}: {wort}")
    assert not gefunden, gefunden


def test_die_readme_nennt_die_einbindung_der_website_nicht_als_offen():
    assert not re.search(r"Einbindung[^.\n]*offen", README) and "geplant" not in README


def test_zufall_nur_ueber_splitmix64_nie_hash_und_nie_random():
    for p in _text_dateien() + [ROOT / "mvg_rng.py"]:
        text = p.read_text(encoding="utf-8")
        assert "hash(" not in text.replace("hasher", ""), p.name
        assert not re.search(r"^\s*(import random|from random|import numpy)", text, re.M), p.name


def test_tools_laufen_mit_hilfe_ohne_fehler():
    for name in ("mvg_make_sets.py", "mvg_make_model.py"):
        r = subprocess.run([sys.executable, "-X", "utf8", str(ROOT / "tools" / name)], capture_output=True, text=True, timeout=60, stdin=subprocess.DEVNULL)
        assert r.returncode == 0 and "--check" in r.stdout, name


def test_modell_wird_in_der_readme_als_ausgedacht_gekennzeichnet():
    readme_hat("ausgedachtes Ankunftsmodell", "Modell, keine reale Ankunftsfolge")
    assert "ausgedacht" in (ROOT / "mvg_texts.py").read_text(encoding="utf-8") and "ausgedacht" in (ROOT / "app.py").read_text(encoding="utf-8")
