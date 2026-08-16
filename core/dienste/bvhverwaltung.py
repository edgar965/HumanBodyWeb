# -*- coding: utf-8 -*-
"""Bvhverwaltung: Dateien und Ordner der BVH-Bibliothek verwalten.

Aus `bvh_manage` in core/api/retarget.py herausgeloest (Umbau 16.08.2026): eine
Funktion mit 149 Zeilen und sieben `elif`-Zweigen, in denen dieselben vier
Zeilen "Pfad pruefen, Existenz pruefen, sonst 404" siebenmal standen.

WAS DABEI AUFFIEL — die Cache-Behandlung lief ins Leere:
Delete, Rename und Move fassten zusaetzlich `pfad.with_suffix('.json')` an, um
den Retarget-Zwischenspeicher mitzunehmen. Diese Dateien heissen aber
`<name>_retarget_<pruefsumme>.json`, nie `<name>.json`. Nachgezaehlt am
16.08.2026: 7.067 BVH-Dateien, 40 Cache-Dateien, davon **null** mit dem
gesuchten Namen. Der Zweig ist also nie gelaufen, und geloeschte Animationen
liessen ihre Zwischenspeicher liegen. Hier wird jetzt nach dem echten Muster
gesucht.
"""

import logging
import shutil

from .bvhablage import Bvhablage

logger = logging.getLogger('core')

#: Muster der Retarget-Zwischenspeicher zu einer BVH-Datei.
CACHE_MUSTER = '%s_retarget_*.json'


class BvhFehler(Exception):
    """Ablehnung mit HTTP-Kennzahl — der Endpunkt macht daraus JSON."""

    def __init__(self, text, kennzahl=400):
        super().__init__(text)
        self.text = text
        self.kennzahl = kennzahl


