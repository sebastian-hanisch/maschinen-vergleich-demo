"""Die zehn Maschinen: Netze aus Behältern, Wegsuche je Folge, Aufzählung aller sortierbaren Folgen, Spuren.

Eine Folge ist eine Anordnung der Zahlen 1 bis n in Ankunftsreihenfolge (links zuerst). **Sortierbar durch eine Maschine** heißt: es gibt
irgendeinen Weg (Einlegen, Umsetzen, Ausgeben; Ausgabe jederzeit erlaubt), der 1, 2, ..., n in dieser Reihenfolge ausgibt.

Behälter: Stapel (S, nur die Spitze ist zugänglich), Warteschlange (Q, nur der Kopf), Pop-Stack (P, nur ganz leerbar, Inhalt von oben nach
unten). Ein Netz legt fest, in welche Behälter eine ankommende Zahl darf (`eingang`), welche Umsetzungen von Behälter zu Behälter
erlaubt sind (`umsetzen`) und aus welchen Behältern ausgegeben wird (`ausgang`).

Eine Konfiguration ist `(m, inhalt_0, inhalt_1, ...)` mit m = Zahl der schon ausgegebenen Zahlen; die Inhalte sind Tupel (Stapel und Pop-Stack:
Spitze = letztes Element, Warteschlange: Kopf = erstes Element). Gesucht wird Ebene für Ebene (nach jedem Einlegen alle erreichbaren
Konfigurationen). Zwei Abkürzungen, die keine Folge verlieren: *gierig* gibt eine Zahl sofort aus, wenn sie die nächste gesuchte ist und
an der zugänglichen Stelle eines Ausgangsbehälters steht (das Ausgeben der nächsten Zahl blockiert nichts), und *Senken-Prüfung*
verwirft eine Konfiguration, wenn ein Behälter, aus dem nur noch ausgegeben wird, schon in falscher Reihenfolge gefüllt ist.
Beide Abkürzungen sind gegen die rohe Suche ohne sie geprüft (tests/test_oracle_maschinen_vergleich.py, bis n = 5).

Geschrieben für diese Demo; die Idee (Netze aus Behältern, Wegsuche über Konfigurationsmengen) ist Lehrbuchstoff (Knuth, Tarjan), der Code ist
neu und importiert nichts aus anderen Demos."""

from __future__ import annotations

from dataclasses import dataclass

KEYS = ("Q", "S", "2Q", "3Q", "SSs", "SSp", "SQ", "QS", "SpQ", "P")


@dataclass(frozen=True)
class Net:
    key: str
    name: str
    types: str  # je Behälter "S", "Q" oder "P"
    eingang: tuple  # Behälter, in die eine ankommende Zahl darf
    umsetzen: tuple  # Paare (von, nach)
    ausgang: tuple  # Behälter, aus denen ausgegeben wird
    labels: tuple  # Anzeigenamen der Behälter

    @property
    def ausgang_sq(self):
        return tuple(a for a in self.ausgang if self.types[a] in "SQ")

    @property
    def ausgang_p(self):
        return tuple(a for a in self.ausgang if self.types[a] == "P")

    @property
    def senken(self):
        quellen = {a for a, _ in self.umsetzen}
        return tuple(a for a in range(len(self.types)) if a not in quellen)

    def start(self):
        return (0,) + tuple(() for _ in self.types)


NETS = {
    "Q": Net("Q", "eine Warteschlange", "Q", (0,), (), (0,), ("Warteschlange",)),
    "S": Net("S", "ein Stapel", "S", (0,), (), (0,), ("Stapel",)),
    "2Q": Net("2Q", "zwei Warteschlangen parallel", "QQ", (0, 1), (), (0, 1), ("Warteschlange 1", "Warteschlange 2")),
    "3Q": Net("3Q", "drei Warteschlangen parallel", "QQQ", (0, 1, 2), (), (0, 1, 2), ("Warteschlange 1", "Warteschlange 2", "Warteschlange 3")),
    "SSs": Net("SSs", "zwei Stapel in Serie", "SS", (0,), ((0, 1),), (1,), ("Stapel A (Eingang)", "Stapel B (Ausgang)")),
    "SSp": Net("SSp", "zwei Stapel parallel", "SS", (0, 1), (), (0, 1), ("Stapel A", "Stapel B")),
    "SQ": Net("SQ", "Stapel, dann Warteschlange", "SQ", (0,), ((0, 1),), (1,), ("Stapel (Eingang)", "Warteschlange (Ausgang)")),
    "QS": Net("QS", "Warteschlange, dann Stapel", "QS", (0,), ((0, 1),), (1,), ("Warteschlange (Eingang)", "Stapel (Ausgang)")),
    "SpQ": Net("SpQ", "Stapel und Warteschlange parallel", "SQ", (0, 1), (), (0, 1), ("Stapel", "Warteschlange")),
    "P": Net("P", "ein Pop-Stack", "P", (0,), (), (0,), ("Pop-Stack",)),
}
NAMES = {k: NETS[k].name for k in KEYS}


