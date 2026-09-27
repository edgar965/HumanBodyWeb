# -*- coding: utf-8 -*-
"""Meshexportablage — jedes fertige Mesh zusätzlich als GLB in einen festen Ordner.

Edgar (26.09.2026): „exportiere das 3D Mesh standardmässig in
A:\\3DTools\\HumanBodyWeb\\output\\Export\\Foto3D, als glb". Gebaut wie
`Ergebnisablage` (dieselbe Rolle für BVH-Läufe): Der Auftragsordner bleibt die
Quelle der Wahrheit, hier liegt nur eine Kopie zum Weiterverwenden.

Der Dateiname ist Name + Datum + Uhrzeit (Edgar: „damira_2026.09.26.12.22 als Name"),
also `<name>_<JJJJ.MM.TT.HH.MM>.glb` — ohne Sekunden. Maßgeblich ist die Anlagezeit
des Auftrags, nicht die des Laufs: Ein zweiter Lauf desselben Auftrags ersetzt damit
seine eigene Kopie, statt den Ordner mit Fassungen zu füllen (wie `Ergebnisablage`);
jeder einzelne Lauf bleibt im Auftragsordner erhalten.

Ein Fehler beim Kopieren darf den Auftrag NICHT scheitern lassen: Der Lauf ist zu
diesem Zeitpunkt fertig, das Ergebnis liegt im Auftragsordner. Der Aufrufer
protokolliert und macht weiter.
"""

import re
import shutil
from pathlib import Path

from django.conf import settings
from django.utils.timezone import template_localtime

__all__ = ['Meshexportablage']


class Meshexportablage:
    """Der gemeinsame Ablageordner der fertigen Mesh-Netze."""

    @staticmethod
    def ordner():
        pfad = Path(settings.MESH_FOTO3D_EXPORT_DIR)
        pfad.mkdir(parents=True, exist_ok=True)
        return pfad

    @staticmethod
    def _stamm(job):
        # Auftragsnamen kommen aus einem Eingabefeld — alles, was unter NTFS einen
        # Datenstrom oder Pfadwechsel auslösen könnte, fällt weg (`helfer.md`: der
        # Doppelpunkt machte aus `video:1.mp4` eine 0-Byte-Datei).
        roh = (job.name or 'mesh').strip()
        sauber = re.sub(r'[<>:"|?*\\/\x00-\x1f]', '_', roh).strip(' .') or 'mesh'
        return '%s_%s' % (sauber, template_localtime(job.created_at).strftime('%Y.%m.%d.%H.%M'))

    @classmethod
    def pfad(cls, job):
        """Der Zielpfad der Kopie — ohne den Ordner anzulegen."""
        return Path(settings.MESH_FOTO3D_EXPORT_DIR) / ('%s.glb' % cls._stamm(job))

    @classmethod
    def kopieren(cls, job, quelle):
        """Kopiert die fertige GLB und gibt den Zielpfad als Text zurück."""
        cls.ordner()
        ziel = cls.pfad(job)
        shutil.copy2(str(quelle), str(ziel))
        return str(ziel)

    @classmethod
    def kopie_von(cls, job):
        """Die Ablagekopie eines Auftrags, wenn sie liegt — sonst ''."""
        if not job or not job.kennung:
            return ''
        ziel = cls.pfad(job)
        return str(ziel) if ziel.is_file() else ''
