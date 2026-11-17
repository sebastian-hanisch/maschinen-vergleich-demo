"""Rechnet die Mengen sortierbarer Folgen vor und schreibt data/mvg_sets.json (vorgerechnet, als Bitmasken in Hex).

    python tools/mvg_make_sets.py --write            Mengen n = 1..8 für die zehn Maschinen, West-2 und Pop-2 neu rechnen und schreiben
                                                     (rund 1 bis 3 Minuten, n = 8 für zwei Stapel in Serie ist der größte Posten);
                                                     die Tabelle n = 9 bleibt aus der vorhandenen Datei erhalten
    python tools/mvg_make_sets.py --write --n9       zusätzlich die Zahlen für n = 9 mit der Wegsuche neu rechnen (viele Minuten)
    python tools/mvg_make_sets.py --n9               nur die Zahlen für n = 9 neu rechnen, die Mengen bleiben
    python tools/mvg_make_sets.py --check            n <= 7 neu rechnen und mit der Datei vergleichen (Sekunden)
    python tools/mvg_make_sets.py --check --voll     zusätzlich n = 8 (wie --write)

Die Tabelle für n = 9 enthält nur Zahlen. Zwei Zahlen sind nicht in dieser Demo nachgerechnet und tragen das in `quelle`: zwei Stapel in Serie
(OEIS A263929, nur gelesen) und, falls die Wegsuche nicht läuft, die jeweilige frühere Messung."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import mvg_machines as M  # noqa: E402
import mvg_patterns as P  # noqa: E402
import mvg_sets as S  # noqa: E402

N9_OEIS_SSS = 337816  # A263929 (Zahl der von zwei Stapeln in Serie sortierbaren Folgen), n = 9; hier nicht nachgerechnet
N9_QUELLE_SSS = "OEIS A263929, nur gelesen, in dieser Demo nicht nachgerechnet (Wegsuche bei n = 9 zu teuer)"


def rechne_menge(key, n):
    if key == "W2":
        ident = tuple(range(1, n + 1))
        return S.maske(p for p in S.folgen(n) if P.zwei_durchlaeufe(P.west_durchlauf, p) == ident)
    if key == "P2":
        ident = tuple(range(1, n + 1))
        return S.maske(p for p in S.folgen(n) if P.zwei_durchlaeufe(P.pop_durchlauf, p) == ident)
    return S.maske(M.sortierbare(key, n))


def rechne_alles(nmax, log=print):
    mengen = {}
    for key in list(M.KEYS) + list(S.EXTRA):
        mengen[key] = {}
        for n in range(1, nmax + 1):
            t = time.time()
            mengen[key][str(n)] = format(rechne_menge(key, n), "x")
            if n >= 7:
                log(f"  {key:4s} n={n}: {S.zaehle(int(mengen[key][str(n)], 16)):6d} ({time.time() - t:.1f} s)")
    return mengen


def rechne_n9(log=print):
    n9 = {}
    for key in M.KEYS:
        if key == "SSs":
            n9[key] = {"zahl": N9_OEIS_SSS, "quelle": N9_QUELLE_SSS, "nachgerechnet": False}
            continue
        t = time.time()
        z = len(M.sortierbare(key, 9))
        log(f"  {key:4s} n=9: {z} ({time.time() - t:.0f} s)")
        n9[key] = {"zahl": z, "quelle": "Wegsuche dieser Demo (Präfixbaum), n = 9", "nachgerechnet": True}
    return n9


def schreibe(mengen, n9):
    daten = {
        "beschreibung": "Mengen sortierbarer Folgen als Bitmasken (Hex): Bit i = i-te Folge in lexikographischer Reihenfolge; vorgerechnet von tools/mvg_make_sets.py",
        "mengen": mengen,
        "n9": n9,
    }
    (ROOT / "data").mkdir(exist_ok=True)
    (ROOT / "data" / "mvg_sets.json").write_text(json.dumps(daten, indent=0, sort_keys=False) + "\n", encoding="utf-8", newline="\n")


def pruefe(nmax, log=print):
    """Rechnet die Mengen bis nmax neu und vergleicht mit der Datei; liefert die Liste der Abweichungen."""
    abweichungen = []
    for key in list(M.KEYS) + list(S.EXTRA):
        for n in range(1, nmax + 1):
            neu = rechne_menge(key, n)
            if neu != S.menge(key, n):
                abweichungen.append((key, n))
                log(f"  ABWEICHUNG {key} n={n}")
    return abweichungen


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--n9", action="store_true")
    ap.add_argument("--voll", action="store_true")
    a = ap.parse_args()
    if a.write:
        t = time.time()
        mengen = rechne_alles(8)
        n9 = rechne_n9() if a.n9 else S.lade()["n9"] if S.DATEI.exists() else {}
        schreibe(mengen, n9)
        print(f"geschrieben ({time.time() - t:.0f} s)")
    if a.n9 and not a.write:
        t = time.time()
        schreibe(S.lade()["mengen"], rechne_n9())
        print(f"n = 9 geschrieben ({time.time() - t:.0f} s)")
    if a.check:
        abw = pruefe(8 if a.voll else 7)
        print("ALLES GLEICH" if not abw else f"{len(abw)} Abweichungen")
        sys.exit(1 if abw else 0)
    if not (a.write or a.check or a.n9):
        ap.print_help()


if __name__ == "__main__":
    main()
