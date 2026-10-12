# -*- coding: utf-8 -*-
"""Engine2d3dKleiderposeliste — die Pose aus dem Foto, wie die Karte „Pose" der Seite sie zeigt (11.10.2026).

Liest `ergebnis.pose` (`Engine2d3dKleiderpose`) und prüft, was davon auf der Platte liegt: nur Kontrollbilder, deren Datei da ist. `veraltet` sagt, dass Optionen oder Netz seit dem Lauf geändert wurden
(die Körper-Kette bräche dann ab, siehe `Engine2d3dKleiderpose.fuer_koerper`); `eingesetzt` heißt: die Körper-Kette nähme die Pose jetzt (Häkchen an, Stand passt).
"""

from ..daten.engine2d3dkleiderablage import Engine2d3dKleiderablage
from .engine2d3dkleideroptionen import Engine2d3dKleideroptionen
from .engine2d3dkleiderpose import Engine2d3dKleiderpose
from .engine2d3dkleiderposegelenke import Engine2d3dKleiderposegelenke

__all__ = ['Engine2d3dKleiderposeliste']


class Engine2d3dKleiderposeliste:
    @staticmethod
    def von(job):
        """`None`, wenn der Schritt noch nicht gerechnet hat, sonst `{stand, drehung, optionen, foto, abbildung, gelenke, masstab, bilder, veraltet, grund, eingesetzt}`."""
        ablage = Engine2d3dKleiderablage(job.kennung)
        pose, grund = Engine2d3dKleiderpose.stand(job, ablage)
        if not pose:
            return None
        bilder = {k: n for k, n in (pose.get('bilder') or {}).items() if ablage.pose(str(n)).is_file()}
        gelenke = dict(pose.get('gelenke') or {})
        gelenke['liste'] = [dict(g, text=Engine2d3dKleiderposegelenke.ANZEIGE.get(g.get('name'), g.get('name'))) for g in gelenke.get('liste') or []]
        an = Engine2d3dKleideroptionen.pose(job.optionen)['rechnen'] == 'an'
        return {
            'stand': pose.get('stand'), 'drehung': pose.get('drehung'), 'optionen': pose.get('optionen'), 'foto': pose.get('foto'), 'abbildung': pose.get('abbildung'),
            'netz_ausdehnung': pose.get('netz_ausdehnung'), 'gelenke': gelenke, 'masstab': pose.get('masstab'), 'bilder': bilder, 'dauer_sam_s': pose.get('dauer_sam_s'),
            'sam_neu_gerechnet': pose.get('sam_neu_gerechnet'), 'veraltet': bool(grund), 'grund': grund, 'eingesetzt': an and not grund,
        }
