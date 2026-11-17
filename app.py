"""Zehn Maschinen im Vergleich: gleiche Zahl, andere Menge - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Zehn Maschinen aus Stapeln, Warteschlangen und einem Pop-Stack, verglichen als Mengen sortierbarer Folgen (vorgerechnet bis n = 8)
und als Zahlen; eine eingegebene Folge prüft die Wegsuche live. Aufbau und Regeln: DEMO-PLAYBOOK.md (§2).

Lauffähig mit: streamlit run app.py
"""

from math import factorial

import pandas as pd
import streamlit as st

import mvg_constants as C
import mvg_evaluation as ev
import mvg_model as MO
import mvg_patterns as P
import mvg_sets as S
import mvg_texts as T
from mvg_evaluation import zd
from mvg_layout import dunkles_design, kopf_css
from mvg_machines import KEYS, NAMES
from mvg_presets import SETTING_SPECS, init_session_state_defaults, load_permalink_settings, randomize_seed, sidebar_presets, sync_query_params
from mvg_visualization import build_hasse, build_modell, build_nur_beide, build_vier, build_zahlen, spur_tabelle

st.set_page_config(page_title="Zehn Maschinen im Vergleich – Sebastian Hanisch", layout="wide")


@st.cache_data(show_spinner=False)
def _zeilen(n):
    return ev.tabelle_zeilen(n)


@st.cache_data(show_spinner=False)
def _alle(folge):
    return ev.pruefe_alle(folge)


@st.cache_data(show_spinner=False)
def _stichprobe(n, d_text, seed):
    return ev.modell_stichprobe(n, d_text, seed)


@st.cache_data(show_spinner=False)
def _frozen():
    return ev.frozen_zeilen()


def _kurz(k):
    return C.KURZ_LANG[k]


def _zeige(verdikt):
    kind, text = verdikt
    getattr(st, kind)(text)


def _zahl_tabelle(spalten):
    """Zahlen aller Maschinen für n = 3 bis 9; gekennzeichnet: † nur gelesen (OEIS), ‡ ab n = 7 nur von der Wegsuche belegt."""
    zeilen = []
    for k in KEYS:
        z = {"Maschine": f"{k}{' ‡' if k in C.NUR_MASCHINE else ''}: {NAMES[k]}"}
        for n in spalten:
            wert = zd(S.zahl(k, n))
            if n == 9 and not S.lade()["n9"][k]["nachgerechnet"]:
                wert += " †"
            z[f"n = {n}"] = wert
        zeilen.append(z)
    kopf = {"Maschine": "alle Folgen n!"}
    for n in spalten:
        kopf[f"n = {n}"] = zd(factorial(n))
    return pd.DataFrame([kopf] + zeilen)


def _zeuge_block(a, b, w, titel):
    """Eine Zeugenfolge: Weg in der Maschine a, die sie sortiert, und Grund, warum b scheitert."""
    ra = ev.pruefe_alle(w)
    st.markdown(f"**{titel}: {P.text_folge(w)}**")
    spalten = st.columns(2)
    with spalten[0]:
        res = ra[a]
        st.caption(f"{a} sortiert sie, Weg in {len(res.schritte)} Schritten:")
        with st.expander(f"Weg von {a} anzeigen"):
            st.dataframe(spur_tabelle(a, res.schritte), hide_index=True, width="stretch")
    with spalten[1]:
        art, grund = P.grund_nein(b, w)
        if grund is None:
            grund = f"Kein einfaches Muster; die Wegsuche untersucht {zd(ra[b].zustaende)} Konfigurationen und findet keinen Weg."
        st.caption(f"{b} sortiert sie nicht. {grund}")


# Fester Kopf: nur der Titel bleibt beim Scrollen oben (Stylesheet in mvg_layout.py).
st.html(kopf_css(dunkles_design()))
with st.container(key="kopf"):
    st.title("🧩 Zehn Maschinen im Vergleich: gleiche Zahl, andere Menge")
st.markdown(T.INTRO)

with st.expander("So funktioniert der Vergleich", expanded=True):
    st.markdown(T.SO_FUNKTIONIERT)

