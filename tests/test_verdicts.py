"""Verdikte an handgesetzten Fällen (DEMO-PLAYBOOK §12): jede Zahl im Text und jede Art (success, info, warning) steht hier.

Die Erwartungen sind von Hand aus den Handbeispielen oder aus den Zahlen der Maschinen abgeleitet (siehe test_sets.py, test_machines.py), nicht aus der Ausgabe abgeschrieben."""

import mvg_evaluation as ev
import mvg_model as MO

NB = " "


def test_zd_und_pz_formate():
    assert ev.zd(15767) == f"15{NB}767" and ev.zd(5) == "5"
    assert ev.pz(18.333, 1) == "18,3" and ev.pz_auto(3.5466) == "3,55" and ev.pz_auto(18.333) == "18,3"
    assert ev.liste_de(["S", "2Q", "SQ"]) == "S, 2Q und SQ" and ev.liste_de(["S"]) == "S" and ev.liste_de([]) == ""


def test_verdikt_tabelle_n6_nennt_132_513_sieben_paare_vier_verschieden_sechs_folgen_acht_mengen():
    kind, text = ev.verdict_tabelle(6)
    assert kind == "success"
    assert "S, 2Q, SQ und QS sortieren je 132 von 720 (18,3 %)" in text and "3Q und SSp sortieren je 513 von 720" in text
    assert "Von 45 Paaren haben 7 dieselbe Zahl unter n! = 720, bei 4 sind die Mengen verschieden" in text
    assert "6 verschiedene Zählfolgen" in text and "8 verschiedene Mengen" in text


def test_verdikt_tabelle_n3_kleinster_fall_5_von_6():
    kind, text = ev.verdict_tabelle(3)
    assert kind == "success" and "S, 2Q, SQ und QS sortieren je 5 von 6 (83,3 %)" in text and "bei 3 sind die Mengen verschieden" in text


def test_verdikt_tabelle_n2_kein_paar_unter_n_fakultaet():
    kind, text = ev.verdict_tabelle(2)
    assert kind == "info" and "kein Paar dieselbe Zahl" in text and "unter 2" in text


def test_verdikt_tabelle_n9_nennt_keine_mengen():
    kind, text = ev.verdict_tabelle(9)
    assert kind == "info" and "nicht vorgerechnet" in text and f"4{NB}862" in text and "Von 45 Paaren haben 6 dieselbe Zahl" in text


def test_verdikt_paar_ssp_gegen_3q_n5():
    kind, text = ev.verdict_paar("SSp", "3Q", 5)
    assert kind == "success"
    assert "je 103 von 120" in text and "nur SSp 17, nur 3Q 17, gemeinsam 86" in text
    assert f"erst bei n = 7 (2{NB}760 gegen 2{NB}761)" in text and "die Menge schon bei n = 4" in text and "nur SSp sortiert 4321, nur 3Q sortiert 2341" in text


def test_verdikt_paar_s_gegen_2q_n3_zahl_trennt_nie():
    kind, text = ev.verdict_paar("S", "2Q", 3)
    assert kind == "success" and "je 5 von 6" in text and "Die Zahl trennt die beiden bis n = 8 nie, die Menge schon bei n = 3" in text
    assert "nur S sortiert 321, nur 2Q sortiert 231" in text


def test_verdikt_paar_gleiche_menge_ist_info_und_sagt_nicht_bewiesen():
    kind, text = ev.verdict_paar("S", "SQ", 6)
    assert kind == "info" and "dieselbe Menge" in text and "gemessen, nicht bewiesen" in text
    assert ev.gleiche_menge_hinweis("S", "QS") is not None and ev.gleiche_menge_hinweis("S", "2Q") is None and ev.gleiche_menge_hinweis("S", "S") is None


def test_verdikt_paar_dieselbe_maschine_ist_eine_warnung():
    assert ev.verdict_paar("S", "S", 5)[0] == "warning" and ev.verdict_ordnung_paar("P", "P", 5)[0] == "warning"


def test_verdikt_paar_verschiedene_zahlen_nennt_beide_zahlen():
    kind, text = ev.verdict_paar("3Q", "SSs", 8)
    assert kind == "info" and f"15{NB}767 gegen 39{NB}374 von 40{NB}320" in text and f"nur 3Q 406, nur SSs 24{NB}013, gemeinsam 15{NB}361" in text


def test_verdikt_folge_2341_vier_von_zehn_und_haeufigkeit():
    folge, fehler = ev.parse_folge("2341")
    assert fehler is None
    kind, text = ev.verdict_folge(folge, ev.pruefe_alle(folge))
    assert kind == "success" and text.startswith("2341: sortiert von 2Q, 3Q, SSs und SpQ (4 von 10).") and "von 24 Folgen der Länge 4" in text


def test_verdikt_folge_n10_nennt_keine_haeufigkeit():
    folge, _ = ev.parse_folge("10 9 8 7 6 5 4 3 2 1")
    kind, text = ev.verdict_folge(folge, ev.pruefe_alle(folge))
    assert "von 10)" in text and "nicht vorgerechnet" in text


