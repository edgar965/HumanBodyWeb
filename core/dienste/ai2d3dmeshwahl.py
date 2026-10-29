# -*- coding: utf-8 -*-
"""Ai2d3dmeshwahl — mit welcher Portierung 2d-3d-AI eine Genesis-Figur in die geometrische Figur einpasst (28.10.2026).

Edgar: „portiere beide Methoden, mach in den Einstellungen - 2d-3d-AI die Option welche Portierung wir dafür nehmen, per default die beste“. Gespeichert in `AppSettings.ui_prefs` wie
`Ai2d3dgesichtswahl`; gelesen von `Genesis9.meshgenesis.G9meshgenesis.gewaehlt` beim nächsten Lauf (`ProjektTemp/_wegwerf/ai2d3d/mesh_auf_genesis.py`) — ein gerechneter Lauf bleibt,
wie er ist. Beide rechnen auf der Grafikkarte im Speicher; Quellen, Lizenzen und Abweichungen: Hilfe → Architektur → Genesis.
"""

import logging

logger = logging.getLogger('core')

__all__ = ['Ai2d3dmeshwahl']


class Ai2d3dmeshwahl:
    SCHLUESSEL = 'ai2d3d_mesh_verfahren'
    #: die beste nach Messung (28.10.2026, EdgarTrip, `mesh_auf_genesis.py --vergleich`, `laeufe/2026.10.27.23.37_form_koerper_vier/mesh_genesis_vergleich_4.json`): Maß ist, wie
    #: dicht die Figur an der Haut des Ziels liegt (Hautpunkte des Ziels → Fläche der Figur) — IPNet 0,80 mm, transfer 2,67 mm; nur Regler und Haltung 4,5 gegen 6,2 mm
    VORGABE = 'ipnet'
    WERTE = (('ipnet', 'IPNet-Verfahren auf Genesis — Abstand zur Fläche'), ('transfer', 'transfer_model-Verfahren auf Genesis — Punkt zu Punkt, Trust-Region-Newton-CG'))
    BESCHREIBUNG = {
        'ipnet': 'Port von IPNet (Bhatnagar 2020) auf das Genesis-Modell: Adam auf Lage, Haltung (das Genesis-Rig ohne Finger, Zehen und Gesichtsknochen) und Reglern gegen '
                 'Abstände Punkt ↔ Fläche in beide Richtungen (kaolin point_to_surface) und Chamfer je Körperteil; den Versatz danach wählt „Versatz danach“. '
                 'Folgt der Fläche, nicht den Punkten des Ziels. Die Zahlen hier stammen noch aus der Fassung mit den Gelenken von SMPL und freiem Versatz: '
                 'Gemessen an EdgarTrip (28.10.2026, Lauf 2026.10.27.23.37): Hautpunkte des Ziels → Figur im Mittel 0,80 mm (höchstens 12,4), nur mit Reglern und Haltung 4,5 mm; '
                 'nach „innen“ 216 von 25.182 Punkten noch außen, höchstens 1,43 mm; 83 s für die Einpassung.',
        'transfer': 'Port des Verfahrens von transfer_model (Choutas) auf das Genesis-Modell: erst nur die Haltung (das Genesis-Rig wie oben) über die Kantenvektoren, dann alles '
                    'über Punkt-zu-Punkt-Abstände, gelöst mit Trust-Region-Newton-CG (torch-trust-ncg). Das Ziel wird einmal an der Startfigur auf die Genesis-Punkte abgebildet '
                    '(nächster Punkt der Fläche). Zahlen der Fassung mit den Gelenken von SMPL-X und fortgesetztem Rest an EdgarTrip: Hautpunkte des Ziels → Figur 2,67 mm '
                    '(höchstens 52,1) — Stellen des Ziels, '
                    'auf die kein Genesis-Punkt abgebildet wurde, bleiben offen —, nur mit Reglern und Haltung 6,2 mm; 164 Punkte außen, höchstens 0,97 mm; 71 s.',
    }

    @classmethod
    def aus(cls, prefs):
        w = str((prefs or {}).get(cls.SCHLUESSEL, cls.VORGABE)).strip()
        return w if w in dict(cls.WERTE) else cls.VORGABE

    @classmethod
    def gewaehlt(cls):
        """Das gespeicherte Verfahren — ohne lesbare Einstellungen die Vorgabe, mit Warnung."""
        try:
            from ..models import AppSettings
            return cls.aus(AppSettings.load().ui_prefs)
        except Exception as fehler:  # noqa: BLE001 — Rechenläufe sollen auch ohne Datenbank laufen, mit der Vorgabe
            logger.warning('Ai2d3dmeshwahl: Einstellung nicht lesbar (%s) — Vorgabe %s', fehler, cls.VORGABE)
            return cls.VORGABE

    @classmethod
    def text(cls, wert):
        return dict(cls.WERTE).get(wert, str(wert))
