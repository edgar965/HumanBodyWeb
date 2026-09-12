# -*- coding: utf-8 -*-
"""Bvhablage — wo BVH-Dateien liegen und wie man sie sicher anspricht.

`_bvh_root`, `_check_bvh_path` und `_read_bvh_frames_from_file` aus
core/api/retarget.py. Die Pfadpruefung ist sicherheitsrelevant (am 15.08.2026
wurden hier zwei Endpunkte gefunden, die jede .bvh-Datei des Rechners
ueberschreiben konnten) und gehoert deshalb an EINE Stelle.
"""

import logging

from ..safe_paths import SafePath, PfadAbgelehnt


logger = logging.getLogger('core')


class Bvhablage:
    """Bvhablage — wo BVH-Dateien liegen und wie man sie sicher anspricht."""

    @staticmethod
    def frames_lesen(bvh_path):
        """Liest den Frames-Zähler aus dem BVH-Header. 0 bei Fehler."""
        try:
            with open(bvh_path, 'r') as f:
                for line in f:
                    if line.strip().startswith('Frames:'):
                        return int(line.strip().split(':')[1])
        except (IOError, ValueError):
            logger.debug('uebergangen', exc_info=True)
        return 0

    @staticmethod
    def wurzel():
        """Return resolved BVH root directory (parent of all category folders)."""
        return SafePath.bvh_wurzel()

    @staticmethod
    def pfad_pruefen(p):
        """Ensure path is within BVH root. Returns resolved Path or None.

        Prüft seit 12.08.2026 über SafePath. Vorher `str(rp).startswith(str(root))` —
        ein Zeichenketten-Vergleich, den auch ein Nachbarverzeichnis mit gleichem
        Namensanfang besteht. Der Rückgabewert bleibt `None` bei Ablehnung, damit die
        Aufrufer unverändert weiterarbeiten.

        BEWUSST NICHT `SafePath.fuer_bvh()`: Diese Fabrik erlaubt zusätzlich
        MEDIA_ROOT und die eingestellten Studio-Ordner. `bvh_manage` löscht,
        verschiebt und benennt um — das soll nur in der Bibliothek gehen, nicht in
        fremden Verzeichnissen. Zwei Reviewer haben die Abweichung als
        Unstimmigkeit gemeldet (13.08.2026); sie ist gewollt und steht deshalb
        hier."""
        try:
            return SafePath([SafePath.bvh_wurzel()]).pruefe(p)
        except PfadAbgelehnt as e:
            logger.warning('BVH-Pfad abgelehnt: %s', e)
            return None

    @classmethod
    def finden(cls, geprueft):
        """Die Datei — oder dieselbe in einem anderen Kategorieordner.

        EIN UMBENANNTER ORDNER LIESS JEDES PROJEKT STUMM (12.09.2026, Edgar:
        „animation abspielen funktioniert nicht"): `Results` hiess seit 22:20
        `A_Results`, das Studio-Projekt nannte seinen Clip weiter
        `Results/00001_Dance1`, der Retarget antwortete 404, und die Figur
        stand. Die Bibliothek bietet das Umbenennen selbst an
        (`Bvhverwaltung._ordner_umbenennen`) — gespeicherte Projekte muessen
        das ueberleben.

        Nur zum LESEN: Liegt `<name>.bvh` in genau einem anderen Ordner, ist
        das die Datei (mit Vermerk im Protokoll). In mehreren: `None`, denn
        raten waere die falsche Bewegung ohne Fehler. Schreibende Endpunkte
        (`bvhtext`, `sichern`) nehmen weiter nur den genannten Pfad.
        """
        if geprueft is None:
            return None
        if geprueft.is_file():
            return geprueft
        treffer = [ordner / geprueft.name for ordner in cls.wurzel().iterdir()
                   if ordner.is_dir() and (ordner / geprueft.name).is_file()]
        if len(treffer) != 1:
            return None
        logger.info('BVH %s/%s liegt jetzt unter %s', geprueft.parent.name,
                    geprueft.name, treffer[0].parent.name)
        return treffer[0]
