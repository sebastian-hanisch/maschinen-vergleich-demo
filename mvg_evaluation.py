"""Kennzahlen und Verdikte der Experimente. Jedes Verdikt ist eine reine Funktion `verdict_*(...) -> (Art, Text)`; die App ruft `getattr(st, Art)(Text)`.

Zähleinheiten: **Folgen** (alle n! Anordnungen) für Zahlen und Mengen, **Maschinenpaare** (45) für die Paarstatistik, **Zufallsfolgen** nur im
ausgedachten Ankunftsmodell V. Alle Aussagen gelten für diese zehn Maschinen mit freier Zwischenausgabe, Mengen bis n = 8."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from math import comb, factorial

import mvg_model as MO
import mvg_patterns as P
import mvg_sets as S
from mvg_machines import KEYS, NAMES, pruefe

NBSP = " "


def zd(x):
    """Ganzzahl mit geschütztem Leerzeichen als Tausendertrenner: 15 767."""
    return f"{x:,}".replace(",", NBSP)


def pz(x, stellen=1):
    """Prozentzahl (0 bis 100) mit Dezimalkomma."""
    return f"{x:.{stellen}f}".replace(".", ",")


def pz_auto(x):
    """Prozentzahl: unter 10 mit zwei Stellen (3,55), sonst mit einer (18,3)."""
    return pz(x, 2 if x < 10 else 1)


def liste_de(items):
    items = list(items)
    if len(items) <= 1:
        return "".join(items)
    return ", ".join(items[:-1]) + " und " + items[-1]


@dataclass(frozen=True)
class Settings:
    e1_n: int = 6
    e2_a: str = "SSp"
    e2_b: str = "3Q"
    e2_n: int = 5
    e3_folge: str = "31524"
    e3_n: int = 8
    e3_d: str = "2"
    e3_seed: int = 12000
    e4_n: int = 7
    e4_a: str = "3Q"
    e4_b: str = "SSs"
    e5_n: int = 5


# ---------------------------------------------------------------- Experiment 1: die Tabelle
def tabelle_zeilen(n):
    """Zeilen der Tabelle für n: Kürzel, Name, Zahl, Anteil an n! in Prozent, erstes n mit Verlust (Zahl < n!), Zahlengruppe (gleiche Zahl = gleicher Buchstabe)."""
    zahlen = {k: S.zahl(k, n) for k in KEYS}
    gruppen = {}
    for k in KEYS:
        gruppen.setdefault(zahlen[k], len(gruppen))
    zeilen = []
    for k in KEYS:
        erstes = next((m for m in range(1, 10) if S.zahl(k, m) < factorial(m)), None)
        zeilen.append({"kuerzel": k, "name": NAMES[k], "zahl": zahlen[k], "anteil": 100 * zahlen[k] / factorial(n),
                       "erstes_n_verlust": erstes, "gruppe": gruppen[zahlen[k]]})
    return zeilen


def gleiche_zahl_gruppen(n):
    """Gruppen von mindestens zwei Maschinen mit derselben Zahl unter n!, als Liste (Zahl, [Kürzel])."""
    nach_zahl = {}
    for k in KEYS:
        nach_zahl.setdefault(S.zahl(k, n), []).append(k)
    return [(z, ks) for z, ks in nach_zahl.items() if len(ks) >= 2 and z < factorial(n)]


def verdict_tabelle(n):
    """Verdikt zu Experiment 1 (alle zehn Maschinen, 45 Paare)."""
    fak = factorial(n)
    gruppen = gleiche_zahl_gruppen(n)
    paare_zahl = sum(comb(len(ks), 2) for _, ks in gruppen)
    if not gruppen:
        return "info", (f"Bei n = {n} hat unter den zehn Maschinen kein Paar dieselbe Zahl sortierbarer Folgen unter {zd(fak)}: "
                        "es gibt noch nichts zu unterscheiden.")
    teile = [f"{liste_de(ks)} sortieren je {zd(z)} von {zd(fak)}" + (f" ({pz_auto(100 * z / fak)} %)" if i == 0 else "")
             for i, (z, ks) in enumerate(gruppen)]
    satz1 = f"n = {n}: " + "; ".join(teile) + "."
    if n > S.N_MENGEN:
        satz2 = (f" Von 45 Paaren haben {paare_zahl} dieselbe Zahl unter n! = {zd(fak)}; ob die Mengen verschieden sind, ist bei n = {n} nicht vorgerechnet "
                 f"(Mengen gibt es bis n = {S.N_MENGEN}).")
        return "info", satz1 + satz2
    gl = S.paare_gleiche_zahl(n)
    verschieden = sum(1 for _, _, gleich in gl if not gleich)
    zf, mg = S.zaehlfolgen_und_mengen(n)
    satz2 = f" Von 45 Paaren haben {len(gl)} dieselbe Zahl unter n! = {zd(fak)}, bei {verschieden} sind die Mengen verschieden."
    satz3 = f" Bis n = {n} haben die zehn Maschinen {zf} verschiedene Zählfolgen, bei n = {n} sind es {mg} verschiedene Mengen."
    return "success" if verschieden else "info", satz1 + satz2 + satz3


# ---------------------------------------------------------------- Experiment 2: gleiche Zahl, andere Menge
def zeugen_text(a, b, n):
    """Kleinste Zeugenfolgen bei n: welche Folge nur a sortiert und welche nur b (nur die Seiten, die welche haben)."""
    v = S.vergleich(a, b, n)
    teile = []
    if v["zeugen_a"]:
        teile.append(f"nur {a} sortiert {P.text_folge(v['zeugen_a'][0])}")
    if v["zeugen_b"]:
        teile.append(f"nur {b} sortiert {P.text_folge(v['zeugen_b'][0])}")
    return ", ".join(teile)


def verdict_paar(a, b, n):
    """Verdikt zu Experiment 2 für die Maschinen a und b bei n (3 bis 8)."""
    if a == b:
        return "warning", "Maschine A und Maschine B sind dieselbe: nichts zu vergleichen. Bitte zwei verschiedene Maschinen wählen."
    v = S.vergleich(a, b, n)
    za, zb, fak = S.zahl(a, n), S.zahl(b, n), factorial(n)
    nz, nm = S.erstes_n_zahl_trennt(a, b), S.erstes_n_menge_trennt(a, b)
    if v["beziehung"] == "gleich":
        return "info", (f"{a} gegen {b} bei n = {n}: dieselbe Menge, je {zd(za)} von {zd(fak)} Folgen. Für alle n bis {S.N_MENGEN} sortieren die beiden "
                        "dieselben Folgen; das ist gemessen, nicht bewiesen.")
    if za == zb:
        kopf = f"{a} gegen {b} bei n = {n}: je {zd(za)} von {zd(fak)} Folgen"
    else:
        kopf = f"{a} gegen {b} bei n = {n}: {zd(za)} gegen {zd(zb)} von {zd(fak)} Folgen"
    teil = f"; nur {a} {zd(v['nur_a'])}, nur {b} {zd(v['nur_b'])}, gemeinsam {zd(v['beide'])}."
    zt = zeugen_text(a, b, nm)
    if nz is None:
        trenn = f" Die Zahl trennt die beiden bis n = {S.N_MENGEN} nie, die Menge schon bei n = {nm} ({zt})."
    elif nm < nz:
        trenn = (f" Die Zahl trennt die beiden erst bei n = {nz} ({zd(S.zahl(a, nz))} gegen {zd(S.zahl(b, nz))}), "
                 f"die Menge schon bei n = {nm} ({zt}).")
    else:
        trenn = f" Zahl und Menge trennen die beiden beim selben n = {nm} ({zt})."
    kind = "success" if za == zb and za < fak else "info"
    return kind, kopf + teil + trenn


def gleiche_menge_hinweis(a, b):
    """Der ehrliche Negativbefund: Maschinen mit gleicher Menge (n <= 8). None, wenn das Paar nicht darunter fällt."""
    if a != b and all(S.menge(a, m) == S.menge(b, m) for m in range(1, S.N_MENGEN + 1)):
        return ("S, SQ und QS haben für n ≤ 8 dieselbe Menge (gleiche Zahl heißt hier gleiche Menge): gemessen bis n = 8, nicht bewiesen; "
                "für größere n steht die Aussage nicht.")
    return None


# ---------------------------------------------------------------- Experiment 3: meine Folge
def parse_folge(text):
    """(Folge, Fehlertext): Zahlen durch Leerzeichen oder Komma getrennt, bei höchstens neun Zahlen auch ohne Trenner (231). Prüft, ob es eine Permutation von 1..n ist."""
    t = text.strip()
    if not t:
        return None, "Leere Eingabe: bitte eine Folge wie 2341 oder 3 1 5 2 4 eingeben."
    teile = t.replace(",", " ").split()
    try:
        if len(teile) == 1 and len(teile[0]) > 1:
            werte = [int(c) for c in teile[0]]
        else:
            werte = [int(x) for x in teile]
    except ValueError:
        return None, "Keine Folge: erlaubt sind nur Ziffern, Leerzeichen und Kommas."
    n = len(werte)
    if n > 10:
        return None, f"Zu lang: höchstens 10 Zahlen (eingegeben: {n})."
    if n < 1:
        return None, "Leere Eingabe."
    if sorted(werte) != list(range(1, n + 1)):
        return None, (f"Keine Permutation der Zahlen 1 bis {n}: jede Zahl von 1 bis {n} muss genau einmal vorkommen "
                      f"(eingegeben: {' '.join(map(str, werte))}).")
    return tuple(werte), None


def pruefe_alle(folge):
    """Ergebnis der Wegsuche für alle zehn Maschinen (mit Spur, wenn sortierbar)."""
    return {k: pruefe(k, folge, spur=True) for k in KEYS}


def verdict_folge(folge, ergebnisse):
    """Verdikt zu 'Meine Folge': wer sortiert sie, Fingerabdruck und Häufigkeit unter allen n! Folgen (n <= 8)."""
    n = len(folge)
    ja = [k for k in KEYS if ergebnisse[k].sortierbar]
    text = f"{P.text_folge(folge)}: sortiert von {liste_de(ja) if ja else 'keiner der zehn Maschinen'} ({len(ja)} von 10)."
    if n <= S.N_MENGEN:
        h = S.haeufigkeit_fingerabdruck(tuple(ja), n)
        text += f" Diesen Fingerabdruck (dieselbe Menge sortierender Maschinen) haben {zd(h)} von {zd(factorial(n))} Folgen der Länge {n}."
    else:
        text += f" Für n = {n} sind die Mengen nicht vorgerechnet, daher keine Häufigkeit des Fingerabdrucks."
    return "success" if ja else "warning", text


def verdict_gleichverteilt(n):
    """Gleichverteilte Folgen der Länge n (n <= 8, exakt aus den Mengen): mittlere Zahl sortierender Maschinen und Folgen, die keine Maschine sortiert."""
    v = S.verteilung_zahl_maschinen(n)
    keine = v.get(0, 0)
    fak = factorial(n)
    mittel = S.mittlere_zahl_maschinen(n)
    return "info", (f"Bei n = {n}, gleichverteilt über alle {zd(fak)} Folgen: im Mittel sortieren {pz(mittel, 2)} von 10 Maschinen eine Folge; "
                    f"{zd(keine)} Folgen ({pz(100 * keine / fak, 2)} %) sortiert keine einzige der zehn.")


def d_wert(text):
    """Verweilzeit-Mittel D als Zahl oder None (∞)."""
    return None if text == "∞" else float(text.replace(",", "."))


def modell_stichprobe(n, d_text, seed):
    """Live-Stichprobe aus dem Modell: (Anteile je Maschine, Mittel Maschinen, Zahl Folgen, Differenzen S-2Q und 3Q-SSp mit Fehler)."""
    d = d_wert(d_text)
    folgen_liste = MO.stichprobe(n, d, MO.ANZAHL_LIVE, seed)
    zaehler = MO.zaehle_maschinen(folgen_liste, n)
    paare = MO.zaehle_paare(folgen_liste, n)
    anz = MO.ANZAHL_LIVE
    return {"anteile": {k: zaehler[k] / anz for k in KEYS}, "mittel": sum(zaehler.values()) / anz, "anzahl": anz, "paare": paare}


def verdict_modell(n, d_text, seed, stich):
    """Verdikt zur Live-Stichprobe: Anteile der Stapel-Maschinen und ob sich S und 2Q (gleiche Zahl) im Anteil unterscheiden lassen (4 Standardfehler der Differenz)."""
    a = stich["anteile"]
    anz = stich["anzahl"]
    na, nb, _ = stich["paare"]["S|2Q"]
    diff, se = MO.differenz_und_fehler(na, nb, anz)
    innerhalb = abs(diff) <= 4 * se
    sa, sb, _ = stich["paare"]["3Q|SSp"]
    d2, se2 = MO.differenz_und_fehler(sa, sb, anz)
    innerhalb2 = abs(d2) <= 4 * se2
    txt = (f"Modell V (ausgedacht), n = {n}, D = {d_text}, {zd(anz)} Folgen, Zufalls-Seed {seed}: S {pz(100 * a['S'])} %, 2Q {pz(100 * a['2Q'])} %, "
           f"3Q {pz(100 * a['3Q'])} %, SSp {pz(100 * a['SSp'])} %. "
           f"Differenz S minus 2Q: {pz(100 * diff, 2)} Punkte (Standardfehler {pz(100 * se, 2)}), "
           f"{'innerhalb' if innerhalb else 'außerhalb'} von vier Standardfehlern; "
           f"3Q minus SSp: {pz(100 * d2, 2)} Punkte (Standardfehler {pz(100 * se2, 2)}), {'innerhalb' if innerhalb2 else 'außerhalb'}. "
           "Gilt für dieses Modell und diese Stichprobe, nicht für echte Ankunftsfolgen.")
    return "info", txt


def frozen_zeilen():
    """Die vorgerechnete Tabelle (n = 8, 20 000 Folgen je D): je D Anteile je Maschine und die Differenzen der beiden Paare mit Fehler."""
    daten = MO.vorgerechnet()
    zeilen = []
    for z in daten["zeilen"]:
        anz = z["anzahl"]
        paare = {}
        for p, (na, nb, _) in z["paare"].items():
            d, se = MO.differenz_und_fehler(na, nb, anz)
            paare[p] = (d, se)
        zeilen.append({"d": z["d"], "seed": z["seed"], "anzahl": anz, "anteile": {k: z["zaehler"][k] / anz for k in KEYS},
                       "mittel": sum(z["zaehler"].values()) / anz, "paare": paare})
    return zeilen


def verdict_frozen(zeilen):
    """Zählung über die sieben Zeilen: in wie vielen liegt die Differenz S minus 2Q (bzw. 3Q minus SSp) innerhalb von vier Standardfehlern."""
    k = len(zeilen)
    innen1 = sum(1 for z in zeilen if abs(z["paare"]["S|2Q"][0]) <= 4 * z["paare"]["S|2Q"][1])
    innen2 = sum(1 for z in zeilen if abs(z["paare"]["3Q|SSp"][0]) <= 4 * z["paare"]["3Q|SSp"][1])
    gross1 = max(abs(z["paare"]["S|2Q"][0]) for z in zeilen) * 100
    gross2 = max(abs(z["paare"]["3Q|SSp"][0]) for z in zeilen) * 100
    anz = zeilen[0]["anzahl"]
    text = (f"Vorgerechnet, n = 8, {zd(anz)} Folgen je D ({k} Werte von D): Die Differenz der Anteile von S und 2Q liegt in {innen1} von {k} Zeilen "
            f"innerhalb von vier Standardfehlern der Differenz (größter Betrag {pz(gross1, 2)} Punkte); bei 3Q und SSp in {innen2} von {k} "
            f"(größter Betrag {pz(gross2, 2)} Punkte).")
    if innen1 == k and innen2 == k:
        text += " Mit dieser Stichprobengröße lässt sich im Modell kein Unterschied der Anteile feststellen; die Mengen unterscheiden sich trotzdem."
    else:
        text += " In den Zeilen außerhalb des Bandes unterscheiden sich die Anteile im Modell auch."
    return "info", text


# ---------------------------------------------------------------- Experiment 4: wer kann mehr?
def verdict_ordnung(n):
    """Verdikt zu Experiment 4: Kanten und unvergleichbare Paare bei n."""
    o = S.ordnung(n)
    return "info", (f"n = {n}: {len(o['klassen'])} verschiedene Mengen unter den zehn Maschinen, {len(o['kanten'])} echte Teilmengenkanten (ohne Zwischenglied), "
                    f"{len(o['unvergleichbar'])} unvergleichbare Paare (je Vertreter einer Klasse). Mehr Behälter heißt nicht mehr Folgen, wenn zwei Mengen "
                    "unvergleichbar sind: jede sortiert Folgen, die die andere nicht schafft.")


def verdict_ordnung_paar(a, b, n):
    if a == b:
        return "warning", "Maschine A und Maschine B sind dieselbe: bitte zwei verschiedene Maschinen wählen."
    v = S.vergleich(a, b, n)
    zahlen = f"nur {a}: {zd(v['nur_a'])}, nur {b}: {zd(v['nur_b'])}, gemeinsam {zd(v['beide'])}"
    if v["beziehung"] == "gleich":
        return "info", f"{a} und {b} sortieren bei n = {n} dieselbe Menge ({zd(v['beide'])} Folgen)."
    if v["beziehung"] == "A in B":
        return "info", f"Bei n = {n} liegt die Menge von {a} echt in der von {b} ({zahlen}); jede Folge, die {a} sortiert, sortiert auch {b}."
    if v["beziehung"] == "B in A":
        return "info", f"Bei n = {n} liegt die Menge von {b} echt in der von {a} ({zahlen}); jede Folge, die {b} sortiert, sortiert auch {a}."
    za, zb = P.text_folge(v["zeugen_a"][0]), P.text_folge(v["zeugen_b"][0])
    return "success", (f"{a} und {b} sind bei n = {n} unvergleichbar: {zahlen}. Zeugen: nur {a} sortiert {za}, nur {b} sortiert {zb}. "
                       "Keine der beiden Mengen liegt in der anderen.")


# ---------------------------------------------------------------- Experiment 5: zwei Stapel sind vier Maschinen
def verdict_vier(n):
    z = S.vier_zwei_stapel(n)
    teil = (f"n = {n}: zwei Stapel in Serie {zd(z['SSs'])}, zwei Stapel parallel {zd(z['SSp'])}, zwei West-Durchläufe {zd(z['W2'])}, "
            f"zwei Pop-Stack-Durchläufe {zd(z['P2'])} von {zd(z['n!'])} Folgen.")
    beziehung = S.vergleich("P2", "W2", n)["beziehung"]
    teil2 = " " + {"unvergleichbar": "West-2 und Pop-2 sind bei diesem n unvergleichbar.", "gleich": "West-2 und Pop-2 sind bei diesem n gleich.",
                   "A in B": "Pop-2 liegt bei diesem n in West-2.", "B in A": "West-2 liegt bei diesem n in Pop-2."}[beziehung]
    erste = next((m for m in range(1, S.N_MENGEN + 1) if S.menge("W2", m) & ~S.menge("SSp", m)), None)
    if erste is None:
        teil3 = f" West-2 liegt für alle n bis {S.N_MENGEN} in zwei Stapeln parallel."
    else:
        zeugen = S.mitglieder(S.menge("W2", erste) & ~S.menge("SSp", erste), erste)
        teil3 = (f" West-2 liegt bis n = {erste - 1} in zwei Stapeln parallel; bei n = {erste} nicht mehr "
                 f"({len(zeugen)} Folge{'n' if len(zeugen) > 1 else ''}, kleinste {P.text_folge(zeugen[0])}).")
    return "info", teil + teil2 + teil3


def kleine_n_fehlfolgen(key, n):
    """Folgen der Länge n, die die Maschine (oder Regel) nicht sortiert (nur sinnvoll für n <= 5, sonst sehr lang)."""
    return S.mitglieder(S.alle_maske(n) & ~S.menge(key, n), n)