def test_verdikt_gleichverteilt_n8_508_folgen_keine_maschine():
    kind, text = ev.verdict_gleichverteilt(8)
    assert kind == "info" and "2,58 von 10" in text and f"508 Folgen (1,26 %) sortiert keine einzige" in text and f"40{NB}320" in text


def test_verdikt_ordnung_n8_acht_mengen_neun_kanten_zehn_paare():
    kind, text = ev.verdict_ordnung(8)
    assert "8 verschiedene Mengen" in text and "9 echte Teilmengenkanten" in text and "10 unvergleichbare Paare" in text


def test_verdikt_ordnung_paar_unvergleichbar_teilmenge_und_gleich():
    kind, text = ev.verdict_ordnung_paar("3Q", "SSs", 8)
    assert kind == "success" and "unvergleichbar" in text and "nur 3Q sortiert 13546872, nur SSs sortiert 12348765" in text
    kind, text = ev.verdict_ordnung_paar("2Q", "3Q", 8)
    assert kind == "info" and "echt in der von 3Q" in text and "nur 2Q: 0" in text
    kind, text = ev.verdict_ordnung_paar("3Q", "2Q", 8)
    assert "Menge von 2Q echt in der von 3Q" in text
    assert "dieselbe Menge" in ev.verdict_ordnung_paar("S", "SQ", 8)[1]


def test_verdikt_vier_n4_und_n5_n8():
    kind, text = ev.verdict_vier(4)
    assert "zwei Stapel in Serie 24, zwei Stapel parallel 23, zwei West-Durchläufe 22, zwei Pop-Stack-Durchläufe 16 von 24" in text
    assert "Pop-2 liegt bei diesem n in West-2" in text and "bei n = 8 nicht mehr (1 Folge, kleinste 58274163)" in text
    assert "unvergleichbar" in ev.verdict_vier(5)[1]


def test_parse_folge_akzeptiert_trenner_und_lehnt_nicht_permutationen_ab():
    assert ev.parse_folge("2341") == ((2, 3, 4, 1), None) and ev.parse_folge("3, 1, 2") == ((3, 1, 2), None)
    assert ev.parse_folge("1 2 3 4 5 6 7 8 9 10")[0] == tuple(range(1, 11))
    assert ev.parse_folge("")[0] is None and "Leere" in ev.parse_folge("   ")[1]
    assert "Permutation" in ev.parse_folge("1123")[1] and "Permutation" in ev.parse_folge("2 3 4")[1]
    assert "Zu lang" in ev.parse_folge("1 2 3 4 5 6 7 8 9 10 11")[1] and "nur Ziffern" in ev.parse_folge("a b")[1]


def test_verdikt_modell_nennt_zahlen_und_modellvorbehalt():
    stich = {"anteile": {k: 0.5 for k in ("S", "2Q", "3Q", "SSp")} | {"Q": 0, "SSs": 1, "SQ": 0.5, "QS": 0.5, "SpQ": 0.9, "P": 0.1}, "mittel": 4.0,
             "anzahl": 2000, "paare": {"S|2Q": [100, 100, 900], "3Q|SSp": [50, 10, 940]}}
    kind, text = ev.verdict_modell(8, "4", 12000, stich)
    assert "Modell V (ausgedacht), n = 8, D = 4, 2" in text and "Zufalls-Seed 12000" in text and "S 50,0 %, 2Q 50,0 %" in text
    assert "Differenz S minus 2Q: 0,00 Punkte" in text and "innerhalb von vier Standardfehlern" in text
    # 3Q minus SSp: (50 - 10) / 2000 = 2,0 Punkte; Var = (60 - 1600 / 2000) / 2000^2, SE = 0,387 Punkte: 2,0 liegt außerhalb von vier SE (1,55)
    assert "3Q minus SSp: 2,00 Punkte" in text and "außerhalb" in text and "nicht für echte Ankunftsfolgen" in text


def test_verdikt_frozen_zaehlt_zeilen_innerhalb_von_vier_standardfehlern():
    zeilen = [{"anzahl": 20000, "paare": {"S|2Q": (0.001, 0.002), "3Q|SSp": (0.02, 0.002)}},
              {"anzahl": 20000, "paare": {"S|2Q": (-0.005, 0.001), "3Q|SSp": (0.001, 0.002)}}]
    kind, text = ev.verdict_frozen(zeilen)
    assert "in 1 von 2 Zeilen" in text and "größter Betrag 0,50 Punkte" in text and "bei 3Q und SSp in 1 von 2" in text and "größter Betrag 2,00 Punkte" in text
    assert "auch." in text and "kein Unterschied" not in text
    alle_innen = [{"anzahl": 20000, "paare": {"S|2Q": (0.001, 0.002), "3Q|SSp": (0.0, 0.002)}}] * 3
    assert "in 3 von 3 Zeilen" in ev.verdict_frozen(alle_innen)[1] and "kein Unterschied der Anteile" in ev.verdict_frozen(alle_innen)[1]


def test_modell_stichprobe_live_hat_2000_folgen_und_ist_reproduzierbar():
    a = ev.modell_stichprobe(6, "2", 5)
    assert a["anzahl"] == MO.ANZAHL_LIVE == 2000 and a == ev.modell_stichprobe(6, "2", 5)
    assert ev.d_wert("0,5") == 0.5 and ev.d_wert("∞") is None
