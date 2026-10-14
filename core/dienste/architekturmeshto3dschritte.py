# -*- coding: utf-8 -*-
"""Architekturmeshto3dschritte — Kurzfassung, Schritte und Zwischendateien des Reiters „MeshTo3D" (Hilfe → Architektur → 2D3D, 11.10.2026).

Edgar (11.10.2026): „füge diese Info hinzu in /hilfe/architektur/2d3d/ in neuem Tab - MeshTo3D, wo du alle infos reintust, wie das geht, was von Blender übernommen
wurde und so weiter mit möglichst vielen Details. Auch Klassenmodell, Workflow und so weiter." Dieser Teil ist der Workflow: die Schritte von `Meshfigurlauf`, je
Schritt die Welt (python14 / python10), die Klassen und was er tut. Die LISTE der Schritte und ihre Bänder liest `Architekturmeshto3d` aus `Meshfigurlauf` (ein Test
hält Text und Code gleich); die Beschreibungen stehen hier von Hand. Jeder Satz stammt aus dem Quelltext oder aus `.claude/rules/meshfigur.md` (Messungen mit Datum);
was nicht gemessen ist, steht nicht darin.
"""

__all__ = ['Architekturmeshto3dschritte']


class Architekturmeshto3dschritte:
    STAND = '11.10.2026'

    #: (Titel, Text) — der Kasten ganz oben.
    KURZ = [
        ('Was es tut',
         'Mesh to 3D legt eine Genesis-9-Figur auf ein Menschen-Netz (Scan, TRELLIS- oder Hunyuan-Netz, der Körper einer .blend). Es stellt die Regler und die Haltung der Figur '
         'so, dass der Abstand Figur ↔ Netz klein wird (Adam auf der Grafikkarte, Abstände per Nächste-Nachbar-Suche). Was die Regler nicht erreichen, legt es als eigenen Morph '
         'dazu (Eigenmorph); die Farbe des Netzes backt es auf die fünf Hautkacheln.'),
        ('Was herauskommt',
         'Das Modell „<Name> Mesh" in data/models (Regler, Eigenmorph, Kacheln, Augenbild) und die Ablage output/Export/MeshTo3D/<Name>_<Zeit>/ mit Bildern und bericht.json '
         '(`Meshfigurspeichern`). Die GLB mit Rig schreibt der Browser (Knopf „Exportieren"). Nichts davon wird über eine fremde Datei geschrieben.'),
        ('Wer es benutzt',
         'Drei Verwender: der Reiter „Mesh to 3D" (Modell aus Dateien) mit einem Netz aus Datei oder Pfad; „2D3D Kleider" im Schritt koerper (Figur übernehmen oder die Kette '
         'rechnen — `Engine2d3dKleiderkoerperlauf` erbt von `Meshfigurlauf`); der Blender-Import im Schritt figur (`Blendimportfigur`, Abschnitt „Mesh to 3D und Blender").'),
        ('Blender?',
         'Nein. Von _run_meshfigur.py aus sind 33 Dateien erreichbar, keine startet ein Programm oder lädt bpy (statische Suche, 11.10.2026); auf der python14-Seite ist kein '
         'Modul mit BLENDER_EXE erreichbar. Im Protokoll des Neulaufs vom 11.10.2026 (cute girl, 08:44–09:10) stehen genau zwei Blender-Starts, beide aus dem Import '
         '(export, umposen), keiner aus dem Auftrag Mesh to 3D.'),
    ]

    #: (Schritt, Welt, Klassen python14, Klassen python10, Was, Ergebnis) — Schlüssel = `Meshfigurlauf.SCHRITTE`.
    SCHRITTE = [
        ('erkennung', 'python14 ruft, python10 rechnen',
         ['Meshfigurlauf'],
         ['Meshfigurerkennungsschritt', 'Meshfigurscan', 'Meshfigurerkennung', 'Meshfiguransichten', 'Meshfigurpunkte', 'Meshfigurtriangulation', 'Meshfigurlandmarkenflaeche',
          'Meshfiguruebersicht', 'Meshfigurkopfnetz', 'Meshfigurkopfabgleich', 'Meshfigurzielnetz', 'Meshfigurfarbangleich', 'Meshfigurnaht'],
         'Das Netz wird geladen (UV-Nähte zusammengeführt) und auf Meter gebracht — Option einheit „auto" rät: über 3 Einheiten Zentimeter, über 30 Millimeter, unter 0,3 wird '
         'auf 1,70 m gestreckt; der Blender-Import setzt „meter". Y ist oben, „vorn" ist die der acht Ansichten, in der MediaPipe frontal sieht, danach aus Schulter- und '
         'Hüftlinie nachgedreht. Körper: acht Ansichten, Pose mit 33 Punkten, in 3D per RANSAC-DLT und Gauß-Newton (2–8 px). Gesicht: 15 Nahaufnahmen, FaceLandmarker mit 478 '
         'Punkten (Median 4,3 px). Die Punkte werden auf die Netzfläche gelegt (≤ 3 mm unverändert, ≤ 30 mm auf die nächste Probe, darüber NaN). Mit eigenem Kopfnetz: Kopf '
         'finden, an den Körper legen, Hautfarbe angleichen, am Hals nähen. Stand 27./29.09.2026 laut meshfigur.md.',
         'ergebnis.erkennung und ergebnis.vorlage: Lage des Netzes (scan_lage.npz), Landmarken, zwei Übersichtsbilder, das Vorlagebild (vorlage.png).'),
        ('haar', 'python14',
         ['Meshfigurhaar'], [],
         'Das Haar wird aus dem Kopfnetz geschnitten (Paket „Haar", Einzelheiten haar.md). Das Objekt auf der Figur entsteht erst im Schritt vorschau — dann gehören '
         'genesis_ende.npz und posiert.npy, also die Ruhelage des Netzhaars, zur Figur.',
         'ergebnis.haar: Karte „Haar" (Netz ohne Haar / nur Haar), Befund.'),
        ('kleidung', 'python14',
         ['Meshfigurkleidung'], ['Meshfigurhautmodell', 'Meshfigurhautkarte', 'Meshfigurhautteilung', 'Meshfigurhautbaender'],
         'Die Kleidung wird aus dem KÖRPERnetz geschnitten (Paket „Kleidung"; Option kleidung: weich | nah | ignorieren | wie_haut; Hüte, die Sapiens als Zubehör sieht, gehen aus dem Haar ins Kleidungsobjekt). Dahinter steht der Hautton der KAHLEN Stellen — er '
         'gilt auch für die Körperkette und die Textur (vorher der von Rumpf und Oberschenkeln, bei Shirt und Shorts der Stoff). Das Objekt entsteht am Ende von vorschau.',
         'ergebnis.kleidung: Karte „Kleidung", Hautton, Bänder (je Körperabschnitt und 5 cm), Stücke.'),
        ('kalibrierung', 'python14 ruft, python10 rechnen',
         ['Meshfigurlauf'], ['Meshfigurerkennungsschritt'],
         'Nur einmal je Rechner (läuft nur, wenn die Tabelle fehlt): Genesis selbst als texturierte GLB (`G9figurglb`) durch DENSELBEN Erkennungsweg; daraus die Tabelle '
         '`G9netzlandmarken` (Gesicht → Dreieck + Anteile, Median 1,0 mm vom Käfig; Gelenke → Ankerknochen + Versatz, der Detektor liegt 5–31 mm neben dem Daz-Gelenk). Die alte '
         '68-Punkte-Tabelle taugt für 3D nicht (Augen 94 mm, Kinnlinie 20 mm daneben). Mit der Kalibrierung stimmte die Höhe auf 1 mm (27.09.2026).',
         'Genesis9/ablage/meshfigur_landmarken_v1.npz.'),
        ('koerper', 'python14 und python10 im Wechsel',
         ['Meshfigurkette', 'Meshfigurregler', 'Meshfigurgenesis'],
         ['Meshfigurrunner', 'Meshfigurregistrierung', 'Meshfigurmodell', 'Meshfigurkinematik', 'Meshfigurabstand', 'Meshfigurlandmarken', 'Meshfigurrumpfpruefung'],
         'Körperkette in Runden (Vorgabe 2). Je Runde rechnet python14 die Figur für die aktuelle Reglerstellung ECHT (Formelketten, Knochenskalierung, Daz-Gelenkkorrekturen '
         'der gefundenen Haltung), der Runner stellt die Regler auf der Karte (torch, Adam) und meldet Werte und Haltung zurück. Runde 1 in vier Stufen — haltung → groesse → '
         'koerpertyp → bereiche —, ab Runde 2 eine Stufe mit allen Reglern. Option Körpergröße: nach Runde 1 wird das Netz um den Boden auf die Größe gestreckt (Runner-Schritt '
         'skalieren). Am Ende das Tor `Meshfigurrumpfpruefung` (Rumpftiefe gegen das Netz, Regler am Anschlag).',
         'ergebnis.koerper (runden mit dem Verlauf je Stufe, haltung, stellung, tor), arbeit/zustand.npz, posiert.npy.'),
        ('gesicht', 'python14 und python10 im Wechsel',
         ['Meshfigurkette', 'Meshfigurregler'],
         ['Meshfigurregistrierung', 'Meshfigurlandmarken', 'Meshfigurmodell'],
         'Eigene Kette über 296 Kopfregler gegen 478 Gesichtspunkte: kopfhaltung → schaedel → zuege → fein. Nur Hals und Kopf drehen; Landmarken zählen nur, wenn ihr Dreieck '
         'ganz im Gesichtskern liegt (Iris Gewicht 0, Umriss ½). Sie startet aus der Stellung der Körperkette, nicht aus dem letzten Stand.',
         'ergebnis.gesicht (Verlauf je Stufe), die Stellung der Kopfregler in ergebnis.regler.'),
        ('rest', 'python10 rechnet, python14 legt ab',
         ['Meshfigurende', 'Meshfiguraugenhoehle'], ['Meshfigurabstand'],
         'Was die Regler nicht erreichen: der Runner liefert je Käfigpunkt den Rest in der Ruhelage (rest.npz, mit Gewicht); python14 mittelt links/rechts (Option symmetrie), '
         'glättet (Lücken aus den Nachbarn, 6 Laplace-Schritte) und legt ihn als Eigenmorph eigen:<kennung> ab (`G9restmorph`, Wert 0…2). Die Augenpartie bleibt Lücke.',
         'Eigenmorph (3DObjects/models/Genesis9/eigenmorphe/<kennung>.npz und .json), ergebnis.rest.'),
        ('textur', 'python10 rechnet, python14 backt',
         ['Meshfigurende', 'Meshfigurtexelpruefung', 'Meshfiguraugenbild', 'Meshfigurtexturoptionen'],
         ['Meshfigurtextur', 'Meshfigurentlichtung', 'Meshfiguriris'],
         'Der Runner liefert je Texel der fünf Kacheln die Farbe des Netzes (meshtextur.npz: Fußpunkt auf der Fläche der nächsten Probe, UV bilinear; am Körper zählt nur Hautfarbe; '
         'Option entlichten rechnet das Licht heraus). python14 säubert die Texel (`Meshfigurtexelpruefung`) und backt sie über die auf den Hautton getönte Daz-Haut '
         '(`G9texturbacken`); dazu das Daz-Augenbild in der Irisfarbe des Netzes.',
         'ergebnis.fototextur: Kacheln (meshfigur_<k>.jpg), Augenbild (meshfigur_augen.jpg), deckung_je_kachel.'),
        ('vorschau', 'python14 ruft, python10 rechnet',
         ['Meshfigurvorschau'], ['Meshfigurvergleichsbild'],
         'Bilder der Figur (Icon, vorn, seitlich, hinten, Kopf), die Abstände Figur ↔ Netz und das Vergleichsbild (Netz · Figur · Tiefenvergleich) aus dem Runner-Schritt bewertung; '
         'mit Referenzfigur (Option referenz) der Testfall Punkt für Punkt und Fläche gegen Fläche. Zum Schluss entstehen die Objekte Haar und Kleidung in der Ruhelage — in drei Fäden zusammen mit der Scham-Messung.',
         'ergebnis.vorschau, vergleich.jpg, Objekte für die Bühne.'),
        ('frisur', 'python14',
         ['Meshfigurfrisur', 'Meshfigurfrisurstueck', 'Meshfigurfrisurdeltas'], [],
         'Eine Daz-Frisur oder „Haar Eigen" gegen das Netzhaar (Option frisur: beste | daz | eigen | aus), Haarkarten aus der Schale (Option haarkarten). Das Modell trägt die Wahl als „kleidung". '
         'Sie startet schon nach dem Runner der Textur, als Faden neben dem Backen der Kacheln und der Vorschau (Meshfigurnebenlauf.frueh); „speichern" wartet auf sie.',
         'Frisur im Modell, Haarkarten.'),
        ('speichern', 'python14',
         ['Meshfigurspeichern'], [],
         'Modell „<Name> Mesh" in data/models (Format der Szene, quelle genesis9; nie über ein fremdes Modell — gehört eine gleichnamige Datei nicht zu diesem Auftrag, kommt eine '
         'Nummer dazu) und Ablage output/Export/MeshTo3D/<Name>_<Zeit>/ mit Kacheln, Eigenmorph, Bildern und bericht.json.',
         'data/models/<Name> Mesh.json, Ablage, Kacheln in data/models/Texturen/<Modell>/.'),
    ]

    #: (Datei, schreibt, liest, Inhalt) — was zwischen den Welten wandert (gegen den Code gelesen: Meshfigurlauf, Meshfigurende, Meshfigurrunner).
    DATEIEN = [
        ('arbeit/auftrag.json', 'python14 (`Meshfigurlauf.auftrag`)', 'python10 (`Meshfigurdaten`)',
         'Netz, Ordner, Optionen (mit Dämpfungswert), Kopfnetz, was die Schritte dazulegen'),
        ('arbeit/genesis_koerper_<runde>.npz, genesis_gesicht.npz, genesis_ende.npz', 'python14 (`Meshfigurgenesis`)', 'python10 (`Meshfigurdaten.genesis`)',
         'Käfig, Skelett, Haut, Landmarken und Gelenkkorrekturen der aktuellen Reglerstellung — „ECHT gerechnet"'),
        ('arbeit/regler_koerper_<runde>.npz, regler_kopf.npz', 'python14 (`Meshfigurregler`)', 'python10 (`Meshfigurdaten.jacobi`)',
         'Ableitung Regler → Punkte und Gelenke (Jacobi-Matrix), aktueller Wert, Stufe, Grenzen'),
        ('arbeit/zustand.npz', 'python10 (`Meshfigurrunner._zustand_speichern`)', 'python10 (der nächste Schritt)',
         'Haltung (theta) und Lage (rg, tg); die Kette beginnt frisch und löscht die Datei des früheren Laufs'),
        ('arbeit/posiert.npy', 'python10 (`Meshfigurrunner._kette`)', 'python14 (`Meshfigurkleidung`, `Meshfigurhaar`)', 'Die Figur in der Haltung des Netzes'),
        ('arbeit/rest.npz', 'python10 (`_rest`)', 'python14 (`Meshfigurende.rest`)', 'Rest je Käfigpunkt in der Ruhelage, Gewicht, ggf. Mindestweg'),
        ('arbeit/meshtextur.npz', 'python10 (`_textur`)', 'python14 (`Meshfigurende.textur`)', 'Punktfarben, Deckung, Netzfarbe je Texel der Kacheln'),
        ('stdout des Runners', 'python10', 'python14 (`Meshfigurlauf.runner`)',
         'Zeilen [fortschritt] <0..100> <Text>, [ergebnis] {…}, [fehler] {…}; Fortschritt wird auf das Band des Schritts umgerechnet'),
    ]
