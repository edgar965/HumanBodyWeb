# -*- coding: utf-8 -*-
"""Studioprojektumbenennung — nach einer BVH-Umbenennung alle gespeicherten
Studio-Projekte auf den neuen Namen ziehen.

WARUM (Edgar, 24.09.2026): Nach dem Umbenennen einer Animation über die
Bibliothek zeigte die Zeitleiste weiter den ALTEN Namen — nicht nur im
gerade offenen Projekt (das erledigt `Clipfehlt.umbenannt` im Browser,
`static/viewer/studio/clipfehlt.js`), sondern in jedem GESPEICHERTEN
`.studio.json`. Beim nächsten Laden wäre der Clip mit 404 verschwunden
(`Clipfehlt.verschwunden`).

Durchsucht werden nur die Projektordner (Vorgabe + eingestellter Pfad), nicht
die ganze Platte — dieselbe Grenze wie beim BVH-Suchverbot
(`.claude/rules/studio.md`, 13.09.2026: „keine Suche nach verschobenen
Dateien"). Der Unterschied: dort wurde eine FEHLENDE Datei GERATEN, hier wird
ein bekannter, bewusst als Projektablage eingestellter Ordner nach genau dem
einen (Kategorie, Name) durchsucht, das gerade — über dieselbe Aktion —
umbenannt wurde.
"""

import json
import logging

from ..atomic_write import AtomarSchreiber
from ..daten.pfadwurzeln import Pfadwurzeln

logger = logging.getLogger('core')

#: Clip-Arten, die eine BVH-Datei referenzieren (wie `Clipfehlt.js`: BVH_ARTEN).
BVH_CLIPARTEN = {'bvh', 'freeze'}


class Studioprojektumbenennung:
    """Clips mit altem (Kategorie, Name) in allen gespeicherten Projekten umstellen."""

    @staticmethod
    def projektordner():
        """Die Ordner, in denen `.studio.json`-Projekte liegen — ohne Duplikate."""
        wurzeln = [Pfadwurzeln.projekt_standard()] + Pfadwurzeln.aus_einstellungen('studio_project_path')
        gesehen = set()
        ordner = []
        for pfad in wurzeln:
            try:
                aufgeloest = pfad.resolve()
            except OSError:
                continue
            if aufgeloest in gesehen or not aufgeloest.is_dir():
                continue
            gesehen.add(aufgeloest)
            ordner.append(aufgeloest)
        return ordner

    @classmethod
    def umbenennen(cls, kategorie, alter_name, neuer_name):
        """Alle betroffenen Projektdateien schreiben. Liefert (Dateien, Clips)."""
        dateien_geaendert = 0
        clips_geaendert = 0
        for ordner in cls.projektordner():
            for datei in ordner.rglob('*.studio.json'):
                geaendert = cls._datei_umbenennen(datei, kategorie, alter_name, neuer_name)
                if geaendert:
                    dateien_geaendert += 1
                    clips_geaendert += geaendert
        if dateien_geaendert:
            logger.info(
                '[bvh-manage] Rename propagated: %s/%s -> %s in %d project file(s), %d clip(s)',
                kategorie, alter_name, neuer_name, dateien_geaendert, clips_geaendert,
            )
        return dateien_geaendert, clips_geaendert

    @staticmethod
    def _datei_umbenennen(pfad, kategorie, alter_name, neuer_name):
        try:
            with open(pfad, encoding='utf-8') as datei:
                projekt = json.load(datei)
        except (OSError, ValueError):
            logger.warning('[bvh-manage] Projekt nicht lesbar, uebersprungen: %s', pfad, exc_info=True)
            return 0
        geaendert = 0
        for spur in projekt.get('tracks') or []:
            for clip in spur.get('clips') or []:
                if (clip.get('type') not in BVH_CLIPARTEN
                        or clip.get('category') != kategorie
                        or clip.get('name') != alter_name):
                    continue
                clip['name'] = neuer_name
                geaendert += 1
        if not geaendert:
            return 0
        try:
            AtomarSchreiber.json_schreiben(pfad, projekt)
        except Exception:  # noqa: BLE001
            logger.exception('[bvh-manage] Projekt nicht geschrieben: %s', pfad)
            return 0
        return geaendert