def _kopf(typ, inhalt):
    """(zugängliches Element, Rest): Warteschlange vorn, Stapel und Pop-Stack hinten."""
    if typ == "Q":
        return inhalt[0], inhalt[1:]
    return inhalt[-1], inhalt[:-1]


def _gierig(net, cfg, n, schritte):
    """Gibt die nächste gesuchte Zahl sofort aus, solange sie an der zugänglichen Stelle eines Ausgangsbehälters steht."""
    m = cfg[0]
    while m < n:
        for a in net.ausgang_sq:
            c = cfg[1 + a]
            if c:
                x, rest = _kopf(net.types[a], c)
                if x == m + 1:
                    cfg = (m + 1,) + cfg[1 : 1 + a] + (rest,) + cfg[2 + a :]
                    m += 1
                    if schritte is not None:
                        schritte.append(("aus", x, a))
                    break
        else:
            break
    return cfg


def _zuege(net, cfg, n):
    """Alle Schritte ohne Ausgeben der nächsten Zahl durch einen Stapel oder eine Warteschlange: Umsetzen und das Leeren des Pop-Stacks."""
    res = []
    m = cfg[0]
    for a, b in net.umsetzen:
        c = cfg[1 + a]
        if c:
            x, rest = _kopf(net.types[a], c)
            neu = list(cfg)
            neu[1 + a] = rest
            neu[1 + b] = cfg[1 + b] + (x,)
            res.append((tuple(neu), ("um", x, a, b)))
    for a in net.ausgang_p:
        c = cfg[1 + a]
        if c and m + len(c) <= n and tuple(reversed(c)) == tuple(range(m + 1, m + len(c) + 1)):
            res.append(((m + len(c),) + cfg[1 : 1 + a] + ((),) + cfg[2 + a :], ("aus_pop", tuple(reversed(c)), a)))
    return res


def _in_ordnung(net, cfg):
    """Senken-Prüfung: aus einer Senke wird nur noch ausgegeben, sie muss also schon richtig geordnet sein
    (Warteschlange: nicht fallend von vorn nach hinten; Stapel und Pop-Stack: fallend von unten nach oben)."""
    for a in net.senken:
        c = cfg[1 + a]
        if len(c) > 1:
            if net.types[a] == "Q":
                if any(c[i] > c[i + 1] for i in range(len(c) - 1)):
                    return False
            elif any(c[i] < c[i + 1] for i in range(len(c) - 1)):
                return False
    return True


def _abschluss(net, starts, n, parent=None, gierig=True, senken=True):
    """Alle Konfigurationen, die aus `starts` durch Umsetzen und gieriges Ausgeben erreichbar sind.

    `starts`: Liste (cfg, vorgaenger oder None, schritt oder None). Mit `parent` (dict) wird je Konfiguration (Vorgänger, Schritte) vermerkt."""
    gesehen = set()
    offen = []

    def aufnehmen(cfg, vorg, schritt):
        schritte = [] if parent is not None else None
        if parent is not None and schritt is not None:
            schritte.append(schritt)
        if gierig:
            cfg = _gierig(net, cfg, n, schritte)
        if cfg in gesehen or (senken and not _in_ordnung(net, cfg)):
            return
        gesehen.add(cfg)
        offen.append(cfg)
        if parent is not None and cfg not in parent:
            parent[cfg] = (vorg, tuple(schritte))

    for cfg, vorg, schritt in starts:
        aufnehmen(cfg, vorg, schritt)
    while offen:
        cfg = offen.pop()
        for neu, schritt in _zuege(net, cfg, n):
            aufnehmen(neu, cfg, schritt)
        if not gierig:
            m = cfg[0]
            for a in net.ausgang_sq:
                c = cfg[1 + a]
                if c and m < n:
                    x, rest = _kopf(net.types[a], c)
                    if x == m + 1:
                        aufnehmen((m + 1,) + cfg[1 : 1 + a] + (rest,) + cfg[2 + a :], cfg, ("aus", x, a))
    return gesehen


