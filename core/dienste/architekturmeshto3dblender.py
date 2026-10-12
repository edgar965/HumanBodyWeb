# -*- coding: utf-8 -*-
"""Architekturmeshto3dblender — „Mesh to 3D und Blender": Texte und Tabellen des Reiters „MeshTo3D" (Hilfe → Architektur → 2D3D, 11.10.2026).

Edgar (11.10.2026): „oder wird bei Mesh to 3D noch Blender genutzt?" und „was von Blender übernommen wurde". Antwort und Belege: Mesh to 3D selbst startet kein Blender
(statische Suche über `_run_meshfigur.py` und die python14-Seite, dazu das Protokoll des Neulaufs vom 11.10.2026). Blender steckt im Import um den Auftrag herum —
in `umwandeln`, `export`, `umposen` und, wählbar, in `haut`. Aus Blender (Cycles v5.2.2, Quelltext) übernommen ist der Rechenweg des Backens der Haut. Die Liste der
Import-Schritte liest `Architekturmeshto3d` aus `Blendimportlauf.SCHRITTE`; die Texte hier gelten je Schritt, ein Test hält beide gleich. Zahlen stehen mit Datum und Fall;
die ausführliche Fassung mit allen Messungen ist `.claude/rules/blendimport-hautbacken.md`.
"""

__all__ = ['Architekturmeshto3dblender']


