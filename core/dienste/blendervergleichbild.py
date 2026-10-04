# -*- coding: utf-8 -*-
"""Blendervergleichbild — Abschnitt „Rendern und Bildvergleich“ der Tabelle „Wie liefe das mit Blender“ (Reiter „Tools“, 03.10.2026).

Schema und Stände: `Architektur2d3dblender`; die letzten zwei Felder je Zeile sind die Ausführungszeiten (lokal, Blender) mit Quelle und Datum, sonst genau „nicht gemessen“ oder „entfällt“. Belege „Blender hat das“: `ProjektTemp/_wegwerf/tools_seite/t5/ergebnis_introspektion*.json` (Blender 5.2.2 LTS,
Werksstart, nur Namen; Render-Engines nur gesetzt, nicht gerendert; Compositor-Knoten nur angelegt). Zeiten und Befunde aus den Regeln des Projekts mit Fundstelle.
"""

__all__ = ['Blendervergleichbild']


class Blendervergleichbild:
    KENNUNG = 'blender-bild'
    TITEL = 'Rendern und Bildvergleich'
    EINLEITUNG = ('Wie Blender Bilder aus Fotowinkeln rendert und was es zum Vergleich mit Fotos mitbringt. Der BlenderModel-Weg renderte mit Workbench; '
                  '2D3D Kleider rendert mit Mitsuba 3 und rechnet die Note in Python — Blender hat dafür Bausteine, aber keine fertige Kennzahl.')
    # (Aufgabe, lokales Werkzeug, lokaler Aufruf, lokale Klassen [(Datei, Klasse)], Blender-Werkzeug, Blender-Aufruf, Blender-Stand, Unterschied, zeit_lokal, zeit_blender)
    ZEILEN = [
        ('Rendern aus Fotowinkeln',
         'Mitsuba 3 auf der GPU (pyrender als Rückfall): Figur, Kleider und Haar freigestellt je Blickwinkel, orthografisch',
         "Genesishaarrender(motor='mitsuba').bild_teile(teile, winkel, pfad)   # teile: [(punkte, dreiecke, farbe rgb 0…1[, textur])], winkel in Grad ab vorn",
         [('HumanBodyWeb/core/dienste/genesishaarrender.py', 'Genesishaarrender'), ('HumanBodyWeb/core/dienste/mitsubaszene.py', 'Mitsubaszene'),
          ('HumanBodyWeb/core/dienste/renderwahl.py', 'Renderwahl')],
         'Render-Engines BLENDER_WORKBENCH, BLENDER_EEVEE und CYCLES (alle drei setzbar), Operator `render.render`',
         "scene.render.engine = 'BLENDER_WORKBENCH'; bpy.ops.render.render(animation=True)   # wie effekte/blender/kostuem/ansichten.py",
         'genutzt',
         'Im BlenderModel-Weg rendert Workbench: Kandidat 0,6–0,8 s nach 4–9 s Start, Render etwa 1,3 s für 8 Ansichten (`blendermodell.md`, 30.09.2026); '
         '`Effektrender` nimmt Workbench als Vorgabe, Eevee ist wählbar, braucht aber einen GPU-Kontext im Hintergrundprozess (`effektrender.py`). Cycles lässt '
         'sich in 5.2.2 setzen (`ergebnis_introspektion2.json`), im Projekt ist es nicht gemessen. Edgar wollte Cycles auf der GPU; gewählt wurde Mitsuba 3 '
         '(`cuda_ad_rgb`, OptiX; Pfadverfolgung wie Cycles, Normalkarten, Strähnen als Kurven): neue Szene 0,6–1,2 s, jede weitere Ansicht 0,1–0,2 s, Kamera '
         'pixelgleich zu pyrender (IoU 0,984–0,991). Die Wahl steht unter Einstellungen → 2D3D Kleider (`Renderwahl`, Vorgabe Mitsuba; `ortsmorphe.md`, 01.10.2026).',
         '0,6–1,2 s neue Szene, 0,1–0,2 s je weitere Ansicht (Mitsuba 3, GPU; ortsmorphe.md, 01.10.2026); dieselbe Runde gesamt Mitsuba '
         '72,1 s gegen pyrender 62,2 s',
         '~1,3 s für 8 Ansichten (Workbench, Kostümmodell, ohne Blender-Start, andere Szene; blendermodell.md, 30.09.2026)'),

        ('Bildvergleich mit Fotos',
         'Note aus Umriss-IoU und Farbabstand auf einem Raster, das mit der Auflösung wächst (128 → … → Fotoauflösung), je Blickwinkel',
         "Iterationsnote.vergleichen(vorlage, render)   # Klassenmethode; Stufen: Aufloesungsstufe (START 128, FAKTOR 2); Gesamtnote.gesamt(...)",
         [('HumanBodyWeb/core/dienste/iterationsnote.py', 'Iterationsnote'), ('HumanBodyWeb/core/dienste/aufloesungsstufe.py', 'Aufloesungsstufe'),
          ('2d3DIterationen/iterationen2d3d/gesamtnote.py', 'Gesamtnote')],
         'Compositor-Bausteine: Mix-Knoten (Blend-Typ DIFFERENCE), Difference Key, Levels (Mean, Standard Deviation, Minimum, Maximum); `Image.pixels`',
         "n = baum.nodes.new('ShaderNodeMix'); n.data_type = 'RGBA'; n.blend_type = 'DIFFERENCE'   # dazu CompositorNodeLevels → Mean",
         'keins',
         'Eine fertige Kennzahl gibt es nicht: Die Namenssuche compare, metric, ssim, psnr, similar über Operatoren, Knoten und Typen findet nur '
         '`FunctionNodeCompare` (Zahlenvergleich), `CompositorNodeDiffMatte` (Differenz-Key) und die Auswahl-Operatoren `*.select_similar` '
         '(`ergebnis_introspektion.json`). Die Bausteine sind da: `ShaderNodeMix` mit DIFFERENCE, `CompositorNodeLevels` mit Mean und Standard Deviation, '
         '`Image.pixels` (`ergebnis_introspektion2.json`). Das Projekt rechnet die Note in Python/NumPy; das Raster wächst mit der Auflösung, seit auf der '
         'Tafel Lippe und Säume nur 1–3 Pixel groß waren (`engine2d3dkleider.md`, 02.10.2026). Auch im BlenderModel-Weg lief die Note in Python '
         '(`Kostuemnote`: (1 − IoU) + Farbabstand), nicht in Blender (`blendermodell.md`).',
         'nicht gemessen',
         'entfällt'),

        ('Blickwinkel aus dem Foto',
         'Blickwinkel je Foto aus Schulter- und Hüftlinie der Pose (fSpy-Ersatz); Normierung über Figurhöhe und Rumpfschwerpunkt',
         "Blickwinkelschaetzung(...).fuer_lauf()   # vor den Runden: Winkel je Foto → kreislauf.winkel_geschaetzt (Landmarken: Fotolandmarken, python10)",
         [('HumanBodyWeb/core/dienste/blickwinkelschaetzung.py', 'Blickwinkelschaetzung'),
          ('2d3DIterationen/iterationen2d3d/blickwinkel.py', 'Blickwinkel'), ('HumanBodyWeb/core/dienste/fotolandmarken.py', 'Fotolandmarken')],
         'fSpy (externes Open-Source-Programm, Kamera aus einem Foto über Fluchtlinien, Übergabe nach Blender); im Kern Motion Tracking (`clip.solve_camera`)',
         '— (fSpy nicht installiert, nicht geprüft); im Kern: bpy.ops.clip.solve_camera()   # Kamera aus verfolgten Markern eines Clips',
         'addon',
         'Quelle für fSpy: Konzept 30.09.2026 §3.4 — nicht installiert und nicht geprüft; im Kern findet die Namenssuche „landmark“ nichts '
         '(`ergebnis_introspektion.json`), `clip.solve_camera` und `clip.detect_features` gibt es (`ergebnis_introspektion4.json`). Unsere Fotos sind Personen ohne '
         'Fluchtlinien; das Projekt normiert statt zu kalibrieren und schätzt den Winkel aus der Pose: an den Fotos von `.51` vorne −6°, hinten −173°, Seite −78° '
         '(`ortsmorphe.md`, 01.10.2026).',
         'nicht gemessen',
         'nicht gemessen'),
    ]
