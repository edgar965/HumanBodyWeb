# -*- coding: utf-8 -*-
"""Engine2d3dKleidersegmentierungsliste — die Fotos nach dem Schritt „Segmentierung", wie die Seite sie zeigt (04.10.2026).

Liest `segmentierung/segmentierung.json` (`sapiens_stand`) und gibt je Foto Datei, Rolle, Überlagerung (Vorschaubild mit den Stückfarben), Anteile je Stück und die Güte der Einpassung
(Silhouetten-IoU Netz ↔ Foto) zurück, dazu die Kennzahlen der Flächen. `veraltet` sagt, dass die Ablage nicht mehr zum Netz und zu den vorbereiteten Fotos passt (ein neues Netz, eine neue
Vorbereitung): Die Seite zeigt sie dann mit Warnung statt als aktuellen Stand — und die Kleidungsmaske nimmt die Stimmen in diesem Fall auch nicht (`Sapiensmaske.laden`, gleiche Prüfung
auf Netzgröße und Änderungszeit).

`kleidung` ist, was der Schritt „kleidung" der Körper-Kette daraus gemacht hat (`job.ergebnis.kleidung.sapiens`): benutzt oder nicht (mit Grund), wie viele Flächen anders als nach Farbe und Lage.
"""

import logging

from ..daten.engine2d3dkleiderablage import Engine2d3dKleiderablage
from ..daten.wrapperpfad import Wrapperpfad
from .engine2d3dkleideroptionen import Engine2d3dKleideroptionen
from .engine2d3dkleidersegmentierung import Engine2d3dKleidersegmentierung
from .engine2d3dkleidersegmentierungsoptionen import Engine2d3dKleidersegmentierungsoptionen

logger = logging.getLogger('core')

__all__ = ['Engine2d3dKleidersegmentierungsliste']


class Engine2d3dKleidersegmentierungsliste:
    @staticmethod
    def von(job):
        """`None`, wenn der Schritt noch nicht gerechnet hat, sonst `{stand, verwenden, veraltet, grund, bilder, kennzahlen, kleidung}`."""
        ablage = Engine2d3dKleiderablage(job.kennung)
        ordner = str(ablage.segmentierung())
        with Wrapperpfad():
            from sapiens_stand import Sapiensstand
        stand = Sapiensstand.lesen(ordner)
        if not stand:
            return None
        aktuelle = {b['datei']: b['png'] for b in Engine2d3dKleidersegmentierung.bilder_fuer(job, ablage)}
        netz = ablage.netzdatei(original=True)
        einstellungen = Engine2d3dKleideroptionen.segmentierung(job.optionen)
        passt, grund = Sapiensstand.aktuell(ordner, str(netz) if netz else None, aktuelle, Engine2d3dKleidersegmentierungsoptionen.rechenoptionen(einstellungen))
        bilder = []
        for e in stand.get('bilder', []):
            if (ablage.segmentierung() / str(e.get('ueberlagerung') or '-')).is_file():
                bilder.append({k: e.get(k) for k in ('datei', 'rolle', 'ueberlagerung', 'anteile', 'iou', 'sichtbar')})
        kleidung = ((job.ergebnis or {}).get('kleidung') or {}).get('sapiens')
        haar = ((job.ergebnis or {}).get('haar') or {}).get('sapiens')
        return {'stand': stand.get('stand'), 'verwenden': einstellungen.get('verwenden'), 'haar_quelle': einstellungen.get('haar'),
                'veraltet': not passt, 'grund': grund, 'bilder': bilder, 'kennzahlen': stand.get('kennzahlen'), 'kleidung': kleidung, 'haar': haar}
