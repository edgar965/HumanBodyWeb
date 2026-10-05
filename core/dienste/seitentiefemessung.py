# -*- coding: utf-8 -*-
"""Seitentiefemessung — die Rumpftiefe von Netz, Körper und Hemd-Stück gegen die Silhouette des Seitenfotos, in der Ruhelage und in Millimetern (05.10.2026).

Die Messgröße der Kleiderstücke (`Kleiderstuecknote`) vergleicht die Stücke mit dem NETZ — ist das Netz am Bauch zu tief, sieht sie das nicht (Edgar, 05.10.2026: „bauch ist viel zu dick beim Modell im vergleich zur
vorlage"; die Note stand bei 0,085). Diese Messung nimmt das Seitenfoto als Maßstab (`Seitentiefe`): je Höhenanteil Tiefe des Fotos, des Netzes (das, auf dem der Körper gerechnet ist), des Körpers der
Figur und des Hemd-Stücks, im Band `Seitentiefe.BAND`; `abweichung_*` ist Modell − Foto, + = zu tief. Der Schritt „Kleiderstücke" legt sie in `ergebnis.kleiderstuecke.seitentiefe` ab, die Karte zeigt sie.

Der Maßstab ist ein Foto: Es zeigt auch den hängenden Arm (liegt innerhalb der Tiefe) und hat Perspektive — es kann die Tiefe überschätzen, nie unterschätzen. Ein Wert um 0 heißt „nicht tiefer als das Foto",
nicht „genau richtig".
"""

import logging

import numpy as np

from .kleiderstueckobjekt import Kleiderstueckobjekt
from .netztiefe import Netztiefe
from .seitentiefe import Seitentiefe

logger = logging.getLogger('core')

__all__ = ['Seitentiefemessung']


class Seitentiefemessung:
    @classmethod
    def messen(cls, job, ablage, bezug, stuecke):
        """`{hoehe_m, foto, netz, koerper, hemd, abweichung_*}` — oder `{'grund': …}`, wenn nicht gemessen werden kann. `bezug`: `Kleiderstueckbezug` (Ruhelage), `stuecke` `{name: Kennung}`."""
        try:
            fotos = Netztiefe(job, ablage).seitenfotos()
            if not fotos:
                return {'grund': 'kein Seitenfoto (Rolle „rechts“ oder „links“)'}
            foto = Seitentiefe.mittel([Seitentiefe.foto_profil(Netztiefe._alpha(png)) for _, png in fotos])
            koerper = np.asarray(bezug.koerper_netz()[0], dtype=np.float64)
            y0, y1 = float(koerper[:, 1].min()), float(koerper[:, 1].max())
            hoehe = y1 - y0
            profile = {'koerper': Seitentiefe.modell_profil(koerper, y0, y1)}
            alles = bezug._ruhelage(np.ones(len(bezug.scan.flaechen), dtype=bool))
            if alles is not None:
                profile['netz'] = Seitentiefe.modell_profil(alles[0], y0, y1)
            hemd = Kleiderstueckobjekt.laden(stuecke['oberteil']) if stuecke.get('oberteil') else None
            if hemd is not None:
                profile['hemd'] = Seitentiefe.modell_profil(hemd[0], y0, y1)
        except Exception as fehler:  # noqa: BLE001 — eine Messung hält den Schritt nicht auf
            logger.exception('2D3D Kleider %s: Seitentiefe nicht gemessen', job.kennung)
            return {'grund': 'Fehler: %s' % str(fehler)[:200]}
        aus = {'hoehe_m': round(hoehe, 3), 'band': list(Seitentiefe.BAND), 'fotos': [r for r, _ in fotos],
               'foto': {str(h): round(foto[h] * hoehe * 1000, 1) for h in sorted(foto) if Seitentiefe.BAND[0] <= h <= Seitentiefe.BAND[1]}}
        for name, profil in profile.items():
            aus[name] = {str(h): round(v['tiefe'] * hoehe * 1000, 1) for h, v in sorted(profil.items()) if Seitentiefe.BAND[0] <= h <= Seitentiefe.BAND[1]}
            ab = Seitentiefe.abweichung(profil, foto, hoehe)
            if ab:
                aus['abweichung_' + name] = {k: ab[k] for k in ('mittel_mm', 'max_mm', 'tiefer_als_foto')}
        return aus
