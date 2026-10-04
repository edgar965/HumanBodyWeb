# -*- coding: utf-8 -*-
"""Werkzeugkleidbau — Reiter „Tools" der Seite Architektur 2D3D, Gruppe T2: Bau ohne Browser und Prüfen des Sitzes.

Kleidermodellbau (ein Rezeptzustand als Netze), Fitting gegen das Durchschimmern, Abnahmeläufe. Reine Daten (Schema:
`ProjektTemp/_wegwerf/stoff_ausbau/AUFTRAG_TOOLS.md`); gelesen von `Architektur2d3dwerkzeuge`. Jede Zeile ist gegen den
Code gelesen (03.10.2026); Zahlen tragen Fundstelle und Datum.
"""

__all__ = ['Werkzeugkleidbau']


class Werkzeugkleidbau:
    G = 'Genesis9/'
    D = 'HumanBodyWeb/core/dienste/'
    A = 'HumanBodyWeb/core/api/'

    KENNUNG = 'kleidbau'
    TITEL = 'Bau ohne Browser und Sitz prüfen (Kleidermodellbau, Fitting)'
    EINLEITUNG = (
        'Ein ModellMitKleidern ist nur Zustand (Regler). Damit daraus Netze werden, ohne dass ein Browser sie anfragt, baut '
        'Kleidermodellbau über DENSELBEN Weg wie die Bühne (G9garderobeapi._kleid je Stück, G9kleidmischbau für Kleider, '
        'G9haarmischbau für Haar) mit dem Rumpf, den der Browser schicken würde — die Iteration sieht, was später auf der Bühne '
        'steht. Reihenfolge: 1. Rezept anwenden (Gruppe „Kleider anziehen …“), 2. Kleidermodellbau(…).teile(m), 3. glb(…) '
        'oder rendern. Läuft nur im Arbeitsprozess (python14 mit Django), nie im Server. Der Sitz (liegt der Stoff an der '
        'Haut, schimmert sie durch?) wird gegen die vier Schichten des Fittings geprüft; die Abnahmeläufe rechnen Sekunden bis '
        'Minuten je Stück und gehören nicht neben Edgars Arbeit.')

    # (Werkzeug, Wofür, Art, Aufruf, Klassen, Hinweis)
    ZEILEN = [
        ('Modell bauen ohne Browser: Teile und GLB',
         'Baut aus einem ModellMitKleidern Körper, Kleider und Haar als Netze (Punkte, Dreiecke, Farbe, Haut) und schreibt '
         'optional eine GLB mit Rig.',
         'python',
         "from pathlib import Path\n"
         "from core.dienste.kleidermodellbau import Kleidermodellbau\n"
         "bau = Kleidermodellbau(stellung={}, drehung=m.drehung(), koerper=m.koerper)   # stellung: Regler der Figur (Auftrag: job.stellung())\n"
         "teile = bau.teile(m)                                   # [Körper] + Anhänge + Kleider + Haar, je Teil ein Dict\n"
         "bau.glb(teile, Path('A:/3DTools/ProjektTemp/_wegwerf/modell.glb'))   # A-Pose mit Rig",
         [(D + 'kleidermodellbau.py', 'Kleidermodellbau'), (D + 'koerperanhaenge.py', 'Koerperanhaenge'),
          (D + 'teilevorrat.py', 'Teilevorrat'), (A + 'g9garderobe.py', 'G9garderobeapi'),
          (D + 'g9kleidmischbau.py', 'G9kleidmischbau'), (D + 'g9haarmischbau.py', 'G9haarmischbau'),
          (D + 'rundenglb.py', 'Rundenglb')],
         'Nur im Django-Prozess (Arbeitsprozess oder manage.py shell); Kleidermodellbau setzt die Käfigstufe selbst '
         '(Netzstufenwahl._gewaehlt.set(0)), sonst rechnete jeder Bau die Unterteilung der Bühne mit. Ergebnis je Teil: '
         '{punkte (N, 3), dreiecke (T, 3), farbe (3,), haut {knochen, index, gewicht}, art, sorte, uv, normalen, gruppen, '
         'textur} in der Lage der Bühne (Meter, Y oben, Füße 0). Der Körper kommt zuerst, dann Augen, Mund, Wimpern, Brauen '
         '(Koerperanhaenge), dann Kleider, dann Haar. Die Farbe je Stück ist das Mittel der Textur × Tönung (flach, weil die '
         'Note Farbflächen vergleicht). Der Teilevorrat hält Kleidung und Haar je Prozess, solange der Rumpf gleich bleibt: '
         'gemessen 02.10.2026 (Teilevorrat, Auftrag 2026.10.01.20.10.04, Fotostücke + Uhr + Mavick mit Bart): Teile kalt '
         '41,7 s (Kleidung 28,9, Haar 10,9), warm 13,5 s — die Zeit steckt in der Bindung an die Figur und der Kollision der '
         'Lagen; eine reine Farbrunde baut nichts neu. glb schreibt seit 01.10.2026 ein Rig mit (138 Knochen, Rundenglb; '
         'davor ohne Skelett). Nicht ausprobiert: der Aufruf im Beispiel (nur gelesen).'),

        ('Durchschimmern messen (Abnahme des Fittings)',
         'Rechnet je Stück und Daz-Pose, wie viele Stoffpunkte im Körper stehen und wie viele Hautpixel vor dem Stoff liegen; '
         'rendert Kontaktbögen.',
         'cli',
         'cd A:/3DTools/HumanBodyWeb && ../python14/Scripts/python.exe manage.py durchschimmern_probe g9_base_shirt angie_jeans\n'
         'manage.py durchschimmern_probe --alle --posen de_g9_base_05_standing\n'
         'manage.py durchschimmern_probe g9_base_shirt --ohne-bilder',
         [(D + 'durchschimmerprobe.py', 'Durchschimmerprobe'), (G + 'oberflaechenbindung.py', 'G9oberflaechenbindung'),
          (G + 'stueckfelder.py', 'G9stueckfelder'), (G + 'garderobe.py', 'G9garderobe')],
         'Hautpixel zählen nur binnen 2 cm vor dem Stoff (der Arm neben dem Rumpf zählte sonst 5.000 Pixel), vier Ansichten '
         '(pyrender, nur mit Bildern), Kontaktbogen nach ProjektTemp/durchschimmern/<kennung>.jpg. Die Zahl ist eine OBERE '
         'Schranke (ohne die Hautmaske, die im Browser entsteht); Schwelle für gebundene Stücke: 0 Pixel. Gemessen 21.09.2026 '
         '(genesis9-passform.md, Shirt Standing / Laufen: Punkte innen, Pixel vorn, hinten, links, rechts): Shirt Standing '
         '240/92/372/546 → 1/19/0/0, Laufen 153/31/31/146 → 0/94/25/0 (Rest: Schenkel unter dem Saum), Punkte innen 857 → 262. '
         'Rechnet Sekunden je Stück und Pose, LongRunner (core/tests/longrunner/test_genesis9_fitting): NICHT nebenbei, nur '
         'auf Ansage. Die Abnahme kennt nur standing/running — eine Kick-Pose mit senkrecht angehobenem Bein war nie darin '
         '(Spagat-Befund 22.09.2026).'),

        ('Genesis-Kleidung auf den HumanBody-Grundfiguren prüfen',
         'Lässt jedes Garderobenstück über den Browser-Endpunkt auf HumanBody anziehen und zählt Hautpixel vor dem Stoff.',
         'cli',
         'cd A:/3DTools/HumanBodyWeb && ../python14/Scripts/python.exe manage.py daz_auf_humanbody_probe [--nur gc_] '
         '[--geschlecht female] [--neu]',
         [(D + 'hbkleidprobe.py', 'Hbkleidprobe'), (D + 'eigenstueckprobe.py', 'Eigenstueckprobe'),
          (A + 'g9kleidhumanbody.py', 'G9kleidhumanbody')],
         'Ergebnis in ProjektTemp/hbprobe/ergebnis.json (nach jedem Stück atomar geschrieben, ein abgebrochener Lauf setzt '
         'fort; --neu rechnet schon Geprüftes neu). Je Stück und Geschlecht ein Aufruf von Eigenstueckprobe.humanbody '
         '(derselbe Weg wie der Browser, vier Ansichten, Hautpixel binnen 2 cm). Rechnet Sekunden je Stück auf CPU/GPU: nicht '
         'nebenbei starten (Docstring des Befehls). Kosten pro Stück: nicht gemessen; „Kin Hair auf HumanBody kalt 88 s, seit '
         '30.09.2026 68 s“ (genesis9-humanbody.md) ist die nächste belegte Zahl.'),

        ('Stoffschwung (dForce) eines Stücks im Browser',
         'Liefert den Bauplan (Kanten, Unterteilungsmatrix, Käfighaut) eines dForce-Stücks, damit der Browser es mit Verlet '
         'in einem Web Worker schwingen lässt.',
         'api',
         'GET /api/character/genesis9-figur/garderobe/<kennung>/stoff/<nummer>/?stufen=1[&laenge=<cm>&weite=<cm>]\n'
         '→ {kennung, nummer, passform, stufen, punkte, zeilen, kanten, indptr, indices, data, hautgewichte}',
         [(A + 'g9stoff.py', 'G9stoffapi'), (G + 'stoff.py', 'G9stoff'), (G + 'garderobe.py', 'G9garderobe')],
         'nummer = Stelle des Teils in G9garderobe.teile(kennung); nur dForce-Stücke (folger.dynamisch), sonst 404 „Kein '
         'dForce-Stück“. Die Antwort hängt nur am Stück und der Stufe, nicht an den Reglern (Passform ausgenommen): der Browser '
         'holt sie einmal je Stück. Größe Dancing Queen Dress, Stufe 1: 75.977 Zeilen, Matrix ~460.000 Einträge (rund 5 MB '
         'base64; 6,6 MB je Kleid einmal laut genesis9-inhalte.md). Eine NÄHERUNG von Daz dForce, nicht dessen Simulation: '
         'Freiheit = Stärke × Abstand zur Haut (HAFT 2 cm), Schwerkraft × 0,3, 32 Kapseln um die Knochen, im Worker '
         'HumanBodyWeb/static/viewer/gemeinsam/stoffarbeiter.js (stoffpendel.js); auf dem Hauptfaden kostete das Kleid '
         '170 ms je Bild, im Worker 92 ms je Bild im versteckten Tab (genesis9-inhalte.md, 18.09.2026). Ein gemischtes Stück '
         'schwingt den Käfig des ursprünglichen Stücks (Bauplan stoff.stueck/nummer). Einen Stoffschwung im Python-Bau der '
         'Runde habe ich nicht gefunden: dort gibt es nur kleid_drapieren (Gruppe „Drapieren …“).'),

        ('Regel: die vier Schichten gegen das Durchschimmern',
         'Hält fest, was Haut hinter dem Stoff verhindert — und was nicht. Konzept statt des 21. Fixes (Edgar 21.09.2026).',
         'regel',
         'Schicht 1 Hautverdeckung (Maske auf allen Seiten), 2 Oberflächenbindung („nur hinaus“, schaltbar), 3 Kapseln im '
         'Shader, 4 Abnahme (durchschimmern_probe).',
         [(G + 'oberflaechenbindung.py', 'G9oberflaechenbindung'), (G + 'kollision.py', 'G9kollision'),
          (G + 'lagen.py', 'G9lagen'), (G + 'hautglaettung.py', 'G9hautglaettung'), (G + 'passformhaut.py', 'G9passformhaut')],
         'Konzept: Docu/konzepte/2026-09-21_kleidung-ohne-durchschimmern-konzept.md, Stand Hilfe → Kleidung → Fitting. Schicht '
         '1: HumanBodyWeb/static/viewer/gemeinsam/hautverdeckung.js (Studio Olesia1: 32.025 Punkte). Schicht 2 (G9oberflaechen'
         'bindung + koerperlage.js, oberflaechenbindung.js): seit 24.09.2026 „nur hinaus“ (LUFT 1 cm, Grenzen 4 cm tief, 3 cm '
         'seitlich), schaltbar unter Einstellungen → Kleider (Vorgabe An), 4–9 ms je Bild mit Shirt, Jeans, Sandalen. Schicht 3: '
         'Kapseln (Koerperzuordnung trennt eigene und fremde Gliedmaßen: der Arm im eigenen Bein, 22.09.2026). Mindestabstand '
         'Stoff–Haut 3 mm (G9kollision.ABSTAND); was bleibt, ist strukturell: ohne Kollision je Bild stehen enge Oberteile im '
         'Stand zu 3–7 % im Körper. Bei Animation zerreißen Klamotten ohne Hautglättung (G9hautglaettung: Gewichte über die Kanten '
         'des Stücks gemittelt: Sitzen 239 → 77 Kanten >2 cm) und ohne einen Stand je Länge/Weite (G9passformhaut). Verworfen: '
         'Kennzahlen als Beleg — „die Kennzahl gab Entwarnung, das Bild nicht“ (20.09.2026): vor jedem „behoben“ rendern.'),
    ]

    # Klassenmodell: (von, 'ruft', nach, womit)
    BEZIEHUNGEN = [
        ('Kleidermodellbau', 'ruft', 'G9garderobeapi', 'G9garderobeapi._kleid(kennung, eintrag, rumpf, vor_antwort): je Stück, rohe Netze über vor_antwort'),
        ('Kleidermodellbau', 'ruft', 'G9kleidmischbau', 'G9kleidmischbau.antwort(): mehrere Kleider → eine Mischung'),
        ('Kleidermodellbau', 'ruft', 'G9haarmischbau', 'G9haarmischbau.antwort(rumpf, kleid): Haar-Mischung'),
        ('Kleidermodellbau', 'ruft', 'Teilevorrat', 'Teilevorrat.antwort(art, rumpf, rechnen, roh): Bauplan gleich → alte Antwort; farben(netz)'),
        ('Kleidermodellbau', 'ruft', 'Koerperanhaenge', 'Koerperanhaenge.teile(bau, modell): Augen, Mund, Wimpern, Brauen'),
        ('Kleidermodellbau', 'ruft', 'Rundenglb', 'Rundenglb(knochen).alle(teile).schreiben(pfad): glb()'),
        ('Durchschimmerprobe', 'ruft', 'G9garderobe', 'G9garderobe.eintrag(), teile(), bilder(): Stück in Ruhe bauen (ruhe())'),
        ('Durchschimmerprobe', 'ruft', 'G9stueckfelder', 'G9stueckfelder.holen("gelenke", …): Gelenkfelder in der Pose (bewegt())'),
        ('Durchschimmerprobe', 'ruft', 'G9oberflaechenbindung', 'G9oberflaechenbindung(fein, normalen, dreiecke, baum): Stoff an die Fläche gebunden messen'),
        ('Hbkleidprobe', 'ruft', 'Eigenstueckprobe', 'Eigenstueckprobe.humanbody(kennung, ziel, geschlecht): je Stück und Geschlecht'),
        ('Eigenstueckprobe', 'ruft', 'G9kleidhumanbody', 'G9kleidhumanbody.antwort(kennung, eintrag, rumpf): derselbe Weg wie der Browser'),
        ('Eigenstueckprobe', 'ruft', 'Durchschimmerprobe', 'Durchschimmerprobe.koerper(), ruhe() und pixel(): Genesis-Probe und Bilder'),
        ('G9stoffapi', 'ruft', 'G9garderobe', 'G9garderobe.teile(kennung): das Teil nummer'),
        ('G9stoffapi', 'ruft', 'G9stoff', 'G9stoff.bauplan(folger, stufe, passform): Kanten, Matrix, Käfighaut'),
    ]
