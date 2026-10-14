# -*- coding: utf-8 -*-
"""Meshfigurhautgewichte — Knochen und Gewichte für die Netz-Objekte von „Mesh to 3D" und Mesh-3D (13.10.2026).

Edgar: „Warum animieren die Kleider nicht?" Kleidung, Haar und Bestandteile (Hut, Stab, Bart, Tasche …) liegen als starre GLB in der Gruppe der Figur; die Animation bewegt nur das Skelett. Jedes Objekt bekommt deshalb
neben seiner GLB eine Hautdatei (`Kleidung/hautdatei.py`), die die Bühne an das Skelett der Figur bindet. Die Gewichte kommen von der Figur selbst — den Daz-Gewichten des Käfigs in `genesis_ende.npz`
(`haut_index`, `haut_gewicht`, `knochen`), kein zweites Skinning-Verfahren:

    folgt     Käfig-Nachbarschaft wie die Rückrechnung in die Ruhelage (`Kleidunghautgewichte`) — Kleidung, Bart, Tasche
    starr     alles an EINEM Knochen: Haar an `head`, ein Requisit an dem Knochen, der das Teil führt, das es berührt (Stab an der Hand)

Eine Figur ohne diese Felder in `genesis_ende.npz` (alte Läufe) gibt `holen` → None; das Objekt bleibt dann starr, wie bisher.
"""

import logging

import numpy as np

logger = logging.getLogger('core')

__all__ = ['Meshfigurhautgewichte']


class Meshfigurhautgewichte:
    def __init__(self, index, gewicht, knochen):
        self.index = np.asarray(index, dtype=np.int64)
        self.gewicht = np.asarray(gewicht, dtype=np.float64)
        self.knochen = [str(k) for k in knochen]

    @classmethod
    def holen(cls, ablage):
        """Die Käfiggewichte des Laufs — None, wenn `genesis_ende.npz` fehlt oder sie nicht trägt."""
        pfad = ablage.arbeit('genesis_ende.npz')
        if not pfad.is_file():
            return None
        with np.load(pfad) as d:
            if not all(k in d.files for k in ('haut_index', 'haut_gewicht', 'knochen')):
                return None
            return cls(d['haut_index'], d['haut_gewicht'], d['knochen'])

    @classmethod
    def kaefig_von(cls, ablage, ruhelage, netz, pruefung=None, name=None, dreiecke=None, ruhe=None):
        """Wie `holen().kaefig(…)`, aber ein Zusatz: fehlt etwas oder scheitert die Rechnung, gibt es None (mit Grund im Log) und das Objekt bleibt starr wie bisher.
        Mit `pruefung` (`Meshfigurtanzpruefung`), `name`, `dreiecke` und `ruhe` (die Punkte des Objekts in der Ruhelage) wählt die Animationsprüfung die Gewichte nach der Dehnung im Tanz."""
        try:
            gewichte = cls.holen(ablage)
            return None if gewichte is None else gewichte.kaefig(ruhelage, netz, pruefung, name, dreiecke, ruhe)
        except Exception:  # noqa: BLE001 — Hautgewichte sind ein Zusatz zum Objekt, nie sein Ausfall
            logger.exception('Hautgewichte (Käfig-Nachbarschaft) gescheitert')
            return None

    @classmethod
    def starr_von(cls, ablage, anzahl, knochen):
        """Wie `holen().starr(…)` mit demselben Verhalten bei Fehlern wie `kaefig_von`."""
        try:
            gewichte = cls.holen(ablage)
            return None if gewichte is None else gewichte.starr(anzahl, knochen)
        except Exception:  # noqa: BLE001
            logger.exception('Hautgewichte (starr an %s) gescheitert', knochen)
            return None

    def kaefig(self, ruhelage, netz, pruefung=None, name=None, dreiecke=None, ruhe=None):
        """`{index, gewicht, knochen}` je Punkt von `netz` (Lage des Netzes) über die Käfig-Nachbarschaft.
        `ruhelage`: die `Meshfigurkleidungsruhelage`, die dieses Netz zuletzt in `punkte` zurückgerechnet hat (deren Körperteile gelten hier).
        Mit `pruefung` (`Meshfigurtanzpruefung`) vergleicht die Animationsprüfung diese Gewichte mit weichen (`Kleidung.hautnaehe`) an der Dehnung im Tanz und nimmt die besten — der Bericht steht in `ergebnis.animation`."""
        from Kleidung.kleidunghautgewichte import Kleidunghautgewichte

        index, gewicht = Kleidunghautgewichte(ruhelage.entposen).berechnen(netz, self.index, self.gewicht, len(self.knochen), ruhelage.teile_zuletzt, ruhe)
        if pruefung is not None and dreiecke is not None and ruhe is not None:
            index, gewicht, _bericht = pruefung.waehlen(name or 'objekt', self, ruhelage, netz, ruhe, dreiecke, index, gewicht)
        return {'index': index, 'gewicht': gewicht, 'knochen': self.knochen}

    @staticmethod
    def abstand_ruhe(ruhelage, ruhe):
        """(M,) Abstand der Punkte des Objekts in der RUHELAGE zum Käfig in Ruhe (m) — `None` ohne `ruhe`. Dort sieht man Figur und Stoff; wer anliegt, bewegt sich wie die Haut (`Kleidunghautgewichte`, `Hautnaehe`, `Kleidunggewebe`)."""
        if ruhe is None:
            return None
        from scipy.spatial import cKDTree

        return cKDTree(ruhelage.entposen.ruhe).query(np.asarray(ruhe, dtype=np.float64), workers=-1)[0]

    def starr(self, anzahl, knochen):
        """`{index, gewicht, knochen}` für `anzahl` Punkte, die ganz an `knochen` hängen — None, wenn die Figur ihn nicht führt."""
        from Kleidung.hautdatei import Hautdatei

        if knochen not in self.knochen:
            return None
        index, gewicht = Hautdatei.starr(anzahl, self.knochen.index(knochen))
        return {'index': index, 'gewicht': gewicht, 'knochen': self.knochen}
