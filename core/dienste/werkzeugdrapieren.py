# -*- coding: utf-8 -*-
"""Werkzeugdrapieren — Reiter „Tools" der Seite Architektur 2D3D, Gruppe T2: Drapieren und Haar-Simulation, nur Wahl und Aufruf.

Die Interna des Stoffsolvers (Federn, Kollision, Felder, Warp) und die Schleife über Blender als Ganzes gehören zu T3;
hier steht, wie ein Rezept den Motor wählt und was der Aufruf kostet. Reine Daten (Schema: `ProjektTemp/_wegwerf/
stoff_ausbau/AUFTRAG_TOOLS.md`); gelesen von `Architektur2d3dwerkzeuge`.
"""

__all__ = ['Werkzeugdrapieren']


class Werkzeugdrapieren:
    G = 'Genesis9/'
    D = 'HumanBodyWeb/core/dienste/'

    KENNUNG = 'drapieren'
    TITEL = 'Drapieren und Haar-Simulation (Newton, Stoffsolver, Blender)'
    EINLEITUNG = (
        'Ein Stück „fällt“ einmal durch eine Stoffsimulation gegen die Grundfigur; das Ergebnis ist ein Morph '
        '<kennung>.eigen.drapiert (in einer Runde drapiert_<auftrag>), linear stellbar 0…1 — Netz, UV und Textur bleiben. '
        'Drei Motoren hinter derselben Rezeptzeile m.kleid_drapieren(…, motor=…): newton (Vorgabe, eigener GPU-Löser), '
        'stoffsolver (Blenders Cloth als Warp-Löser auf der GPU) und blender (nur nach Ansage von Edgar). Dieselbe Wahl '
        'gilt für das Haar: haar_dynamik (Stoffsolver auf Strähnen) und haar_knoten (Blenders Hair-Nodes). Reihenfolge: '
        '1. das Stück anziehen und passend formen (Gruppen „Kleider anziehen …“, „Kleider formen“), 2. drapieren, 3. den '
        'Morph mit morph_wert nachstellen. Alle Aufrufe hier brauchen die Runde (Rezeptumgebung mit den Arbeitern) oder '
        'eine selbst gebaute Umgebung — siehe die Zeile „Drapierer ohne Runde einhängen“. Die Automatik ruft nur newton '
        '(IterationKleider.drapieren) und rechnet kein Haar (Stoffsolver/README.md).')

    # (Werkzeug, Wofür, Art, Aufruf, Klassen, Hinweis)
    ZEILEN = [
        ('Wahl des Motors',
         'Entscheidungshilfe: welcher Motor für welchen Fall, und wer ihn wählen darf.',
         'regel',
         'Kein Aufruf. newton = Vorgabe; stoffsolver = wenn Druck (Ausgebeultheit) gebraucht wird und eine CUDA-GPU frei ist; '
         'blender und haar_knoten NUR nach ausdrücklicher Ansage von Edgar.',
         [(G + 'rezeptumgebung.py', 'Rezeptumgebung'), (G + 'modellform.py', 'ModellFormMixin')],
         'newton kann keinen Druck (nur Log-Hinweis, Kleiddrapierung.drapieren). stoffsolver rechnet dasselbe wie Blender '
         'auf der GPU, braucht eine CUDA-GPU und lehnt sonst ab (rechner „warp“ = Gerät oder Fehler, Stoffsolver/README.md '
         'Abschnitt „Benutzung“; Stoffsolver/stoffsimulation.py); auf dem Host (NumPy) brauchte die Hose 462 s gegen 9 s bei '
         'Blender (README, 02.10.2026). blender ist die Referenz, kostet je Aufruf einen Prozessstart und ist die '
         'Schleife, die die Seite nur nach Ansage zulässt. Blender darf nur über EINE Klasse laufen '
         '(Engine2d3dKleiderblender, Test BlenderNurUeberEinenArbeiterTest; engine2d3dkleider.md, 30.09.2026). Edgar '
         '(30.09.2026): „die kleiderphysik war noch relativ schlecht“ — darum ist das Drapieren ein Regler 0…1 mit Messung '
         'im Steckbrief, kein Zwang.'),

        ('Drapieren mit Newton (Vorgabe)',
         'Lässt ein Stück einmal mit dem eigenen GPU-Stofflöser (Newton Style3D) gegen die Grundfigur fallen: Falten, Fall.',
         'rezept',
         "m.kleid_drapieren('g9_base_shirt', bilder=24, motor='newton')",
         [(G + 'modellform.py', 'ModellFormMixin'), (G + 'rezeptumgebung.py', 'Rezeptumgebung'),
          (D + 'kleiddrapierung.py', 'Kleiddrapierung'), (G + 'kleidmorphe.py', 'G9kleidmorphe')],
         'Braucht die Runde (Rezeptumgebung.drapierer[newton]), sonst ValueError „braucht den Drapierer“. Das obere Band des '
         'Stücks (fest_oben 0,08 der Höhe: Bund, Schultern) bleibt fest, Schwerkraft ohne Wind, bilder Bilder bei 24 fps; '
         'Y oben ↔ Z oben wird umgerechnet; der Löser läuft als Prozess in EFFEKTE_NEWTON_PYTHON (Zeitgrenze 900 s). '
         'Gemessen 30.09.2026 (ortsmorphe.md, Base Shirt, 24 Bilder): 142 s (Warp-Kernel erstmals übersetzt; 590 ms je '
         'Bild), 7.552 Punkte, Saumband 22 mm gefallen, in der Haut 27 → 21, Kantendehnung p99 1,45. Grenze: Qualität „noch '
         'relativ schlecht“ (Edgar, 30.09.2026), Ergebnis nur als stellbarer Morph. Auf GarmentCode-Stücken gemessen besser '
         'als Blender Cloth (Knick 4–8° statt 35–47°, Docstring Kleiddrapierung, effekte.md).'),

        ('Drapieren mit dem Stoffsolver (GPU)',
         'Dieselbe Rechnung wie Blender Cloth (Federn, Winkelbiegung, Innendruck, Kollision) auf der GPU; kann Druck.',
         'rezept',
         "m.kleid_drapieren('g9_base_shirt', bilder=24, druck=0.0, motor='stoffsolver')",
         [(G + 'modellform.py', 'ModellFormMixin'), (G + 'rezeptumgebung.py', 'Rezeptumgebung'),
          (D + 'stoffsolverdrapierung.py', 'Stoffsolverdrapierung'), (G + 'kleidmorphe.py', 'G9kleidmorphe')],
         'Prozess in python14 über Stoffsolver/werkzeug/stoff_lauf.py (settings.STOFFSOLVER_SKRIPT), derselbe Auftrag wie bei '
         'Blender; Zeitgrenze 900 s; ohne CUDA-GPU RuntimeError („der Gerätemotor braucht eine CUDA-GPU“). Schwerkraft −Y, '
         'oberes Band fest wie bei Newton. Gemessen 02.10.2026 (Stoffsolver/README.md, Messungen, RTX PRO 4500): Oberteil '
         '17.552 Punkte, 12 Bilder 2,0 s gegen 26,7 s Blender, 24 Bilder 2,3 s gegen 55,0 s; Ergebnis im Mittel 1,8 mm '
         '(12 Bilder) bzw. 2,7 mm (24 Bilder) von Blender, bei 2,3 mm Blender-Eigenrauschen. Die Solver-Interna (Federn, '
         'Material, Kollision) beschreibt die Gruppe Stoffsolver (T3).'),

        ('Drapieren mit Blender (nur nach Ansage)',
         'Blender Cloth gegen die Grundfigur, kann Druck (Pressure) — die Referenz, wenn der Stoffsolver nicht geht.',
         'rezept',
         "m.kleid_drapieren('g9_base_shirt', bilder=24, druck=0.0, motor='blender')",
         [(G + 'modellform.py', 'ModellFormMixin'), (G + 'rezeptumgebung.py', 'Rezeptumgebung'),
          (D + 'engine2d3dkleiderblender.py', 'Engine2d3dKleiderblender'), (G + 'kleidmorphe.py', 'G9kleidmorphe')],
         'NUR nach ausdrücklicher Ansage von Edgar. Ein Blender-Prozess je Aufruf (Blender 5.2.2 portable, '
         'settings.BLENDER_EXE; Start 4–9 s, die Rechnung Sekunden — Docstring Engine2d3dKleiderblender), Zeitgrenze 900 s; '
         'Netze über from_pydata, kein Importer (sonst geht die Punktreihenfolge verloren). Gemessen 02.10.2026 '
         '(Stoffsolver/README.md): Oberteil 12 Bilder 26,7 s, 24 Bilder 55,0 s als ganzer Prozess. Seit 02.10.2026 fällt '
         'Blender entlang −Y und hält das obere Band fest (fest_oben 0,08 wie Newton); alte Morphe eigen.drapiert aus '
         'Blender-Läufen DAVOR sind mit falscher Schwerkraft gerechnet (nach −Z; 533 mm Weg in 11 Bildern, nichts '
         'angeheftet) und müssen neu gerechnet werden (ortsmorphe.md, 02.10.2026).'),

        ('Drapierer ohne Runde einhängen',
         'Setzt einem ModellMitKleidern die Arbeiter selbst in die Umgebung, wenn kein Auftrag läuft (Probe, Skript).',
         'python',
         "# im Django-Prozess (z. B. manage.py shell), weil die Klassen settings.* lesen\n"
         "from pathlib import Path\n"
         "from Genesis9.rezeptumgebung import Rezeptumgebung\n"
         "from core.dienste.stoffsolverdrapierung import Stoffsolverdrapierung\n"
         "m.umgebung = Rezeptumgebung(drapierer={'stoffsolver': Stoffsolverdrapierung(Path('A:/3DTools/ProjektTemp/_wegwerf/stoff'))})\n"
         "m.kleid_drapieren('g9_base_shirt', bilder=24, motor='stoffsolver')",
         [(G + 'rezeptumgebung.py', 'Rezeptumgebung'), (D + 'begutachtungswerkzeug.py', 'Begutachtungswerkzeug'),
          (D + 'stoffsolverdrapierung.py', 'Stoffsolverdrapierung')],
         'Nur gelesen, nicht ausprobiert (Rezeptumgebung.drapierung gibt self.drapierer[motor] zurück; kleid_drapieren ruft '
         'drapierer.drapieren(kennung, bilder, druck, name=…) und liest drapierer.NAME). Die Runde baut dieselben Arbeiter '
         'mit Begutachtungswerkzeug.drapierer(): newton → Kleiddrapierung(arbeit/stoff), blender → '
         'Engine2d3dKleiderblender(arbeit/blender), stoffsolver → Stoffsolverdrapierung(arbeit/stoffsolver). Der Arbeitsordner '
         'gehört ins Projekt (ProjektTemp/_wegwerf/…), nie in System-Temp. Rechnen darf nur, wer die GPU frei weiß: eine '
         'Blender-Messreihe oder ein TRELLIS-Lauf belegt sie sonst.'),

        ('Haar-Dynamik: Strähnen fallen lassen (Stoffsolver)',
         'Lässt das STRANGHAAR einer Frisur einige Bilder fallen: Wurzeln fest, Körper als Kollider; Ergebnis ist ein Morph.',
         'rezept',
         "m.haar_dynamik('g9_base_dforce_pixie_hair', bilder=24, name='dynamik', wert=1.0, material='vorgabe', mindestabstand_mm=2.0)",
         [(G + 'modellhaar.py', 'ModellHaarMixin'), (G + 'rezeptumgebung.py', 'Rezeptumgebung'),
          (D + 'haardynamik.py', 'Haardynamik'), (D + 'haarstraehnen.py', 'Haarstraehnen'),
          (G + 'kleidmorphe.py', 'G9kleidmorphe')],
         'Nur von Hand: die Automatik schreibt die Zeile nie, die Prüf-KI darf sie nicht (Begutachtungskritik.VERBOTEN). '
         'Stranghaar (Pixie g9_base_dforce_pixie_hair, Hime Cut dforce_mk_hime_cut_hair, Viola hs_viola_hair_g9); Kartenhaar '
         'ist ein ValueError (haar_trim u. a. nehmen). Braucht eine CUDA-GPU (Haarkollision gibt es nur dort — sonst '
         'RuntimeError, nie still durch den Kopf). material = Preset des Solvers (vorgabe|baumwolle|seide|jeans|leder|'
         'gummi); weitere Argumente (kontinuum, biegung_zufall, zufall_seed, abstand) gehen unverändert an die Simulation. '
         'Mindestabstand 2 mm statt Blenders 31 mm gemessen (Pixie 0 eingedrungene Punkte bei 1/2/3 mm, Hime Cut 43 bei 1 mm, '
         '0 ab 1,5 mm). Zeiten (Probe an der Bibliothek, NICHT in der Pipeline, warmer Warp-Cache, 24 Bilder, 02.10.2026, '
         'ortsmorphe.md): Pixie 5,7 s (erster Lauf im Prozess 8,8 s), Hime Cut 4,4 s (7,5 s). Offener Fehler im Solver: ab '
         'Reichweite abstand + dicke 3,4 mm stürzt der Gerätelauf an Hime Cut ab (CUDA 700). Strähnen mit sehr kurzem '
         'Segment friert Blenders Regel ein (Pixie 65 %, Hime Cut 20 %). Nicht geprüft: wie das Haar danach im Render aussieht.'),

        ('Haar-Knoten: Blenders Hair-Nodes auf Stranghaar (nur nach Ansage)',
         'Rechnet eine von Blenders Hair-Node-Gruppen (Trim, Clump, Curl, Frizz, Shrinkwrap, Duplicate …) auf das Stranghaar.',
         'rezept',
         "m.haar_knoten('g9_base_dforce_pixie_hair', 'kuerzer', 'trim', ort=None, wert=1.0, length_factor=0.5)",
         [(G + 'modellhaar.py', 'ModellHaarMixin'), (G + 'rezeptumgebung.py', 'Rezeptumgebung'),
          (D + 'engine2d3dkleiderblender.py', 'Engine2d3dKleiderblender'), (D + 'haarknotenauftrag.py', 'Haarknotenauftrag'),
          (G + 'haarzusatz.py', 'G9haarzusatz'), (G + 'kleidmorphe.py', 'G9kleidmorphe')],
         'NUR nach ausdrücklicher Ansage von Edgar (Blender). knoten ∈ trim, clump, curl, frizz, noise, straighten, roll, '
         'smooth, braid, displace, rotate, shrinkwrap, attach, duplicate, interpolate, generate (Engine2d3dKleiderblender.'
         'KNOTEN); parameter heißen wie die Sockets (length_factor → „Length Factor“); ort wirkt als Mask je Punkt (in Python '
         'je Punkt angelegt, sonst wirkt Mask je Strähne). Zwei Fallen gemessen am Pixie (01.10.2026): Trim „Replace Length“ '
         'steht in Blender auf An und setzt jede Strähne auf Length (500 mm Weg) — der Code schaltet es aus und nimmt Length '
         'Factor 0,5; Blenders „Amount“ 10 machte 2,6 Mio. Punkte, Vorgabe jetzt 2. duplicate/interpolate/generate legen '
         'Zusatzsträhnen an (Regler str.<name>); attach, interpolate und generate brauchen die Kopfhaut mit eindeutiger UV '
         '(G9kopfhaut). Zeiten: Pixie 236.136 Punkte 2,4 s in Blender, 6 s mit Start (ortsmorphe.md); je 5–6 s mit Start für '
         'Attach/Interpolate/Generate. Kartenhaar: haar_trim, haar_clump u. a. (Gruppe „Haar formen“). Der Docstring von '
         'haar_knoten (modellhaar.py) nennt interpolate/generate noch „ohne Kopfhaut-Bindung nichts“ — seit der '
         'Kopfhaut-Bindung (01.10.2026) stehen sie in KNOTEN und laufen.'),
    ]

    # Klassenmodell: (von, 'ruft', nach, womit)
    BEZIEHUNGEN = [
        ('ModellFormMixin', 'ruft', 'Rezeptumgebung', 'Rezeptumgebung.drapierung(motor): der Drapierer zum Motor, sonst ValueError'),
        ('ModellHaarMixin', 'ruft', 'Rezeptumgebung', 'Rezeptumgebung.haardynamik() und blender(): die Arbeiter der Runde'),
        ('Begutachtungswerkzeug', 'ruft', 'Kleiddrapierung', 'Kleiddrapierung(arbeit/stoff): drapierer() baut den Motor newton'),
        ('Begutachtungswerkzeug', 'ruft', 'Stoffsolverdrapierung', 'Stoffsolverdrapierung(arbeit/stoffsolver): drapierer()'),
        ('Begutachtungswerkzeug', 'ruft', 'Engine2d3dKleiderblender', 'Engine2d3dKleiderblender(arbeit/blender): drapierer()'),
        ('Begutachtungswerkzeug', 'ruft', 'Haardynamik', 'Haardynamik(arbeit/haardynamik): haardynamik() für haar_dynamik'),
        ('Kleiddrapierung', 'ruft', 'G9kleidmorphe', 'G9kleidmorphe.kaefige(), koerper(), ablegen(): Käfig lesen, Delta als Morph'),
        ('Stoffsolverdrapierung', 'ruft', 'G9kleidmorphe', 'G9kleidmorphe.kaefige(), koerper(), ablegen()'),
        ('Stoffsolverdrapierung', 'ruft', 'Engine2d3dKleiderblender', 'Engine2d3dKleiderblender._dreiecke() und FEST_OBEN'),
        ('Engine2d3dKleiderblender', 'ruft', 'G9kleidmorphe', 'G9kleidmorphe.kaefige(), ablegen(): drapieren() und haar()'),
        ('Engine2d3dKleiderblender', 'ruft', 'Haarknotenauftrag', 'Haarknotenauftrag.schreiben(), delta(), zusatz(): haar()'),
        ('Engine2d3dKleiderblender', 'ruft', 'G9haarzusatz', 'G9haarzusatz.ketten() und ablegen(): Strähnen, Zusatzsträhnen'),
        ('Haardynamik', 'ruft', 'Haarstraehnen', 'Haarstraehnen(punkte, ketten, haut): Strähnen, Wurzel zuerst; delta()'),
        ('Haardynamik', 'ruft', 'G9kleidmorphe', 'G9kleidmorphe.kaefige(), koerper(), ablegen(): Morph <sorte>.eigen.<name>'),
        ('Haardynamik', 'ruft', 'G9haarzusatz', 'G9haarzusatz.ketten(): die Ketten eines Strang-Teils'),
        ('ModellHaarMixin', 'ruft', 'G9haarzusatz', 'G9haarzusatz.PRAEFIX: der Reglername str.<name> bei Zusatzsträhnen'),
    ]
