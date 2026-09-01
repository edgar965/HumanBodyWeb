# -*- coding: utf-8 -*-
"""Review-Bereiche: die Kern-Bibliothek (humanbody_core)

Mathematik und Daten ohne Django und ohne Browser:
Retarget, Unterteilung, Morphs, Posen, Skelett.

Aus ui/review_bereiche.py herausgeloest (17.08.2026): Die Datei hatte 965 Zeilen und 59
Bereiche in einer Liste — der Spitzenbefund von `dateigroesse`.
"""
BEREICHE = [
    {'slug': 'retarget', 'name': 'Retarget-Mathematik',
     'dateien': ['HumanBody/humanbody_core/skeleton/retarget.py'],
     'hinweis': (
         'BVH-Animationen werden auf das DEF-Skelett (Rigify, 176 Knochen) '
         'übertragen. Quaternionen [w,x,y,z] in NumPy, Y ist oben. Zwei '
         'Betriebsarten: Standard (desiredWorldQ = bvhWeltQ x offsetQ) und '
         'Delta (Frame-0-Drehung abziehen, für AIST/Bandai/SMPL). '
         'Richtungskorrektur richtet BVH-Knochenrichtungen an DEF-Richtungen '
         'aus. Füße und Hals überspringen sie, weil die Topologien nicht '
         'zusammenpassen. Fehler hier sehen im Bild nach „unsauberer '
         'Animation" aus, nicht nach einem Fehler.'),
     'fragen': [
         'Wo kippt die Quaternionen-Kette, ohne dass es auffällt? Achte auf '
         'Vorzeichen, Reihenfolge der Multiplikation und den doppelten '
         'Überzug (q und -q sind dieselbe Drehung).',
         'parse_bvh: Welche gültige BVH-Datei wird falsch gelesen? '
         '(Kanal-Reihenfolge, Euler-Konvention, End Sites, Frame-Zeit)',
         'Die Höhenskalierung nimmt die Ausdehnung in Y aus Frame 0. Wann '
         'ist das falsch?',
         'Was passiert bei Knochen, die in der Zuordnung fehlen?',
     ]},
    {'slug': 'geometrie', 'name': 'Geometrie & Unterteilung',
     'dateien': ['HumanBody/humanbody_core/catmull_clark.py'],
     'hinweis': (
         'Catmull-Clark-Unterteilung des Körpernetzes (18k Basis-Vertices → '
         '70k). WICHTIG: Blenders ausgewertetes Netz hat eine ANDERE '
         'Vertex-Reihenfolge als diese Implementierung — Skin-Weights werden '
         'deshalb auf dem Basisnetz exportiert und hier durchgereicht. Eine '
         'Abweichung in der Reihenfolge zerstört die Gewichte, fällt in der '
         'Ruhepose aber nicht auf (dort sind alle Knochenmatrizen die '
         'Einheitsmatrix).'),
     'fragen': [
         'Wo weicht diese Implementierung von der Catmull-Clark-Definition '
         'ab (Randkanten, Ecken, Nicht-Vierecke, Vertices mit Valenz 3)?',
         'Ist die Reihenfolge der erzeugten Vertices deterministisch — auch '
         'bei anderer Reihenfolge der Eingabeflächen?',
         'Wo ist die Laufzeit quadratisch, wo werden Kanten doppelt gesucht?',
     ]},
    {'slug': 'morph', 'name': 'Morph-System',
     # `morphing` ist seit dem 31.08.2026 ein PAKET, keine Datei mehr:
     # 522 Zeilen, elf Klassen. Der Importpfad blieb gleich, der
     # Dateipfad nicht — ein Verzeichnis meint alle Quelldateien darin.
     'dateien': ['HumanBody/humanbody_core/morphing/',
                 'HumanBody/humanbody_core/character.py'],
     'hinweis': (
         'Morph-Ziele (.npy) verformen das Basisnetz über Regler. '
         'Voll-Morphs betreffen alle Vertices, Teil-Morphs nur einen Index-'
         'Ausschnitt. MinMax-Morphs mischen zwei Richtungen um eine Mitte. '
         'Die .npy-Dateien sind unersetzliche Produktivdaten.'),
     'fragen': [
         'Wo kann ein Regler die Basis-Vertices dauerhaft verändern statt '
         'eine Kopie zu verformen? (In-place-Addition, geteilte Arrays)',
         'Was passiert bei Reglerwerten ausserhalb des Bereichs, bei NaN, '
         'bei float32 gegen float64?',
         'Ist die Reihenfolge der angewandten Morphs bedeutsam — und ist sie '
         'stabil?',
     ]},
    {'slug': 'stoff', 'name': 'Stoff- und Kleidungsgeometrie',
     'dateien': ['HumanBody/humanbody_core/cloth.py'],
     'hinweis': (
         'Erzeugt Kleidungsnetze aus dem Körpernetz: Ringe um den Körper '
         'messen, Ringe zu Flächen verbrücken, doppelte Vertices verschmelzen '
         '(Union-Find), Laplace-glätten, aus dem Körper herausdrücken. Alles '
         'reine NumPy-Geometrie ohne Physik. Y ist oben, Maße in Metern, '
         'Vierecke (Quads) als Flächen. Fehler zeigen sich als Löcher, '
         'umgeklappte Normalen oder Kleidung, die im Körper steckt — nicht '
         'als Absturz.'),
     'fragen': [
         '_remove_doubles nutzt Union-Find mit einem Abstand von 8 mm. Wo '
         'verschmilzt es Vertices, die getrennt bleiben müssten, und wo '
         'hängt das von der Reihenfolge der Eingabe ab?',
         '_laplacian_smooth: Was passiert an Rändern und an Vertices ohne '
         'Nachbarn? Wird über die Iterationen der ursprüngliche oder der '
         'schon geglättete Stand gelesen — und ist das gewollt?',
         '_push_outside_body prüft gegen Körper-Vertices. Wann drückt es in '
         'den Körper hinein statt heraus (dünne Stellen, Achseln, zwischen '
         'den Beinen)?',
         '_compute_normals: Wo kann die Orientierung umklappen, ohne dass es '
         'in der Ruhelage auffällt?',
     ]},
    {'slug': 'pose', 'name': 'Pose-System und Koordinaten-Umrechnung',
     'dateien': ['HumanBody/humanbody_core/pose/pose_data.py',
                 'HumanBody/humanbody_core/coordinates.py'],
     'hinweis': (
         'Lädt Posen aus CharMorph und MB-Lab (JSON: '
         '{Kontrollknochen: [w,x,y,z]}) und rechnet sie auf das DEF-Skelett '
         'um. Drei Konventionen treffen aufeinander: Blender [w,x,y,z] mit Z '
         'oben, Three.js [x,y,z,w] mit Y oben, und die DEF-Knochen mit eigenen '
         'lokalen Achsen. Bekannte Grenze: Ruheposen (T-Pose) sitzen, komplexe '
         'Posen zeigen Rig/Netz-Versatz, weil CharMorph/MB-Lab andere lokale '
         'Knochenachsen benutzen als Rigify.\n'
         'ACHTUNG, KORREKTUR (13.08.2026): Ein früherer Hinweis hier nannte '
         'einen "leg_multiplier=2.5". Den gibt es im Code NICHT (mehr) — die '
         'Notiz stammte aus einer veralteten Projektaufzeichnung. Ein '
         'Hinweistext, der Code beschreibt, den es nicht gibt, erzeugt '
         'Befunde zu Code, den es nicht gibt.'),
     'fragen': [
         'to_threejs bildet [w,x,y,z] auf [x,z,-y,w] ab. Ist diese Abbildung '
         'für eine DREHUNG korrekt, oder nur für einen Punkt? Prüfe an einer '
         'konkreten Drehung um 90 Grad, und achte auf die Händigkeit.',
         'Wo wird ein Faktor auf eine Quaternion angewandt, statt auf einen '
         'Winkel (leg_multiplier)? Was ist daran mathematisch falsch, und '
         'wann fällt es nicht auf?',
         'Was passiert mit Kontrollknochen, die in CONTROL_TO_DEF fehlen, und '
         'mit Posen, die nur einen Teil der Knochen setzen?',
     ]},
    {'slug': 'skelett', 'name': 'Skelett-Klasse und IK',
     'dateien': ['HumanBody/humanbody_core/skeleton/skeleton.py',
                 'HumanBody/humanbody_core/skeleton/skeleton_geometry.py'],
     'hinweis': (
         'Vorgeschichte, die du wissen musst: In dieser Datei standen ~300 '
         'Zeilen der Klasse monatelang UNERREICHBAR, weil eine nicht '
         'eingerückte Funktion mitten in der Klasse den Klassenkörper beendet '
         'hat. Python meldet das nicht. Repariert am 12.08.2026 mit einem '
         'Golden-Master-Vergleich (Retarget-Ausgabe vorher/nachher identisch). '
         'Genau diese Sorte Fehler suche ich hier: Code, der aussieht als '
         'liefe er, und es nicht tut.'),
     'fragen': [
         'Gibt es weitere Stellen, die nie ausgeführt werden — unerreichbare '
         'Zweige, Methoden die von niemandem gerufen werden, Rückgaben nach '
         'einem return?',
         'Die IK fängt jetzt KeyError statt allem. Welcher Fehler wird dadurch '
         'sichtbar, den vorher der nackte except geschluckt hat — und ist die '
         'Behandlung danach richtig?',
         'Wo wird ein veränderbarer Zustand über Aufrufe hinweg gehalten, der '
         'zwischen zwei Skeletten geteilt werden kann?',
     ]},
    {'slug': 'zuordnung', 'name': 'Formaterkennung und Knochen-Zuordnung',
     # `formats` ist seit dem 31.08.2026 ein PAKET, keine Datei mehr: acht
     # Formate zu 504 Zeilen lagen in einer. Der Importpfad blieb gleich,
     # der Dateipfad nicht.
     'dateien': ['HumanBody/humanbody_core/skeleton/formats/',
                 'HumanBody/humanbody_core/skeleton/retarget_mappings.py',
                 'HumanBody/humanbody_core/skeleton/mapping.py'],
     'hinweis': (
         'Erkennt am Knochennamen, aus welcher Quelle eine BVH-Datei kommt '
         '(CMU, Mixamo, MocapNET, OpenPose, Bandai, SMPL, AIST) und wählt die '
         'passende Zuordnungstabelle BVH-Knochen → DEF-Knochen (Rigify, 176 '
         'Knochen). EIN falscher Tabelleneintrag oder eine Erkennung, die auf '
         'das falsche Format fällt, ruiniert die ganze Animation — sichtbar '
         'als „verdrehte Figur", nicht als Fehlermeldung. Genau deshalb dieser '
         'Bereich: Hier ist ein Fehler billig zu machen und teuer zu finden.'),
     'fragen': [
         'Die Formaterkennung arbeitet mit Namensmerkmalen. Welche echte '
         'BVH-Datei fällt auf das falsche Format, und was ist die '
         'Reihenfolge-Abhängigkeit der Prüfungen?',
         'Gibt es in den Tabellen doppelte Ziele (zwei BVH-Knochen auf '
         'denselben DEF-Knochen) oder Ziele, die es im DEF-Skelett nicht gibt? '
         'Nenne sie konkret, das ist prüfbar.',
         'Wo unterscheiden sich links/rechts-Suffixe zwischen den Formaten, und '
         'wo könnte eine Seite vertauscht sein?',
         'Was passiert, wenn kein Format erkannt wird?',
     ]},
    {'slug': 'hb_mesh',
     'name': 'Kern: Netzdaten, Voreinstellungen, Gesichts-Blendshapes',
     'dateien': ['HumanBody/humanbody_core/mesh.py',
                 'HumanBody/humanbody_core/skeleton/presets.py',
                 'HumanBody/humanbody_core/skeleton/face_blendshapes.py'],
     'hinweis': ('mesh.py laedt das Basisnetz (Vertices, Vierecke, UVs, '
                 'Material-Gruppen) aus .npy/.npz — unersetzliche Produktivdaten, '
                 'read-only zu behandeln. presets.py haelt Skelett-Voreinstellungen, '
                 'face_blendshapes bildet Gesichtsausdruecke auf Knochen ab.'),
     'fragen': [
         'Wo wird ein geladenes Array veraendert oder ohne Schreibschutz '
         'weitergegeben?',
         'Was passiert bei einer fehlenden oder halb geschriebenen Datendatei — klare '
         'Meldung oder spaeterer Folgefehler?',
         'Werden Datentyp und Form der geladenen Daten geprueft, bevor damit gerechnet '
         'wird?',
     ]},
]
