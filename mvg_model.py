"""Das ausgedachte Ankunftsmodell V (und U): Zufallsfolgen für Experiment 3. KEINE reale Ankunftsfolge, kein echter Betrieb.

Modell V: n Container kommen zu den Zeiten 1, 2, ..., n an und bleiben eine exponentialverteilte Verweilzeit mit Mittel D (gemessen in
Ankunftsabständen). Die Folge p ist der Abholrang: p_i = Rang der Abfahrtszeit von Container i unter allen n Abfahrtszeiten (Gleichstand
nach Ankunftsindex; bei Gleitkommazeiten praktisch nie). Eine Maschine sortiert p, wenn sie die Container in der Reihenfolge der Abfahrt
ausgeben kann. Modell V nutzt nur die Rangfolge der Abfahrten. D = ∞ (Modell U) ist die Gleichverteilung über alle n! Folgen.
Es gibt in den Quellen keine reale Ankunftsfolge; die Zahlen gelten für dieses Modell, nicht für einen Hafen oder Bahnhof.

Zufall ausschließlich aus mvg_rng.py (SplitMix64, plattformfest); die Zählungen sind deshalb auf jeder Plattform ganzzahlig gleich."""

from __future__ import annotations

import json
from math import sqrt
from pathlib import Path

import mvg_sets as S
from mvg_machines import KEYS
from mvg_rng import SplitMix64

DATEI = Path(__file__).resolve().parent / "data" / "mvg_modell_v.json"
D_WERTE = (0.5, 1.0, 2.0, 4.0, 8.0, 16.0, None)  # None = ∞ (Modell U, gleichverteilt)
ANZAHL_LIVE = 2000
ANZAHL_FROZEN = 20000
BLOCK = 2000  # die ersten BLOCK Folgen je D sind in der Datei zusätzlich einzeln gezählt (schnelle Neuprüfung)
SEED_BASIS = 20000  # vorgerechnete Zeilen: Zufalls-Seed = SEED_BASIS + Index des D-Werts


def d_text(d):
    return "∞" if d is None else (f"{d:g}".replace(".", ","))


def folge(rng, n, d):
    """Eine Zufallsfolge der Länge n: Modell V mit Verweilzeit-Mittel d, bei d = None Modell U (gleichverteilt)."""
    if d is None:
        p = list(range(1, n + 1))
        rng.shuffle(p)
        return tuple(p)
    zeiten = [(i + 1) + rng.expovariate(d) for i in range(n)]
    ordnung = sorted(range(n), key=lambda i: (zeiten[i], i))
    rang = [0] * n
    for r, i in enumerate(ordnung):
        rang[i] = r + 1
    return tuple(rang)


def stichprobe(n, d, anzahl, seed):
    """`anzahl` Zufallsfolgen aus einem Strom mit dem Zufalls-Seed `seed`."""
    rng = SplitMix64(seed)
    return [folge(rng, n, d) for _ in range(anzahl)]


def zaehle_maschinen(folgen_liste, n):
    """Je Maschine die Zahl der Folgen, die sie sortiert (n <= 8), und die Summe über alle Maschinen (für das Mittel)."""
    zaehler = {k: 0 for k in KEYS}
    for p in folgen_liste:
        r = S.rang(p)
        for k in KEYS:
            if S.ist_mitglied(k, n, r):
                zaehler[k] += 1
    return zaehler


def anteile(n, d, anzahl, seed):
    """Anteil (0 bis 1) je Maschine unter `anzahl` Zufallsfolgen und mittlere Zahl sortierender Maschinen je Folge."""
    z = zaehle_maschinen(stichprobe(n, d, anzahl, seed), n)
    return {k: z[k] / anzahl for k in KEYS}, sum(z.values()) / anzahl


def band(anteil_wert, anzahl, faktor=4.0):
    """Halbe Breite des Bandes (Standardfehler mal `faktor`) für einen Anteil aus `anzahl` Folgen."""
    return faktor * sqrt(max(anteil_wert * (1 - anteil_wert), 1e-12) / anzahl)


def lade():
    return json.loads(DATEI.read_text(encoding="utf-8"))


def vorgerechnet():
    """Die eingefrorene Tabelle (n = 8): je D die Zählungen über 20 000 Folgen und über die ersten 2000."""
    return lade()


PAARE = (("S", "2Q"), ("3Q", "SSp"))  # die beiden Paare mit (fast) gleicher Zahl, deren Anteile im Modell verglichen werden


def zaehle_paare(folgen_liste, n):
    """Je Paar (a, b) in PAARE: [nur a, nur b, beide] unter den Folgen (n <= 8). Gebraucht für den Standardfehler der Differenz zweier Anteile
    aus derselben Stichprobe: Var(Anteil a minus Anteil b) = (nur a + nur b - (nur a - nur b)^2 / N) / N^2."""
    res = {f"{a}|{b}": [0, 0, 0] for a, b in PAARE}
    for p in folgen_liste:
        r = S.rang(p)
        for a, b in PAARE:
            ia, ib = S.ist_mitglied(a, n, r), S.ist_mitglied(b, n, r)
            if ia and ib:
                res[f"{a}|{b}"][2] += 1
            elif ia:
                res[f"{a}|{b}"][0] += 1
            elif ib:
                res[f"{a}|{b}"][1] += 1
    return res


def differenz_und_fehler(nur_a, nur_b, anzahl):
    """(Anteil a minus Anteil b, Standardfehler dieser Differenz) aus den Zählungen `nur a`, `nur b` unter `anzahl` Folgen (gepaarte Stichprobe)."""
    d = (nur_a - nur_b) / anzahl
    var = (nur_a + nur_b - (nur_a - nur_b) ** 2 / anzahl) / anzahl**2
    return d, sqrt(max(var, 0.0))
