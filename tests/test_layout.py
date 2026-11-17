"""Layout (DEMO-PLAYBOOK §2): fester Kopf, Schnellstart oben in der Seitenleiste, aktives Preset hervorgehoben.

Die Hervorhebung ist zustandslos (`aktives_preset` vergleicht jeden Regler aus SETTING_SPECS mit dem Preset). Der Test unten stellt
sicher, dass wirklich JEDER Regler der Seitenleiste dort steht: sonst bliebe das Preset trotz Änderung markiert."""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

import mvg_constants as C
import mvg_presets as P

APP = str(Path(__file__).resolve().parent.parent / "app.py")
REGLER_ARTEN = ("slider", "number_input", "select_slider", "selectbox", "radio", "toggle", "checkbox", "text_input")


def _app() -> AppTest:
    at = AppTest.from_file(APP, default_timeout=180)
    at.run()
    assert not at.exception, [str(e) for e in at.exception]
    return at


def _typen(at) -> dict:
    """Button-Typ je Preset-Name (die Preset-Buttons der Seitenleiste)."""
    return {b.label: b.proto.type for b in at.sidebar.button if b.label in C.PRESETS}


def _regler(at, key):
    """Die Regler der Experimente stehen im Hauptbereich (die Seitenleiste hat nur den Schnellstart)."""
    for art in REGLER_ARTEN:
        try:
            return getattr(at.main, art)(key=key)
        except KeyError:
            continue
    raise AssertionError(f"Regler {key} steht nicht im Hauptbereich")


def _anderer_wert(key, aktuell):
    """Ein gültiger Wert, der vom aktuellen verschieden ist und mit den Standardwerten der übrigen Regler zu keinem Preset gehört."""
    spec = P.SETTING_SPECS[key]
    if spec.options is not None:
        kandidaten = list(reversed(spec.options))
    elif spec.caster is int:
        kandidaten = [spec.hi, spec.lo, (spec.lo + spec.hi) // 2]
    else:
        kandidaten = ["2431", "4321"]
    for wert in kandidaten:
        zustand = {k: s_.default for k, s_ in P.SETTING_SPECS.items()} | {key: wert}
        if wert != aktuell and all(any(zustand[k] != preset.get(k, P.SETTING_SPECS[k].default) for k in zustand) for preset in C.PRESETS.values()):
            return wert
    raise AssertionError(f"kein Wert für {key}, der zu keinem Preset gehört")


def test_presets_stehen_in_der_seitenleiste_und_nicht_im_hauptbereich():
    at = _app()
    assert [b.label for b in at.sidebar.button][: len(C.PRESETS)] == list(C.PRESETS)  # die ersten Buttons der Seitenleiste
    assert not [b for b in at.main.button if b.label in C.PRESETS]


def test_titel_steht_im_festen_kopf():
    at = _app()
    assert "st-key-kopf" in " ".join(h.proto.body for h in at.get("html"))  # das Stylesheet setzt an der Klasse des Containers an
    assert at.title[0].value


def test_beim_start_ist_genau_das_standard_preset_hervorgehoben():
    typen = _typen(_app())
    assert [name for name, typ in typen.items() if typ == "primary"] == [next(iter(C.PRESETS))]


@pytest.mark.parametrize("name", list(C.PRESETS))
def test_angeklicktes_preset_ist_hervorgehoben_und_bleibt_es_im_naechsten_lauf(name):
    at = _app()
    at.sidebar.button(key=f"preset_{name}").click().run()
    assert [n for n, typ in _typen(at).items() if typ == "primary"] == [name]
    at.run()
    assert [n for n, typ in _typen(at).items() if typ == "primary"] == [name]


def test_jeder_regler_steht_in_setting_specs_und_umgekehrt():
    at = _app()
    schluessel = {w.key for art in REGLER_ARTEN for w in getattr(at.main, art) if w.key} | {w.key for art in REGLER_ARTEN for w in getattr(at.sidebar, art) if w.key}
    fehlt = schluessel - set(P.SETTING_SPECS)
    assert not fehlt, f"Regler {sorted(fehlt)} fehlen in SETTING_SPECS: ihre Änderung hebt das aktive Preset nicht auf"
    assert set(P.SETTING_SPECS) <= schluessel, "ein Eintrag in SETTING_SPECS ohne Regler in der App"


@pytest.mark.parametrize("state_key", list(P.SETTING_SPECS))
def test_jede_aenderung_eines_reglers_hebt_die_hervorhebung_auf(state_key):
    at = _app()
    spec = P.SETTING_SPECS[state_key]
    regler = _regler(at, state_key)
    regler.set_value(_anderer_wert(state_key, regler.value)).run()
    assert not at.exception
    assert "primary" not in _typen(at).values()
    # erneutes Anklicken markiert wieder
    name = next(iter(C.PRESETS))
    at.sidebar.button(key=f"preset_{name}").click().run()
    assert _typen(at)[name] == "primary"
