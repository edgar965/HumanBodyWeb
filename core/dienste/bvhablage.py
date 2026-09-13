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
