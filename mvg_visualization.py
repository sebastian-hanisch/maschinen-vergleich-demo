"""Plotly-Abbildungen. Alle Achsen sind gesperrt (fixedrange), damit Touch-Geräte beim Scrollen nicht am Diagramm hängen bleiben."""

import plotly.graph_objects as go

import mvg_constants as C
import mvg_model as MO
import mvg_sets as S
from mvg_machines import KEYS


def lock_axes(fig):
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    return fig


def _base(fig, height=360, legend=True):
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=10, b=10), plot_bgcolor="rgba(0,0,0,0)", showlegend=legend)
    if legend:
        fig.update_layout(legend=dict(orientation="h", y=-0.2))
    return lock_axes(fig)


def build_zahlen(zeilen, n):
    """Balken je Maschine (Zahl der sortierbaren Folgen bei n); Maschinen mit gleicher Zahl haben dieselbe Farbe."""
    farben = [C.GRUPPEN_FARBEN[z["gruppe"] % len(C.GRUPPEN_FARBEN)] for z in zeilen]
    fig = go.Figure(go.Bar(
        x=[z["kuerzel"] for z in zeilen], y=[z["zahl"] for z in zeilen], marker_color=farben,
        text=[f"{z['zahl']:,}".replace(",", " ") for z in zeilen], textposition="outside", cliponaxis=False,
        hovertemplate="%{x}: %{y} Folgen<extra></extra>",
    ))
    fig.update_yaxes(title_text=f"sortierbare Folgen bei n = {n}", rangemode="tozero")
    fig.update_xaxes(title_text="Maschine (gleiche Farbe = gleiche Zahl)", type="category")
    fig.update_layout(margin=dict(l=10, r=10, t=30, b=10))
    return _base(fig, legend=False)


def build_nur_beide(a, b, v):
    """Gestapelter Balken: nur A, gemeinsam, nur B."""
    fig = go.Figure()
    for name, wert, farbe in ((f"nur {a}", v["nur_a"], C.COLOR_A), ("gemeinsam", v["beide"], C.COLOR_BEIDE), (f"nur {b}", v["nur_b"], C.COLOR_B)):
        fig.add_trace(go.Bar(y=[""], x=[wert], orientation="h", name=name, marker_color=farbe, text=[f"{name}: {wert}"], textposition="inside",
                             hovertemplate=f"{name}: {wert} Folgen<extra></extra>"))
    fig.update_layout(barmode="stack")
    fig.update_xaxes(title_text="Folgen")
    return _base(fig, height=170)


def hasse_positionen(klassen, kanten):
    """Ebene je Klasse: 0 ohne Vorgänger, sonst 1 + größte Ebene eines Vorgängers; x gleichmäßig je Ebene. Rückgabe {Vertreter: (x, y)}."""
    rep = [kl[0] for kl in klassen]
    unter = {r: [a for a, b in kanten if b == r] for r in rep}
    ebene = {}

    def tiefe(r):
        if r not in ebene:
            ebene[r] = 0 if not unter[r] else 1 + max(tiefe(a) for a in unter[r])
        return ebene[r]

    for r in rep:
        tiefe(r)
    pos = {}
    for e in sorted(set(ebene.values())):
        auf = [r for r in rep if ebene[r] == e]
        for i, r in enumerate(auf):
            pos[r] = ((i + 1) / (len(auf) + 1), e)
    return pos


def build_hasse(n):
    """Ordnungsdiagramm der Mengenklassen bei n: unten die kleineren Mengen, ein Verbindungsstrich heißt „echte Teilmenge, nichts dazwischen“."""
    o = S.ordnung(n)
    pos = hasse_positionen(o["klassen"], o["kanten"])
    namen = {kl[0]: "=".join(kl) for kl in o["klassen"]}
    fig = go.Figure()
    for a, b in o["kanten"]:
        (xa, ya), (xb, yb) = pos[a], pos[b]
        fig.add_trace(go.Scatter(x=[xa, xb], y=[ya, yb], mode="lines", line=dict(color="rgba(120,120,120,0.8)", width=2), hoverinfo="skip", showlegend=False))
    fig.add_trace(go.Scatter(
        x=[pos[r][0] for r in pos], y=[pos[r][1] for r in pos], mode="markers+text", text=[namen[r] for r in pos], textposition="top center",
        marker=dict(size=14, color=C.COLOR_LINE), customdata=[S.zahl(r, n) for r in pos],
        hovertemplate="%{text}: %{customdata} Folgen<extra></extra>", showlegend=False))
    fig.update_xaxes(visible=False, range=[0, 1])
    fig.update_yaxes(visible=False, range=[-0.5, max(p[1] for p in pos.values()) + 0.7])
    fig.update_layout(margin=dict(l=10, r=10, t=10, b=10))
    return _base(fig, height=330, legend=False)


def build_modell(anteile, anzahl, titel_n):
    """Anteil je Maschine im Modell mit Band (vier Standardfehler)."""
    ys = [100 * anteile[k] for k in KEYS]
    fehler = [100 * MO.band(anteile[k], anzahl) for k in KEYS]
    fig = go.Figure(go.Bar(x=list(KEYS), y=ys, marker_color=C.COLOR_LINE, error_y=dict(type="data", array=fehler, visible=True),
                           hovertemplate="%{x}: %{y:.1f} %<extra></extra>"))
    fig.update_yaxes(title_text=f"sortierte Zufallsfolgen (%), n = {titel_n}", range=[0, 105])
    fig.update_xaxes(type="category")
    return _base(fig, legend=False)


def build_vier(ns):
    """Anteil an n! der vier „zwei Stapel“ über n."""
    namen = {"SSs": "in Serie (SSs)", "SSp": "parallel (SSp)", "W2": "West-2", "P2": "Pop-2"}
    fig = go.Figure()
    for k, name in namen.items():
        fig.add_trace(go.Scatter(x=list(ns), y=[100 * S.anteil(k, n) for n in ns], mode="lines+markers", name=name))
    fig.update_xaxes(title_text="n", dtick=1)
    fig.update_yaxes(title_text="Anteil an n! (%)", range=[0, 105])
    return _base(fig)


def spur_tabelle(key, schritte):
    """Tabelle eines Weges: Schritt, Aktion, Inhalt der Behälter nach dem Schritt und bisherige Ausgabe (Stapel und Pop-Stack: unten → Spitze, Warteschlange: vorn → hinten)."""
    import pandas as pd

    from mvg_machines import NETS, abspielen, beschreibe, inhalt_text

    net = NETS[key]
    zustand = abspielen(key, schritte)
    zeilen = []
    for i, (s, (cfg, aus)) in enumerate(zip(schritte, zustand), start=1):
        zeile = {"Schritt": i, "Aktion": beschreibe(key, s)}
        for b, label in enumerate(net.labels):
            richtung = "vorn → hinten" if net.types[b] == "Q" else "unten → Spitze"
            zeile[f"{label} ({richtung})"] = inhalt_text(net.types[b], cfg[1 + b])
        zeile["Ausgabe bisher"] = " ".join(map(str, aus)) if aus else "·"
        zeilen.append(zeile)
    return pd.DataFrame(zeilen)
