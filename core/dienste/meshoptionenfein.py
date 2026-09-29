"""Meshoptionenfein — die Feineinstellungen des Reiters „Mesh" (im Formular zugeklappt).

Am 29.09.2026 aus `meshoptionen.py` herausgelöst (die Datei stand bei 390 Zeilen); `Meshoptionen.KATALOG`
hängt diese Einträge unverändert an sein Ende.
"""

__all__ = ['Meshoptionenfein']


class Meshoptionenfein:
    EINTRAEGE = [
        # --- Feineinstellungen (`fein`: im Formular in einem zugeklappten Bereich) -------
        # Bis 27.09.2026 standen diese Werte fest im Runner. Edgar: „Es gibt doch sicherlich
        # Einstellungen für alle Jobs - mach die im UI sichtbar und einstellbar vor dem Lauf."
        # Jeder Wert ist an der Pipeline nachgelesen, nicht geraten: TRELLIS.2 aus seiner
        # `pipeline.json` (`steps` 12, `guidance_strength` 7,5) und `o_voxel.postprocess
        # .to_glb`, Hunyuan3D aus `Hunyuan3DDiTFlowMatchingPipeline.__call__`
        # (`num_inference_steps` 50, `guidance_scale` 5,0).
        {'schluessel': 'schritte', 'titel': 'Rechenschritte', 'art': 'zahl', 'vorgabe': 0,
         'min': 0, 'max': 200, 'fein': True,
         'hinweis': '0 = Vorgabe des Modells (TRELLIS.2 12, Hunyuan3D 50). Mehr Schritte: '
                    'feiner und deutlich langsamer.'},
        {'schluessel': 'fuehrung', 'titel': 'Bildtreue (Guidance)', 'art': 'zahl', 'vorgabe': 0,
         'min': 0, 'max': 30, 'schritt': 0.5, 'fein': True,
         'hinweis': '0 = Vorgabe des Modells (TRELLIS.2 7,5, Hunyuan3D 5,0). Höher hält sich '
                    'enger ans Foto, kann aber Artefakte verstärken.'},
        {'schluessel': 'netzaufbau', 'titel': 'Netz neu aufbauen (nur TRELLIS.2)', 'art': 'wahl',
         'vorgabe': 'remesh', 'fein': True, 'werte': [
            ('remesh', 'Ja — Dual Contouring, gleichmäßige Dreiecke (Vorgabe)'),
            ('direkt', 'Nein — das Rohnetz nur vereinfachen'),
        ], 'hinweis': 'Ohne Neuaufbau bleibt die Voxeltreppe im Netz, dafür sitzt die Textur '
                      'genauer (sie wird auf das Rohnetz zurückprojiziert).'},
        {'schluessel': 'aufbau_band', 'titel': 'Aufbau-Band (Voxel)', 'art': 'zahl', 'vorgabe': 1,
         'min': 1, 'max': 8, 'fein': True,
         'hinweis': 'Wie weit der Neuaufbau um die Rohfläche herum rechnet (`remesh_band`). '
                    'Breiter schließt Löcher, rundet aber ab.'},
        {'schluessel': 'aufbau_anziehen', 'titel': 'Auf die Rohfläche ziehen', 'art': 'zahl',
         'vorgabe': 0, 'min': 0, 'max': 1, 'schritt': 0.1, 'fein': True,
         'hinweis': '`remesh_project`: 0 = das neu aufgebaute Netz bleibt glatt, 1 = jeder Punkt '
                    'wird auf die Rohfläche zurückgezogen (schärfer, aber auch zackiger).'},
        {'schluessel': 'fusion_gitter', 'titel': 'Fusion-Gitter', 'art': 'wahl', 'vorgabe': '96',
         'fein': True, 'werte': [
            ('64', '64³ — grob, schnell'), ('96', '96³ (Vorgabe)'), ('128', '128³ — feiner, langsamer'),
        ], 'hinweis': 'Nur bei „Mehrere Fotos: Fusion" — das gemeinsame Gitter, auf dem die '
                      'Einzelnetze gemittelt werden.'},
    ]