class Architekturmeshto3dblender:
    #: (Schritt, Blender?, Was der Schritt tut, Klassen). „ja" = startet Blender, „nein" = läuft ohne, „Option" = wählbar.
    IMPORT_SCHRITTE = [
        ('umwandeln', 'ja', 'Nur bei OBJ und FBX: Blender importiert die Datei, sucht fehlende Bilder, klärt die Deckkraft der Materialien und speichert quelle.blend (blendumwandeln.py).',
         ['Blendimportumwandeln', 'Blendimportformate']),
        ('export', 'ja', 'Blender liest die .blend (blendexport.py): je Netz Punkte, Dreiecke, UV, Hautgewichte; je Material den Knotengraph (blendmaterialgraph.py) und die Netzattribute '
                         '(blendnetzattribute.py); die Bilder je Kanal. Es wird nichts an der .blend geändert.', ['Blendimportlauf', 'Blendimportblender', 'Blendimportrollen']),
        ('umposen', 'ja', 'Blender stellt das Rig auf REST und dreht je Segment (Schlüsselbein, Oberarm, Unterarm, Hand, Oberschenkel, Unterschenkel, Fuß, Zehen) auf die Genesis-Richtung — '
                          'kürzester Bogen, starr um das Gelenk, lineare Häutung mit den Gewichten der .blend (blendumposen.py).', ['Blendimportumposen']),
        ('koerper', 'nein', 'Der nackte Körper samt Augen wird zu EINER GLB mit einem Atlas (numpy, PIL); Achsen Blender Z oben → glTF Y oben = (x, z, −y).', ['Blendimportkoerper']),
        ('segmentierung', 'nein', 'Nur beim Weg „netz“ (ein verschmolzenes Netz, Mesh-3D): Sapiens2 0.4B zerlegt Renderings des Netzes rundum in Haut, Kleidung und Haar; die Etiketten gehen als Stimmen auf die Netzflächen '
                                  '(Abstimmnetz mit 150.000 Flächen), „Mesh to 3D“ nimmt Hautton und Kleidungsmaske daraus. Am Zauberer-Netz (1.935.797 Dreiecke) 200,7 s; Flächen mit Stimme: 1,5 % auf dem Rohnetz, 57,3 % auf dem Abstimmnetz.',
         ['Blendimportsegmentierung', 'Blendimportweg']),
        ('pose', 'nein', 'Einstellung „Pose bestimmen“ (Vorgabe aus): SAM 3D Body findet die Gelenke am Rendering des Körpers, „Mesh to 3D“ nimmt sie statt MediaPipe (`landmarken_hand`). Ist die Einstellung aus, tut der Schritt nichts. '
                         'Am Zauberer-Netz 80–97 s, Übereinstimmung Netz ↔ Rendering (IoU) 0,977.', ['Blendimportpose', 'Posebestimmung']),
        ('figur', 'nein', 'Mesh to 3D auf diesem Körper (dieser Reiter): Regler, Gesicht, Eigenmorph. Die Optionen stehen in `Blendimportfigur.OPTIONEN`.', ['Blendimportfigur', 'Meshfigurlauf']),
        ('finger', 'nein', 'Die Finger der Figur an die Hände des Originals anpassen; ein Griff für das Requisit in der Hand.', ['Blendimportfinger']),
        ('stuecke', 'nein', 'Kleider und Haar als eigene Genesis-Stücke: Ruhelage über Kleidungsentposen (Haar: Kabsch am Kopf), OBJ mit der Original-Textur, `G9eigenstueck.schreiben`. Es wird nichts gebacken; die Gewichte der .blend '
                            'gelten nicht (anderes Rig).', ['Blendimportstuecke', 'Blendimportbilder']),
        ('haut', 'Option', 'Die Originalhaut auf die Genesis-Kacheln backen. Einstellung Charakter → Backen: „Lokal" (Vorgabe) rechnet auf der GPU (Warp) nach dem Cycles-Quelltext v5.2.2; '
                           '„Blender" startet blendbacken.py (Cycles „Selected to Active"). Kachel 1005 (Nägel) wird nicht gebacken.', ['Blendimporthaut', 'Blendimporthautlokal', 'Blendimportbackenwahl']),
        ('augen', 'nein', 'Die Originalaugen ins Genesis-Augenbild — oder das Daz-Bild aus Mesh to 3D.', ['Blendimportaugen']),
        ('modell', 'nein', 'data/models/<Name>.json mit Reglern, Stücken, Haut und Augen.', ['Blendimportmodell']),
    ]

    #: Belege für die Spalte „Blender?" (Datum, Weg).
    BELEGE = [
        'Aufrufer: `Blendimportblender.laufen` wird nur in blendimportumwandeln.py, blendimportlauf.py (export), blendimportumposen.py und blendimporthaut.py aufgerufen (Suche im Quelltext, 11.10.2026).',
        'Statisch: von den Schritten koerper, figur, finger, stuecke, augen und modell aus ist kein Modul erreichbar, das `BLENDER_EXE` benutzt; von `_run_meshfigur.py` aus sind 33 Dateien erreichbar, '
        'keine startet ein Programm oder lädt bpy (11.10.2026, ProjektTemp/_wegwerf/cycles_vergleich/blender_erreichbar.py und meshfigur_blender.py). „Erreichbar" heißt nicht „aufgerufen".',
        'Zur Laufzeit: im Protokoll des Neulaufs cute girl (2026.10.08.19.31.50, 08:44–09:10 am 11.10.2026) stehen genau zwei Blender-Starts — blendexport.py um 08:44:25 und blendumposen.py um 08:44:49; '
        'jeder Start steht dort, weil er über `Blendimportblender.laufen` geht.',
    ]

    #: (Blender-Quelle v5.2.2, Was dort geschieht, Eigene Stelle, Stand) — die Übernahme des Backens. Quellen lokal unter ProjektTemp/_wegwerf/cycles_quelle/, jede Datei Blob-gleich dem Tag v5.2.2 geprüft.
    UEBERNAHMEN = [
        ('intern/cycles/blender/shader.cpp (add_nodes_inlined)', 'Der Knotengraph, wie Cycles ihn sieht: Gruppen aufgelöst, stumme Knoten und Reroutes durch ihre inneren Verbindungen ersetzt.',
         'blendmaterialgraph.py (läuft beim Export in Blender) und hautbacken/graph: Hautgraph, Hautbackengraph', 'Zoo: 296 Materialien'),
        ('Knoten-Kerne (kernel/svm, shader_nodes.cpp)', 'Mix, Math, Vector Math, Map Range, Clamp, Farbe, Trennen/Kombinieren, Verlauf, Kurven, Bild, Mapping, Koordinate, Attribut, Normal Map, Bump.',
         'hautbacken/graph/knoten/', 'Überblendungen (Mix: ADD, MULTIPLY, SUBTRACT, MIX) nach v5.2.2 mit interp, nicht nach main'),
        ('intern/cycles/blender/mesh.cpp', 'UV-Karten, Farbattribute (Byte-Farben nach Linear), glatt/flach, Normalen-Domain, Polygon-Struktur.',
         'blendnetzattribute.py (in Blender), hautbackenquelle.py', 'Rohdaten für Blenders Normalenrechnung gegen me.corner_normals und vertex_normals geprüft (10.10.2026)'),
        ('mesh_normals.cc', 'Punkt-, Flächen- und Eckennormalen, scharfe Kanten, eigene Normalen.', 'hautbackenblendernormalen.py', 'gegen me.corner_normals/vertex_normals geprüft'),
        ('MikkTSpace', 'Tangenten — unverändert, als DLL (MSVC, gebaut beim ersten Aufruf).', 'hautbackentangenten.py, mikktspace/, mikkhuelle/', 'Modus cycles für die Quelle, blender für die Figur'),
        ('corner_tris_calc', 'Vierecke werden nach den Punkten der RUHELAGE zerlegt (Diagonale 0–2, es sei denn sie fällt aus dem Viereck).', 'hautbackenretri.py',
         'hinako: 1.328 Vierecke wechseln; n-Ecke (> 4) nicht nachgebaut, die Zahl steht im Bericht'),
        ('RE_bake_pixels_populate (bake.cc)', 'Der Abtastpunkt eines Texels liegt 0,001 / 0,002 Texel neben der Mitte.', 'hautbackenkachel.py (VERSATZ)',
         'Zoo: 18 Materialien über 3 Stufen → 4; Normalen-Mittel der Importe 0,06–0,22 → 0,02–0,05'),
        ('film.cpp, film_write_data_passes', 'Bei Alpha < 0,5 schreibt Cycles keinen Normal-Pass; Blender liefert (128, 128, 128).', 'graph/hautalpha.py (Hautalpha)',
         'Asian_Girl „Std_Eyelash": vorher wich die Wimper bei 92 % der Texel um ~113 Stufen ab'),
        ('surface_shader_average_normal, Principled BSDF', 'Die gebackene Normale ist das gewichtete Mittel der Closure-Normalen: Sheen → Coat → Metall → Transmission → Glanz → Untergrund/Diffus, mit den '
                                                          'Albedo-Tabellen von Cycles (cycles_tabellen.npz, 63 KB) und der Energieerhaltung (GGX und Glas).', 'hautbacken/closure/, graph/hautglanz.py',
         '49 Zoo-Materialien backt Blender mit „Bump Map Correction"; Mittel Normalen ≤ 0,05'),
        ('integrator.cpp, surface_shader.h', 'Beim Backen wird die Transparent-Closure zur Holdout-Closure und zählt nicht in den Mittelwert.', 'Kommentar und Verhalten in hautclosurekernel.py',
         'ohne Principled gemessen (transparent_probe.py, Blender 5.2.2 CPU), 11.10.2026'),
        ('ImageTextureNode::image_params, OpenImageIO', 'Farbraum, Alpha-Modus, Quelle des Bildes; 8- und 16-Bit-Bilder bleiben Ganzzahlen.', 'hautbackenbild.py, blendmaterialbild.py (in Blender)',
         'Farbraum-Umrechnung im Zoo gegen Blender gemessen, nicht aus dem Quelltext gefolgert'),
    ]

    #: Gemessen: (Was, Wert, Quelle/Datum).
    MESSUNG = [
        ('Zoo: 296 kleine Materialien gegen Blender 5.2.2 auf der CPU', 'Mittlere Abweichung (Stufen von 255): Farbe ≤ 0,02, Rauheit ≤ 0,00, Normalen ≤ 0,05; Anteil der Texel über 6 Stufen ≤ 0,02 %',
         'core/tests/unit/test_hautbacken_zoo.py, zoo_schwellen.py, Stand 11.10.2026'),
        ('Sieben echte Importe, Kachel 1001 (1024 px), gegen Blender auf der CPU', 'Normalen-Mittel 0,02–0,05; Anteil über 10 Stufen höchstens 0,001 %; Farbe: Anteil über 10 Stufen überall 0,000 %',
         'blendimport-hautbacken.md, Stand 11.10.2026'),
        ('Zeit des Schritts haut, cute girl', 'Blender (08.10.2026): 1.143,7 s — lokal im Neulauf (11.10.2026, 09:10): 134,8 s. Zwei Läufe zu verschiedenen Zeiten auf demselben Rechner, ohne gleiche Last — '
                                              'kein sauberer Vergleich',
         'stand.json des Imports 2026.10.08.19.31.50, Feld dauer.haut'),
        ('Zeit des Schritts haut, Rosemary (vier Kacheln à 8192²)', 'Blender 1.522 s → lokal 420 s (mit CPU-Nacharbeit; die GPU-Nacharbeit einer Kachel 120 → 12 s)', 'blendimport-hautbacken.md'),
        ('Referenz', 'Blender auf der CPU. Gegen Blender auf der GPU weicht der Bump-Fall mit Filterbreite 0,01 im Mittel um 3,7 Stufen ab (gegen die CPU 0,1) — Deutung, nicht geprüft: '
                     'die Texturhardware rundet die Abtastposition', 'blendimport-hautbacken.md'),
    ]

    #: Nicht übernommen oder nicht geprüft — der Backer meldet es im Bericht oder als Hautgraphfehler.
    OFFEN = [
        'Rand: Blender füllt mit ADJACENT_FACES (texture_margin.cc, rund 550 Zeilen) — nicht nachgebaut; der Backer nimmt den nächsten getroffenen Texel bis 16 px. Normalen im Rand weichen im Mittel 15–26 Stufen ab, Farbe 0–8 px 1–3 Stufen.',
        'Closure-Mittel nicht gerechnet, aber gemeldet (glanz_korrektur): Thin Wall, Dünnfilm, andere Verteilung als GGX/Multi-GGX, älterer Export. Nicht geprüft: Mehrfach-Principled (es gilt der erste), Glas von der Rückseite.',
        'Als Hautgraphfehler abgelehnt: Fließkomma-Bilder (EXR/HDR), gepackte Bilder mit mehr als 8 Bit, UDIM, Bildfolgen, Box-Projektion, echte Verschiebung. Keiner der sieben geprüften Importe braucht sie.',
        'Restliche Ausreißer: größte Abweichung bis 217 Stufen an höchstens 0,002 % der Texel — nicht aufgeschlüsselt, vermutlich Sprungstellen (Blender rechnet die Schwerpunkte in double, der Backer in float).',
        'Ob sich export und umposen ohne Blender ersetzen ließen, ist nicht untersucht.',
    ]

    #: Was der Import vom Auftrag Mesh to 3D liest, und was offen ist (Rainy, 10.10.2026).
    IMPORT_VERZAHNUNG = [
        'Der Auftrag ist ein gewöhnlicher `Meshfigurauftrag`: Er steht in der Liste von „Mesh to 3D", seine Seite zeigt Erkennung, Runden und Vergleich. Er wird im Prozess des Imports gerechnet, nicht in einem zweiten.',
        'Der Import liest vom Auftrag nur regler/stellung, den Rest (Eigenmorph) und die Fototextur (Kacheln, Augenbild).',
        'Das Körper-Tor hielt den ersten Lauf an (11 Regler am Anschlag: Brust, Schulterblatt, Brustbein, Hals; Soll höchstens 8) — der Import setzt tor = „melden"; die Rumpftiefe stimmte (Verhältnis ≥ 0,957).',
        'Gemessen (Lauf 2026.10.08.11.28.06): Anpassung 958,8 s; Körperkette 13,55 → 2,72 mm RMS, Gesichtskette 0,97 mm, Eigenmorph Rest 2,32 → 0,80 mm. Zwei Maße, nicht verwechseln: das Maß von Mesh to 3D '
        '(0,78 / 0,93 mm RMS) zählt nur zugeordnete Paare ohne Ausreißer; ALLE 54.369 Körperpunkte gegen die Fläche der Figur: Median 0,99 mm, p95 14,4 mm, 12,3 % über 8 mm, RMS 5,74 mm.',
        'Offen (Rainy, 10.10.2026, blendimport-dauer.md): „haar", „kleidung" und „vorschau" rechnen im Import 810 s (40 % des Auftrags), obwohl frisur/haarkarten aus und kleidung „wie_haut" stehen. Ob spätere Schritte '
        'Zwischendateien von ihnen brauchen, ist nicht belegt — erst `Meshfigurlauf` und `Meshfigurende.textur` daraufhin lesen, dann eine Option „Import" (Schritte überspringen).',
    ]

    #: Blender anderswo im Projekt (nicht Mesh to 3D) — nur der Verweis.
    ANDERSWO = ('Außerhalb von Mesh to 3D und des Imports: der Stoffsolver (Blenders Cloth und Haar-Dynamik als Python/Warp-Paket) und der Blender-Weg beim Drapieren (`Engine2d3dKleiderblender`, nur nach Ansage). '
                'Beides steht im Reiter „Tools", Bereiche „Aus Blender übernommen: der Stoffsolver" und „Schleifen über Blender".')
