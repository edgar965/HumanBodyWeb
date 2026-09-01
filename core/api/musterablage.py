# -*- coding: utf-8 -*-
"""Musterablage — ein Schnittmuster in die Kleidungsbibliothek legen.

Herausgelöst aus `api/schnittmuster_ablage.pattern_save` (99 Zeilen, Grenze 60).
Die Ansicht tat vier Dinge: Eingaben prüfen, Netz aus dem Muster erzeugen, das
Netz aus dem Körper herausschieben, drei Dateien schreiben.

WAS IN DER BIBLIOTHEK LIEGT
===========================
Je Kleidungsstück ein Ordner `<kategorie>/<name>/` mit drei Dateien:

    garment.obj          das Netz
    specification.json   das 2D-Muster — nur damit ist es wieder bearbeitbar
    garment.json         Name, Kategorie, Farbe, Rauheit, Metallanteil

Fehlt `specification.json`, kann der Musterentwurf das Stück später nicht mehr
öffnen; deshalb wird es zusammen mit dem Netz geschrieben und nicht nachträglich.

DIE PRÜFUNG DES NAMENS IST EINE SICHERHEITSPRÜFUNG
==================================================
Der Name wird zu einem Ordner unter der Bibliothek. `/`, `\\` und `..` sind
deshalb verboten — sonst legt ein Aufruf Dateien irgendwo im Dateisystem ab.
"""

import json
import logging
import os

import numpy as np
from django.conf import settings
from humanbody_core.cloth import generate_from_pattern

from ..daten.objdatei import Objdatei
from ..dienste.charakterdaten import Charakterdaten
from humanbody_core.koerperabstand import Koerperabstand

logger = logging.getLogger(__name__)


class Musterablage:
    """Prüft die Eingaben, erzeugt das Netz und legt die drei Dateien ab."""

    #: Zeichen, mit denen ein Name aus der Bibliothek ausbrechen könnte.
    VERBOTEN = ('/', '\\', '..')
    VORGABE_FARBE = (0.25, 0.30, 0.45)
    VORGABE_ABSTAND = 0.006
    VORGABE_STEIFE = 0.5

    def __init__(self, rumpf):
        self.rumpf = rumpf or {}
        self.name = str(self.rumpf.get('name', '')).strip()
        self.kategorie = str(self.rumpf.get('category', 'custom')).lower()
        self.muster = self.rumpf.get('pattern')
        self.farbe = self.rumpf.get('color', list(self.VORGABE_FARBE))
        self.rauheit = float(self.rumpf.get('roughness', 0.8))
        self.metall = float(self.rumpf.get('metalness', 0.0))
        self.wickeln = bool(self.rumpf.get('wrap', False))
        self.abstand = float(self.rumpf.get('offset', self.VORGABE_ABSTAND))
        self.steife = float(self.rumpf.get('stiffness', self.VORGABE_STEIFE))

    # -------------------------------------------------------------- Prüfungen

    def fehler(self):
        """Der erste Einwand gegen die Eingabe — oder `None`."""
        if not self.name:
            return 'Name is required'
        if any(zeichen in self.name for zeichen in self.VERBOTEN):
            return 'Invalid name'
        if not self.muster or not self.muster.get('panels'):
            return 'Pattern with panels is required'
        return None

    # ------------------------------------------------------------------ Netz

    def netz(self, koerper, flaechen, geschlecht):
        """Das Kleidungsnetz zum Muster — `None`, wenn es nicht aufgeht."""
        ergebnis = generate_from_pattern(self.muster, koerper,
                                         body_faces=flaechen,
                                         wrap=self.wickeln, offset=self.abstand,
                                         stiffness=self.steife)
        if ergebnis is None:
            return None
        return self._herausschieben(ergebnis, koerper, geschlecht)

    def _herausschieben(self, ergebnis, koerper, geschlecht):
        """Stoff aus dem UNTERTEILTEN Körper schieben, nicht aus dem grob en.

        Der angezeigte Körper ist Catmull-Clark-unterteilt und damit an den
        Rundungen dicker als das Grundnetz. Gegen das Grundnetz geschoben sitzt
        der Stoff sichtbar in der Haut.
        """
        unterteiler = Charakterdaten.unterteiler(geschlecht)
        if unterteiler is None:
            return ergebnis
        stoff = Koerperabstand.radial(
            ergebnis['vertices'].astype(np.float64),
            unterteiler.subdivide(koerper),
            mindestabstand=self.abstand)
        ergebnis['vertices'] = stoff.astype(np.float32)
        return ergebnis

    # ----------------------------------------------------------- Ablegen

    def ordner(self):
        pfad = os.path.join(str(settings.HUMANBODY_GARMENT_LIBRARY_DIR),
                            self.kategorie, self.name)
        os.makedirs(pfad, exist_ok=True)
        return pfad

    def ablegen(self, ergebnis):
        """Netz, Muster und Beschreibung schreiben; liefert die Kennung."""
        ordner = self.ordner()
        Objdatei(ergebnis['vertices'], ergebnis['faces'],
                 kopfzeile='Pattern Editor export: %s' % self.name
                 ).schreiben(os.path.join(ordner, 'garment.obj'))
        self._json(os.path.join(ordner, 'specification.json'), self.muster)
        self._json(os.path.join(ordner, 'garment.json'), self.beschreibung())
        kennung = '%s/%s' % (self.kategorie, self.name)
        logger.info('Saved pattern garment to library: %s (%d verts, %d tris)',
                    kennung, len(ergebnis['vertices']), len(ergebnis['faces']))
        return kennung

    @staticmethod
    def _json(pfad, daten):
        with open(pfad, 'w', encoding='utf-8') as datei:
            json.dump(daten, datei, indent=2, ensure_ascii=False)

    def beschreibung(self):
        """`garment.json` — dasselbe Format wie bei den MakeHuman-Stücken."""
        # Dictionary gewollt: geht unveraendert als Datei in die Bibliothek.
        return {
            'name': self.name,
            'category': self.kategorie,
            'tags': [],
            'author': 'Pattern Editor',
            'source': 'pattern-editor',
            'mesh_file': 'garment.obj',
            'default_params': {'offset': self.VORGABE_ABSTAND,
                               'stiffness': self.VORGABE_STEIFE},
            'color': list(self.farbe),
            'roughness': self.rauheit,
            'metalness': self.metall,
        }
