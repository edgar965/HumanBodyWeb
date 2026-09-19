# -*- coding: utf-8 -*-
"""Bildmodellsichtungskatalog — die Felder des Schritts „Zuschnitt und Sichtung".

Aus `Bildmodellkatalog` herausgelöst (19.09.2026, die Datei stand bei 305
Zeilen), als das Feld `umfang` dazukam: Seit Bilder einzeln ersetzt und
hinzugefügt werden können (`Bildmodelldateien`), sichtet der Schritt in der
Vorgabe nur, was noch keinen Befund hat oder dem ein gewähltes Rig fehlt —
die Sichtung aller 20 Damira-Dateien mit vier Rigs kostet zwei Minuten,
ein neues Bild darunter zehn Sekunden.
"""

__all__ = ['Bildmodellsichtungskatalog']


class Bildmodellsichtungskatalog:
    #: (feld, anzeige, [(wert, anzeige, erklärung)], vorgabe)
    FELDER = [
        (
            'zuschnitt',
            'Zuschnitt',
            [
                (
                    'yolo',
                    'Objekte trennen (YOLO11-Pose)',
                    'Jede Person, jeder Kopf wird ein eigenes Bild; Collagen zerfallen',
                ),
                ('ganz', 'Bilder ganz lassen', 'Jedes Bild bleibt, wie es ist'),
            ],
            'yolo',
        ),
        (
            'rig',
            'Rig auf den Bildern',
            [
                ('alle', 'Alle vier', 'MediaPipe (33) ordnet ein; dazu YOLO11-Pose, openpifpaf, ViTPose'),
                ('yolo', 'MediaPipe + YOLO11-Pose', 'YOLO sieht Rumpf, Beine, Füße auch auf Details'),
                ('openpifpaf', 'MediaPipe + openpifpaf', '133 Punkte mit Füßen, Gesicht, Händen'),
                ('vitpose', 'MediaPipe + ViTPose-H',
                 'Das Rig von GVHMR (COCO 17); Start 36 s, dann 0,1 s je Bild'),
                ('mediapipe', 'Nur MediaPipe', 'Wie bis zum 19.09.: nur ganze Personen'),
            ],
            'alle',
        ),
        (
            'umfang',
            'Umfang',
            [
                (
                    'neue',
                    'Nur neue Dateien',
                    'Dateien ohne Befund — und solche, denen ein gewähltes Rig fehlt',
                ),
                ('alle', 'Alle Dateien neu sichten', 'Wie bis zum 19.09.: jede Datei noch einmal'),
            ],
            'neue',
        ),
        (
            'einordnung',
            'Einordnung',
            [
                (
                    'auto',
                    'Automatisch (MediaPipe)',
                    'Haupt-/Nebenbild, Ansicht und Haltung aus den Landmarken',
                ),
                (
                    'manuell',
                    'Meine Einordnung behalten',
                    'Kategorie und Gewicht, wie auf der Seite gestellt',
                ),
            ],
            'auto',
        ),
    ]
