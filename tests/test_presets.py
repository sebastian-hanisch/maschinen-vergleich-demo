"""Presets: Vollständigkeit, gültige Werte, Standard-Preset = Standardeinstellungen, jedes Preset ändert etwas; alle Regler stehen in SETTING_SPECS."""

import mvg_constants as C
import mvg_evaluation as ev
import mvg_presets as P
from mvg_machines import KEYS


def test_every_preset_has_help_and_only_known_keys():
    assert set(C.PRESETS) == set(C.PRESET_HELP)
    for name, preset in C.PRESETS.items():
        assert set(preset) <= set(P.SETTING_SPECS), name
        assert C.PRESET_HELP[name]


def test_preset_values_are_inside_the_widget_bounds():
    for name, preset in C.PRESETS.items():
        for key, wert in preset.items():
            spec = P.SETTING_SPECS[key]
            if spec.options is not None:
                assert wert in spec.options, (name, key)
            elif spec.caster is int:
                assert spec.lo <= wert <= spec.hi, (name, key)


def test_default_preset_equals_the_default_settings():
    assert C.PRESETS[C.STANDARD] == {}
    assert ev.Settings(**{k: P.SETTING_SPECS[k].default for k in P.SETTING_SPECS}) == ev.Settings()


def test_defaults_are_inside_the_bounds_and_names_are_machines():
    for key, spec in P.SETTING_SPECS.items():
        if spec.options is not None:
            assert spec.default in spec.options, key
        elif spec.caster is int:
            assert spec.lo <= spec.default <= spec.hi, key
    assert C.E2_A in KEYS and C.E2_B in KEYS and C.E4_A in KEYS and C.E4_B in KEYS and C.E2_A != C.E2_B and C.E4_A != C.E4_B


def test_preset_states_are_pairwise_different():
    zustaende = [tuple(p.get(k, s.default) for k, s in P.SETTING_SPECS.items()) for p in C.PRESETS.values()]
    assert len(set(zustaende)) == len(zustaende)


def test_mengen_regler_bleiben_im_bereich_der_vorgerechneten_mengen():
    assert C.E2_N[1] == C.E3_N[1] == C.E4_N[1] == C.E5_N[1] == 8 and C.E1_N[1] == 9