def _einlegen(net, cfgs, v):
    for cfg in cfgs:
        for a in net.eingang:
            yield cfg[: 1 + a] + (cfg[1 + a] + (v,),) + cfg[2 + a :], cfg, ("ein", v, a)


@dataclass(frozen=True)
class Ergebnis:
    sortierbar: bool
    zustaende: int  # Zahl der untersuchten Konfigurationen (alle Ebenen)
    schritte: tuple | None  # ein Weg als Schrittfolge, nur wenn sortierbar und `spur=True`


def pruefe(key, folge, spur=False, gierig=True, senken=True):
    """Sortiert die Maschine `key` die Folge? Mit `spur=True` kommt ein Weg als Schrittfolge zurück.

    Schritte: ("ein", v, behälter), ("um", v, von, nach), ("aus", v, behälter), ("aus_pop", (v1, v2, ...), behälter)."""
    net = NETS[key]
    n = len(folge)
    parent = {} if spur else None
    cfgs = _abschluss(net, [(net.start(), None, None)], n, parent, gierig, senken)
    gesamt = len(cfgs)
    for v in folge:
        cfgs = _abschluss(net, list(_einlegen(net, cfgs, v)), n, parent, gierig, senken)
        gesamt += len(cfgs)
        if not cfgs:
            return Ergebnis(False, gesamt, None)
    ziel = [c for c in cfgs if c[0] == n]
    if not ziel:
        return Ergebnis(False, gesamt, None)
    if not spur:
        return Ergebnis(True, gesamt, None)
    kette = []
    cfg = ziel[0]
    while cfg is not None:
        vorg, schritte = parent[cfg]
        kette.append(schritte)
        cfg = vorg
    weg = tuple(s for schritte in reversed(kette) for s in schritte)
    return Ergebnis(True, gesamt, weg)


def ist_sortierbar(key, folge):
    return pruefe(key, folge).sortierbar


def sortierbare(key, n, gierig=True):
    """Alle von der Maschine sortierbaren Folgen der Länge n in lexikographischer Reihenfolge (Präfixbaum über die Ebenen der Wegsuche)."""
    net = NETS[key]
    ergebnis = []
    rest = list(range(1, n + 1))
    prefix = []

    def rec(cfgs):
        if not rest:
            if any(c[0] == n for c in cfgs):
                ergebnis.append(tuple(prefix))
            return
        for v in sorted(rest):
            neu = _abschluss(net, list(_einlegen(net, cfgs, v)), n, None, gierig)
            if neu:
                rest.remove(v)
                prefix.append(v)
                rec(neu)
                prefix.pop()
                rest.append(v)

    rec(_abschluss(net, [(net.start(), None, None)], n))
    return ergebnis


def erzeugbare(key, n):
    """Zweiter Rechenweg: Eingabe 1..n, alle Bewegungen frei; gesammelt werden alle vollständigen Ausgaben (erzeugbare Ausgaben)."""
    net = NETS[key]
    k = len(net.types)
    start = (0,) + tuple(() for _ in range(k)) + ((),)
    gesehen = {start}
    offen = [start]
    fertig = set()
    while offen:
        s = offen.pop()
        i, inhalt, aus = s[0], s[1 : 1 + k], s[1 + k]
        if len(aus) == n:
            fertig.add(aus)
            continue
        folgende = []
        if i < n:
            for a in net.eingang:
                neu = list(inhalt)
                neu[a] = neu[a] + (i + 1,)
                folgende.append((i + 1,) + tuple(neu) + (aus,))
        for a, b in net.umsetzen:
            if inhalt[a]:
                x, rest = _kopf(net.types[a], inhalt[a])
                neu = list(inhalt)
                neu[a] = rest
                neu[b] = neu[b] + (x,)
                folgende.append((i,) + tuple(neu) + (aus,))
        for a in net.ausgang:
            if inhalt[a]:
                neu = list(inhalt)
                if net.types[a] == "P":
                    neu[a] = ()
                    folgende.append((i,) + tuple(neu) + (aus + tuple(reversed(inhalt[a])),))
                else:
                    x, rest = _kopf(net.types[a], inhalt[a])
                    neu[a] = rest
                    folgende.append((i,) + tuple(neu) + (aus + (x,),))
        for z in folgende:
            if z not in gesehen:
                gesehen.add(z)
                offen.append(z)
    return fertig


