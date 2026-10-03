# -*- coding: utf-8 -*-
"""Blendervergleichkleider — Abschnitt „Kleidung: Schnitt, Passform, Stoff, Kollision“ der Tabelle „Wie liefe das mit Blender“ (03.10.2026).

Schema und Stände: `Architektur2d3dblender`. Belege „Blender hat das“: `ProjektTemp/_wegwerf/tools_seite/t5/ergebnis_introspektion*.json`
(Blender 5.2.2 LTS, Werksstart, nur Namen). Belege „gemessen“: `Stoffsolver/README.md`, Abschnitt „Messungen“, und die Werkzeuge `Stoffsolver/werkzeug/vergleich_*.py`.
"""

__all__ = ['Blendervergleichkleider']


class Blendervergleichkleider:
    KENNUNG = 'blender-kleider'
    TITEL = 'Kleidung: Schnitt, Passform, Stoff und Kollision'
    EINLEITUNG = ('Wie Blender Kleidung erzeugt, anpasst und simuliert — und wo das Projekt Blender wirklich aufruft: Drapieren mit Blenders Cloth '
                  '(`motor=\'blender\'`, nur nach Ansage) und „Kleid + Wind“. Der Stoffsolver ist Blenders Cloth als Python/Warp-Nachbau und gegen '
                  'Blender 5.2.2 gemessen; die Zeiten stehen mit Quelle in der Zeile.')
    # (Aufgabe, lokales Werkzeug, lokaler Aufruf, lokale Klassen [(Datei, Klasse)], Blender-Werkzeug, Blender-Aufruf, Blender-Stand, Unterschied)
    ZEILEN = [
        ('Kleidung aus Schnittmuster erzeugen',
         'GarmentCode-Schnitt → drapiert → Genesis-Stück (`kleid_schnitt`)',
         "m.kleid_schnitt('oberteil', titel='Probe', farbe='#808080')   # ≈ 25 s; vorlage oberteil|hose|shorts|rock|kleid|anzug|unterwaesche|schuh",
         [('Genesis9/modellform.py', 'ModellFormMixin'), ('Genesis9/gceigenes.py', 'G9gceigenes'),
          ('Assets/GarmentCode/katalog.py', 'Katalog'), ('Assets/GarmentCode/drapierung.py', 'Drapierung')],
         'Im Kern kein Schnittmuster-Werkzeug; Add-ons im Profil: Bystedts Cloth Builder („Addon for cloth creation and simulation“), MakeClothes',
         "— (Oberflächen der Add-ons); Nähte im Kern: stoff.settings.use_sewing_springs = True   # lose Kanten ziehen zusammen",
         'addon',
         'Die Namenssuche „sewing“, „garment“ und „pattern“ über 2.499 Operatoren findet nur `object.select_pattern` (Auswahl nach Namensmuster; '
         '`ergebnis_introspektion.json`). Im Nutzerprofil liegen Bystedts Cloth Builder 1.0.1 und MakeClothes 2.3.1 (`bl_info`), beide nicht Teil von Blender; '
         'ein „Garment Tool“ (Gumroad) und ClothingFit nennt das Konzept 30.09.2026 §3.4 (nicht installiert, nicht geprüft). Das Projekt baut Schnitte mit '
         'GarmentCode (Warp-Simulation in `python10_Garment`) und legt das Ergebnis als Genesis-Stück ab: ≈ 25 s je Stück, 171 von 171 Katalogstücken gebaut '
         '(`genesis9-garderobe.md`, 25.09.2026). Das eigene Blender-Add-on HumanBodyBlender übernimmt Muster aus Bystedts Cloth Builder (`cloth_builder.py`, '
         'Kopfkommentar) und gehört nicht zur 2D3D-Pipeline.'),

        ('Kleidung modellieren (Mesh, Modifier)',
         'Kostümmodell des BlenderModel-Wegs: Teile aus Querschnittsringen (Rohr), etwa 60 Maße als Wertesatz, in Blender gebaut und gerendert',
         "blender -b --factory-startup --python effekte/blender/kostuembau.py -- --auftrag <auftrag.json>   # BlenderModel, nicht 2D3D Kleider; Dienst über Postfach-Ordner",
         [('HumanBodyWeb/effekte/blender/kostuembau.py', 'Kostuembau'), ('HumanBodyWeb/effekte/blender/kostuem/rohr.py', 'Rohr'),
          ('HumanBodyWeb/core/dienste/kostuemarbeiter.py', 'Kostuemarbeiter')],
         'Mesh-Aufbau per Skript (`from_pydata`, Ringe zu Vierecken) mit den Modifiern SUBSURF und SOLIDIFY (Stoffdicke); für prozedurale Formen der Modifier NODES (Geometry Nodes)',
         "obj.modifiers.new('Glaetten', 'SUBSURF'); obj.modifiers.new('Dicke', 'SOLIDIFY')   # wie effekte/blender/kostuem/rohr.py",
         'genutzt',
         'Der BlenderModel-Weg (ab 29.09.2026) baut das Kostüm in Blender aus Teilen: je Stück eine Folge von Querschnittsringen (Mitte, Halbbreite, Halbtiefe), am '
         'Ende ein Objekt mit Material, SUBSURF und SOLIDIFY (`kostuem/rohr.py`); die Maße sind ein Wertesatz, den ein Optimierer und die Prüf-KI drehen '
         '(`blendermodell.md`). Gemessen: Blender starten und Figur laden 4–9 s, danach ein Kandidat 0,6–0,8 s (`kostuembau.py`, 30.09.2026). Grenze: Das Modell '
         'aus Teilen bleibt blockig, Ärmel als Kästen, Haar und Bart als Platten (`blendermodell.md`). 2D3D Kleider zieht dagegen fertige Stücke an (Daz, GarmentCode) '
         'und formt sie mit Eigenmorphen. Geometry Nodes ruft das Projekt nur für Haar auf (`haarknoten.py`), nicht für Kleidung.'),

        ('Kleiderbibliothek',
         'Daz-Garderobe, MakeHuman- und GarmentCode-Stücke als Genesis-Assets; „Kleidung – Generisch“ mischt sie',
         "m.kleid_nur('g9_base_shirt', 'angie_jeans')   # Kennungen aus G9garderobe.liste(); m.kleid_anteil(kennung, 0.5) mischt",
         [('Genesis9/garderobe.py', 'G9garderobe'), ('Genesis9/kleidgenerisch.py', 'G9kleidgenerisch')],
         'Keine im Kern; MPFB lädt `.mhclo`-Stücke aus der MakeHuman-Bibliothek und passt sie über Helfergeometrie an',
         "HumanService.add_mhclo_asset(mhclo_pfad, basemesh, subdiv_levels=0)   # MPFB, wie effekte/blender/effektfigur.py",
         'genutzt',
         'Add-on MPFB, wie in „Kleid + Wind“ (`effektfigur.py`). Im Kern fehlt eine Kleiderbibliothek: In den 15 Asset-Dateien von 5.2.2 (`assets/brushes`, '
         '`assets/nodes`) liegen keine Objekte (`ergebnis_introspektion.json`). Das Projekt führt 390 Stücke in „Kleidung – Generisch“ '
         '(165 MakeHuman, 172 GarmentCode, 53 Daz; `genesis9-garderobe.md`, 30.09.2026); gemischt wird über die Haut: In der Mischzone steht nur eine '
         'Fläche, ihr Versatz über der Haut ist der gewichtete Mittelwert beider Stücke.'),

        ('Passform: Länge, Weite, Umriss',
         'Passform-Regler Länge und Weite je Stück, Ringmaß und Umriss-Hülle (Eigenmorphe)',
         "m.passform(laenge_cm=-4, weite_cm=1.5)   # Länge ±20 cm, Weite −3…+6 cm; dazu m.kleid_ring(...) und m.kleid_huelle(...)",
         [('Genesis9/modellmitkleidern.py', 'ModellMitKleidern'), ('Genesis9/passform.py', 'G9passform'),
          ('Genesis9/kleidring.py', 'G9kleidring'), ('Genesis9/huellenmorph.py', 'G9huellenmorph'), ('Genesis9/kollision.py', 'G9kollision')],
         'Modifier SHRINKWRAP (Offset), SOLIDIFY (Dicke), SURFACE_DEFORM und MESH_DEFORM (Folgen), DATA_TRANSFER',
         "m = kleid.modifiers.new('Anlegen', 'SHRINKWRAP'); m.target = koerper; m.offset = 0.003",
         'vorhanden',
         'Alle Typen gibt es in 5.2.2 (Introspektion). Die Probe des Projekts (Konzept §6.1, Blender 5.0.1) legte eine Kugel mit 3 mm Offset auf 0,203 m '
         'Radius um ein Ziel von 0,20 m. Das Projekt passt ohne Blender an: `G9passform` verschiebt den Käfig entlang der Haut (Länge als Schnitt, nicht als '
         'Stauchung; Weite entlang der Hautnormale, nach innen höchstens bis 3 mm über die Haut, `genesis9-passform.md`), `G9kollision` hebt jedes Stück aus der '
         'Haut (Mindestabstand 3 mm). Shrinkwrap nach AUSSEN auf den Sichtkörper der Fotos (Hülle, Stärke 0,7) ist als Eigenmorph gebaut, nicht über Blender '
         '(`G9huellenmorph`, `ortsmorphe.md`).'),

        ('Stoffsimulation',
         'Stoffsolver: Blenders Cloth als Python/Warp-Löser (GPU), Motor „stoffsolver“',
         "m.kleid_drapieren('g9_base_shirt', bilder=24, motor='stoffsolver')   # Morph eigen.drapiert; Python: Drapierauftrag.rechnen(stueck_punkte, "
         "stueck_dreiecke, koerper_punkte, koerper_dreiecke, bilder=24)",
         [('HumanBodyWeb/core/dienste/stoffsolverdrapierung.py', 'Stoffsolverdrapierung'), ('Stoffsolver/drapierauftrag.py', 'Drapierauftrag'),
          ('Stoffsolver/stoffsimulation.py', 'Stoffsimulation'), ('Stoffsolver/warpmotor.py', 'WarpMotor')],
         'Modifier CLOTH (`settings`: Masse, Steifigkeiten, Quality, Druck, Nähfedern) mit COLLISION am Körper',
         "c = stueck.modifiers.new('Stoff', 'CLOTH'); c.settings.quality = 6; scene.frame_set(f)   # wie effekte/blender/engine2d3dkleider/drapieren.py",
         'gemessen',
         'Der Solver ist ein Nachbau aus dem Quelltext (Tag v5.2.2) und in echtem Blender 5.2.2 verglichen (`Stoffsolver/README.md`, „Messungen“, 02.10.2026). '
         'Abstand zu Blender im letzten Bild: Oberteil 12 Bilder 1,8 mm, 24 Bilder 2,7 mm (Blender gegen Blender 2,3 mm); Federn, Gruppen, Schrumpfen, '
         'Innenfedern, Nähte, Material, Druck und Presets gleich in etwa 100 Fällen (höchstens 0,003 mm). Die unangeheftete Hose ist chaotisch; mit 200 '
         'Blender- und 500 Solver-Läufen sind die Streuungen gleich (44,3 gegen 45,2 mm, `vergleich_streuung.py`). Zeit (vor dem Ausbau, 30 % Last durch '
         'andere Sitzungen): Oberteil 17.552 Punkte, 12 Bilder: Blender-Prozess 26,7 s, Solver-Prozess 2,0 s; Hose 3.123 Punkte: 10,1 s gegen 1,9 s. Nur mit '
         'CUDA-GPU — auf dem Host (NumPy) braucht die Hose 462 s.'),

        ('Drapieren mit Blender-Cloth',
         '`motor=\'blender\'` beim Drapieren: ein Blender-Prozess je Stück (nur nach Ansage von Edgar)',
         "m.kleid_drapieren('g9_base_shirt', bilder=24, druck=0.0, motor='blender')   # Standard ist Newton; Blender nur auf Ansage",
         [('HumanBodyWeb/core/dienste/engine2d3dkleiderblender.py', 'Engine2d3dKleiderblender'), ('Genesis9/modellform.py', 'ModellFormMixin')],
         'Cloth und Collision, wie oben — derselbe Auftrag wie beim Solver',
         "blender -b --factory-startup --python effekte/blender/engine2d3dkleider/drapieren.py -- --auftrag <auftrag.json>",
         'genutzt',
         'Der tatsächliche Blender-Weg der Pipeline: Netze über `from_pydata` (kein Importer, jeder Punkt kommt an seiner Nummer zurück), Körper als Kollider '
         '(Abstand 4 mm), Stück als Cloth (Masse 0,3, Zug/Druck 15, Scherung 5, Biegung 0,5, Luft 1), Schwerkraft entlang −Y, oberes Band (8 %) fest; Ergebnis '
         'als Morph `eigen.drapiert` (`drapieren.py`). Gemessen am 02.10.2026: Blenders Szene fällt ohne Setzen nach −Z (ein waagerechtes Tuch auf Y = 1 m '
         'fiel in 11 Bildern 533 mm nach −Z), nichts war angeheftet — die Hose rutschte 400 mm in 24 Bildern (`ortsmorphe.md`); Morphe aus Läufen davor sind mit '
         'falscher Schwerkraft gerechnet. Auf denselben Daten war Blender Cloth mit Baumwoll-Vorgabe schlechter als Newton (Knick 35–47°, Rock über der Hüfte, '
         '`effekte.md`, 12.09.2026) — Newton bleibt die Vorgabe.'),

        ('Kollision',
         'Körperkollision des Stoffsolvers (Dreieck gegen Dreieck, mehrere und bewegte Körper)',
         "Drapierauftrag.rechnen(stueck_punkte, stueck_dreiecke, koerper_punkte, koerper_dreiecke, abstand=0.004, dicke=0.004, selbstabstand=0.003)",
         [('Stoffsolver/kollisionsablauf.py', 'Kollisionsablauf'), ('Stoffsolver/kollisionseinstellungen.py', 'Kollisionseinstellungen'),
          ('Stoffsolver/koerperantwort.py', 'Koerperantwort')],
         'Modifier COLLISION am Körper (thickness_outer, damping, cloth_friction) und Cloth-Kollision (distance_min, use_self_collision, self_distance_min)',
         "koerper.modifiers.new('Kollision', 'COLLISION').settings.thickness_outer = 0.004; stoff.collision_settings.use_self_collision = True",
         'gemessen',
         'Anheften, Wind, Kollision und bewegter Körper: gleich, 0,0001 bis 0,04 mm; die Kollision liegt im Rauschen von Blender (`vergleich_pins.py`, '
         '`vergleich_kollision.py`, `vergleich_ensemble.py`; `Stoffsolver/README.md`, 02.10.2026). Offen: `impulse_clamp` 0,04 und `self_impulse_clamp` 0,02 '
         '(Blender selbst chaotisch) und Fünfeck-Szenen (README, Stand 03.10.2026). Der Nebenzweig `kollision=\'schnell\'` (nächster Hautpunkt) ist eine '
         'Näherung, nicht Blenders Verfahren. Die Pipeline ruft Blenders COLLISION an zwei Stellen: `drapieren.py` (Abstand 4 mm) und „Kleid + Wind“ '
         '(`effekte/blender/stoffsimulation.py`).'),

        ('Nähte',
         'Nähte im Stoffsolver: Punktpaare, lose Kanten als Nähfedern; Blenders Regel für Nähte beim Kollidieren nachgebaut',
         "Drapierauftrag.rechnen(stueck_punkte, stueck_dreiecke, koerper_punkte, koerper_dreiecke, naehte=paare)   # paare: (K, 2) Punktnummern",
         [('Stoffsolver/naehte.py', 'Naehte'), ('Stoffsolver/drapierauftrag.py', 'Drapierauftrag')],
         'Cloth-Nähfedern: `settings.use_sewing_springs`, `settings.sewing_force_max` (lose Kanten ziehen sich zusammen)',
         "stoff.settings.use_sewing_springs = True   # Grenze der Zugkraft: stoff.settings.sewing_force_max",
         'gemessen',
         'Nähte stehen in der Messreihe „Federn, Gruppen, Schrumpfen, Innenfedern, Nähte, Material, Druck, Presets“: gleich in etwa 100 Fällen, höchstens '
         '0,003 mm (`vergleich_federn.py`, `Stoffsolver/README.md`). Blenders Regel für Nähte beim Kollidieren (`collision.cc:1060-1068`) steckt in '
         '`Naehte.verbunden`. GarmentCode näht in seiner EIGENEN Simulation (Mehrteiliges ist genäht, `MetaGarment`; `garmentcode.md`, 09.09.2026); der '
         'Stoffsolver bekommt Nähte nur über den Auftrag (`naehte`).'),

        ('Stoff in der Bewegung',
         'Film von 2D3D Kleider: lineare Häutung der Kleider je Bild, kein Stoff-Löser (`Kleidertanz`, `G9tanzhaut`)',
         'POST /api/engine2d3dkleider/<job_id>/starten/   {"ab": "film", "bis": "film"}   # Option film: BVH, Bilder, Breite, Höhe',
         [('HumanBodyWeb/core/dienste/engine2d3dkleiderfilm.py', 'Engine2d3dKleiderfilm'),
          ('HumanBodyWeb/core/dienste/kleidertanz.py', 'Kleidertanz'), ('Genesis9/tanzhaut.py', 'G9tanzhaut')],
         'Cloth-Modifier über die Animation (Point Cache: `ptcache.bake`), mit Wind-Feldern',
         "blender -b --python effekte/blender/kleidwind.py -- --bvh <datei.bvh> --kleid <kleid.mhclo> --ausgabe <video.mp4> --bilder 300",
         'genutzt',
         'In „Kleid + Wind“ simuliert Blender den Stoff Bild für Bild (Anker, Unterteilung, Cloth, Kollider, Wind; `effekte/blender/kleidwind.py`) — nur für das '
         'Offline-Video, im Theatre bleibt Newton (Edgar, 10.09.2026; `effekte.md`). Der Film von 2D3D Kleider häutet die Kleider mit dem Skelett: Der Abstand zur '
         'Körperoberfläche bleibt (Shirt 9,5 → 10,0 mm zwischen erstem und mittlerem Bild; `engine2d3dkleider.md`, 30.09.2026). `ptcache.bake` gibt es in '
         '5.2.2 (Introspektion); eine Stoff-Simulation im Film von 2D3D Kleider ist nicht gebaut.'),

        ('Dynamik als Geometry Nodes',
         'kein lokales Werkzeug',
         '— (kein lokaler Aufruf)',
         [],
         'Simulationszonen (`GeometryNodeSimulationInput`/`-Output`) und die Assets „Cloth Dynamics (Experimental)“, „Hair Dynamics“, „Collider“, „Custom Effector“',
         "# Gruppe aus assets/nodes/geometry_nodes_dynamics_assets.blend per bpy.data.libraries.load(pfad, assets_only=True) holen",
         'vorhanden',
         'Die Datei `geometry_nodes_dynamics_assets.blend` liegt in 5.2.2 bei und enthält sechs Gruppen: Cloth Dynamics (Experimental), Collider, Custom '
         'Effector, Custom Force, Hair Dynamics, Set Effector (`ergebnis_introspektion.json`). Das Projekt nutzt den klassischen Cloth-Modifier und den eigenen '
         'Solver; diese Assets sind weder aufgerufen noch gemessen. Der Zusatz „Experimental“ im Namen steht in der Datei selbst.'),
    ]