class Bvhverwaltung:
    """Die sieben Verwaltungsaktionen der BVH-Bibliothek."""

    @staticmethod
    def ausfuehren(daten):
        """Aktion aus den Anfragedaten ausfuehren. Wirft BvhFehler."""
        aktion = daten.get('action', '')
        arbeit = {
            'delete': Bvhverwaltung._loeschen,
            'rename': Bvhverwaltung._umbenennen,
            'move': Bvhverwaltung._verschieben,
            'copy': Bvhverwaltung._kopieren,
            'create_folder': Bvhverwaltung._ordner_anlegen,
            'rename_folder': Bvhverwaltung._ordner_umbenennen,
            'delete_folder': Bvhverwaltung._ordner_loeschen,
        }.get(aktion)
        if not arbeit:
            raise BvhFehler(f'Unknown action: {aktion}')
        logger.info('[bvh-manage] action=%s, category=%s, name=%s', aktion,
                    daten.get('category', ''), daten.get('name', ''))
        return arbeit(daten)

    # ------------------------------------------------------------- Hilfsmittel

    @staticmethod
    def _pflicht(daten, *felder):
        """Verlangte Felder lesen; fehlt eines, mit 400 abbrechen."""
        werte = [str(daten.get(f, '')).strip() for f in felder]
        if not all(werte):
            raise BvhFehler('%s required' % ', '.join(felder))
        return werte

    @staticmethod
    def _datei(kategorie, name):
        """Vorhandene BVH-Datei in der Bibliothek."""
        pfad = Bvhablage.pfad_pruefen(
            Bvhablage.wurzel() / kategorie / f'{name}.bvh')
        if not pfad or not pfad.is_file():
            raise BvhFehler('File not found', 404)
        return pfad

    @staticmethod
    def _freies_ziel(pfad, meldung):
        """Geprueftes Ziel, das es noch nicht gibt."""
        ziel = Bvhablage.pfad_pruefen(pfad)
        if not ziel:
            raise BvhFehler('Invalid target path')
        if ziel.exists():
            raise BvhFehler(meldung, 409)
        return ziel

    @staticmethod
    def _caches(pfad):
        """Retarget-Zwischenspeicher zu einer BVH-Datei."""
        return sorted(pfad.parent.glob(CACHE_MUSTER % pfad.stem))

    # ----------------------------------------------------------------- Dateien

    @staticmethod
    def _loeschen(daten):
        kategorie, name = Bvhverwaltung._pflicht(daten, 'category', 'name')
        pfad = Bvhverwaltung._datei(kategorie, name)
        caches = Bvhverwaltung._caches(pfad)
        pfad.unlink()
        for c in caches:
            c.unlink()
        logger.info('[bvh-manage] Deleted: %s (+%d Cache)', pfad, len(caches))
        return {'ok': True}

    @staticmethod
    def _umbenennen(daten):
        kategorie, name, neu = Bvhverwaltung._pflicht(
            daten, 'category', 'name', 'new_name')
        alt = Bvhverwaltung._datei(kategorie, name)
        ziel = Bvhverwaltung._freies_ziel(
            Bvhablage.wurzel() / kategorie / f'{neu}.bvh',
            f'{neu}.bvh exists already')
        caches = Bvhverwaltung._caches(alt)
        alt.rename(ziel)
        for c in caches:
            c.rename(c.with_name(c.name.replace(alt.stem, ziel.stem, 1)))
        logger.info('[bvh-manage] Renamed: %s -> %s', alt, ziel)
        return {'ok': True, 'new_name': neu}

    @staticmethod
    def _verschieben(daten):
        kategorie, name, neue_kategorie = Bvhverwaltung._pflicht(
            daten, 'category', 'name', 'new_category')
        alt = Bvhverwaltung._datei(kategorie, name)
        ordner = Bvhablage.pfad_pruefen(Bvhablage.wurzel() / neue_kategorie)
        if not ordner:
            raise BvhFehler('Invalid target category')
        ordner.mkdir(parents=True, exist_ok=True)
        ziel = ordner / f'{name}.bvh'
        if ziel.exists():
            raise BvhFehler(f'{name}.bvh already in {neue_kategorie}', 409)
        caches = Bvhverwaltung._caches(alt)
        shutil.move(str(alt), str(ziel))
        for c in caches:
            shutil.move(str(c), str(ordner / c.name))
        logger.info('[bvh-manage] Moved: %s -> %s', alt, ziel)
        return {'ok': True}

    @staticmethod
    def _kopieren(daten):
        kategorie, name, neu = Bvhverwaltung._pflicht(
            daten, 'category', 'name', 'new_name')
        neue_kategorie = str(daten.get('new_category', '')).strip() or kategorie
        alt = Bvhverwaltung._datei(kategorie, name)
        ordner = Bvhablage.wurzel() / neue_kategorie
        ordner.mkdir(parents=True, exist_ok=True)
        ziel = Bvhverwaltung._freies_ziel(ordner / f'{neu}.bvh',
                                          f'{neu}.bvh already exists')
        shutil.copy2(str(alt), str(ziel))
        logger.info('[bvh-manage] Copied: %s -> %s', alt, ziel)
        return {'ok': True}

    # ------------------------------------------------------------------ Ordner

    @staticmethod
    def _ordner_anlegen(daten):
        (name,) = Bvhverwaltung._pflicht(daten, 'folder_name')
        ordner = Bvhablage.pfad_pruefen(Bvhablage.wurzel() / name)
        if not ordner:
            raise BvhFehler('Invalid folder name')
        if ordner.exists():
            raise BvhFehler('Folder already exists', 409)
        ordner.mkdir(parents=True)
        logger.info('[bvh-manage] Created folder: %s', ordner)
        return {'ok': True}

    @staticmethod
    def _ordner_umbenennen(daten):
        kategorie, neu = Bvhverwaltung._pflicht(daten, 'category', 'new_name')
        alt = Bvhablage.pfad_pruefen(Bvhablage.wurzel() / kategorie)
        if not alt or not alt.is_dir():
            raise BvhFehler('Folder not found', 404)
        ziel = Bvhverwaltung._freies_ziel(Bvhablage.wurzel() / neu,
                                          f'Folder {neu} already exists')
        alt.rename(ziel)
        logger.info('[bvh-manage] Renamed folder: %s -> %s', alt, ziel)
        return {'ok': True, 'new_name': neu}

    @staticmethod
    def _ordner_loeschen(daten):
        (kategorie,) = Bvhverwaltung._pflicht(daten, 'category')
        ordner = Bvhablage.pfad_pruefen(Bvhablage.wurzel() / kategorie)
        if not ordner or not ordner.is_dir():
            raise BvhFehler('Folder not found', 404)
        inhalt = list(ordner.iterdir())
        if inhalt:
            raise BvhFehler(f'Folder not empty ({len(inhalt)} items)', 409)
        ordner.rmdir()
        logger.info('[bvh-manage] Deleted folder: %s', ordner)
        return {'ok': True}
