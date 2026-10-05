# -*- coding: utf-8 -*-
"""Hosenteil — die Hose der Iterationsbilder aus dem Körpernetz, dieselbe wie auf der Bühne und im Film (04.10.2026).

Edgar: „Modell ist nicht wie die letzte Iteration … zwischen den Beinen hat die Hose Fehler: Textur ist rot (auf der Vorlage weiß), und die Hose geht
nicht an den Körper zwischen den Beinen." Bühne und Film zeigten seit Runde 57 die Hose aus dem verschweißten Körpernetz (`Hosenkoerper`, geschlossen im
Schritt, Streifen nur an der Außennaht); die Iterationsbilder (`Begutachtungsrunde`) rechneten weiter mit der drapierten GarmentCode-Hose, deren Schritt
klafft und deren Streifenbild an der Innennaht rot und kariert endet. Gemessen: Eine Änderung der Standhose (Abstand 22 → 12 mm) änderte die Beinbreite im
Render der Runde nur um 3 % — die Bilder wussten nichts davon.

`ersetzen(teile, ordner)` tauscht das Hosenteil (`sorte` beginnt mit `gc_hose`) gegen die Hose aus dem Körper DERSELBEN Runde (gehäutet, in der Haltung der
Fotos). Das Höhenband (Saum bis Bund) nimmt es vom Hosenteil, wie `Standmodellglb._hose`; die Textur (weiß mit den Seitenstreifen) liegt als PNG in `ordner`.
"""

import numpy as np

__all__ = ['Hosenteil']


class Hosenteil:
    HOSE = 'gc_hose'

    @classmethod
    def ersetzen(cls, teile, ordner):
        """`teile` mit der Körpernetz-Hose statt der GarmentCode-Hose; ohne Körper oder ohne Hose unverändert."""
        koerper = next((t for t in teile if t.get('art') == 'koerper'), None)
        if koerper is None:
            return teile
        return [cls._bauen(t, koerper, ordner) if t.get('art') != 'koerper' and str(t.get('sorte') or '').startswith(cls.HOSE) else t for t in teile]

    @staticmethod
    def _bauen(teil, koerper, ordner):
        from .hosenkoerper import Hosenkoerper
        y = np.asarray(teil['punkte'], dtype=np.float64)[:, 1]
        gebaut = Hosenkoerper(koerper['punkte'], koerper['dreiecke']).bauen(float(y.min()), float(y.max()) - Hosenkoerper.BUND_UNTER_HOSE)
        ordner.mkdir(parents=True, exist_ok=True)
        bild = ordner / 'hose_textur.png'
        Hosenkoerper.textur(gebaut).save(bild)
        anzahl = len(gebaut['dreiecke'])
        weiss = (1.0, 1.0, 1.0)
        neu = dict(teil, punkte=gebaut['punkte'], dreiecke=gebaut['dreiecke'], normalen=gebaut['normalen'], uv=gebaut['uv'], farbe=weiss,
                   textur=[{'ab': 0, 'anzahl': anzahl, 'albedo': str(bild), 'faktor': weiss}],
                   gruppen=[{'name': 'hose', 'index_ab': 0, 'index_anzahl': 3 * anzahl}])
        # Gehäutete Teile tragen ihre Ruhelage unter `ruhe`; die Fotoprojektion (`Begutachtungswerkzeug.fototextur`) kopiert deren Textur zurück —
        # mit der alten Ruhelage bekäme die neue Hose das Bild der GarmentCode-Hose. Deshalb eine eigene Kopie ohne `ruhe`.
        neu['ruhe'] = {k: v for k, v in neu.items() if k != 'ruhe'}
        return neu
