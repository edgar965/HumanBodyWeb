# -*- coding: utf-8 -*-
"""Engine2d3dKleiderkopfliste — die Kopfausschnitte und das Kopfnetz, wie die Karte „Kopf" der Seite sie zeigt (07.10.2026).

Liest `ergebnis.kopf` (`Engine2d3dKleiderkopf`) und prüft, was davon auf der Platte liegt: nur Ausschnitte, deren Datei da ist; das Netz nur, wenn `kopf/mesh.glb` da ist. `veraltet` sagt, dass Modell oder
Flächenzahl seit dem Lauf geändert wurden — die Karte zeigt dann die Warnung statt eines aktuellen Stands. `eingesetzt` heißt: Die Körper-Kette nähme das Netz jetzt (Häkchen an, Netz da).
"""

from ..daten.engine2d3dkleiderablage import Engine2d3dKleiderablage
from .engine2d3dkleiderkopf import Engine2d3dKleiderkopf
from .engine2d3dkleideroptionen import Engine2d3dKleideroptionen

__all__ = ['Engine2d3dKleiderkopfliste']


class Engine2d3dKleiderkopfliste:
    ANZEIGE = ('rolle', 'quelle', 'datei', 'breite', 'hoehe', 'kopf_anteil')

    @staticmethod
    def von(job):
        """`None`, wenn der Schritt noch nicht gerechnet hat, sonst `{stand, bilder, netz, optionen, veraltet, grund, eingesetzt}`."""
        kopf = (job.ergebnis or {}).get('kopf')
        if not kopf:
            return None
        ablage = Engine2d3dKleiderablage(job.kennung)
        bilder = [{k: b.get(k) for k in Engine2d3dKleiderkopfliste.ANZEIGE} for b in kopf.get('bilder') or [] if ablage.kopf(str(b.get('datei') or '-')).is_file()]
        netz = kopf.get('netz')
        if netz and not ablage.kopf(str(netz.get('datei') or '-')).is_file():
            netz = None
        jetzt = Engine2d3dKleideroptionen.kopf(job.optionen)
        gerechnet = kopf.get('optionen') or {}
        anders = [k for k in ('modell', 'flaechen') if gerechnet.get(k) != jetzt[k]]
        return {
            'stand': kopf.get('stand'), 'bilder': bilder, 'netz': netz, 'optionen': gerechnet,
            'veraltet': bool(anders), 'grund': 'geändert seit dem Lauf: %s' % ', '.join(anders) if anders else '',
            'eingesetzt': Engine2d3dKleiderkopf.netz_fuer(job, ablage) is not None,
        }
