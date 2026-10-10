# -*- coding: utf-8 -*-
"""Blendimportfigur — der Körper einer .blend wird über „Mesh to 3D" zur Genesis-9-Figur.

Konzept (Hilfe → Architektur → Genesis, 08.10.2026): Regler-Fit, Gesichtskette und Eigenmorph von „Mesh to 3D" sind
gebaut und gemessen; der Import gibt ihnen statt eines Scans den NACKTEN Körper (`Blendimportkoerper`). Dafür passen die
Optionen: keine Frisur und keine Haarkarten (das Haar wird ein eigenes Stück), Kleidung „wie Haut" (es gibt keine im
Netz), Kopfhaut „Haut lassen" (eigenes Haar), kein Modell `<Name> Mesh` — das Modell schreibt der Import selbst
(`Blendimportmodell`), mit Kleidern, Haar und der gebackenen Haut.

Der Auftrag ist ein gewöhnlicher `Meshfigurauftrag`: Er steht in der Liste von „Mesh to 3D", seine Seite zeigt Erkennung,
Runden und Vergleich. Gerechnet wird er im Prozess des Imports (`Meshfigurlauf.ausfuehren`), nicht in einem zweiten.
"""

import logging

from django.utils import timezone

logger = logging.getLogger('core')

__all__ = ['Blendimportfigur']


class Blendimportfigur:
    OPTIONEN = {
        'frisur': 'aus',
        'haarkarten': 'aus',
        'kleidung': 'wie_haut',
        'kopfhaut': 'haut',
        'textur': 'mesh',
        'modell': 'aus',
        'einheit': 'meter',
        'gesicht': 'an',
        'eigenmorph': 'an',
    }

    def __init__(self, ablage, name, basis):
        self.ablage = ablage
        self.name = name
        self.basis = basis

    def anlegen(self, glb):
        from ..daten.auftragskennung import Auftragskennung
        from ..daten.meshfigurablage import Meshfigurablage
        from ..models import Meshfigurauftrag
        from .meshfigureingang import Meshfigureingang
        from .meshfiguroptionen import Meshfiguroptionen

        kennung = Auftragskennung.frei(timezone.now(), lambda k: Meshfigurauftrag.objects.filter(kennung=k).exists())
        ablage = Meshfigurablage(kennung)
        eingang = Meshfigureingang(ablage).anlegen([], str(glb), None)
        optionen = Meshfiguroptionen.pruefen(dict(self.OPTIONEN, basis=self.basis))
        job = Meshfigurauftrag.objects.create(kennung=kennung, name=self.name, eingang=eingang, optionen=optionen)
        logger.info('Blender-Import %s: Auftrag „Mesh to 3D" %s angelegt', self.ablage.kennung, kennung)
        return job

    @staticmethod
    def rechnen(job):
        """Den Auftrag in DIESEM Prozess rechnen; danach muss er „fertig" sein, sonst ein Fehler mit seinem Grund."""
        from ..models import Meshfigurauftrag
        from .meshfigurlauf import Meshfigurlauf

        job.status = 'laeuft'
        job.started_at = timezone.now()
        job.save(update_fields=['status', 'started_at', 'updated_at'])
        lauf = Meshfigurlauf(job.id)
        # Das Körper-Tor (`Meshfigurrumpfpruefung`, 01.10.2026) fängt Scans mit Stoff ab, deren Rumpf nicht stimmt. Hier ist
        # der Körper nackt und sauber: im ersten Lauf (2026.10.08.11.28.34) Rumpftiefe 95,5–101 % des Netzes, Abstand
        # Figur↔Netz 2,67 mm RMS, aber 11 Brust-/Schulterregler am Anschlag (Soll ≤ 8) — die Brust ist größer, als die Regler
        # hergeben. „melden": der Lauf geht weiter, der Befund steht in `ergebnis.koerper.tor` (wie bei „2D3D Kleider").
        lauf.tor = 'melden'
        lauf.ausfuehren()
        job = Meshfigurauftrag.objects.get(pk=job.pk)
        if job.status != 'fertig':
            raise RuntimeError('Mesh to 3D %s: %s (%s)' % (job.kennung, job.status, job.error_message or 'ohne Grund'))
        return job
