# Zehn Maschinen im Vergleich: gleiche Zahl, andere Menge – Streamlit-Demo

<!-- TODO nach dem Deploy: direkt hierher den Live-Link setzen (Leerzeile davor und danach):
**[→ Demo live ausprobieren](https://sebastianhanisch-maschinen-vergleich-demo.streamlit.app/)** -->

Eine von mehreren Demos zu **Sortiermaschinen und Permutationen** für die Website „Sebastian Hanisch – Operations Research und Machine Learning“. Sie nimmt die Annahme heraus, die
[`stapel-sortieren-demo`](https://github.com/sebastian-hanisch/stapel-sortieren-demo) noch macht: dass die Maschine **ein Stapel** ist und die Zahl seiner sortierbaren Folgen (Catalan-Zahl) kennzeichnet,
was eine Maschine schafft. Hier stehen **zehn Maschinen** aus Stapeln, Warteschlangen und einem Pop-Stack nebeneinander, alle mit freier Zwischenausgabe, und die Demo vergleicht sie als
**Mengen** (welche Folgen) und als **Zahlen** (wie viele). Die Mengen bis n = 8 sind durch Aufzählung aller n! Folgen vorgerechnet; eine eingegebene Folge mit bis zu 10 Zahlen prüft die App live und zeigt
einen Weg oder den Grund des Scheiterns.

**Die Mengenvergleiche brauchen kein Vehikel**: die Zahlen sind Eigenschaften der Menge aller n! Folgen, nicht eines Betriebs. Ein Stapel, der 5 von 6 Folgen sortiert, ist keine Aussage über einen Bahnhof.
Nur Experiment 3 benutzt zusätzlich ein **ausgedachtes Ankunftsmodell** (Verweilzeit exponentialverteilt mit Mittel D, Abholrang aus der Abfahrtsordnung): ein **Modell, keine reale Ankunftsfolge**; es gibt in den
gelesenen Quellen keine. Nachbarn: [`stapel-sortieren-demo`](https://github.com/sebastian-hanisch/stapel-sortieren-demo) (ein Stapel allein),
[`mehrere-durchlaeufe-demo`](https://github.com/sebastian-hanisch/mehrere-durchlaeufe-demo) (Durchläufe: West-k, Pop-Stack-k),
[`zwei-stapel-serie-demo`](https://github.com/sebastian-hanisch/zwei-stapel-serie-demo) (zwei Stapel in Serie: wo sie scheitern),
[`patience-stapel-demo`](https://github.com/sebastian-hanisch/patience-stapel-demo) (Ablage ohne Zwischenausgabe, längste Teilfolgen),
[`ablaufberg-demo`](https://github.com/sebastian-hanisch/ablaufberg-demo) (Gleise als Warteschlangen, Radix mit Gruppen),
[`mehrhafenstau-demo`](https://github.com/sebastian-hanisch/mehrhafenstau-demo) (Stapel als Ablage mit Patience Sorting).

## Warum dieses Problem

Eine Zählfolge (1, 2, 5, 14, 42, …) sieht aus wie ein Name für die Maschine. Sie ist keiner. **Heißt gleiche Zahl sortierbarer Folgen auch gleiche Menge, und welche Maschine kann mehr als welche?**

Bei n = 3 sortieren ein Stapel und zwei Warteschlangen parallel je 5 von 6 Folgen: der Stapel scheitert an 231, die zwei Warteschlangen an 321. Zwei Stapel parallel (SSp) und drei Warteschlangen parallel (3Q)
sortieren bei n = 4, 5 und 6 je 23, 103 und 513 Folgen, aber 1, 17 und 171 Folgen sortiert nur SSp und ebenso viele nur 3Q; erst bei n = 7 trennt auch die Zahl (2760 gegen 2761). Unter den 45 Paaren der zehn Maschinen
haben bei n = 4, 5 und 6 je 7 Paare dieselbe Zahl unter n!, und bei je 4 davon sind die Mengen verschieden; bei n = 7 und 8 sind es 6 Paare und 3 mit verschiedenen Mengen. Die zehn Maschinen haben bis n = 8
**sieben verschiedene Zählfolgen, aber acht verschiedene Mengen.** Ehrlich dazu: Stapel, Stapel→Warteschlange (SQ) und Warteschlange→Stapel (QS) sortieren für n ≤ 8 dieselbe Menge (gemessen, nicht bewiesen), und
im ausgedachten Ankunftsmodell bei n = 8 unterscheiden sich die Anteile von Stapel und zwei Warteschlangen in keiner der 7 vorgerechneten Zeilen (je 20 000 Folgen) um mehr als vier Standardfehler der Differenz:
der Unterschied zeigt sich in der **Menge**; in der Häufigkeit ist im Modell mit 20 000 Folgen je Zeile kein Unterschied feststellbar (kleinere Unterschiede sind nicht ausgeschlossen). Alles gilt für diese zehn Maschinen mit freier Zwischenausgabe, lauter verschiedene Werte, Zähleinheit Folgen (Maschinenpaare für die Paarzählung).

## Modell

* **Folge, sortierbar:** eine Folge ist eine Anordnung der Zahlen 1 bis n in Ankunftsreihenfolge (links = zuerst). **Sortierbar durch eine Maschine** heißt: es gibt irgendeinen Weg aus Einlegen, Umsetzen und Ausgeben
  (Ausgabe jederzeit erlaubt), der 1, 2, …, n in dieser Reihenfolge ausgibt. „Sortierbar“ ist nicht „pop-stacked“ (Bild der Pop-Stack-Abbildung).
* **Behälter:** Stapel (nur die Spitze zugänglich), Warteschlange (nur der Kopf), Pop-Stack (nur ganz leerbar, Inhalt von oben nach unten; ein Durchlauf). **Eingabe** einer von einem Stapel sortierbaren Folge vermeidet 231;
  die erzeugbaren Ausgaben (Eingabe 1..n, Ausgabe frei) vermeiden 312: Sortieren und Erzeugen sind invers.
* **Die zehn Maschinen:** Q (eine Warteschlange), S (ein Stapel), 2Q und 3Q (zwei bzw. drei Warteschlangen parallel), SSs (zwei Stapel in Serie), SSp (zwei Stapel parallel), SQ (Stapel, dann Warteschlange),
  QS (Warteschlange, dann Stapel), SpQ (Stapel und Warteschlange parallel), P (ein Pop-Stack). **„Zwei Stapel“ steht nie allein:** in Serie, parallel, zwei West-Durchläufe oder zwei Pop-Stack-Durchläufe
  sind vier Maschinen (Experiment 5).
* **Zähleinheiten:** Folgen (alle n! Anordnungen) für Zahlen und Mengen; Maschinenpaare (45) für die Paarstatistik; Zufallsfolgen nur im Ankunftsmodell.
* **Ausdrückliche Grenze:** Zwischenausgabe ist überall erlaubt. Ohne sie sind es andere Maschinen („erst alles hinein, dann alles hinaus“): m parallele Stapel sortieren dann genau die Folgen mit längster wachsender
  Teilfolge höchstens m (Tarjan 1971, Lemma 3, nach der Vorfassung); zwei parallele Stapel sortieren so bei n = 6 nur 132 statt 513 Folgen.
* **Ankunftsmodell V (ausgedacht):** Container i kommt zur Zeit i an und bleibt eine exponentialverteilte Verweilzeit mit Mittel D (in Ankunftsabständen); die Folge ist der Rang der Abfahrtszeit. Es nutzt nur die
  Rangfolge der Abfahrten. D = ∞ ist die Gleichverteilung über alle n! Folgen (Modell U).

## Methodik

* **Wegsuche (`mvg_machines.py`):** Ebene für Ebene alle erreichbaren Konfigurationen (Zahl der ausgegebenen Zahlen und die Inhalte aller Behälter); zwei Abkürzungen, die keine Folge verlieren (gieriges Ausgeben der
  nächsten gesuchten Zahl, Senken-Prüfung auf falsch gefüllte Ausgangsbehälter), sind gegen die rohe Suche ohne sie für alle zehn Maschinen und alle Folgen bis n = 5 geprüft. Aus der Wegsuche kommt auch die Spur eines Weges,
  die ein eigener Abspieler in den Tests Schritt für Schritt nachvollzieht.
* **Mengen (`mvg_sets.py`, `data/mvg_sets.json`):** je Maschine und n = 1 bis 8 eine Bitmaske über die lexikographisch geordneten n! Folgen, vorgerechnet von `tools/mvg_make_sets.py` („vorgerechnet“ in der App);
  Mengenoperationen sind Ganzzahloperationen. Für n = 9 gibt es nur die Zahlen (Aufzählung aller 362 880 Folgen wäre live zu teuer).
* **Gründe für „nein“ (`mvg_patterns.py`):** Muster 231 (Stapel), fallende Teilfolge der Länge 3 bzw. 4 (zwei bzw. drei Warteschlangen), Muster 231 und 312 (Pop-Stack), ungerader Zyklus im Konfliktgraphen (zwei parallele Stapel);
  für SSs und SpQ gibt es keine einfache Beschreibung, dort steht nur die Zahl untersuchter Konfigurationen.
* **Zufall (`mvg_rng.py`):** ausschließlich ein ganzzahliger SplitMix64, plattformfest. `below(n)` ist der Rest einer 64-Bit-Zahl; der Fehler gegen die Gleichverteilung ist höchstens n·2⁻⁶⁴ und hier ohne Belang (Fisher-Yates-Mischen
  für das Modell U). Die Zählungen aus Neu-Rechnung sind deshalb ganzzahlig auf jeder Plattform gleich; Stichprobenanteile werden trotzdem nur als Band (vier Standardfehler) gelesen.
* **Live-Rechnung:** die Wegsuche für eine Folge mit n ≤ 10 (alle zehn Maschinen, Umkehrfolge als schwerster Fall unter fünf Sekunden im Test) und eine Stichprobe von 2000 Zufallsfolgen (rund eine Sekunde).

## Befunde (gemessen, keine Behauptungen)

Zähleinheit Folgen, alle zehn Maschinen mit freier Zwischenausgabe; Zahlen bis n = 8 aus der Aufzählung aller n! Folgen, n = 9 nur Zahlen (Wegsuche dieser Demo, außer † = OEIS A263929, nur gelesen):

| n | n! | Q | S | 2Q | 3Q | SSs | SSp | SQ | QS | SpQ | P |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 3 | 6 | 1 | 5 | 5 | 6 | 6 | 6 | 5 | 5 | 6 | 4 |
| 4 | 24 | 1 | 14 | 14 | 23 | 24 | 23 | 14 | 14 | 24 | 8 |
| 5 | 120 | 1 | 42 | 42 | 103 | 120 | 103 | 42 | 42 | 118 | 16 |
| 6 | 720 | 1 | 132 | 132 | 513 | 720 | 513 | 132 | 132 | 668 | 32 |
| 7 | 5 040 | 1 | 429 | 429 | 2 761 | 5 018 | 2 760 | 429 | 429 | 4 150 | 64 |
| 8 | 40 320 | 1 | 1 430 | 1 430 | 15 767 | 39 374 | 15 741 | 1 430 | 1 430 | 27 413 | 128 |
| 9 | 362 880 | 1 | 4 862 | 4 862 | 94 359 | 337 816 † | 93 944 | 4 862 | 4 862 | 188 785 | 256 |

Q, S/2Q/SQ/QS, 3Q, SSp, SSs und P stimmen bis n = 8 mit den Reihen 1, A000108 (Catalan), A005802, A216040, A263929 und 2^(n−1) überein. Die Reihe für SpQ (1, 2, 6, 24, 118, 668, 4150, 27 413, 188 785) hat keinen
OEIS-Treffer; sie ist nur durch ein zweites Verfahren (Erzeugen aus der Identität, invertiert) bis n = 5 gesichert, die Zahlen ab n = 6 stützt allein die Wegsuche dieser Demo. Anteile an n! bei n = 8: S, 2Q, SQ, QS 3,55 %,
3Q 39,10 %, SSp 39,04 %, SpQ 67,99 %, SSs 97,65 %, P 0,32 %.

| Frage | Befund (n ≤ 8, Zähleinheit Folgen bzw. Maschinenpaare) |
|---|---|
| Kleinster Fall von „gleiche Zahl, andere Menge“ | n = 3: S gegen 2Q, je 5 von 6; nur S sortiert 321, nur 2Q sortiert 231 |
| S gegen 2Q | gleiche Zahl für alle n ≤ 8 (Catalan), die Mengen sind ab n = 3 verschieden; bei n = 8 nur S 1302, nur 2Q 1302, gemeinsam 128 |
| 3Q gegen SSp | je 23, 103, 513 bei n = 4, 5, 6; nur SSp 1, 17, 171 und nur 3Q 1, 17, 171; n = 5: gemeinsam 86; n = 7: 2760 gegen 2761 (nur SSp 1395, nur 3Q 1396, gemeinsam 1365); kleinste Zeugen bei n = 4: 4321 (nur SSp), 2341 (nur 3Q) |
| Paare mit gleicher Zahl unter n! und davon mit verschiedener Menge | n = 3: 6 und 3; n = 4, 5, 6: 7 und 4; n = 7, 8: 6 und 3 (von 45 Paaren) |
| Zählfolgen gegen Mengen | n = 3: 4 gegen 5; n = 4: 5 gegen 7; n = 5 und 6: 6 gegen 8; n = 7 und 8: 7 gegen 8 |
| Gleiche Menge | S = SQ = QS für n ≤ 8 (gemessen, nicht bewiesen); alle übrigen Paare haben bei n = 8 verschiedene Mengen |
| Ordnung bei n = 8 | 8 verschiedene Mengen, 9 echte Teilmengenkanten ohne Zwischenglied, 10 unvergleichbare Paare (je Vertreter einer Klasse); SSp liegt in SSs, nicht in SpQ (nur SSp 3758, nur SpQ 15 430) |
| Mehr Behälter, mehr Folgen? | 3Q und SSs bei n = 8: nur 3Q 406, nur SSs 24 013, gemeinsam 15 361; beide Richtungen schon bei n = 7 (2435761: 3Q ja, SSs nein; 4321567: SSs ja, 3Q nein) |
| Fingerabdruck (Menge der Maschinen, die eine Folge sortieren) | verschiedene Fingerabdrücke bei n = 3 bis 8: 5, 9, 13, 16, 20, 21; 2341: 2Q, 3Q, SSs, SpQ (4 von 10); 4321: 7 von 10 |
| Folgen ohne passende Maschine | n = 8: 508 von 40 320 (1,26 %) sortiert keine der zehn Maschinen; im Mittel sortieren 2,58 Maschinen eine gleichverteilte Folge |
| „Zwei Stapel“ sind vier Maschinen | n = 4: SSs 24, SSp 23, West-2 22, Pop-2 16 von 24; West-2 und Pop-2 unvergleichbar (n = 5: 41352); West-2 liegt bis n = 7 in SSp, bei n = 8 nicht mehr (eine Folge, 58274163) |
| SSs bei n = 7 | 22 von 5040 Folgen unsortierbar |
| Ankunftsmodell V, n = 8, 20 000 Folgen je D | S und 2Q: Differenz der Anteile −0,36 bis +0,43 Punkte, in 7 von 7 Zeilen innerhalb von vier Standardfehlern der Differenz; 3Q und SSp: −0,33 bis +0,78 Punkte, ebenfalls 7 von 7 (Tabelle unten) |

Anteil in Prozent, Modell V, n = 8, je D 20 000 Folgen (Zufalls-Seed 20000 + Index der Zeile; vorgerechnet von `tools/mvg_make_model.py`). In Klammern der Standardfehler der Differenz aus derselben Stichprobe, Punkte:

| D | Q | S | 2Q | 3Q | SSs | SSp | SQ | QS | SpQ | P | Mittel | S − 2Q | 3Q − SSp |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0,5 | 59,08 | 99,76 | 99,75 | 100,00 | 100,00 | 100,00 | 99,76 | 99,76 | 100,00 | 94,75 | 9,528 | +0,01 (0,05) | +0,00 (0,00) |
| 1 | 18,20 | 93,22 | 93,17 | 99,92 | 100,00 | 99,95 | 93,22 | 93,22 | 100,00 | 66,27 | 8,572 | +0,04 (0,25) | −0,03 (0,03) |
| 2 | 2,86 | 66,47 | 66,68 | 97,61 | 100,00 | 97,72 | 66,47 | 66,47 | 99,89 | 27,79 | 6,919 | −0,21 (0,45) | −0,11 (0,15) |
| 4 | 0,30 | 33,86 | 34,17 | 87,09 | 100,00 | 86,73 | 33,86 | 33,86 | 97,97 | 7,74 | 5,156 | −0,31 (0,45) | +0,36 (0,34) |
| 8 | 0,03 | 15,75 | 15,32 | 69,86 | 99,87 | 69,88 | 15,75 | 15,75 | 91,33 | 2,28 | 3,958 | +0,43 (0,35) | −0,03 (0,48) |
| 16 | 0,02 | 8,39 | 8,43 | 56,00 | 99,36 | 56,33 | 8,39 | 8,39 | 83,62 | 0,95 | 3,299 | −0,04 (0,27) | −0,33 (0,52) |
| ∞ | 0,00 | 3,45 | 3,81 | 39,47 | 97,80 | 38,69 | 3,45 | 3,45 | 68,06 | 0,36 | 2,585 | −0,36 (0,18) | +0,78 (0,50) |

Die Zeile ∞ ist eine Stichprobe von 20 000 gleichverteilten Folgen; exakt aus den Mengen sind die Anteile bei n = 8 für S, 2Q, SQ, QS 3,55 %, 3Q 39,10 %, SSs 97,65 %, SSp 39,04 %, SpQ 67,99 %, P 0,32 %, im Mittel 2,583 Maschinen. Beim
Lesen: die Anteile hängen vom Modell ab (Verweilzeit, Rangbildung) und gelten nur für n = 8; sie sind keine Aussage über echte Ankunftsfolgen. Dass sich die Anteile von S und 2Q **mit 20 000 Folgen je Zeile nicht
unterscheiden lassen**, belegt nicht, dass sie gleich sind: unterscheidbar wären erst Unterschiede oberhalb von vier Standardfehlern der Differenz, das sind je nach Zeile 0,2 bis 1,8 Punkte.

### Zahl → Test

Alle Zahlen der README stehen in `tests/test_claims.py` (Zahl und Satz in der README) und in den genannten Tests; die Tests rechnen die Mengen bis n = 7 jedes Mal neu (n = 8 mit `MVG_VOLL=1`), die Anteile des Modells V
sind ganzzahlige Zählungen aus dem plattformfesten Zufall (erster Block je D neu gerechnet), alle Stichprobenaussagen als Band.

| Zahl | Test | Art |
|---|---|---|
| Zahlen der Tabelle, n = 3 bis 8 | `test_oracle_maschinen_vergleich.py::test_a_*` (Wegsuche, n ≤ 7), `::test_f_zahlen_der_eingefrorenen_mengen_*` (n ≤ 8) | exakt |
| Zahlen n = 9 | `test_sets.py::test_tabelle_n9_*`, `test_claims.py` | exakt (aus der JSON; Neu-Rechnung: `tools/mvg_make_sets.py --n9`, nicht in der CI) |
| 5 von 6 bei n = 3, 231 und 321 | `test_machines.py::test_handbeispiel_n3_*`, `test_sets.py::test_handbeispiel_n3_*` | exakt |
| 23, 103, 513; 1, 17, 171; 2760 gegen 2761 | `test_sets.py::test_ssp_gegen_3q_*` | exakt |
| 7 und 4 Paare, 6 und 3 Paare, 7 gegen 8 | `test_sets.py::test_paare_*`, `::test_zaehlfolgen_und_mengen` | exakt |
| 8 Mengen, 9 Kanten, 10 unvergleichbare Paare | `test_sets.py::test_ordnung_*` | exakt |
| Fingerabdrücke 5, 9, 13, 16, 20, 21; 508 Folgen; 2,58 | `test_sets.py::test_zahl_verschiedener_fingerabdruecke`, `::test_verteilung_n8_*` | exakt |
| vier „zwei Stapel“, 41352, 58274163, 22 bei n = 7 | `test_sets.py::test_zwei_stapel_*`, `::test_west2_*` | exakt |
| Tabelle des Modells V | `test_model.py::test_eingefrorene_tabelle_*` (erster Block je D neu gerechnet, innere Stimmigkeit, ∞-Zeile im Band), `test_claims.py` | ganzzahlig / Band |
| Differenzen und „7 von 7“ | `test_verdicts.py::test_verdikt_frozen_*`, `test_claims.py` | rechnerisch |
| Verdikt-Texte der App | `test_verdicts.py` | exakt |

## Befunde und Korrekturen gegenüber der ersten Rechnung

* **Die Wegsuche ist neu geschrieben**, nicht aus der früheren Messung kopiert; alle 80 Zahlen (zehn Maschinen, n = 1 bis 8) stimmen mit der früheren Messung und den OEIS-Reihen überein.
* **Modell V neu mit dem Zufall der Demo gemessen.** Die frühere Messung (anderer Zufallsgenerator, andere Zufalls-Seeds) nannte für Stapel und zwei Warteschlangen „höchstens 0,35 Punkte“ Unterschied; mit dem
  Zufall der Demo liegt die Differenz zwischen −0,36 und +0,43 Punkten, jeweils innerhalb von vier Standardfehlern der Differenz. Die Aussage „nicht unterscheidbar“ bleibt, die frühere Zahl 0,35 gilt nicht mehr.
  Alle 70 Anteile (zehn Maschinen, sieben Werte von D) liegen innerhalb von vier Standardfehlern der Differenz beider Messungen; die größte Abweichung beträgt 0,68 Punkte (3Q bei D = 16: 56,00 % statt 56,68 %).
* **Zusätzlich nachgerechnet bei n = 9:** 3Q (94 359), SSp (93 944), SpQ (188 785), QS (4862) und P (256) mit der Wegsuche dieser Demo, SQ (4862) wie in der früheren Messung. Nur SSs (337 816) bleibt eine gelesene
  OEIS-Zahl (die Wegsuche braucht dort zu lange).
* **Experiment 1 ohne Auswahl der Maschinen:** alle zehn stehen immer in der Tabelle; die Verdikte beziehen sich auf alle zehn.
* **Der Standard von Experiment 4 ist n = 7**, nicht 8: dort sind 3Q und SSs schon unvergleichbar, und Experiment 4 mit n = 8 ist ein eigener Schnellstart.
* **Seitenlänge:** alle fünf Experimente blieben; die Seite ist lang (Messung dieser README, nicht im Test: rund 11 800 Pixel Höhe bei 1024 Pixel Fensterbreite), die Kernfragen stehen am Anfang jedes Abschnitts.

## Quellen

Nur so zitiert, wie gelesen: Bóna, „A survey of stack-sorting disciplines“, Electron. J. Combin. 9(2) (2003), #A1 (Satz 1.3: Stapel und 231, geschichtete Folgen für den Pop-Stack, West-2; ganz gelesen). Tarjan, „The Switchyard
Problem“, Stanford CS-TR-71-213 (1971): die Vorfassung des Aufsatzes in J. ACM 19 (1972); Lemma 2 (parallele Warteschlangen und fallende Teilfolgen) und Lemma 3 gelesen, **die JACM-Fassung nicht**. Albert/Bousquet-Mélou,
Eur. J. Combin. 43 (2015) (Einleitung und Reihenwerte gelesen). OEIS A000108, A005802, A216040, A263929, A000139, A011782 (gelesen). **Nicht gelesen:** Tarjan 1972 im Original, Even/Itai 1971 (der Konfliktgraph steht
nach Tarjan und Albert/Bousquet-Mélou, die hier benutzte Kantendefinition ist eine eigene Fassung, gegen die Wegsuche bis n = 8 bestätigt), Knuth, Pratt. Alles ist Lehrbuchstoff; neu ist nur die Vorführbarkeit mit
Zähleinheiten und der gemessene Mengenvergleich aller 45 Paare in diesem Modell, n ≤ 8.

## Abgrenzung zu Nachbar-Demos

[`stapel-sortieren-demo`](https://github.com/sebastian-hanisch/stapel-sortieren-demo): ein Stapel allein, Catalan, 231, Gleichstände. [`mehrere-durchlaeufe-demo`](https://github.com/sebastian-hanisch/mehrere-durchlaeufe-demo):
Durchläufe; hier erscheinen West-2 und Pop-2 nur als Zahl und als Zeugen in Experiment 5. [`zwei-stapel-serie-demo`](https://github.com/sebastian-hanisch/zwei-stapel-serie-demo): SSs hier nur als Spalte.
[`patience-stapel-demo`](https://github.com/sebastian-hanisch/patience-stapel-demo): Einlagern ohne Zwischenausgabe. [`ablaufberg-demo`](https://github.com/sebastian-hanisch/ablaufberg-demo): dort sind k Gleise Warteschlangen
und Wagen gleicher Zielgruppe austauschbar; hier ein Durchgang mit verschiedenen Wagen. Catalan-Zahlen, Muster-Klassen und Wachstum stehen auf der Seite
[Abzählen](https://sebastianhanisch.net/konzepte-abzaehlen.html) und kommen hier nur als Spalten und Zähleinheiten vor.

## Ehrliche Grenzen

* **Mengenaussagen nur bis n = 8, aufgezählt, nicht bewiesen.** „Gleiche Menge“ (S, SQ, QS), „unvergleichbar“, die 45 Paare und die Ordnung gelten für n ≤ 8; bei n = 9 gibt es nur Zahlen, und die Zahl für SSs ist dort nur
  aus OEIS A263929 gelesen.
* **SpQ:** keine OEIS-Reihe; ein zweites Verfahren sichert die Zahlen nur bis n = 5.
* **Zehn Maschinen, nicht mehr:** Deque, Prioritätswarteschlange, drei Stapel und Netze mit mehr Behältern sind nicht gemessen.
* **Das Ankunftsmodell ist ausgedacht** (Verweilzeit exponentialverteilt, nur n = 8 als Tabelle); der Befund „Anteile von S und 2Q nicht unterscheidbar“ gilt für dieses Modell, diese Stichprobengröße und n = 8. Die
  Live-Stichprobe der App (2000 Folgen) hat wenig Trennschärfe: der Standardfehler eines Anteils beträgt höchstens 1,12 Punkte (bei 50 %).
* **Die Zahl der Maschinenpaare mit gleicher Zahl bei n ≥ 9 ist nicht gemessen.** Die Wegsuche untersuchte in einer Stichprobe von 56 Zufallsfolgen mit n = 9 und 10 und der Umkehrfolge je Maschine höchstens 2 047 Konfigurationen; für alle Folgen mit n = 10 ist das nicht gemessen.
* **Zufall:** `below(n)` rechnet mit dem Rest; der Fehler gegen die Gleichverteilung ist höchstens n·2⁻⁶⁴.

## Verifikation

Die Suite hat 246 Tests (245 laufen immer, einer nur mit `MVG_VOLL=1`).

* **Wegsuche:** Handbeispiele von Hand (n = 3 mit 5 von 6, n = 4 mit den zehn Zahlen, 2341 und 4321, 2435761 und 4321567), eigene Breitensuche für alle zehn Maschinen und alle Folgen bis n = 5, jede Spur von einem
  unabhängigen Abspieler nachvollzogen, Abkürzungen gegen die rohe Suche (`tests/test_machines.py`).
* **Orakel** (`tests/test_oracle_maschinen_vergleich.py`): Zahlen gegen die OEIS-Reihen und die Catalan-Formel; Erzeugen aus der Identität, invertiert (n ≤ 6, SSs, SSp, SpQ n ≤ 5); Muster (S = Av(231), 2Q und 3Q über
  die längste fallende Teilfolge, Q = Identität, P = Av(231, 312), SQ = QS = S, n ≤ 7); zwei parallele Stapel gegen den zweifärbbaren Konfliktgraphen (eigene Union-Find-Rechnung, n ≤ 7); die eingefrorene JSON gegen
  Neu-Rechnung (n ≤ 7 immer, n = 8 mit `MVG_VOLL=1`) und gegen die Muster bei n = 8.
* **Eigenschaften** (`tests/test_eigenschaften_maschinen_vergleich.py`): Streichen einer Zahl bleibt sortierbar, Inklusionen aus der Konstruktion, Charakterisierungen und Spuren an 56 Zufallsfolgen mit n = 9 und 10.
* **Modell und Mengen:** Rang-Abbildung von Hand, Orakel für einen Stapel bei n = 10 gegen die frühere Messreihe, Gleichverteilung exakt gegen die Mengen im Band, erster Block der eingefrorenen Tabelle ganzzahlig
  neu gerechnet (`tests/test_model.py`, `tests/test_sets.py`).
* **Verdikte und Randfälle:** jede Zahl im Text und jede Art an handgesetzten Fällen (`tests/test_verdicts.py`), n = 1, n = 2, ungültige Eingaben, gleiche Maschinen, Permalink, Umkehrfolge n = 10 (`tests/test_edge_cases.py`).
* **Oberfläche:** AppTest-Rauchtest (jeder Button, jeder Regler am Minimum und Maximum), Schnellstart in der Seitenleiste, fester Kopf, aktives Preset hervorgehoben, jede Änderung eines Reglers hebt die Markierung auf
  (`tests/test_app.py`, `tests/test_layout.py`), Footer-Test, Laufzeit-Importe.
* **Claims:** `tests/test_claims.py` rechnet die Zahlen der README nach und prüft, dass die Sätze in der README stehen; keine Planungswörter in README, App und Quelltext.

## Dateistruktur

| Datei | Zweck |
|---|---|
| `.github/workflows/tests.yml` | CI: Push, Pull Request, wöchentlicher Canary |
| `.gitignore` | venv, Caches, Streamlit-Secrets |
| `.streamlit/config.toml` | Streamlit-Einstellungen (keine Nutzungsstatistik) |
| `app.py` | Streamlit-App: drei Kernfragen, fünf Experimente, Grenzen, Formeln |
| `data/mvg_sets.json` | vorgerechnete Mengen (Bitmasken) n ≤ 8 und die Zahlen für n = 9 |
| `data/mvg_modell_v.json` | vorgerechnete Tabelle des Ankunftsmodells V (n = 8, 20 000 Folgen je D) |
| `mvg_constants.py` | Regler-Grenzen, Voreinstellungen, Farben, Presets |
| `mvg_evaluation.py` | Kennzahlen und Verdikte als reine Funktionen |
| `mvg_layout.py` | Fester Kopf (Stylesheet) |
| `mvg_machines.py` | Netze, Wegsuche, Aufzählung, Spuren, Abspielen |
| `mvg_model.py` | Ankunftsmodell V und U, Stichproben, Band, Differenz mit Standardfehler |
| `mvg_patterns.py` | Muster, Teilfolgen, Konfliktgraph, West- und Pop-Stack-Durchlauf, Gründe |
| `mvg_presets.py` | Permalink (Begrenzen), Presets (Schnellstart in der Seitenleiste), Zufalls-Seed-Button |
| `mvg_rng.py` | SplitMix64 (plattformfest), Vorlage aus dem Website-Repo |
| `mvg_sets.py` | Bitmasken, Vergleich, Paarstatistik, Fingerabdrücke, Ordnung |
| `mvg_texts.py` | längere Texte der App |
| `mvg_visualization.py` | Plotly-Abbildungen (Achsen gesperrt) und Spur-Tabelle |
| `requirements-dev.txt` | Laufzeit plus pytest |
| `requirements.txt` | Laufzeit-Bibliotheken (ungepinnt) |
| `tools/mvg_make_sets.py` | rechnet die Mengen vor (`--write`, `--n9`, `--check`, `--voll`) |
| `tools/mvg_make_model.py` | rechnet die Tabelle des Modells V vor (`--write`, `--check`) |
| `tests/` | Wegsuche, Orakel, Eigenschaften, Mengen, Modell, Verdikte, Randfälle, Claims, Presets, Layout, AppTest, Footer, Laufzeit-Importe, unabhängige Referenz (`ref_maschinen.py`) |

## Bewusst nicht umgesetzt

* **Deque, Prioritätswarteschlange, drei Stapel, größere Netze:** nicht gemessen, nicht in der Demo.
* **Auswahl der Maschinen in Experiment 1:** alle zehn immer sichtbar.
* **Mengenvergleiche für n ≥ 9:** zu teuer live; als Zahlen nur in der Tabelle.
* **Ein Beweis für S = SQ = QS:** die Demo bleibt bei der Messung bis n = 8.
* **Erklärung der Durchläufe:** West-2 und Pop-2 kommen nur als Zahl und Zeugen vor.
* **PDF-Export:** nicht vorgesehen.

## Lokal ausführen

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

## Tests ausführen

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
MVG_VOLL=1 pytest tests/ -v        # zusätzlich n = 8 für alle zehn Maschinen neu rechnen (rund zwei Minuten)
python tools/mvg_make_sets.py --check            # eingefrorene Mengen n <= 7 gegen Neu-Rechnung
python tools/mvg_make_model.py --check           # Tabelle des Modells V, erster Block je D
```

Gebaut mit Streamlit, Plotly und pandas.

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html).
