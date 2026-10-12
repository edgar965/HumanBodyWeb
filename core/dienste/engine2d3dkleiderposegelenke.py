# -*- coding: utf-8 -*-
"""Engine2d3dKleiderposegelenke — die Gelenke, die der Schritt „pose" von SAM 3D Body (MHR-70) in die Landmarken der Körper-Kette (MediaPipe-Pose, 33 Punkte) übersetzt (11.10.2026).

Die Körper-Kette erwartet die 33 Punkte von MediaPipe Pose (`landmarken.npz`, `koerper (33, 3)`). SAM 3D Body liefert 70 Punkte (`mhr70`); die Zuordnung steht hier an EINER Stelle: 21 der 33 Punkte
(Nase, Augen, Ohren, Schultern, Ellbogen, Handgelenke, Hüften, Knie, Knöchel, Fersen, große Zehen) haben ein Gegenstück, die Hand- und Mundpunkte nicht — sie bleiben leer (NaN).
Links und rechts sind die der Person (anatomisch), wie bei MediaPipe: Index 11 ist die linke Schulter der Person, in einer Vorderansicht also rechts im Bild — an der Probe geprüft (Skelett auf dem Gemälde).
"""

__all__ = ['Engine2d3dKleiderposegelenke']


class Engine2d3dKleiderposegelenke:
    #: MediaPipe-Pose-Nummer → Name des Gelenks in MHR-70.
    ZUORDNUNG = {
        0: 'nose', 2: 'left-eye', 5: 'right-eye', 7: 'left-ear', 8: 'right-ear',
        11: 'left-shoulder', 12: 'right-shoulder', 13: 'left-elbow', 14: 'right-elbow', 15: 'left-wrist', 16: 'right-wrist',
        23: 'left-hip', 24: 'right-hip', 25: 'left-knee', 26: 'right-knee', 27: 'left-ankle', 28: 'right-ankle',
        29: 'left-heel', 30: 'right-heel', 31: 'left-big-toe-tip', 32: 'right-big-toe-tip',
    }
    #: Die Gelenke, aus denen Schulter-, Hüft- und Gliedmaßenlinie bestehen — für das Kontrollbild (Linien zwischen Gelenken).
    KNOCHEN = (
        ('left-shoulder', 'right-shoulder'), ('left-hip', 'right-hip'), ('left-shoulder', 'left-hip'), ('right-shoulder', 'right-hip'),
        ('left-shoulder', 'left-elbow'), ('left-elbow', 'left-wrist'), ('right-shoulder', 'right-elbow'), ('right-elbow', 'right-wrist'),
        ('left-hip', 'left-knee'), ('left-knee', 'left-ankle'), ('right-hip', 'right-knee'), ('right-knee', 'right-ankle'),
        ('left-ankle', 'left-heel'), ('right-ankle', 'right-heel'), ('left-heel', 'left-big-toe-tip'), ('right-heel', 'right-big-toe-tip'),
        ('nose', 'left-eye'), ('nose', 'right-eye'), ('left-eye', 'left-ear'), ('right-eye', 'right-ear'),
    )
    #: Anzeigename für die Tabelle der Karte.
    ANZEIGE = {
        'nose': 'Nase', 'left-eye': 'Linkes Auge', 'right-eye': 'Rechtes Auge', 'left-ear': 'Linkes Ohr', 'right-ear': 'Rechtes Ohr',
        'left-shoulder': 'Linke Schulter', 'right-shoulder': 'Rechte Schulter', 'left-elbow': 'Linker Ellbogen', 'right-elbow': 'Rechter Ellbogen',
        'left-wrist': 'Linkes Handgelenk', 'right-wrist': 'Rechtes Handgelenk', 'left-hip': 'Linke Hüfte', 'right-hip': 'Rechte Hüfte',
        'left-knee': 'Linkes Knie', 'right-knee': 'Rechtes Knie', 'left-ankle': 'Linker Knöchel', 'right-ankle': 'Rechter Knöchel',
        'left-heel': 'Linke Ferse', 'right-heel': 'Rechte Ferse', 'left-big-toe-tip': 'Linke große Zehe', 'right-big-toe-tip': 'Rechte große Zehe',
    }
    #: Die zwölf Hauptgelenke: Schultern, Ellbogen, Handgelenke, Hüften, Knie, Knöchel — zählen für „wie viele Gelenke gefunden".
    HAUPT = ('left-shoulder', 'right-shoulder', 'left-elbow', 'right-elbow', 'left-wrist', 'right-wrist',
             'left-hip', 'right-hip', 'left-knee', 'right-knee', 'left-ankle', 'right-ankle')

    @classmethod
    def index(cls, namen):
        """`{MHR-Name: Zeile}` aus der Namensliste, die der Runner in `sam3d.json` ablegt."""
        return {n: i for i, n in enumerate(namen)}
