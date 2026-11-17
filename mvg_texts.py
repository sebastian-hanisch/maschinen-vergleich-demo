"""Längere Texte der App (Markdown), damit app.py übersichtlich bleibt."""

INTRO = """
Eine **Maschine** nimmt Container (Zahlen 1 bis n) in der Reihenfolge ihrer Ankunft entgegen und soll sie in der Reihenfolge 1, 2, …, n wieder ausgeben. Sie besteht aus **Stapeln**
(nur die Spitze ist zugänglich), **Warteschlangen** (nur der Kopf) oder einem **Pop-Stack** (nur ganz leerbar). Welche der n! Ankunftsfolgen eine Maschine schafft, ist eine **Menge**;
wie viele es sind, eine **Zahl**. Diese Demo stellt **zehn Maschinen** nebeneinander, mit freier Zwischenausgabe (ausgegeben werden darf jederzeit) und lauter verschiedenen Werten.

**Die Kernbehauptung zum Prüfen:** Die Zahl sortierbarer Folgen kennzeichnet eine Maschine **nicht**. Zwei Maschinen mit derselben Zahl können verschiedene Folgen sortieren; die zehn Maschinen haben bis n = 8
sieben verschiedene Zählfolgen, aber acht verschiedene Mengen. Alle Mengen bis n = 8 sind **vorgerechnet** (Aufzählung aller n! Folgen); eine eingegebene Folge mit bis zu 10 Zahlen prüft die App live.
Das ausgedachte Ankunftsmodell in Experiment 3 ist ein **Modell, keine reale Ankunftsfolge**.

Weiter unten: drei Kernfragen mit fünf Experimenten, der Abschnitt **🚧 Wo die Annahmen enden** und der Expander **📐 Mathematische Formulierung**.
"""

SO_FUNKTIONIERT = """
**Die zehn Maschinen** (Kürzel in allen Tabellen):

| Kürzel | Maschine | Zugang |
|---|---|---|
| **Q** | eine Warteschlange | nur der Kopf |
| **S** | ein Stapel | nur die Spitze |
| **2Q**, **3Q** | zwei bzw. drei Warteschlangen parallel | Eingang in eine beliebige, Ausgang aus einer beliebigen |
| **SSs** | zwei Stapel in Serie | Ausgang des ersten ist Eingang des zweiten |
| **SSp** | zwei Stapel parallel | Eingang in einen beliebigen, Ausgang aus einem beliebigen |
| **SQ**, **QS** | Stapel, dann Warteschlange; Warteschlange, dann Stapel | in Serie |
| **SpQ** | Stapel und Warteschlange parallel | wie SSp, mit einer Warteschlange |
| **P** | ein Pop-Stack | nur ganz leerbar, Inhalt von oben nach unten |

1. **Sortierbar** heißt: es gibt irgendeinen Weg (Einlegen, Umsetzen, Ausgeben), der 1, 2, …, n in dieser Reihenfolge ausgibt. Ein Weg wird als Schrittfolge gezeigt.
2. **Zählen:** eine Folge ist eine Anordnung der Zahlen 1 bis n (links = zuerst angekommen). Für n = 3 gibt es 6 Folgen; ein Stapel sortiert 5 davon (nicht 231), zwei Warteschlangen parallel ebenfalls 5 (nicht 321).
3. **Zwischenausgabe ist erlaubt:** ohne sie wären es andere Maschinen („erst alles hinein, dann alles hinaus“: zwei parallele Stapel sortieren so bei n = 6 nur 132 statt 513 Folgen).
4. **„Zwei Stapel“ steht nie allein:** in Serie, parallel, zwei West-Durchläufe oder zwei Pop-Stack-Durchläufe sind vier verschiedene Maschinen (Experiment 5).
"""

