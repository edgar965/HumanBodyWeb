# -*- coding: utf-8 -*-
"""Mesh3daiautorig — der Zwischenschritt „nur Rig“ auf der Seite Mesh3D-AI (16.10.2026): das Genesis-Skelett, das „Mesh to 3D“ in die Außenfläche einer Probe legt.

Edgar: „Du kannst doch das Mesh riggen, es gibt diese AutoRig-Funktion … Warum machst du das nicht als Erster?“ — „mach das!“ — „mach doch einen Zwischenschritt, wo du nur das Rigging auf das Mesh machst?
Mit Einschalten des Rig-Toggles wird das Rig angezeigt im Mesh.“
Woher: ein Mesh-3D-Auftrag (Weg „netz“, Pose mit SAM 3D Body) auf `proben/NNNN/eingabe.glb`, ganze Figur oder Option `umfang = rig`. `ProjektTemp/_wegwerf/mesh3dai_autorig_messen.py` rechnet die 138 Gelenke der
angepassten Figur nach (`Meshfigurmodell.vorwaerts`), legt sie in den Rahmen des Datensatzes zurück (`scan_lage.npz`) und schreibt `proben/NNNN/autorig.npz`:
    rig (138, 3) m · mesh3d (Kennung des Imports) · meshfigur (Kennung des Auftrags „Mesh to 3D“) · umfang (figur | rig) · fassung
Die Seite zeigt es im Feld „Start“, wenn der Knopf „Rig“ an ist — gefärbt nach dem Abstand zum Ziel-Rig wie das Ergebnis.
"""

import logging

import numpy as np

logger = logging.getLogger('core')

__all__ = ['Mesh3daiautorig']


class Mesh3daiautorig:
    DATEI = 'autorig.npz'
    #: Fassung der Datei; eine andere wird nicht gezeigt (`artefakte-benennen.md`).
    FASSUNG = 1

    @classmethod
    def stand(cls, ordner):
        """Stempel aller Dateien des Zwischenschritts im Datensatz (für die Ablage von `Mesh3daidaten`: eine neue Datei soll sofort erscheinen)."""
        return tuple(sorted((p.parent.name, p.stat().st_mtime_ns) for p in (ordner / 'proben').glob('*/' + cls.DATEI)))

    @classmethod
    def lesen(cls, ordner, nr, soll, namen):
        """`{rig, je_mm, info}` für die Probe `nr` oder `None` (keine Datei, andere Fassung, anderes Rig)."""
        datei = ordner / 'proben' / ('%04d' % int(nr)) / cls.DATEI
        if not datei.is_file():
            return None
        try:
            with np.load(datei) as d:
                if int(d['fassung']) != cls.FASSUNG:
                    logger.warning('Mesh3daiautorig: %s hat Fassung %s statt %s — nicht gezeigt', datei, int(d['fassung']), cls.FASSUNG)
                    return None
                rig = d['rig'].astype(float)
                info = {'mesh3d': str(d['mesh3d']), 'meshfigur': str(d['meshfigur']), 'umfang': str(d['umfang'])}
        except (OSError, KeyError, ValueError) as fehler:
            logger.warning('Mesh3daiautorig: %s nicht lesbar (%s)', datei, fehler)
            return None
        if rig.shape != (len(namen), 3):
            logger.warning('Mesh3daiautorig: %s hat %s Punkte, das Rig %d — nicht gezeigt', datei, rig.shape, len(namen))
            return None
        je = 1000.0 * np.linalg.norm(rig - soll, axis=1)
        info.update(mittel_mm=round(float(je.mean()), 1), median_mm=round(float(np.median(je)), 1))
        return {'rig': np.round(rig, 4).tolist(), 'je_mm': np.round(je, 1).tolist(), 'info': info}