st.caption("🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, um ein Szenario zu teilen.")

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    sidebar_presets()  # Schnellstart oben, das aktive Preset ist hervorgehoben
    st.header("ℹ️ Hinweis")
    st.caption("Die Regler stehen bei den Experimenten im Hauptbereich. Ein Schnellstart setzt alle Regler gemeinsam.")

# --- Kernfrage 1 ---------------------------------------------------------------------------------------------------------------------------

st.markdown("## ❓ Kernfrage 1: Welche Folgen sortiert jede Maschine, und wie viele?")
st.subheader("🔬 Experiment 1: Die Tabelle der zehn Maschinen")
n1 = st.slider("Länge n der Folgen", C.E1_N[0], C.E1_N[1], key="e1_n", help="Bei n = 9 gibt es nur Zahlen (Mengen sind bis n = 8 vorgerechnet).")
zeilen1 = _zeilen(int(n1))
df1 = pd.DataFrame([{"Kürzel": z["kuerzel"], "Maschine": z["name"], "Zahl sortierbarer Folgen": z["zahl"], "Anteil an n! (%)": z["anteil"],
                     "Erstes n mit Verlust": z["erstes_n_verlust"] if z["erstes_n_verlust"] else None} for z in zeilen1])
st.plotly_chart(build_zahlen(zeilen1, int(n1)), width="stretch", key="chart_zahlen")
st.dataframe(df1, hide_index=True, width="stretch", column_config={
    "Anteil an n! (%)": st.column_config.NumberColumn(format="%.2f %%"),
    "Erstes n mit Verlust": st.column_config.NumberColumn(help="Kleinstes n (bis 9), bei dem die Maschine nicht mehr alle n! Folgen sortiert"),
})
_zeige(ev.verdict_tabelle(int(n1)))
st.markdown("**Zahlen aller zehn Maschinen, n = 3 bis 9** (Zähleinheit: Folgen)")
st.dataframe(_zahl_tabelle(range(3, 10)), hide_index=True, width="stretch")
st.caption(
    "† zwei Stapel in Serie bei n = 9: nur OEIS A263929 gelesen, in dieser Demo nicht nachgerechnet. ‡ Stapel und Warteschlange parallel: keine OEIS-Reihe gefunden, "
    "die Zahlen ab n = 7 stützt allein die Wegsuche dieser Demo (zweites Verfahren, Erzeugen aus der Identität, nur bis n = 5). Alle übrigen Zahlen stammen aus der Wegsuche dieser Demo "
    "(n = 9: nur Zahlen, vorgerechnet). Bis n = 8 stimmen sie mit den OEIS-Reihen A000108 (S, 2Q, SQ, QS), A005802 (3Q), A216040 (SSp), A263929 (SSs) und 2^(n−1) (P) überein (Test); bei n = 9 ist nur die Catalan-Zahl 4862 über die Formel geprüft."
)

st.markdown("---")

# --- Kernfrage 2 ---------------------------------------------------------------------------------------------------------------------------

st.markdown("## ❓ Kernfrage 2: Heißt gleiche Zahl auch gleiche Menge?")
st.subheader("🔬 Experiment 2: Gleiche Zahl, andere Menge")
c1, c2, c3 = st.columns(3)
a2 = c1.selectbox("Maschine A", KEYS, key="e2_a", format_func=_kurz)
b2 = c2.selectbox("Maschine B", KEYS, key="e2_b", format_func=_kurz)
n2 = c3.slider("Länge n", C.E2_N[0], C.E2_N[1], key="e2_n", help="Mengen sind bis n = 8 vorgerechnet.")
_zeige(ev.verdict_paar(a2, b2, int(n2)))
if a2 != b2:
    v2 = S.vergleich(a2, b2, int(n2))
    st.plotly_chart(build_nur_beide(a2, b2, v2), width="stretch", key="chart_nur_beide")
    if v2["zeugen_a"] or v2["zeugen_b"]:
        teile = []
        if v2["zeugen_a"]:
            teile.append(f"nur {a2}: " + ", ".join(P.text_folge(w) for w in v2["zeugen_a"]))
        if v2["zeugen_b"]:
            teile.append(f"nur {b2}: " + ", ".join(P.text_folge(w) for w in v2["zeugen_b"]))
        st.markdown("**Die kleinsten Zeugenfolgen** (lexikographisch, höchstens fünf je Seite): " + "; ".join(teile))
        if v2["zeugen_a"]:
            _zeuge_block(a2, b2, v2["zeugen_a"][0], f"Zeuge, den nur {a2} sortiert")
        if v2["zeugen_b"]:
            _zeuge_block(b2, a2, v2["zeugen_b"][0], f"Zeuge, den nur {b2} sortiert")
