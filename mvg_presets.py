"""Permalink (Begrenzen), Presets (Schnellstart in der Seitenleiste) und Zufalls-Seed-Button.

Die Regler der Experimente stehen im Hauptbereich bei ihrem Experiment; ein Preset setzt ALLE Regler (die nicht genannten auf ihren Standardwert),
damit der Zustand ein bestimmtes Szenario ist und `aktives_preset` ihn zustandslos erkennt."""

import re
import time
from dataclasses import dataclass

import streamlit as st

import mvg_constants as C
from mvg_machines import KEYS
from mvg_rng import SplitMix64


@dataclass(frozen=True)
class SettingSpec:
    url_param: str
    caster: type
    default: object
    lo: float | None = None
    hi: float | None = None
    options: tuple | None = None


SETTING_SPECS = {
    "e1_n": SettingSpec("n1", int, C.E1_N[2], C.E1_N[0], C.E1_N[1]),
    "e2_a": SettingSpec("a2", str, C.E2_A, options=KEYS),
    "e2_b": SettingSpec("b2", str, C.E2_B, options=KEYS),
    "e2_n": SettingSpec("n2", int, C.E2_N[2], C.E2_N[0], C.E2_N[1]),
    "e3_folge": SettingSpec("folge", str, C.E3_FOLGE),
    "e3_n": SettingSpec("n3", int, C.E3_N[2], C.E3_N[0], C.E3_N[1]),
    "e3_d": SettingSpec("d", str, C.D_STANDARD, options=C.D_OPTIONEN),
    "e3_seed": SettingSpec("seed", int, C.E3_SEED[2], C.E3_SEED[0], C.E3_SEED[1]),
    "e4_n": SettingSpec("n4", int, C.E4_N[2], C.E4_N[0], C.E4_N[1]),
    "e4_a": SettingSpec("a4", str, C.E4_A, options=KEYS),
    "e4_b": SettingSpec("b4", str, C.E4_B, options=KEYS),
    "e5_n": SettingSpec("n5", int, C.E5_N[2], C.E5_N[0], C.E5_N[1]),
}
PRESET_KEYS = {key: key for key in SETTING_SPECS}  # Schlüssel in C.PRESETS = Schlüssel im Session State

_FOLGE_ERLAUBT = re.compile(r"[^0-9 ,]")


def init_session_state_defaults():
    for state_key, spec in SETTING_SPECS.items():
        if state_key not in st.session_state:
            st.session_state[state_key] = spec.default


def bounds(state_key):
    spec = SETTING_SPECS[state_key]
    return spec.lo, spec.hi


def _begrenze(spec, roh):
    """Wert aus der Adresszeile auf einen gültigen Wert bringen oder None."""
    if spec.caster is int:
        try:
            wert = int(roh)
        except (ValueError, TypeError):
            return None
        return max(spec.lo, min(spec.hi, wert))
    wert = str(roh)
    if spec.options is not None:
        return wert if wert in spec.options else None
    return _FOLGE_ERLAUBT.sub("", wert)[:40]


def load_permalink_settings():
    """Einmal je Sitzung: Werte aus der Adresszeile übernehmen, auf gültige Werte begrenzt."""
    if "permalink_loaded" in st.session_state:
        return
    qp = st.query_params
    for state_key, spec in SETTING_SPECS.items():
        if spec.url_param in qp:
            wert = _begrenze(spec, qp[spec.url_param])
            if wert is not None:
                st.session_state[state_key] = wert
    st.session_state["permalink_loaded"] = True


def sync_query_params(values):
    """`values`: {state_key: aktueller Wert}; die Adresszeile spiegelt die Konfiguration."""
    try:
        for state_key, value in values.items():
            st.query_params[SETTING_SPECS[state_key].url_param] = str(value)
    except Exception:
        pass


def apply_preset(name):
    """Setzt alle Regler: die im Preset genannten auf ihren Wert, alle übrigen auf den Standardwert."""
    for state_key, spec in SETTING_SPECS.items():
        st.session_state[state_key] = C.PRESETS[name].get(state_key, spec.default)


def aktives_preset():
    """Name des Presets, dessen Werte GENAU den aktuellen Einstellungen entsprechen, sonst None (zustandslos; jeder Regler steht in SETTING_SPECS)."""
    for name, preset in C.PRESETS.items():
        if all(st.session_state.get(state_key, spec.default) == preset.get(state_key, spec.default) for state_key, spec in SETTING_SPECS.items()):
            return name
    return None


def sidebar_presets():
    """Schnellstart oben in der Seitenleiste; das aktive Preset ist hervorgehoben (`type="primary"`)."""
    if not C.PRESETS:
        return
    st.header("🎯 Schnellstart")
    st.caption("Ein Beispielszenario laden (setzt alle Regler der Experimente):")
    aktiv = aktives_preset()
    for name in C.PRESETS:
        st.button(
            name, width="stretch", on_click=apply_preset, args=(name,), help=C.PRESET_HELP.get(name, ""), key=f"preset_{name}",
            type="primary" if aktiv == name else "secondary",
        )


def randomize_seed():
    st.session_state["e3_seed"] = SplitMix64(time.time_ns()).below(C.E3_SEED[1] + 1)
