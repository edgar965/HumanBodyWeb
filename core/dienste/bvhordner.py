# -*- coding: utf-8 -*-
"""Bvhordner — die Kategorieordner der BVH-Bibliothek anlegen, umbenennen, loeschen.

Aus `bvhverwaltung.py` abgeteilt (16.10.2026), als der Ordner-Teil um den
Projektabgleich und das Loeschen mit Inhalt wuchs.

Edgar, 16.10.2026 (Szene-Reiter „Animationen"): „ein Kontextmenue bei dem
Ordner, sodass ich den auch umbenennen kann, loeschen kann. Wenn der
umbenannt wird, dann wird auch der Pfad auf dem lokalen Rechner umbenannt."
Ein Ordner IST hier ein Verzeichnis unter `3DObjects/animations/bvh/`; die
Umbenennung benennt dieses Verzeichnis um, nicht einen Eintrag in einer Liste.
"""

import logging

from .bvhablage import Bvhablage
from .bvhfehler import BvhFehler
from .studioprojekt_umbenennung import Studioprojektumbenennung

logger = logging.getLogger('core')

#: Papierkorb fuer geloeschte Ordner mit Inhalt, direkt in der BVH-Wurzel.
#: `Bvhverzeichnis.kategorienamen` laesst Ordner mit Punkt vorn aus — er
#: erscheint weder in der Liste noch in den Auswahlfeldern.
PAPIERKORB = '.trash'

#: Wird von `Bvhauslieferung.dazbewegungen` bei jedem Listenabruf befuellt
#: (`G9bewegungen.ORDNER`; hier als Text, damit die Verwaltung nicht Genesis9 laedt).
DAZ_ORDNER = 'Daz'


class Bvhordner:
    """Ordneraktionen der BVH-Bibliothek. Wirft `BvhFehler`."""

    @staticmethod
    def vorhanden(kategorie):
        """Der Kategorieordner als Pfad; nicht verwaltbar: `Daz`, Papierkorb, Unsinn.

        `Daz/` legt die Liste bei JEDEM Abruf neu an, sobald seine Dateien
        fehlen — umbenannt stuenden die Bewegungen danach doppelt da, geloescht
        kaemen sie beim naechsten Laden zurueck.
        """
        if kategorie == DAZ_ORDNER:
            raise BvhFehler(f'Der Ordner „{kategorie}" wird aus den Daz-Bewegungen '
                            'automatisch angelegt und laesst sich nicht umbenennen oder loeschen.', 409)
        if kategorie.startswith('.'):
            raise BvhFehler(f'Ungueltiger Ordner: {kategorie}')
        ordner = Bvhablage.pfad_pruefen(Bvhablage.wurzel() / kategorie)
        if not ordner or not ordner.is_dir():
            raise BvhFehler('Folder not found', 404)
        return ordner

    @staticmethod
    def anlegen(name):
        ordner = Bvhablage.pfad_pruefen(Bvhablage.wurzel() / name)
        if not ordner:
            raise BvhFehler('Invalid folder name')
        if ordner.exists():
            raise BvhFehler('Folder already exists', 409)
        ordner.mkdir(parents=True)
        logger.info('[bvh-manage] Created folder: %s', ordner)
        return {'ok': True}

    @staticmethod
    def umbenennen(kategorie, neu):
        """Das Verzeichnis umbenennen und gespeicherte Studio-Projekte nachziehen.

        Ohne den Projektabgleich verloere jedes `.studio.json` mit Clips aus
        diesem Ordner sie beim naechsten Laden (404 -> `Clipfehlt.verschwunden`).
        """
        # Nur EIN Namensteil: `a/b` legte den Ordner unter `a` ab, wo ihn die
        # Liste (nur die oberste Ebene) nicht mehr zeigt; ein Punkt vorn waere
        # der Papierkorb und alles, was die Liste auslaesst.
        if '/' in neu or '\\' in neu or neu.startswith('.'):
            raise BvhFehler(f'Ungueltiger Ordnername: {neu}')
        alt = Bvhordner.vorhanden(kategorie)
        ziel = Bvhablage.pfad_pruefen(Bvhablage.wurzel() / neu)
        if not ziel:
            raise BvhFehler('Invalid target path')
        # `samefile`: nur Gross-/Kleinschreibung geaendert — unter Windows
        # „existiert" das Ziel dann schon, es ist aber derselbe Ordner.
        if ziel.exists() and not ziel.samefile(alt):
            raise BvhFehler(f'Folder {neu} already exists', 409)
        try:
            alt.rename(ziel)
        except OSError as fehler:  # eine Datei darin ist gerade offen
            raise BvhFehler(f'Ordner nicht umbenannt: {fehler}', 409) from fehler
        logger.info('[bvh-manage] Renamed folder: %s -> %s', alt, ziel)
        # Der Ordner heisst schon neu — schlaegt der Abgleich fehl, bleibt die
        # Umbenennung gueltig (wie `Bvhverwaltung._umbenennen`).
        try:
            dateien, clips = Studioprojektumbenennung.ordner_umbenennen(kategorie, neu)
        except Exception:  # noqa: BLE001
            logger.exception('[bvh-manage] Projektabgleich fehlgeschlagen: Ordner %s -> %s', kategorie, neu)
            dateien, clips = 0, 0
        return {'ok': True, 'new_name': neu, 'projects_updated': dateien, 'clips_updated': clips}

    @staticmethod
    def loeschen(kategorie, mit_inhalt=False):
        """Leer: entfernen. Mit Inhalt nur auf `mit_inhalt` — dann in den Papierkorb.

        Ohne `mit_inhalt` bleibt es bei der alten Abweisung (das BVH Studio
        fragt „Nur wenn leer"). Ein voller Ordner wandert nach
        `<bibliothek>/.trash/<kategorie>/` statt von der Platte — Mixamo allein
        hat 2.339 Dateien, und die Bibliothek liegt in den Produktivdaten (wie
        `Kleiderverwaltung._loeschen`). Geleert wird `.trash` von Hand.
        """
        ordner = Bvhordner.vorhanden(kategorie)
        inhalt = list(ordner.iterdir())
        if not inhalt:
            ordner.rmdir()
            logger.info('[bvh-manage] Deleted folder: %s', ordner)
            return {'ok': True, 'files': 0}
        if not mit_inhalt:
            raise BvhFehler(f'Folder not empty ({len(inhalt)} items)', 409)
        korb = Bvhablage.wurzel() / PAPIERKORB
        korb.mkdir(parents=True, exist_ok=True)
        ziel, zaehler = korb / kategorie, 2
        while ziel.exists():  # derselbe Name zum zweiten Mal geloescht
            ziel, zaehler = korb / f'{kategorie}_{zaehler}', zaehler + 1
        bvh = sum(1 for p in inhalt if p.suffix.lower() == '.bvh')
        try:
            ordner.rename(ziel)
        except OSError as fehler:
            raise BvhFehler(f'Ordner nicht geloescht: {fehler}', 409) from fehler
        logger.info('[bvh-manage] Ordner in den Papierkorb: %s -> %s (%d BVH, %d Eintraege)',
                    ordner, ziel, bvh, len(inhalt))
        return {'ok': True, 'files': bvh, 'papierkorb': f'{PAPIERKORB}/{ziel.name}'}