hinweis = ev.gleiche_menge_hinweis(a2, b2)
if hinweis:
    st.info(hinweis)
klassen8 = [kl for kl in S.ordnung(8)["klassen"] if len(kl) > 1]
st.caption("Gemessen für n ≤ 8, nicht bewiesen: Maschinen mit gleicher Menge sind " + "; ".join(", ".join(kl) for kl in klassen8) + ". Alle übrigen Paare haben bei n = 8 verschiedene Mengen.")

st.subheader("🔬 Experiment 3: Meine Folge – wer schafft sie?")
st.text_input("Eigene Folge (Permutation von 1 bis n, n = 3 bis 10; Leerzeichen oder Komma als Trenner, bis n = 9 auch ohne)", key="e3_folge",
              help="Zum Beispiel 2341 oder 3 1 5 2 4. Eine Permutation: jede Zahl von 1 bis n genau einmal.")
folge, fehler = ev.parse_folge(st.session_state["e3_folge"])
if fehler:
    st.error(fehler)
elif len(folge) < 3:
    st.warning("Bitte mindestens drei Zahlen eingeben (kürzere Folgen sortieren alle Maschinen außer Q bei 21).")
else:
    ergebnisse = _alle(folge)
    _zeige(ev.verdict_folge(folge, ergebnisse))
    zeilen3 = []
    for k in KEYS:
        r = ergebnisse[k]
        if r.sortierbar:
            grund = f"Weg in {len(r.schritte)} Schritten (unten)"
        else:
            art, g = P.grund_nein(k, folge)
            grund = g if g else f"kein einfaches Muster: die Wegsuche untersucht {zd(r.zustaende)} Konfigurationen und findet keinen Weg"
        zeilen3.append({"Kürzel": k, "Maschine": NAMES[k], "sortiert?": "ja" if r.sortierbar else "nein", "Weg bzw. Grund": grund})
    st.dataframe(pd.DataFrame(zeilen3), hide_index=True, width="stretch")
    for k in KEYS:
        if ergebnisse[k].sortierbar:
            with st.expander(f"Weg von {k} ({NAMES[k]}) für {P.text_folge(folge)}"):
                st.dataframe(spur_tabelle(k, ergebnisse[k].schritte), hide_index=True, width="stretch")
    if len(folge) <= S.N_MENGEN:
        _zeige(ev.verdict_gleichverteilt(len(folge)))

st.markdown("**Zufallsfolgen aus einem ausgedachten Ankunftsmodell** (Modell V: Verweilzeit exponentialverteilt mit Mittel D; ∞ = gleichverteilt)")
st.warning("Das Ankunftsmodell ist **ausgedacht**: es gibt in den Quellen keine reale Ankunftsfolge. Die Zahlen unten gelten für dieses Modell, nicht für einen Hafen oder Bahnhof.")
m1, m2, m3, m4 = st.columns([2, 3, 2, 2])
n3 = m1.slider("Länge n der Zufallsfolgen", C.E3_N[0], C.E3_N[1], key="e3_n", help="Mengen sind bis n = 8 vorgerechnet; die vorgerechnete Tabelle unten gilt für n = 8.")
d3 = m2.select_slider("Verweilzeit-Mittel D (in Ankunftsabständen)", options=C.D_OPTIONEN, key="e3_d", help="Klein: die Reihenfolge der Abfahrt bleibt fast die der Ankunft. ∞: gleichverteilt.")
seed3 = m3.number_input("Zufalls-Seed", C.E3_SEED[0], C.E3_SEED[1], key="e3_seed", step=1)
m4.button("🎲 Neuer Zufalls-Seed", width="stretch", on_click=randomize_seed)
with st.spinner(f"Rechne {zd(MO.ANZAHL_LIVE)} Zufallsfolgen (etwa 1 Sekunde) …"):
    stich = _stichprobe(int(n3), d3, int(seed3))
