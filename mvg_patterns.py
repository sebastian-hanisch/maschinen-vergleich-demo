"""Muster, Teilfolgen, Konfliktgraph und die beiden Durchlauf-Regeln (West, Pop-Stack); Gründe, warum eine Maschine eine Folge nicht schafft.

Alles reine Ganzzahl- und Tupelrechnung (plattformfest). Eine Folge p enthält ein Muster mu (eine Permutation), wenn es Stellen
i_1 < ... < i_k gibt, deren Werte dieselbe Ordnung haben wie mu. Die Charakterisierungen unten sind Lehrbuchstoff (Bóna, Kombinatorik der
Permutationen; Tarjan 1971 in der Vorfassung); hier dienen sie der Anzeige des Grundes und als unabhängiger Rechenweg gegen die
Wegsuche in mvg_machines.py."""

from itertools import combinations


def finde_muster(p, mu):
    """Stellen (i_1 < ... < i_k) des ersten Vorkommens von mu in p (lexikographisch kleinste Stellenfolge) oder None."""
    k = len(mu)
    for stellen in combinations(range(len(p)), k):
        w = [p[i] for i in stellen]
        if all((w[a] < w[b]) == (mu[a] < mu[b]) for a in range(k) for b in range(a + 1, k)):
            return stellen
    return None


def vermeidet(p, *muster):
    return all(finde_muster(p, mu) is None for mu in muster)


def laengste_fallende(p):
    """Länge der längsten fallenden Teilfolge (LDS)."""
    best = []
    for i, v in enumerate(p):
        best.append(1 + max((best[j] for j in range(i) if p[j] > v), default=0))
    return max(best, default=0)


def laengste_wachsende(p):
    best = []
    for i, v in enumerate(p):
        best.append(1 + max((best[j] for j in range(i) if p[j] < v), default=0))
    return max(best, default=0)


def fallende_teilfolge(p, laenge):
    """Stellen einer fallenden Teilfolge der Länge `laenge` (erste in lexikographischer Stellenfolge) oder None."""
    for stellen in combinations(range(len(p)), laenge):
        if all(p[stellen[i]] > p[stellen[i + 1]] for i in range(laenge - 1)):
            return stellen
    return None


def west_durchlauf(p):
    """Ein gieriger Stapeldurchlauf (West): vor dem Einlegen werden alle kleineren Zahlen an der Spitze ausgegeben."""
    stapel, aus = [], []
    for x in p:
        while stapel and stapel[-1] < x:
            aus.append(stapel.pop())
        stapel.append(x)
    while stapel:
        aus.append(stapel.pop())
    return tuple(aus)


def pop_durchlauf(p):
    """Ein Pop-Stack-Durchlauf: jeder maximale fallende Lauf wird umgekehrt (der Pop-Stack wird geleert, sobald die nächste Zahl größer ist)."""
    if not p:
        return ()
    aus, lauf = [], [p[0]]
    for x in p[1:]:
        if x < lauf[-1]:
            lauf.append(x)
        else:
            aus.extend(reversed(lauf))
            lauf = [x]
    aus.extend(reversed(lauf))
    return tuple(aus)


def zwei_durchlaeufe(regel, p):
    """Zwei Durchläufe hintereinander (`regel` = west_durchlauf oder pop_durchlauf)."""
    return regel(regel(p))


def konfliktkanten(p):
    """Kanten des Konfliktgraphen für zwei parallele Stapel: Stellen i < j mit p[i] < p[j], hinter denen noch eine Zahl kleiner als p[i] kommt.

    Zwei solche Zahlen dürfen nicht im selben Stapel liegen: die größere läge oben und müsste vor der kleineren heraus, die
    kleinere vor der späteren kleinen Zahl. Eigene Fassung der Kantendefinition (nach Even/Itai 1971 und Tarjan, im Original nicht
    gelesen); gegen die Wegsuche der Maschine bis n = 8 bestätigt (tests/test_oracle_maschinen_vergleich.py)."""
    n = len(p)
    return [(i, j) for i in range(n) for j in range(i + 1, n) if p[i] < p[j] and any(p[k] < p[i] for k in range(j + 1, n))]


