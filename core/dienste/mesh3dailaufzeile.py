# -*- coding: utf-8 -*-
"""Mesh3dailaufzeile — die Zeile oben auf der Jobseite von Mesh3D-AI: wann gerechnet, wie lange (22.10.2026, Edgar: „im job schreibe oben eine Zeile mit dem Datum des Laufs und die Dauer“).

Dieselben Zahlen wie die Spalten „Zuletzt gerechnet“ (`Mesh3dairechendatum`) und „Laufzeit“ (`Mesh3dailaufzeit`) der Jobliste, dazu — falls der Job Trainingsjob der Kleider-KI ist — der jüngste Lauf von
Stufe 2 mit seiner Anfangszeit (aus dem Namen des Laufs) und Dauer (`lauf_ergebnis.json` → `sekunden.gesamt`). Nur gemessene Zeiten; fehlt eine, steht „—“ und der Grund im Tooltip.

    Mesh3dailaufzeile.teile(job) -> [{'titel', 'wert', 'tipp'}]
"""
import json
import logging
import re
from datetime import datetime

from .mesh3daidatensatz import Mesh3daidatensatz
from .mesh3dailaufzeit import Mesh3dailaufzeit
from .mesh3dairechendatum import Mesh3dairechendatum

logger = logging.getLogger('core')

__all__ = ['Mesh3dailaufzeile']


class Mesh3dailaufzeile:
    #: Name eines Stufe-2-Laufs: `JJJJ.MM.TT.HH.MM_<job>_…` — die Zeit ist der Start.
    LAUFNAME = re.compile(r'^(\d{4})\.(\d{2})\.(\d{2})\.(\d{2})\.(\d{2})_')

    @classmethod
    def teile(cls, job):
        aus = []
        letztes = Mesh3dairechendatum.letztes(job)
        if letztes:
            aus.append({'titel': 'Zuletzt gerechnet', 'wert': '%s (%s)' % (datetime.fromtimestamp(letztes['zeit']).strftime('%d.%m.%Y %H:%M'), letztes['was']),
                        'tipp': '%s — %s' % (letztes['was'], letztes['datei'])})
        else:
            aus.append({'titel': 'Zuletzt gerechnet', 'wert': '—', 'tipp': 'Noch nichts gerechnet'})
        laufzeit = Mesh3dailaufzeit.job(job)
        aus.append({'titel': 'Dauer', 'wert': Mesh3dailaufzeit.text(laufzeit['sekunden']) if laufzeit else '—',
                    'tipp': Mesh3dailaufzeit.titel(laufzeit) if laufzeit else 'Keine gemessene Laufzeit abgelegt'})
        stufe2 = cls._stufe2(job)
        if stufe2:
            aus.append(stufe2)
        return aus

    @classmethod
    def _stufe2(cls, job):
        """Der jüngste Lauf der Kleider-KI (Stufe 2), an dem dieser Job Trainingsjob war — oder None."""
        from .mesh3daitestfaelle import Mesh3daitestfaelle
        try:
            laeufe = Mesh3daitestfaelle.fuer_job(job['id'])
        except (OSError, ValueError) as fehler:
            logger.warning('Mesh3dailaufzeile: Testfälle von %s nicht lesbar (%s)', job.get('id'), fehler)
            return None
        name = (laeufe[0].get('lauf') if laeufe else None) or ''
        treffer = cls.LAUFNAME.match(name)
        if not treffer:
            return None
        j, m, t, h, mi = treffer.groups()
        try:
            e = json.loads((Mesh3daidatensatz.ordner('_stufe2') / 'laeufe' / name / 'lauf_ergebnis.json').read_text(encoding='utf-8'))
            sekunden = float((e.get('sekunden') or {}).get('gesamt'))
        except (OSError, ValueError, TypeError):
            sekunden = None
        dauer = Mesh3dailaufzeit.text(sekunden) if sekunden else '— (keine Dauer im Lauf abgelegt)'
        return {'titel': 'Kleider-KI', 'wert': 'Lauf %s.%s.%s %s:%s, Dauer %s' % (t, m, j, h, mi, dauer), 'tipp': 'Jüngster Lauf von Stufe 2 mit diesem Job als Trainingsjob: %s' % name}