beispiel = MO.stichprobe(int(n3), ev.d_wert(d3), 1, int(seed3))[0]
st.caption(f"Die erste Zufallsfolge dieses Zufalls-Seeds: {P.text_folge(beispiel)}, sortiert von {', '.join(S.fingerabdruck(beispiel)) or 'keiner Maschine'}.")
st.plotly_chart(build_modell(stich["anteile"], stich["anzahl"], int(n3)), width="stretch", key="chart_modell")
_zeige(ev.verdict_modell(int(n3), d3, int(seed3), stich))
st.markdown("**Vorgerechnet: n = 8, 20 000 Folgen je Verweilzeit-Mittel D** (Anteil in Prozent; Zufalls-Seed 20000 + Index der Zeile)")
fz = _frozen()
tab = []
for z in fz:
    zeile = {"D": MO.d_text(z["d"])}
    zeile.update({k: 100 * z["anteile"][k] for k in KEYS})
    zeile["Mittel Maschinen"] = z["mittel"]
    zeile["S − 2Q (Punkte)"] = 100 * z["paare"]["S|2Q"][0]
    zeile["3Q − SSp (Punkte)"] = 100 * z["paare"]["3Q|SSp"][0]
    tab.append(zeile)
exakt = {"D": "∞ exakt (alle Folgen)"}
exakt.update({k: 100 * S.anteil(k, 8) for k in KEYS})
exakt.update({"Mittel Maschinen": S.mittlere_zahl_maschinen(8), "S − 2Q (Punkte)": 0.0, "3Q − SSp (Punkte)": 100 * (S.anteil("3Q", 8) - S.anteil("SSp", 8))})
tab.append(exakt)
cfg = {k: st.column_config.NumberColumn(format="%.2f") for k in KEYS}
cfg.update({"Mittel Maschinen": st.column_config.NumberColumn(format="%.3f"), "S − 2Q (Punkte)": st.column_config.NumberColumn(format="%+.2f"),
            "3Q − SSp (Punkte)": st.column_config.NumberColumn(format="%+.2f")})
st.dataframe(pd.DataFrame(tab), hide_index=True, width="stretch", column_config=cfg)
_zeige(ev.verdict_frozen(fz))

st.markdown("---")

# --- Kernfrage 3 ---------------------------------------------------------------------------------------------------------------------------

st.markdown("## ❓ Kernfrage 3: Welche Maschine kann mehr als welche?")
st.subheader("🔬 Experiment 4: Wer kann mehr?")
o1, o2, o3 = st.columns(3)
n4 = o1.slider("Länge n", C.E4_N[0], C.E4_N[1], key="e4_n", help="Mengen sind bis n = 8 vorgerechnet.")
a4 = o2.selectbox("Maschine A", KEYS, key="e4_a", format_func=_kurz)
b4 = o3.selectbox("Maschine B", KEYS, key="e4_b", format_func=_kurz)
st.plotly_chart(build_hasse(int(n4)), width="stretch", key="chart_hasse")
st.caption("Ordnungsdiagramm: ein Verbindungsstrich von unten nach oben heißt „die untere Menge liegt echt in der oberen, nichts dazwischen“. Maschinen mit gleicher Menge stehen zusammen (S=SQ=QS). "
           "Zwei Maschinen sind vergleichbar, wenn man über Verbindungsstriche von der einen nach oben zur anderen kommt, sonst unvergleichbar.")
_zeige(ev.verdict_ordnung(int(n4)))
_zeige(ev.verdict_ordnung_paar(a4, b4, int(n4)))
unv = []
for a_, b_ in S.ordnung(int(n4))["unvergleichbar"]:
    v = S.vergleich(a_, b_, int(n4))
    unv.append({"Paar": f"{a_} / {b_}", "nur erste Maschine": v["nur_a"], "gemeinsam": v["beide"], "nur zweite Maschine": v["nur_b"],
                "kleinster Zeuge (nur erste)": P.text_folge(v["zeugen_a"][0]), "kleinster Zeuge (nur zweite)": P.text_folge(v["zeugen_b"][0])})
