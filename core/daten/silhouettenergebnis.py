# -*- coding: utf-8 -*-
"""Silhouettenergebnis — was der Ausrichtungsassistent ueber ein Foto weiss.

WARUM EINE KLASSE (Umbau 15.08.2026): Diese zwoelf Werte entstanden ueber 338
Zeilen hinweg in `photo_silhouette_data` und wurden am Ende zu einem Dict
zusammengesetzt. Zwischendurch wurden sie mehrfach ueberschrieben (erst
SMPL-X-Kontur, dann MediaPipe, dann Rueckfall), und welcher Wert am Ende
gesetzt war, liess sich nur durch Lesen der ganzen Funktion beantworten.

Das Dict am Ende BLEIBT — es geht als JSON an den Browser, und dort ist ein
Dict die Zielform. Der Weg dorthin fuehrt jetzt aber ueber benannte Felder.
"""


class Silhouettenergebnis:
    """Konturen, Rahmen und Herkunftsangaben einer Foto-Ausrichtung."""

    __slots__ = ('koerperkontur', 'gesichtskontur', 'netz_rahmen',
                 'gesichtsrahmen_erkannt', 'gesichtsrahmen_netz', 'yolo_rahmen',
                 'breite', 'hoehe', 'posiert', 'ausrichtung', 'aus_smplx')

    def __init__(self, breite, hoehe):
        self.breite = breite
        self.hoehe = hoehe
        self.koerperkontur = []
        self.gesichtskontur = []
        self.netz_rahmen = None
        self.gesichtsrahmen_erkannt = None
        self.gesichtsrahmen_netz = None
        self.yolo_rahmen = None
        self.posiert = False
        self.ausrichtung = None
        self.aus_smplx = False        # Gesichtskontur stammt aus SMPL-X-Vertices

    # ---------------------------------------------------------------- Nachlese

    def bearbeitete_konturen_uebernehmen(self):
        """Von Hand nachgezogene Konturen aus der gespeicherten Ausrichtung.

        Sie gewinnen gegen alles Gerechnete — der Nutzer hat sie ja gerade
        deshalb korrigiert."""
        a = self.ausrichtung or {}
        if a.get('body_contour_edited'):
            self.koerperkontur = a['body_contour_edited']
        if a.get('face_contour_edited'):
            self.gesichtskontur = a['face_contour_edited']

    @property
    def hat_ausrichtung(self):
        a = self.ausrichtung or {}
        return bool(a.get('body_transform') or a.get('proj_2d_offset'))

    def als_dict(self):
        """Die Form, die der Browser erwartet — Feldnamen unveraendert."""
        return {
            'ok': True,
            'body_contour': self.koerperkontur,
            'face_contour': self.gesichtskontur,
            'mesh_bbox': self.netz_rahmen,
            'face_bbox_detected': self.gesichtsrahmen_erkannt,
            'face_bbox_mesh': self.gesichtsrahmen_netz,
            'yolo_bbox': self.yolo_rahmen,
            'photo_width': self.breite,
            'photo_height': self.hoehe,
            'use_posed': self.posiert,
            'has_alignment': self.hat_ausrichtung,
            'alignment_method': (self.ausrichtung or {}).get('method', ''),
            'saved_alignment': self.ausrichtung or None,
        }
