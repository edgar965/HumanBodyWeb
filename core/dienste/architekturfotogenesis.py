# -*- coding: utf-8 -*-
"""Architekturfotogenesis — die Daten für Hilfe → Architektur → Foto-Genesis (24.10.2026): Fotos → KI → Genesis-Modell.

Edgar: „erstelle eine neue Seite hilfe - Architektur - 3d-3d-AI [gemeint 2d-3d-AI] in der Art von /hilfe/architektur/mesh3dai/ und mach genau wie diese Seite die komplette Dokumentation, inkl. grafischer
Darstellung des neuronalen Netzes“. Teile: Grafik und Netz (`Architekturfotogenesisbild`, `…netz`), Messwerte (`…messung`), andere Anbieter (`…andere`), Entscheidungen, Plan, GPU (`…plan`),
dazu die Jobs von der Platte (`Fotogenesisjobs`). Gelesen wird beim Aufruf; was nicht gelesen werden kann, steht als Befund oben auf der Seite.
"""

import logging

from .fotogenesisjobs import Fotogenesisjobs
from .architekturfotogenesisandere import Architekturfotogenesisandere
from .architekturfotogenesisbild import Architekturfotogenesisbild
from .architekturfotogenesiskette import Architekturfotogenesiskette
from .architekturfotogenesispshuman import Architekturfotogenesispshuman
from .architekturfotogenesiskis import Architekturfotogenesiskis
from .architekturfotogenesiskopfnetz import Architekturfotogenesiskopfnetz
from .architekturfotogenesismessung import Architekturfotogenesismessung
from .architekturfotogenesisnetz import Architekturfotogenesisnetz
from .architekturfotogenesisplan import Architekturfotogenesisplan
from .architekturfotogenesisstand import Architekturfotogenesisstand

logger = logging.getLogger('core')

__all__ = ['Architekturfotogenesis']


class Architekturfotogenesis:
    @classmethod
    def kontext(cls):
        befunde = []

        def teil(name, rechnung):
            """Ein Teil darf die Seite nicht mitnehmen — der Grund steht oben als Befund und im Log (wie die Mesh-Genesis-Seite)."""
            try:
                return rechnung()
            except Exception as fehler:     # noqa: BLE001 - Grund steht auf der Seite und im Log
                logger.exception('Hilfe Foto-Genesis: Teil %s', name)
                befunde.append('%s: %s: %s' % (name, type(fehler).__name__, fehler))
                return None

        jobs = Fotogenesisjobs.alle()
        edgar = next((j for j in jobs if j['id'] == 'edgartrip'), None)
        vergleich = Architekturfotogenesismessung.netzvergleich()
        if vergleich is None:
            befunde.append('Der Netzvergleich OlesiaWalk (_bild3d/OlesiaWalk_tripovergleich/vergleich.json) fehlt — die Tabelle in Abschnitt 1 bleibt leer.')
        pakete = Architekturfotogenesismessung.pakete()
        fehlt = [p for p, f in pakete.items() if not f]
        if fehlt:
            befunde.append('In python10 fehlt: %s.' % ', '.join(fehlt))
        return {
            # 24.10.2026 abends: die gebaute Kette zuerst (Edgar: „eine übergeordnete Grafik mit Kästchen und Ablauf“, „für alle KIs eine einzelne Grafik“, „Mach die KopfKI, Haut KI rein“)
            'kette': teil('Kette', Architekturfotogenesiskette.uebersicht), 'kopfki_bild': teil('KopfKI', Architekturfotogenesiskette.kopfki),
            # 07.11.2026 (Edgar: „Passe die seite … an mit dem was wir jetzt tun, und füge die Beschreibung der pshuman ein“)
            'heute_bild': teil('Heute', Architekturfotogenesispshuman.heute), 'pshuman_bild': teil('PSHuman', Architekturfotogenesispshuman.pshuman), 'master_bild': teil('Mehrere Fotos', Architekturfotogenesispshuman.master),
            'fotokopf': ((edgar or {}).get('kopf') or {}).get('fotokopf'),
            'kis': teil('KIs (architekturfotogenesisnetze.json)', Architekturfotogenesiskis.kontext),
            # 26.10.2026 (Edgar: „aktualisiere … damit wir das nicht wieder vergessen“): die Kopf-KI, eigenes Netz aus Teilen der KopfKI
            'kopfnetz': teil('Kopf-KI', Architekturfotogenesiskopfnetz.kontext),
            'stand': {'einpassung': teil('Einpassung', Architekturfotogenesisstand.einpassung), 'pruefungen': teil('Prüfung', Architekturfotogenesisstand.pruefungen) or [],
                      'gruppen': Architekturfotogenesisstand.GRUPPEN, 'heute': Architekturfotogenesisstand.HEUTE},
            'bild': Architekturfotogenesisbild.svg(),
            'schichten': Architekturfotogenesisnetz.schichten(),
            'gewichte': Architekturfotogenesisnetz.summe(),
            'danach': Architekturfotogenesisnetz.danach(),
            'masse': {'tokens': Architekturfotogenesisnetz.tokens(), 'ansichten': Architekturfotogenesisnetz.ANSICHTEN, 'bild': Architekturfotogenesisnetz.BILD,
                      'formregler': Architekturfotogenesisnetz.FORMREGLER, 'knochen': Architekturfotogenesisnetz.KNOCHEN},
            'jobs': [j for j in jobs if j['art'] == 'export'],
            'tests': [j for j in jobs if j['art'] == 'foto'],
            'deckung': Architekturfotogenesismessung.DECKUNG,
            'deckung_quelle': Architekturfotogenesismessung.DECKUNG_QUELLE,
            'fehlmessung': Architekturfotogenesismessung.FEHLMESSUNG,
            'netzvergleich': vergleich,
            'zeiten': Architekturfotogenesismessung.zeiten(),
            'vorrat': Architekturfotogenesismessung.VORRAT,
            'pakete': pakete,
            'andere': Architekturfotogenesisandere.eintraege(),
            'einordnung': Architekturfotogenesisandere.EINORDNUNG,
            'entscheidungen': Architekturfotogenesisplan.ENTSCHEIDUNGEN,
            'schritte': Architekturfotogenesisplan.SCHRITTE,
            'gpu': Architekturfotogenesisplan.GPU,
            'offen': Architekturfotogenesisplan.OFFEN,
            'befunde': befunde,
        }
