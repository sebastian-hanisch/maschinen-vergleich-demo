"""Rechnet die Tabelle des ausgedachten Ankunftsmodells V vor (n = 8, je D 20 000 Folgen) und schreibt data/mvg_modell_v.json.

    python tools/mvg_make_model.py --write     rechnet und schreibt (7 Werte von D, 140 000 Folgen; etwa 40 bis 60 Sekunden)
    python tools/mvg_make_model.py --check     rechnet den ersten Block (2000 Folgen) jedes D neu und vergleicht ganzzahlig mit der Datei (wenige Sekunden)
    python tools/mvg_make_model.py --check --voll   rechnet alle 20 000 Folgen je D neu

Voraussetzung: data/mvg_sets.json (tools/mvg_make_sets.py). Zufalls-Seed der Zeile mit Index j: 20000 + j (mvg_model.SEED_BASIS). Die Zählungen sind
ganzzahlig und wegen des plattformfesten Zufalls (mvg_rng.py) auf jeder Plattform gleich."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import mvg_model as MO  # noqa: E402
from mvg_machines import KEYS  # noqa: E402

N = 8


def rechne_zeile(j, d, anzahl):
    folgen_liste = MO.stichprobe(N, d, anzahl, MO.SEED_BASIS + j)
    return (MO.zaehle_maschinen(folgen_liste, N), MO.zaehle_maschinen(folgen_liste[: MO.BLOCK], N),
            MO.zaehle_paare(folgen_liste, N), MO.zaehle_paare(folgen_liste[: MO.BLOCK], N))


def schreibe():
    zeilen = []
    for j, d in enumerate(MO.D_WERTE):
        t = time.time()
        voll, block, paare, paare_block = rechne_zeile(j, d, MO.ANZAHL_FROZEN)
        zeilen.append({"d": d, "seed": MO.SEED_BASIS + j, "anzahl": MO.ANZAHL_FROZEN, "zaehler": voll, "paare": paare,
                       "block": MO.BLOCK, "zaehler_block": block, "paare_block": paare_block})
        print(f"  D = {MO.d_text(d)}: {time.time() - t:.0f} s", flush=True)
    daten = {"beschreibung": "Ankunftsmodell V (ausgedacht), n = 8: je D die Zahl der Folgen, die jede Maschine sortiert; vorgerechnet von tools/mvg_make_model.py",
             "n": N, "zeilen": zeilen}
    (ROOT / "data").mkdir(exist_ok=True)
    (ROOT / "data" / "mvg_modell_v.json").write_text(json.dumps(daten, indent=0) + "\n", encoding="utf-8", newline="\n")


def pruefe(voll):
    daten = MO.lade()
    fehler = []
    for j, (d, zeile) in enumerate(zip(MO.D_WERTE, daten["zeilen"])):
        assert zeile["d"] == d and zeile["seed"] == MO.SEED_BASIS + j
        anzahl = zeile["anzahl"] if voll else zeile["block"]
        z, zb, p, pb = rechne_zeile(j, d, anzahl)
        if voll:
            ok = z == zeile["zaehler"] and p == zeile["paare"]
        else:
            ok = zb == zeile["zaehler_block"] and pb == zeile["paare_block"]
        if not ok:
            fehler.append(d)
    return fehler


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--voll", action="store_true")
    a = ap.parse_args()
    if a.write:
        schreibe()
    if a.check:
        f = pruefe(a.voll)
        print("ALLES GLEICH" if not f else f"Abweichungen bei D = {f}")
        sys.exit(1 if f else 0)
    if not (a.write or a.check):
        ap.print_help()
    _ = KEYS


if __name__ == "__main__":
    main()
