# -*- coding: utf-8 -*-
"""Werkzeughaarfoto — Reiter „Tools" der Seite Architektur 2D3D, Gruppe T2: Haar aus Fotos (Haarmaske, Frisurwahl).

Genesis ist kahl; das Netz der Fotos (Hunyuan/TRELLIS) trägt die Frisur als Teil EINER Fläche. Reine Daten (Schema:
`ProjektTemp/_wegwerf/stoff_ausbau/AUFTRAG_TOOLS.md`); gelesen von `Architektur2d3dwerkzeuge`. Jede Zeile ist gegen den
Code gelesen (03.10.2026); Zahlen tragen Fundstelle und Datum.
"""

__all__ = ['Werkzeughaarfoto']


class Werkzeughaarfoto:
    G = 'Genesis9/'
    D = 'HumanBodyWeb/core/dienste/'
    A = 'HumanBodyWeb/core/api/'
    H = 'Haar/'

    KENNUNG = 'haarfoto'
    TITEL = 'Haar aus Fotos: Haarmaske, Frisurwahl, Haarkarten'
    EINLEITUNG = (
        'Zwei Schritte von „Mesh to 3D“ machen aus dem Haar im Netz der Fotos eine Frisur der Garderobe: Schritt „haar“ '
        'schneidet das Haar aus dem Netz (Haarmaske, Farbe, Bartzone), Schritt „frisur“ wählt die Frisur, die dem Netzhaar am '
        'nächsten kommt, stellt ihre Regler und baut optional Haarkarten aus der Haarschale. Reihenfolge der Schritte: '
        'erkennung, haar, kleidung, kalibrierung, koerper, gesicht, rest, textur, vorschau, frisur, speichern. Das Ergebnis '
        'trägt das gespeicherte Modell als kleidung (Frisur, Regler, Farbe); 2D3D Kleider nimmt die Kandidaten als Startwert '
        'und führt die Frisur in den Runden weiter (Gruppe „Haar“, „Haar formen“, „Automatik …“).')

    # (Werkzeug, Wofür, Art, Aufruf, Klassen, Hinweis)
    ZEILEN = [
        ('Schritt „haar“: das Haar aus dem Netz schneiden',
         'Trennt im Netz Haar und Rest, schätzt die belichtete Haarfarbe und erkennt den Bart; legt Maske und Bilder ab.',
         'api',
         'POST /api/meshfigur/<job_id>/starten/   {"ab": "haar", "optionen": {"kopfhaut": "haar"}}\n'
         '→ {ok, pid, neu_eingelesen}   Ablage arbeit/haar_maske.npz (haar, geschuetzt, unten, bart), '
         'ergebnis/haar_<ohne|nur>_<vorn|seite|hinten>.png, ergebnis.haar, ergebnis/haar.glb',
         [(A + 'meshfigur.py', 'Meshfigurendpunkte'), (D + 'meshfigurhaar.py', 'Meshfigurhaar'),
          (H + 'haarmaske.py', 'Haarmaske'), (H + 'haarteilung.py', 'Haarteilung'), (H + 'haarobjekt.py', 'Haarobjekt'),
          (H + 'haarbild.py', 'Haarbild')],
         '„ab“ rechnet den Schritt UND alle danach neu (Minuten, anderes Ergebnis). kopfhaut haar (Vorgabe: Haarfarbe des '
         'Netzes aufmalen) | haut (für eigenes Haar). Haarmaske je Fläche: Hauttest des Hautmodells der kahlen Stellen (Gesicht, '
         'Hände, Unterarme, Unterschenkel — nicht „rot vor blau“), Helligkeit 0,55–1,7 × Hautton, Schutz nur für das INNERE '
         'Gesicht (konvexe Hülle um Augen, Brauen, Nase, Mund + 6 mm), 4 Runden Mehrheit über die Kanten, Haut ohne '
         'Verbindung zu Gesicht/Hals wird Haar, Inseln < 0,2 % klappen um; _kopfhaar nimmt nur Haar, das am Scheitel hängt '
         '(Kragen nicht); _bart: Bartzone ist Haut statt Haar, aber nur bei KURZEM Haar (mehr als 12 % des Haars hinter den '
         'Ohren tiefer als 3 cm über dem Kinn → langes Haar, dann gilt die alte Regel). Haarteilung._farbe liefert die '
         'belichtete Farbe (Median der hellsten Hälfte): Lauf 13.42.12 Haar 84,8 → 23,3 % der Kopffläche, Farbe Median '
         '(86, 73, 75) → belichtet (104, 93, 90) (haar.md, 29.09.2026). Damira (Auftrag 2026.09.27.15.52.13): Haar 68,9 % der '
         'Kopffläche (2.854 cm²), Laden 2,4 s, Maske 0,7 s, Bilder 5,2 s; haar.glb 202.394 Flächen, 5,9 MB, 2,8 s. Grenzen: '
         'orange beleuchtete Strähnen, die AUF die Stirn gemalt sind, bleiben Haut; unter langer Haarschicht liegt echte '
         'Geometrie (das „ohne Haar“ von hinten ist kein Renderfehler). Haarbild (pyrender) läuft nur im Arbeitsprozess, '
         'nie im Server.'),

        ('Schritt „frisur“: eine echte Frisur statt der Haarschale',
         'Wählt aus allen Frisuren der Garderobe die mit der kleinsten Hülle gegen das Netzhaar, stellt ihre Regler und '
         'baut Haarkarten als eigenes Objekt.',
         'api',
         'POST /api/meshfigur/<job_id>/starten/   {"ab": "frisur", "optionen": {"frisur": "beste", "haarkarten": "an"}}\n'
         '→ {ok, pid, neu_eingelesen}   ergebnis.frisur = {kandidaten, fein, wahl, kleidung, karten, sekunden}, '
         'ergebnis/haarkarten.glb',
         [(A + 'meshfigur.py', 'Meshfigurendpunkte'), (D + 'meshfigurfrisur.py', 'Meshfigurfrisur'),
          (D + 'meshfigurfrisurstueck.py', 'Meshfigurfrisurstueck'), (H + 'haarhuelle.py', 'Haarhuelle'),
          (H + 'frisurregler.py', 'Frisurregler'), (H + 'haarkarten.py', 'Haarkarten'), (H + 'haarglb.py', 'Haarglb'),
          (G + 'haareigen.py', 'G9haareigen')],
         'frisur: beste (Daz oder „Haar Eigen“) | daz | eigen | aus; haarkarten an | aus. A Frisurwahl: jede Frisur der Garderobe '
         '(Art haar, ohne Bart und Toon, auch die Klone G1/G2/G8) in jedem formenden Stil, gemessen als HÜLLE '
         '(Haarhuelle: je 5°-Feld um die Kopfmitte der größte Radius; fehlendes und überzähliges Haar zählen mit; Haar in '
         'Richtung des geschützten Gesichts +30 mm), nicht Punkt zu Punkt; die besten OBERSTE (2) Daz-Frisuren und „Haar '
         'Eigen“ bekommen ihre Regler gestellt (Frisurregler: linear, Δ je Regler einmal echt, Koordinatensuche). '
         'B „Haar Eigen“: Kin Hair als eigenes Stück mit Länge, Kurz, Dichte, Wellig, Dutt, gebaut wenn es fehlt (64 s). '
         'C Haarkarten (Haarkarten): Strähnen von der Kopfhaut an der Schale entlang, Karten mit Deckkraftbild + Punktfarbe, '
         'darunter die abgedunkelte Schale; Abtastung auf 12 Punkte je Strähne (25,5 → 4,4 MB). Gemessen Auftrag '
         '2026.09.28.23.42.28 (Hochsteckfrisur, haar.md): Messen 144 s (17 Frisuren), Regler 16 s, Karten 4 s; gewählt Mavick '
         'Hair Style 14,1 mm (Deckung 0,78), Basic Hair 14,2, „Haar Eigen“ Dutt 0,875 + Kurz 0,25 19,6 mm. Die Flecken an '
         'Schläfe und Auge sind aufgemalte Kopfhaut (Option kopfhaut haar), nicht die Frisur. Bühne: Auswahl „Haar“ '
         '(Frisur | Haar aus dem Netz | Haarkarten), sichtbar je Netz; „Kein Haar“ ist das Kästchen „Haare“. Nur den '
         'Frisurschritt nachrechnen: ProjektTemp/_wegwerf/frisur/frisur_schritt.py <kennung> (Wegwerf, schreibt '
         'ergebnis.frisur; läuft nicht, solange der Auftrag läuft).'),

        ('Nur den Haarschritt nachrechnen (Wegwerfskript)',
         'Rechnet den Schritt „haar“ allein, ohne Kalibrierung, Ketten, Textur und Vorschau neu zu rechnen.',
         'cli',
         'cd A:/3DTools && python14/Scripts/python.exe ProjektTemp/_wegwerf/meshto3d/haar_schritt.py <kennung> [objekt]',
         [(D + 'meshfigurhaar.py', 'Meshfigurhaar'), (D + 'meshfigurlauf.py', 'Meshfigurlauf')],
         '„objekt“ schreibt nur ergebnis/haar.glb neu (wie am Ende von „vorschau“). Das Skript meldet sich ab, wenn der '
         'Auftrag läuft („nicht dazwischen rechnen“). Es schreibt in das Ergebnis eines Auftrags (Maske, Bilder): nur auf '
         'Ansage und nur an einer Kopie, wenn das Ergebnis erhalten bleiben soll. Ein Wegwerfskript, kein Werkzeug der '
         'Pipeline.'),

        ('Regel: Haar im Netz ist Ziel, nicht Eingabe der Bühne',
         'Hält fest, wie das Haar aus dem Netz mit der Figur zusammenhängt, damit niemand doppelt rechnet.',
         'regel',
         'Das Haar aus dem Netz ist ein EXTRA-Objekt (haar.glb, Ruhelage der Figur), Ziel der Frisurwahl; kein zweites Mal als '
         'Bibliothekshaar bauen.',
         [(D + 'meshfigurhaar.py', 'Meshfigurhaar'), (D + 'meshfigurfrisur.py', 'Meshfigurfrisur')],
         'Meshfigurhaar.objekt legt haar.glb in die RUHELAGE der Figur (am Ende von „vorschau“, erst dann gehören '
         'genesis_ende.npz und posiert.npy zur aktuellen Figur); scheitert es, steht der Grund in ergebnis.haar.objekt.fehler. '
         'Bühne: meshfigurhaarobjekt.js hängt es in die Gruppe der Figur, Schalter „Haare“. In 2D3D Kleider wird das Haar des '
         'Netzes NICHT mehr als Fotostück gebaut: das Fotohaar legte ein schwarzes Band über die Augen (die Haarmaske nimmt '
         'Brauen mit) und haar_keins ließ die Grundsorte stehen (Runde 17, Kleiderwahl.FOTO_REIHE) — das Haar bleibt eine '
         'Bibliotheksfrisur. Die Kennzahl „Gesamtabweichung“ belohnt dabei das Falsche (die lange Frisur hatte 1,799, die '
         'richtige kurze 1,937 — Netznote; die Seiten-IoU dagegen 0,68 → 0,79): Die Zahl ist ein Hilfsmaß, die Tafel '
         'entscheidet (engine2d3dkleider.md, 01.10.2026).'),
    ]

    # Klassenmodell: (von, 'ruft', nach, womit)
    BEZIEHUNGEN = [
        ('Meshfigurhaar', 'ruft', 'Haarmaske', 'Haarmaske.rechnen(): je Fläche Haar ja/nein, geschützt, Bart'),
        ('Meshfigurhaar', 'ruft', 'Haarteilung', 'Haarteilung: Teilnetze „ohne Haar“ und „nur Haar“, kennzahlen(), Farbe haar'),
        ('Meshfigurhaar', 'ruft', 'Haarobjekt', 'Haarobjekt.schreiben(): haar.glb in der Ruhelage der Figur'),
        ('Meshfigurhaar', 'ruft', 'Haarbild', 'Haarbild.rendern() und speichern(): Bilder ohne/nur Haar (nur im Arbeitsprozess)'),
        ('Meshfigurfrisur', 'ruft', 'Meshfigurfrisurstueck', 'Meshfigurfrisurstueck: eine Frisur in einem Stil auf der angepassten Figur'),
        ('Meshfigurfrisur', 'ruft', 'Haarhuelle', 'Haarhuelle: Hülle des Netzhaars gegen die Hülle der Frisur (Abstand in mm, Deckung)'),
        ('Meshfigurfrisur', 'ruft', 'Frisurregler', 'Frisurregler(messung, grund, deltas, grenzen).suchen(): Regler der besten Frisuren stellen'),
        ('Meshfigurfrisur', 'ruft', 'Haarkarten', 'Haarkarten.schreiben(pfad): Weg C → haarkarten.glb'),
        ('Meshfigurfrisur', 'ruft', 'G9haareigen', 'G9haareigen.sicherstellen(): baut „Haar Eigen“, wenn es fehlt'),
        ('Haarkarten', 'ruft', 'Haarglb', 'Haarglb().netz() und schreiben(): GLB mit Punktfarbe und Bild'),
    ]