GRENZEN = """
| Annahme | Was passiert, wenn sie verletzt ist | Wo es weitergeht |
|---|---|---|
| **Zwischenausgabe ist erlaubt** | Ohne sie sind es andere Maschinen: m parallele Stapel sortieren dann genau die Folgen mit längster wachsender Teilfolge höchstens m (nach Tarjan 1971, Vorfassung; bei n = 6 und zwei Stapeln 132 statt 513 Folgen). | [`patience-stapel-demo`](https://github.com/sebastian-hanisch/patience-stapel-demo) |
| **Ein Durchlauf** (außer in Experiment 5) | Mehrere Durchläufe durch dieselbe Maschine sortieren mehr; „k Durchläufe“ hat mehrere Lesarten. Hier kommen West-2 und Pop-2 nur als Zahl und als Zeugen vor. | [`mehrere-durchlaeufe-demo`](https://github.com/sebastian-hanisch/mehrere-durchlaeufe-demo) |
| **Alle Werte verschieden** | Mit gleichen Zielgruppen (Gleichständen) ändern sich die Zahlen; die Catalan-Zahl gilt dann nicht mehr. | [`stapel-sortieren-demo`](https://github.com/sebastian-hanisch/stapel-sortieren-demo) |
| **Mengen nur bis n = 8** | Alle Mengenaussagen („gleiche Menge“, „unvergleichbar“, 45 Paare) sind für n ≤ 8 aufgezählt, nicht bewiesen; bei n = 9 gibt es nur Zahlen, und die Zahl für zwei Stapel in Serie ist dort nur aus OEIS A263929 gelesen. | – |
| **Nur diese zehn Maschinen** | Deque, Prioritätswarteschlange, drei Stapel und Netze mit mehr Behältern sind nicht gemessen. | – |
| **Ausgedachtes Ankunftsmodell** (Experiment 3) | Verweilzeit exponentialverteilt, Abholrang aus der Abfahrtsordnung, nur n = 8 als Tabelle: ein Modell, keine Betriebsdaten; es gibt in den Quellen keine reale Ankunftsfolge. | – |
| **Zwei Stapel in Serie als Maschine** | Wo diese Maschine scheitert (bei n = 7 an 22 von 5040 Folgen) und wie man das erkennt, ist eigener Stoff. | [`zwei-stapel-serie-demo`](https://github.com/sebastian-hanisch/zwei-stapel-serie-demo) |
"""

FORMELN_KONVENTION = r"""
**Gegeben und gesucht.** Gegeben ist eine Folge $p = (p_1, \dots, p_n)$, eine Permutation von $1, \dots, n$ (links = zuerst angekommen) und eine Maschine $M$. Gesucht ist die Antwort auf die Frage, ob $M$ die Folge sortiert, also ob es einen Weg gibt, der $1, 2, \dots, n$ in dieser Reihenfolge ausgibt, und die Menge $\mathrm{Sort}_n(M)$ aller solchen $p$.

| Symbol | Bedeutung |
|---|---|
| $n$ | Länge der Folge (Zahl der Container) |
| $p$ | Folge: Anordnung von $1, \dots, n$ in Ankunftsreihenfolge |
| $\mathrm{Sort}_n(M)$ | Menge der Folgen der Länge $n$, die die Maschine $M$ sortiert |
| $\lvert\mathrm{Sort}_n(M)\rvert$ | **Zahl** der sortierbaren Folgen (Zähleinheit: Folgen) |
| $n!$ | Zahl aller Folgen der Länge $n$ |
| $C_n$ | Catalan-Zahl $\binom{2n}{n}/(n+1)$ |
| $\mathrm{lds}(p)$ | Länge der längsten fallenden Teilfolge von $p$ |
"""

