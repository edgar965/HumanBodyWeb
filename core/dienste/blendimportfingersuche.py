# -*- coding: utf-8 -*-
"""Blendimportfingersuche — die Fingerhaltung einer Hand finden (10.10.2026).

Begrenzte kleinste Quadrate (`scipy.optimize.least_squares`, Verlust `soft_l1`) über die 21 Winkel und die Größe von `Blendimportfingermodell`,
aus mehreren Startwerten: gestreckt (0), ein Viertel und drei Viertel der Greifpose von Daz (`CTRL…HandGrasp` 1). Das beste Ergebnis gilt nur,
wenn es das Maß um `VORTEIL` verbessert gegenüber der gestreckten Hand — sonst bleibt die Hand gestreckt (`uebernommen` falsch). Die zweite,
härtere Probe (Passung in der Ruhelage) macht `Blendimportfinger`.

Gemessen 10.10.2026 an Rosemary Winters (`ProjektTemp/_wegwerf/finger_fit_proto.py`): rechte Hand um den Griff des Katana, Abstand
Original → Käfigpunkte Median 9,24 → 3,13 mm (p90 30,1 → 7,8), jede Auswertung 12–33 ms, ein Start 10–30 s.
"""

import time

import numpy as np
from scipy.optimize import least_squares

__all__ = ['Blendimportfingersuche']


class Blendimportfingersuche:
    #: Anteil der Greifpose von Daz als Startwert (0 = gestreckt).
    STARTS = (0.0, 0.25, 0.75)
    #: Das Maß der Lösung muss unter diesem Anteil des Maßes der gestreckten Hand liegen, damit sie gilt.
    VORTEIL = 0.85
    #: Schritt der Differenzen in Einheiten von `EINHEIT` Grad; Rechenschritte je Start.
    EINHEIT = 10.0
    DIFFERENZ = 0.1
    SCHRITTE = 40
    #: Verlust und seine Breite (m): wenige Original-Punkte ohne Gegenstück ziehen nicht mit.
    BREITE_M = 0.008

    def __init__(self, modell, melden=None):
        self.modell = modell
        self.melden = melden or (lambda text: None)

    def suchen(self):
        """`{uebernommen, phi, start, vorher, nachher, wert_vorher, wert_nachher, sekunden, auswertungen}` — `phi` in Grad, Reihenfolge von
        `modell.parameter`; ohne Vorteil die gestreckte Hand (Nullen)."""
        m = self.modell
        t0 = time.perf_counter()
        null = np.zeros(m.anzahl)
        wert0 = m.wert(null)
        beste, auswertungen = None, 0
        for g in self.STARTS:
            start = np.clip(m.griffpose * g, m.unten, m.oben)
            erg = least_squares(lambda u: m.reste(u * self.EINHEIT), start / self.EINHEIT, bounds=(m.unten / self.EINHEIT, m.oben / self.EINHEIT),
                                loss='soft_l1', f_scale=self.BREITE_M, diff_step=self.DIFFERENZ, max_nfev=self.SCHRITTE)
            phi = erg.x * self.EINHEIT
            wert = m.wert(phi)
            auswertungen += int(erg.nfev) * (len(null) + 1)
            self.melden('Finger %s: Start %.2f → %.3e (gestreckt %.3e)' % (m.seite, g, wert, wert0))
            if beste is None or wert < beste['wert']:
                beste = {'wert': wert, 'phi': phi, 'start': g}
        gilt = beste['wert'] < self.VORTEIL * wert0
        phi = beste['phi'] if gilt else null
        return {'uebernommen': bool(gilt), 'phi': phi, 'start': beste['start'], 'vorher': m.kennzahlen(null), 'nachher': m.kennzahlen(phi),
                'wert_vorher': wert0, 'wert_nachher': beste['wert'], 'sekunden': round(time.perf_counter() - t0, 1), 'auswertungen': auswertungen}
