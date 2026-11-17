"""Gemeinsame Fixtures und Pfade. Handbeispiel: n = 3 und n = 4 mit allen Folgen (DEMO-PLAYBOOK §1b)."""

import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

# Die langsamen Neuberechnungen (n = 8 für alle zehn Maschinen, rund zwei Minuten) laufen nur mit MVG_VOLL=1.
VOLL = os.environ.get("MVG_VOLL") == "1"
nur_voll = pytest.mark.skipif(not VOLL, reason="langsam: MVG_VOLL=1 setzen (n = 8 für alle zehn Maschinen neu rechnen)")


@pytest.fixture
def alle3():
    """Alle 6 Folgen der Länge 3 (Handbeispiel: ein Stapel scheitert nur an 231, zwei Warteschlangen parallel nur an 321)."""
    from ref_maschinen import alle

    return alle(3)
