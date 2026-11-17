"""Vorgerechnete Mengen sortierbarer Folgen (n <= 8) als Bitmasken, Vergleiche, Fingerabdrücke, Ordnung der Maschinen.

Jede Menge ist eine Ganzzahl: Bit i gehört zur i-ten Folge in lexikographischer Reihenfolge aller n! Folgen (Ränge nach dem Lehmer-Code).
Mengenoperationen sind dann Ganzzahloperationen. Die Mengen stehen in data/mvg_sets.json (vorgerechnet von tools/mvg_make_sets.py,
`--check` rechnet sie neu); für n = 9 gibt es nur Zahlen, keine Mengen (die Aufzählung wäre live zu teuer)."""

from __future__ import annotations

import json
from functools import lru_cache
from itertools import combinations, permutations
from math import factorial
from pathlib import Path

from mvg_machines import KEYS

DATEI = Path(__file__).resolve().parent / "data" / "mvg_sets.json"
N_MENGEN = 8  # größtes n mit vorgerechneten Mengen
EXTRA = ("W2", "P2")  # zwei Durchlauf-Regeln neben den zehn Maschinen (Experiment 5)


@lru_cache(maxsize=None)
def folgen(n):
    """Alle n! Folgen in lexikographischer Reihenfolge (Index = Rang)."""
    return tuple(permutations(range(1, n + 1)))


def rang(p):
    """Rang einer Folge unter allen n! Folgen in lexikographischer Reihenfolge (Lehmer-Code)."""
    n = len(p)
    r = 0
    for i, v in enumerate(p):
        kleiner = sum(1 for w in p[i + 1 :] if w < v)
        r += kleiner * factorial(n - 1 - i)
    return r


def maske(folgen_liste):
    m = 0
    for p in folgen_liste:
        m |= 1 << rang(p)
    return m


def zaehle(m):
    return m.bit_count()


def mitglieder(m, n, grenze=None):
    """Die Folgen einer Maske in lexikographischer Reihenfolge, höchstens `grenze` Folgen."""
    alle = folgen(n)
    res = []
    while m and (grenze is None or len(res) < grenze):
        tief = m & -m
        res.append(alle[tief.bit_length() - 1])
        m ^= tief
    return res


def alle_maske(n):
    return (1 << factorial(n)) - 1


@lru_cache(maxsize=1)
def lade():
    return json.loads(DATEI.read_text(encoding="utf-8"))


def menge(key, n):
    """Maske der von `key` sortierbaren Folgen der Länge n (n = 1 bis 8; key: eine der zehn Maschinen oder W2, P2)."""
    if not 1 <= n <= N_MENGEN:
        raise ValueError(f"Mengen gibt es nur für n = 1 bis {N_MENGEN}")
    return int(lade()["mengen"][key][str(n)], 16)


