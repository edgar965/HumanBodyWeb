# -*- coding: utf-8 -*-
"""Meshfigureinstellungen — die Auftragsseite „Mesh to 3D" speichert jede Eingabe sofort (29.09.2026).

Edgar: „bei eingabe in irgend ein feld soll das automatisch gespeichert werden" und „mach mir bei den Jobs
Mesh to 3D die auswahl des Kopfes optional". Bis dahin kamen Optionen und Pfade erst mit „Neu berechnen" an
den Server — wer die Seite verließ, verlor sie.

    POST /api/meshfigur/<id>/einstellungen/   {optionen?, pfade?: {koerper, kopf}, kopf_an?: bool}
         → {ok, optionen, eingang, neu_eingelesen}   (400 mit Klartext bei einem falschen Pfad — die
           Optionen sind dann trotzdem gespeichert; 409 während eines Laufs)

Ein geänderter Pfad wird SOFORT eingelesen (`Meshfigureingang.aendern`, die Datei wird kopiert). Damit der
nächste Start trotzdem bei der Erkennung beginnt — ein anderes Netz ist ein anderer Auftrag —, steht
`eingang.neu_eingelesen`; `Meshfigurendpunkte.starten` nimmt es heraus. `kopf_an: false` nimmt das Kopfnetz
heraus, merkt sich aber seinen Pfad (`eingang.kopf_gemerkt`), damit das Wiedereinschalten ihn kennt.
"""

import json

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST

from ..daten.meshfigurablage import Meshfigurablage
from ..dienste.meshfigurarbeiter import Meshfigurarbeiter
from ..dienste.meshfigureingang import Meshfigureingang
from ..dienste.meshfiguroptionen import Meshfiguroptionen
from ..models import Meshfigurauftrag

__all__ = ['Meshfigureinstellungen']


class Meshfigureinstellungen:
    NEU = 'neu_eingelesen'
    GEMERKT = 'kopf_gemerkt'

    @staticmethod
    @require_POST
    def speichern(request, job_id):
        job = get_object_or_404(Meshfigurauftrag, pk=job_id)
        if job.laeuft and Meshfigurarbeiter.lebt(job):
            return JsonResponse({'error': 'Der Auftrag läuft — Änderungen erst nach dem Lauf'}, status=409)
        try:
            rumpf = json.loads(request.body or b'{}')
        except ValueError:
            rumpf = {}
        felder = []
        if isinstance(rumpf.get('optionen'), dict):
            job.optionen = Meshfiguroptionen.pruefen({**(job.optionen or {}), **rumpf['optionen']})
            felder.append('optionen')
        fehler, neu = None, False
        if isinstance(rumpf.get('pfade'), dict):
            try:
                kopf_an = rumpf.get('kopf_an', True) is not False
                neu = Meshfigureinstellungen.pfade(job, rumpf['pfade'], kopf_an)
                felder.append('eingang')
            except ValueError as f:
                fehler = str(f)
        if felder:
            job.save(update_fields=felder + ['updated_at'])
        antwort = {'ok': fehler is None, 'optionen': job.optionen, 'eingang': job.eingang,
                   'neu_eingelesen': neu}
        if fehler:
            antwort['error'] = fehler
        return JsonResponse(antwort, status=400 if fehler else 200)

    @classmethod
    def pfade(cls, job, pfade, kopf_an):
        """Pfade übernehmen (ValueError bei falschem Pfad) → ob ein Netz neu eingelesen wurde."""
        eingang = dict(job.eingang or {})
        kopf = str(pfade.get('kopf') or '').strip()
        if kopf_an:
            eingang.pop(cls.GEMERKT, None)
        elif kopf:
            eingang[cls.GEMERKT] = kopf
        gemerkt = eingang.pop(cls.GEMERKT, None)
        neu_vorher = eingang.pop(cls.NEU, False)
        eingang, geaendert = Meshfigureingang(Meshfigurablage(job.kennung)).aendern(
            eingang, {'koerper': pfade.get('koerper'), 'kopf': kopf if kopf_an else ''})
        if gemerkt:
            eingang[cls.GEMERKT] = gemerkt
        if geaendert or neu_vorher:
            eingang[cls.NEU] = True
        job.eingang = eingang
        return geaendert

    @classmethod
    def neu_eingelesen(cls, job):
        """Für `starten`: war seit dem letzten Start ein Netz neu eingelesen? Nimmt die Marke heraus."""
        eingang = dict(job.eingang or {})
        if not eingang.pop(cls.NEU, False):
            return False
        job.eingang = eingang
        job.save(update_fields=['eingang', 'updated_at'])
        return True