def inverse(p):
    """Inverse Permutation: q[p[i] - 1] = i + 1. Sortieren und Erzeugen sind invers."""
    q = [0] * len(p)
    for i, v in enumerate(p):
        q[v - 1] = i + 1
    return tuple(q)


def abspielen(key, schritte):
    """Spielt eine Schrittfolge nach (jeder Schritt wird auf Zulässigkeit geprüft) und liefert je Schritt (Konfiguration, Ausgabe bisher).

    Wirft ValueError bei einem unzulässigen Schritt. Dient der Anzeige der Spur; die Tests prüfen Spuren zusätzlich mit einem
    eigenen, unabhängigen Abspieler."""
    net = NETS[key]
    cfg = net.start()
    ausgabe = ()
    zustand = []
    for s in schritte:
        art = s[0]
        if art == "ein":
            _, v, a = s
            if a not in net.eingang:
                raise ValueError(f"Einlegen in Behälter {a} nicht erlaubt")
            cfg = cfg[: 1 + a] + (cfg[1 + a] + (v,),) + cfg[2 + a :]
        elif art == "um":
            _, v, a, b = s
            if (a, b) not in net.umsetzen or not cfg[1 + a] or _kopf(net.types[a], cfg[1 + a])[0] != v:
                raise ValueError(f"Umsetzen von {v} nicht erlaubt")
            rest = _kopf(net.types[a], cfg[1 + a])[1]
            neu = list(cfg)
            neu[1 + a] = rest
            neu[1 + b] = cfg[1 + b] + (v,)
            cfg = tuple(neu)
        elif art == "aus":
            _, v, a = s
            if a not in net.ausgang_sq or not cfg[1 + a] or _kopf(net.types[a], cfg[1 + a])[0] != v:
                raise ValueError(f"Ausgeben von {v} nicht erlaubt")
            rest = _kopf(net.types[a], cfg[1 + a])[1]
            cfg = (cfg[0] + 1,) + cfg[1 : 1 + a] + (rest,) + cfg[2 + a :]
            ausgabe += (v,)
        elif art == "aus_pop":
            _, werte, a = s
            if a not in net.ausgang_p or tuple(reversed(cfg[1 + a])) != tuple(werte):
                raise ValueError("Leeren des Pop-Stacks nicht erlaubt")
            cfg = (cfg[0] + len(werte),) + cfg[1 : 1 + a] + ((),) + cfg[2 + a :]
            ausgabe += tuple(werte)
        else:
            raise ValueError(art)
        zustand.append((cfg, ausgabe))
    return zustand


def beschreibe(key, schritt):
    """Ein Schritt in einem deutschen Satz."""
    net = NETS[key]
    art = schritt[0]
    if art == "ein":
        return f"{schritt[1]} in {net.labels[schritt[2]]} legen"
    if art == "um":
        return f"{schritt[1]} von {net.labels[schritt[2]]} nach {net.labels[schritt[3]]} umsetzen"
    if art == "aus":
        return f"{schritt[1]} ausgeben (aus {net.labels[schritt[2]]})"
    return "Pop-Stack leeren: " + " ".join(map(str, schritt[1])) + " ausgeben"


def inhalt_text(typ, inhalt):
    """Inhalt eines Behälters als Text: Stapel und Pop-Stack von unten nach oben (Spitze rechts), Warteschlange von vorn nach hinten."""
    return " ".join(map(str, inhalt)) if inhalt else "·"