@lru_cache(maxsize=None)
def _bytes(key, n):
    return menge(key, n).to_bytes((factorial(n) + 7) // 8, "little")


def ist_mitglied(key, n, r):
    """Gehört die Folge mit dem Rang r zur Menge von `key` (n <= 8)? Schneller als eine Verschiebung der ganzen Maske."""
    return bool((_bytes(key, n)[r >> 3] >> (r & 7)) & 1)


def zahl(key, n):
    """Zahl der sortierbaren Folgen: aus den Mengen (n <= 8) oder aus der Tabelle für n = 9."""
    if n <= N_MENGEN:
        return zaehle(menge(key, n))
    return lade()["n9"][key]["zahl"]


def quelle_n9(key):
    return lade()["n9"][key]["quelle"]


def anteil(key, n):
    return zahl(key, n) / factorial(n)


# ---------------------------------------------------------------- Vergleich zweier Maschinen
def vergleich(a, b, n):
    """Nur A, beide, nur B und die Beziehung der beiden Mengen."""
    ma, mb = menge(a, n), menge(b, n)
    nur_a, nur_b, beide = ma & ~mb, mb & ~ma, ma & mb
    if not nur_a and not nur_b:
        beziehung = "gleich"
    elif not nur_a:
        beziehung = "A in B"
    elif not nur_b:
        beziehung = "B in A"
    else:
        beziehung = "unvergleichbar"
    return {"nur_a": zaehle(nur_a), "beide": zaehle(beide), "nur_b": zaehle(nur_b), "beziehung": beziehung,
            "zeugen_a": mitglieder(nur_a, n, 5), "zeugen_b": mitglieder(nur_b, n, 5)}


def erstes_n_zahl_trennt(a, b, nmax=N_MENGEN):
    return next((n for n in range(1, nmax + 1) if zahl(a, n) != zahl(b, n)), None)


def erstes_n_menge_trennt(a, b, nmax=N_MENGEN):
    return next((n for n in range(1, nmax + 1) if menge(a, n) != menge(b, n)), None)


def paare_gleiche_zahl(n, schluessel=KEYS):
    """Maschinenpaare mit gleicher Zahl unter n! (Zähleinheit: Maschinenpaare), als Liste (a, b, gleiche_menge)."""
    res = []
    for a, b in combinations(schluessel, 2):
        za, zb = zahl(a, n), zahl(b, n)
        if za == zb and za < factorial(n):
            res.append((a, b, menge(a, n) == menge(b, n)))
    return res


def zaehlfolgen_und_mengen(n, schluessel=KEYS):
    """(Zahl verschiedener Zählfolgen n' = 1..n, Zahl verschiedener Mengen bei n)."""
    folgen_z = {tuple(zahl(k, m) for m in range(1, n + 1)) for k in schluessel}
    mengen_n = {menge(k, n) for k in schluessel} if n <= N_MENGEN else None
    return len(folgen_z), (len(mengen_n) if mengen_n is not None else None)


# ---------------------------------------------------------------- Fingerabdruck
def fingerabdruck(p):
    """Menge der Maschinen, die p sortieren (Tupel der Schlüssel in der Reihenfolge von KEYS), für n <= 8."""
    n, r = len(p), rang(p)
    return tuple(k for k in KEYS if (menge(k, n) >> r) & 1)


def haeufigkeit_fingerabdruck(fp, n):
    """Zahl der Folgen der Länge n mit genau diesem Fingerabdruck (n <= 8)."""
    m = alle_maske(n)
    for k in KEYS:
        m &= menge(k, n) if k in fp else ~menge(k, n)
    return zaehle(m)


def verteilung_zahl_maschinen(n):
    """{Zahl der sortierenden Maschinen: Zahl der Folgen} für n <= 8 (Zähleinheit: Folgen)."""
    masken = [menge(k, n) for k in KEYS]
    verteilung = {}
    for p_rang in range(factorial(n)):
        z = sum((m >> p_rang) & 1 for m in masken)
        verteilung[z] = verteilung.get(z, 0) + 1
    return dict(sorted(verteilung.items()))


def zahl_verschiedener_fingerabdruecke(n):
    return len({fingerabdruck(p) for p in folgen(n)})


def mittlere_zahl_maschinen(n):
    """Mittlere Zahl der Maschinen, die eine gleichverteilte Folge der Länge n sortieren (n <= 8)."""
    return sum(zahl(k, n) for k in KEYS) / factorial(n)


# ---------------------------------------------------------------- Ordnung (Teilmengen)
def klassen_gleicher_menge(n, schluessel=KEYS):
    klassen = []
    for k in schluessel:
        for kl in klassen:
            if menge(kl[0], n) == menge(k, n):
                kl.append(k)
                break
        else:
            klassen.append([k])
    return klassen


def ordnung(n, schluessel=KEYS):
    """Klassen gleicher Menge, Kanten des Ordnungsdiagramms (echte Teilmenge ohne Zwischenglied) und unvergleichbare Paare (je ein Vertreter)."""
    klassen = klassen_gleicher_menge(n, schluessel)
    rep = [kl[0] for kl in klassen]
    echt = {(a, b) for a in rep for b in rep if a != b and menge(a, n) & ~menge(b, n) == 0 and menge(a, n) != menge(b, n)}
    kanten = sorted((a, b) for (a, b) in echt if not any((a, c) in echt and (c, b) in echt for c in rep))
    unvergleichbar = [(a, b) for a, b in combinations(rep, 2) if (a, b) not in echt and (b, a) not in echt]
    return {"klassen": klassen, "kanten": kanten, "unvergleichbar": unvergleichbar}


def vier_zwei_stapel(n):
    """Zahlen der vier „zwei Stapel“ (SSs, SSp, West-2, Pop-2) und n!."""
    return {"SSs": zahl("SSs", n), "SSp": zahl("SSp", n), "W2": zahl("W2", n), "P2": zahl("P2", n), "n!": factorial(n)}