def ungerader_zyklus(p):
    """Ein ungerader Zyklus im Konfliktgraphen (Stellen in Zyklusreihenfolge) oder None, wenn der Graph zweifärbbar ist."""
    n = len(p)
    nachbarn = [[] for _ in range(n)]
    for i, j in konfliktkanten(p):
        nachbarn[i].append(j)
        nachbarn[j].append(i)
    farbe = [-1] * n
    eltern = [-1] * n
    tiefe = [0] * n
    for s in range(n):
        if farbe[s] >= 0:
            continue
        farbe[s] = 0
        schlange = [s]
        for u in schlange:
            for v in nachbarn[u]:
                if farbe[v] < 0:
                    farbe[v] = 1 - farbe[u]
                    eltern[v] = u
                    tiefe[v] = tiefe[u] + 1
                    schlange.append(v)
                elif farbe[v] == farbe[u]:
                    a, b = u, v
                    pa, pb = [a], [b]
                    while a != b:
                        if tiefe[a] >= tiefe[b]:
                            a = eltern[a]
                            pa.append(a)
                        else:
                            b = eltern[b]
                            pb.append(b)
                    # pa endet beim gemeinsamen Vorfahren, pb ebenfalls (letztes Element gleich)
                    return tuple(pa + pb[-2::-1])
    return None


def konflikt_zweifaerbbar(p):
    return ungerader_zyklus(p) is None


def grund_nein(key, p):
    """Warum die Maschine die Folge nicht sortiert, als (Art, Text) für Maschinen mit einfacher Charakterisierung; sonst (None, None).

    Nur aufrufen, wenn die Wegsuche „nein“ gesagt hat. Jeder Text nennt die Stellen (ab 1 gezählt) und die Werte des Zeugen."""

    def zeuge(stellen):
        return ", ".join(f"{p[i]} (Stelle {i + 1})" for i in stellen)

    if key in ("S", "SQ", "QS"):
        s = finde_muster(p, (2, 3, 1))
        if s:
            a, b, c = (p[i] for i in s)
            zusatz = "" if key == "S" else " (Dass diese Maschine genau die Folgen ohne 231 sortiert, ist nur bis n = 8 gemessen, nicht bewiesen.)"
            return "muster", (f"Muster 231: {zeuge(s)}. Die {a} und die {b} müssen warten, bis die {c} heraus ist; dann läge die {b} über der {a} "
                              f"und käme vor ihr heraus, soll aber nach ihr kommen.{zusatz}")
    elif key == "2Q":
        s = fallende_teilfolge(p, 3)
        if s:
            return "muster", f"Fallende Teilfolge der Länge 3: {zeuge(s)}. Drei fallende Zahlen brauchen drei Warteschlangen."
    elif key == "3Q":
        s = fallende_teilfolge(p, 4)
        if s:
            return "muster", f"Fallende Teilfolge der Länge 4: {zeuge(s)}. Vier fallende Zahlen brauchen vier Warteschlangen."
    elif key == "Q":
        for i in range(len(p)):
            for j in range(i + 1, len(p)):
                if p[i] > p[j]:
                    return "muster", f"Umkehrung: {p[i]} steht vor {p[j]} (Stellen {i + 1} und {j + 1}). Eine Warteschlange behält die Reihenfolge."
    elif key == "P":
        for mu, name in (((2, 3, 1), "231"), ((3, 1, 2), "312")):
            s = finde_muster(p, mu)
            if s:
                return "muster", f"Muster {name}: {zeuge(s)}. Ein Pop-Stack sortiert in einem Durchlauf nur Folgen ohne 231 und ohne 312."
    elif key == "SSp":
        z = ungerader_zyklus(p)
        if z:
            teile = ", ".join(str(p[i]) for i in z)
            return "zyklus", (f"Konfliktzyklus ungerader Länge {len(z)} (Werte {teile}; Stellen {', '.join(str(i + 1) for i in z)}): "
                              "je zwei aufeinanderfolgende dürfen nicht im selben Stapel liegen, zwei Stapel reichen dafür nicht.")
    return None, None


def alle_folgen(n):
    from itertools import permutations

    return list(permutations(range(1, n + 1)))


def text_folge(p):
    """Eine Folge als Text: bis n = 9 ohne Trenner, sonst mit Leerzeichen."""
    return "".join(map(str, p)) if all(x < 10 for x in p) else " ".join(map(str, p))