FORMELN_MODELL = r"""
**Vollständiges Modell einer Maschine.** Eine Maschine hat Behälter $B_1, \dots, B_k$, jeder ein Stapel, eine Warteschlange oder ein Pop-Stack, eine Menge $E$ von Behältern, in die eine ankommende Zahl darf, eine Menge $U$ von erlaubten Umsetzungen $(B_a \to B_b)$ und eine Menge $A$ von Ausgangsbehältern. Ein **Zustand** ist $(m, c_1, \dots, c_k)$ mit der Zahl $m$ der schon ausgegebenen Zahlen und den Inhalten $c_i$. Erlaubte **Züge**:

- Einlegen der nächsten Zahl der Folge ans Ende eines Behälters aus $E$ (an der Spitze bzw. hinten);
- Umsetzen der zugänglichen Zahl von $B_a$ ans Ende von $B_b$ für $(a, b) \in U$;
- Ausgeben der zugänglichen Zahl eines Behälters aus $A$ (Stapel: Spitze, Warteschlange: Kopf); bei einem Pop-Stack nur Leeren des ganzen Behälters, Inhalt von oben nach unten.

$p$ ist sortierbar, wenn vom Zustand $(0, \emptyset, \dots, \emptyset)$ nach dem Einlegen aller $n$ Zahlen ein Zustand mit $m = n$ erreichbar ist **und die Ausgabe $1, 2, \dots, n$ ist**; die App prüft das, indem nur die jeweils nächste gesuchte Zahl ausgegeben wird.

**Zwei sichere Abkürzungen** der Wegsuche: Die nächste gesuchte Zahl wird sofort ausgegeben, wenn sie an der zugänglichen Stelle eines Ausgangsbehälters steht; ein Behälter, aus dem nur noch ausgegeben wird, muss schon richtig geordnet sein. Beide sind gegen die rohe Suche geprüft (bis $n = 5$).

**Charakterisierungen** (Lehrbuchstoff; die Tests rechnen sie gegen die Wegsuche nach):

$$\mathrm{Sort}_n(S) = \mathrm{Av}_n(231), \qquad \lvert\mathrm{Sort}_n(S)\rvert = C_n$$

$$\mathrm{Sort}_n(mQ) = \{p : \mathrm{lds}(p) \le m\}, \qquad \lvert\mathrm{Sort}_n(P)\rvert = 2^{\,n-1},\ \mathrm{Sort}_n(P) = \mathrm{Av}_n(231, 312)$$

$\mathrm{Av}_n(\mu)$ ist die Menge der Folgen ohne das Muster $\mu$. Für zwei parallele Stapel gilt: $p$ ist sortierbar genau dann, wenn der Konfliktgraph zweifärbbar ist; Konfliktkanten sind die Stellenpaare $i < j$ mit $p_i < p_j$, hinter denen noch eine Zahl kleiner als $p_i$ kommt (eigene Fassung der Kantendefinition, gegen die Wegsuche bis $n = 8$ bestätigt).

**Gleiche Zahl, andere Menge** heißt: $\lvert\mathrm{Sort}_n(M)\rvert = \lvert\mathrm{Sort}_n(M')\rvert$ bei $\mathrm{Sort}_n(M) \ne \mathrm{Sort}_n(M')$. Bei $n = 3$ ist $\mathrm{Sort}_3(S)$ alle Folgen außer $231$, $\mathrm{Sort}_3(2Q)$ alle außer $321$: beide haben $5$ Elemente.

**Ankunftsmodell V (ausgedacht).** Ankunftszeit $i$, Abfahrtszeit $t_i = i + D \cdot E_i$ mit $E_i$ exponentialverteilt (Mittel 1), die Folge ist $p_i = $ Rang von $t_i$ unter $t_1, \dots, t_n$. $D = \infty$ ist die Gleichverteilung über alle $n!$ Folgen. Standardfehler eines Anteils $\hat q$ aus $N$ Folgen: $\sqrt{\hat q (1 - \hat q) / N}$; die Bänder der App sind vier Standardfehler.

**Literatur** (Stufe: gelesen, soweit angegeben). Bóna, „A survey of stack-sorting disciplines“, Electron. J. Combin. 9(2) (2003), #A1: Satz 1.3 (Stapel und 231), Pop-Stack und geschichtete Folgen, West-2 (gelesen). Tarjan, „The Switchyard Problem“, Stanford CS-TR-71-213 (1971), Vorfassung des Aufsatzes in J. ACM 19 (1972): Lemma 2 (parallele Warteschlangen und fallende Teilfolgen) und Lemma 3 (nur die Vorfassung gelesen). Zwei parallele Stapel und der Konfliktgraph: Even/Itai 1971, nur über Tarjan und Albert/Bousquet-Mélou gelesen (Original nicht gelesen); Albert/Bousquet-Mélou, Eur. J. Combin. 43 (2015) (Einleitung und Reihenwerte gelesen). OEIS A000108, A005802, A216040, A263929, A000139, A011782 (gelesen). Die Originale von Tarjan 1972, Even/Itai und Knuth sind nicht gelesen.
"""
