# -*- coding: utf-8 -*-
"""Architekturai2d3d — die Daten für Hilfe → Architektur → 2d-3d-AI (24.10.2026): Fotos → KI → Genesis-Modell.

Edgar: „erstelle eine neue Seite hilfe - Architektur - 3d-3d-AI [gemeint 2d-3d-AI] in der Art von /hilfe/architektur/mesh3dai/ und mach genau wie diese Seite die komplette Dokumentation, inkl. grafischer
Darstellung des neuronalen Netzes“. Teile: Grafik und Netz (`Architekturai2d3dbild`, `…netz`), Messwerte (`…messung`), andere Anbieter (`…andere`), Entscheidungen, Plan, GPU (`…plan`),
dazu die Jobs von der Platte (`Ai2d3djobs`). Gelesen wird beim Aufruf; was nicht gelesen werden kann, steht als Befund oben auf der Seite.
"""

from .ai2d3djobs import Ai2d3djobs
from .architekturai2d3dandere import Architekturai2d3dandere
from .architekturai2d3dbild import Architekturai2d3dbild
from .architekturai2d3dmessung import Architekturai2d3dmessung
from .architekturai2d3dnetz import Architekturai2d3dnetz
from .architekturai2d3dplan import Architekturai2d3dplan

__all__ = ['Architekturai2d3d']


class Architekturai2d3d:
    @classmethod
    def kontext(cls):
        befunde = []
        jobs = Ai2d3djobs.alle()
        vergleich = Architekturai2d3dmessung.netzvergleich()
        if vergleich is None:
            befunde.append('Der Netzvergleich OlesiaWalk (_bild3d/OlesiaWalk_tripovergleich/vergleich.json) fehlt — die Tabelle in Abschnitt 1 bleibt leer.')
        pakete = Architekturai2d3dmessung.pakete()
        fehlt = [p for p, f in pakete.items() if not f]
        if fehlt:
            befunde.append('In python10 fehlt: %s.' % ', '.join(fehlt))
        return {
            'bild': Architekturai2d3dbild.svg(),
            'schichten': Architekturai2d3dnetz.schichten(),
            'gewichte': Architekturai2d3dnetz.summe(),
            'danach': Architekturai2d3dnetz.danach(),
            'masse': {'tokens': Architekturai2d3dnetz.tokens(), 'ansichten': Architekturai2d3dnetz.ANSICHTEN, 'bild': Architekturai2d3dnetz.BILD,
                      'formregler': Architekturai2d3dnetz.FORMREGLER, 'knochen': Architekturai2d3dnetz.KNOCHEN},
            'jobs': [j for j in jobs if j['art'] == 'export'],
            'tests': [j for j in jobs if j['art'] == 'foto'],
            'deckung': Architekturai2d3dmessung.DECKUNG,
            'deckung_quelle': Architekturai2d3dmessung.DECKUNG_QUELLE,
            'fehlmessung': Architekturai2d3dmessung.FEHLMESSUNG,
            'netzvergleich': vergleich,
            'zeiten': Architekturai2d3dmessung.zeiten(),
            'vorrat': Architekturai2d3dmessung.VORRAT,
            'pakete': pakete,
            'andere': Architekturai2d3dandere.eintraege(),
            'einordnung': Architekturai2d3dandere.EINORDNUNG,
            'entscheidungen': Architekturai2d3dplan.ENTSCHEIDUNGEN,
            'schritte': Architekturai2d3dplan.SCHRITTE,
            'gpu': Architekturai2d3dplan.GPU,
            'offen': Architekturai2d3dplan.OFFEN,
            'befunde': befunde,
        }
