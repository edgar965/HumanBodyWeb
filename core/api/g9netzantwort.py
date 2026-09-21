# -*- coding: utf-8 -*-
u"""G9netzantwort — ein Genesis-9-Netz (Koerper, Anhang, Kleidungsteil) als
Antwort-Dict: Punkte, Dreiecke, Normalen, UV, Gruppen, Haut — base64 mit den
Breiten aus `Netzantwort.TYPEN`, Hautgewichte kompakt (uint16/uint8).

Aus `g9figur.py` herausgeloest (18.09.2026 nachts, die Datei stand bei 304
Zeilen); `G9figur._netzantwort` zeigt weiter hierher.
"""
import numpy as np

from ..daten.netzantwort import Netzantwort

__all__ = ['G9netzantwort']


class G9netzantwort:

    @staticmethod
    def aus(netz):
        antwort = Netzantwort.aus(netz['punkte'], faces=netz['dreiecke'],
                                  normals=netz['normalen'], uvs=netz['uv'])
        antwort['gruppen'] = netz['gruppen']
        antwort['hautgewichte'] = Netzantwort.hautgewichte(netz.get('haut'),
                                                           kompakt=True)
        if netz.get('dicke') is not None:
            # Duenne 0..1 je Punkt — das Durchlicht der Haut (`G9dicke`).
            antwort['dicke'] = Netzantwort.feld(netz['dicke'], 'dicke')
        if netz.get('stoff') is not None:
            # dForce-Kleidung (`G9stoff`): Freiheit 0..1 und Lage je Kaefigpunkt.
            antwort['stoff'] = {'frei': Netzantwort.feld(netz['stoff']['frei'], 'frei'),
                                'kaefig': Netzantwort.feld(netz['stoff']['kaefig'],
                                                           'kaefig')}
        if netz.get('bindung') is not None:
            # Oberflaechenbindung (`G9oberflaechenbindung`, 21.09.2026): je Punkt
            # drei Koerperpunkte (als float32 — der Shader liest Attribute als
            # Gleitkomma, -1 = ungebunden), Baryzentrik, Abstand, Mischung.
            b = netz['bindung']
            antwort['bindung'] = {art: Netzantwort.feld(b[art], art, typ=np.float32)
                                  for art in ('dreieck', 'bary', 'abstand', 'mischung')}
            # Die Stufe des KOERPERS (nicht des Stuecks: Nieten bleiben Kaefig).
            antwort['bindung']['stufen'] = int(b.get('stufen') or 0)
        if netz.get('art'):
            # Stranghaar: Linien statt Flaechen, `anteil` 0 (Wurzel) .. 1 (Spitze);
            # `kappe`: die Haarkappe darunter, unbeleuchtet.
            antwort['art'] = netz['art']
            if netz.get('anteil') is not None:
                antwort['anteil'] = Netzantwort.feld(netz['anteil'], 'anteil')
        return antwort
