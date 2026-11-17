"""Unabhängige Referenz für die Tests: eigener Abspieler für Spuren, eigene Wegsuche und eigene Musterprüfer.

Nichts davon benutzt mvg_machines oder mvg_patterns. Die Netze sind hier noch einmal in einer anderen Darstellung angeschrieben (Behältertyp,
Eingang, Umsetzen, Ausgang), das ist die Festlegung der Maschinen selbst und kein Rechenweg."""

from collections import deque
from itertools import combinations, permutations

# (Behältertypen, Eingang, Umsetzen, Ausgang)
NETZE = {
    "Q": ("Q", (0,), (), (0,)),
    "S": ("S", (0,), (), (0,)),
    "2Q": ("QQ", (0, 1), (), (0, 1)),
    "3Q": ("QQQ", (0, 1, 2), (), (0, 1, 2)),
    "SSs": ("SS", (0,), ((0, 1),), (1,)),
    "SSp": ("SS", (0, 1), (), (0, 1)),
    "SQ": ("SQ", (0,), ((0, 1),), (1,)),
    "QS": ("QS", (0,), ((0, 1),), (1,)),
    "SpQ": ("SQ", (0, 1), (), (0, 1)),
    "P": ("P", (0,), (), (0,)),
}
SCHLUESSEL = tuple(NETZE)


def spiele_ab(key, folge, schritte):
    """Spielt eine Schrittfolge mit Listen/deque nach. Gibt (True, '') zurück, wenn jeder Schritt zulässig ist, die Eingabe
    genau in der Reihenfolge der Folge verbraucht wird, am Ende alle Behälter leer sind und die Ausgabe 1..n ist."""
    typen, eingang, umsetzen, ausgang = NETZE[key]
    beh = [deque() for _ in typen]
    naechste = 0
    aus = []

    def entnehmen(b):
        if not beh[b]:
            return None
        return beh[b].popleft() if typen[b] == "Q" else beh[b].pop()

    def zugaenglich(b):
        if not beh[b]:
            return None
        return beh[b][0] if typen[b] == "Q" else beh[b][-1]

    for s in schritte:
        if s[0] == "ein":
            _, v, b = s
            if b not in eingang or naechste >= len(folge) or folge[naechste] != v:
                return False, f"Einlegen {s}"
            beh[b].append(v)
            naechste += 1
        elif s[0] == "um":
            _, v, a, b = s
            if (a, b) not in umsetzen or zugaenglich(a) != v:
                return False, f"Umsetzen {s}"
            beh[b].append(entnehmen(a))
        elif s[0] == "aus":
            _, v, a = s
            if a not in ausgang or typen[a] == "P" or zugaenglich(a) != v:
                return False, f"Ausgeben {s}"
            aus.append(entnehmen(a))
        elif s[0] == "aus_pop":
            _, werte, a = s
            if a not in ausgang or typen[a] != "P" or list(werte) != list(reversed(beh[a])):
                return False, f"Pop-Leeren {s}"
            aus.extend(werte)
            beh[a].clear()
        else:
            return False, f"unbekannter Schritt {s}"
    if naechste != len(folge) or any(beh) or aus != list(range(1, len(folge) + 1)):
        return False, f"Ende: Eingabe {naechste}/{len(folge)}, Behälter {[list(b) for b in beh]}, Ausgabe {aus}"
    return True, ""


def sortierbar(key, folge):
    """Eigene Wegsuche (Breitensuche über Zustände (Eingabeposition, Behälterinhalte, Zahl der Ausgaben)); ausgegeben wird nur die nächste gesuchte Zahl, ohne Abkürzungen."""
    typen, eingang, umsetzen, ausgang = NETZE[key]
    n = len(folge)
    start = (0, tuple(() for _ in typen), 0)
    gesehen = {start}
    todo = deque([start])
    while todo:
        i, inh, m = todo.popleft()
        if m == n:
            return True
        nachfolger = []
        if i < n:
            for b in eingang:
                neu = list(inh)
                neu[b] = neu[b] + (folge[i],)
                nachfolger.append((i + 1, tuple(neu), m))
        for a, b in umsetzen:
            if inh[a]:
                x = inh[a][0] if typen[a] == "Q" else inh[a][-1]
                neu = list(inh)
                neu[a] = inh[a][1:] if typen[a] == "Q" else inh[a][:-1]
                neu[b] = neu[b] + (x,)
                nachfolger.append((i, tuple(neu), m))
        for a in ausgang:
            if not inh[a]:
                continue
            if typen[a] == "P":
                oben_unten = tuple(reversed(inh[a]))
                if m + len(oben_unten) <= n and oben_unten == tuple(range(m + 1, m + len(oben_unten) + 1)):
                    neu = list(inh)
                    neu[a] = ()
                    nachfolger.append((i, tuple(neu), m + len(oben_unten)))
            else:
                x = inh[a][0] if typen[a] == "Q" else inh[a][-1]
                if x == m + 1:
                    neu = list(inh)
                    neu[a] = inh[a][1:] if typen[a] == "Q" else inh[a][:-1]
                    nachfolger.append((i, tuple(neu), m + 1))
        for z in nachfolger:
            if z not in gesehen:
                gesehen.add(z)
                todo.append(z)
    return False


def hat_muster(p, mu):
    k = len(mu)
    for stellen in combinations(range(len(p)), k):
        w = [p[i] for i in stellen]
        if all((w[a] < w[b]) == (mu[a] < mu[b]) for a in range(k) for b in range(a + 1, k)):
            return True
    return False


def lds(p):
    """Längste fallende Teilfolge über die Zahl der Stellenmengen (andere Rechnung als die Dynamik des Moduls: Patience-Sortieren auf -p)."""
    from bisect import bisect_left

    enden = []
    for x in (-v for v in p):
        j = bisect_left(enden, x)
        if j == len(enden):
            enden.append(x)
        else:
            enden[j] = x
    return len(enden)


def alle(n):
    return list(permutations(range(1, n + 1)))


def catalan(n):
    from math import comb

    return comb(2 * n, n) // (n + 1)


def konflikt_zweifaerbbar(p):
    """Zwei parallele Stapel: zweifärbbar ist der Graph auf den Stellen mit Kante {i, j}, wenn p[i] < p[j] und hinter j noch ein Wert unter p[i] liegt
    (Färbung mit Parität über Vereinigen/Suchen, andere Rechnung als die Breitensuche im Modul)."""
    n = len(p)
    eltern = list(range(2 * n))  # Knoten (i, Farbe)

    def finde(x):
        while eltern[x] != x:
            eltern[x] = eltern[eltern[x]]
            x = eltern[x]
        return x

    for i in range(n):
        for j in range(i + 1, n):
            if p[i] < p[j] and min(p[j + 1:], default=n + 1) < p[i]:
                eltern[finde(2 * i)] = finde(2 * j + 1)
                eltern[finde(2 * i + 1)] = finde(2 * j)
    return all(finde(2 * i) != finde(2 * i + 1) for i in range(n))
