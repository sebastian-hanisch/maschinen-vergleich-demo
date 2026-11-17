"""Konstanten: Regler-Grenzen, Voreinstellungen, Farben und Presets."""

from mvg_machines import KEYS, NAMES

# --- Regler (alle im Hauptbereich bei ihrem Experiment; die Seitenleiste hat nur den Schnellstart) -----------------------------
E1_N = (1, 9, 6)  # Experiment 1: n (Mengen bis 8, bei 9 nur Zahlen)
E2_N = (3, 8, 5)
E2_A, E2_B = "SSp", "3Q"
E3_N = (3, 8, 8)  # Länge der Zufallsfolgen (Mengen nur bis n = 8)
E3_FOLGE = "31524"
E3_FOLGE_MAX_N = 10
E3_SEED = (0, 999999, 12000)
D_OPTIONEN = ("0,5", "1", "2", "4", "8", "16", "∞")  # Verweilzeit-Mittel D des Modells V (∞ = Modell U)
D_STANDARD = "2"
E4_N = (3, 8, 7)
E4_A, E4_B = "3Q", "SSs"
E5_N = (4, 8, 5)

# --- Anzeige ----------------------------------------------------------------------------------------------------------------------
KURZ_LANG = {k: f"{k}: {NAMES[k]}" for k in KEYS}
NUR_MASCHINE = ("SpQ",)  # Zahlen ab n = 7 stützt allein die Wegsuche, keine OEIS-Reihe gefunden
COLOR_A = "#2F6B65"
COLOR_B = "#C46A2B"
COLOR_BEIDE = "rgba(150,150,150,0.65)"
COLOR_LINE = "#4c78a8"
GRUPPEN_FARBEN = ("#4c78a8", "#f58518", "#54a24b", "#e45756", "#72b7b2", "#b279a2", "#9d755d", "#bab0ac", "#eeca3b", "#ff9da6")

# --- Presets: nur die Regler, die vom Standard abweichen (der Standard ist das erste Preset) ----------------------------------------
STANDARD = "Gleiche Zahl: SSp gegen 3Q (n = 5)"
PRESETS = {
    STANDARD: {},
    "Stapel gegen zwei Warteschlangen (n = 3)": {"e2_a": "S", "e2_b": "2Q", "e2_n": 3},
    "Alle zehn bei n = 4": {"e1_n": 4},
    "Fingerabdruck 2341": {"e3_folge": "2341"},
    "Ordnung bei n = 8": {"e4_n": 8},
    "Zwei Stapel sind vier Maschinen": {"e5_n": 4},
    "Modell V, D = 4": {"e3_d": "4"},
}
PRESET_HELP = {
    STANDARD: "Experiment 2: zwei Stapel parallel gegen drei Warteschlangen parallel bei n = 5, je 103 von 120 Folgen, aber nicht dieselben. Alle übrigen Regler stehen auf ihrem Standardwert.",
    "Stapel gegen zwei Warteschlangen (n = 3)": "Der kleinste Fall: beide sortieren 5 von 6 Folgen, der Stapel scheitert an 231, die zwei Warteschlangen an 321 (Experiment 2).",
    "Alle zehn bei n = 4": "Experiment 1 bei n = 4: die Zahlen aller zehn Maschinen bei 24 Folgen.",
    "Fingerabdruck 2341": "Experiment 3 mit der Folge 2341: welche der zehn Maschinen sie sortieren und wie viele Folgen denselben Fingerabdruck haben.",
    "Ordnung bei n = 8": "Experiment 4 bei n = 8: welche Maschine welche Menge in sich enthält und welche Paare unvergleichbar sind.",
    "Zwei Stapel sind vier Maschinen": "Experiment 5 bei n = 4: zwei Stapel in Serie, parallel, zwei West-Durchläufe, zwei Pop-Stack-Durchläufe.",
    "Modell V, D = 4": "Experiment 3, Zufallsfolgen aus dem ausgedachten Ankunftsmodell mit Verweilzeit-Mittel D = 4 (Länge n = 8).",
}