if unv:
    st.markdown("**Unvergleichbare Paare** (je Vertreter einer Klasse gleicher Menge; Zähleinheit: Folgen)")
    st.dataframe(pd.DataFrame(unv), hide_index=True, width="stretch")

st.subheader("🔬 Experiment 5: „Zwei Stapel“ sind vier Maschinen")
n5 = st.slider("Länge n", C.E5_N[0], C.E5_N[1], key="e5_n", help="Mengen sind bis n = 8 vorgerechnet.")
vier = []
for n_ in range(4, 9):
    z = S.vier_zwei_stapel(n_)
    vier.append({"n": n_, "n!": zd(z["n!"]), "in Serie (SSs)": zd(z["SSs"]), "parallel (SSp)": zd(z["SSp"]), "West-2": zd(z["W2"]), "Pop-2": zd(z["P2"])})
st.dataframe(pd.DataFrame(vier), hide_index=True, width="stretch")
st.plotly_chart(build_vier(range(4, 9)), width="stretch", key="chart_vier")
_zeige(ev.verdict_vier(int(n5)))
if int(n5) <= 5:
    st.markdown(f"**Folgen der Länge {int(n5)}, die die Maschine nicht sortiert**")
    fehl = []
    for k, name in (("SSp", "zwei Stapel parallel"), ("W2", "zwei West-Durchläufe"), ("P2", "zwei Pop-Stack-Durchläufe")):
        liste = ev.kleine_n_fehlfolgen(k, int(n5))
        fehl.append({"Maschine": f"{name}", "Zahl": len(liste), "Folgen": " ".join(P.text_folge(w) for w in liste) if len(liste) <= 20 else "(zu viele zum Aufzählen)"})
    st.dataframe(pd.DataFrame(fehl), hide_index=True, width="stretch")
    st.caption("Zwei Stapel in Serie sortieren bis n = 6 alle Folgen.")
zeuge5 = (4, 1, 3, 5, 2)
st.markdown("**Zeuge: West-2 und Pop-2 sind unvergleichbar (n = 5)**")
spuren = []
for name, regel in (("Pop-Stack", P.pop_durchlauf), ("West", P.west_durchlauf)):
    eins = regel(zeuge5)
    zwei = regel(eins)
    spuren.append({"Regel": f"zwei {name}-Durchläufe", "Eingabe": P.text_folge(zeuge5), "nach 1. Durchlauf": P.text_folge(eins),
                   "nach 2. Durchlauf": P.text_folge(zwei), "sortiert?": "ja" if zwei == tuple(range(1, 6)) else "nein"})
st.dataframe(pd.DataFrame(spuren), hide_index=True, width="stretch")
st.caption("Was ein Durchlauf ist und wie viele Durchläufe eine Folge braucht, steht in der Nachbar-Demo "
           "[`mehrere-durchlaeufe-demo`](https://github.com/sebastian-hanisch/mehrere-durchlaeufe-demo). West-Durchlauf: ein Stapel, der vor dem Einlegen alle kleineren Zahlen an der Spitze ausgibt; "
           "Pop-Stack-Durchlauf: jeder maximale fallende Lauf wird umgekehrt.")

st.markdown("---")

# --- Grenzen -------------------------------------------------------------------------------------------------------------------------------

st.subheader("🚧 Wo die Annahmen enden")
st.markdown(T.GRENZEN)
st.caption("Catalan-Zahlen, Muster-Klassen und Wachstum sind Stoff der Seite [Abzählen](https://sebastianhanisch.net/konzepte-abzaehlen.html); "
           "hier erscheinen sie nur als Spalten der Tabelle. Vorgänger-Demo: [`stapel-sortieren-demo`](https://github.com/sebastian-hanisch/stapel-sortieren-demo) (ein Stapel allein).")

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(T.FORMELN_KONVENTION)
    st.markdown(T.FORMELN_MODELL)

sync_query_params({key: st.session_state[key] for key in SETTING_SPECS})

st.markdown("---")
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html)."
)
