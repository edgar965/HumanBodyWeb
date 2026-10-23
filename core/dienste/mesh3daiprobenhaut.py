# -*- coding: utf-8 -*-
"""Mesh3daiprobenhaut — die Haut der Ergebnisfigur einer Grundjob-Probe AUS DER KI (21.10.2026 abends, Konzept „Kleider wie das Ziel“ Abschnitt 10).

Edgar: „Die KI gibt keine Haut aus … die KI sollte die Textur, die Haut und so weiter ausgeben“ — und: „nicht die komplette Textur vom Eingang backen. Das ist doch eine normale KI.“
Der Hautkopf (`ProjektTemp/_wegwerf/mesh3dai_haut_*.py`, Training Eingang → Ziel) gibt je Texel der fünf Hautkacheln die Farbe aus; `mesh3dai_haut_einsatz.py` legt sie unter
`<Job>/kleider_ki/<nnnn>/haut/` ab (`1001.jpg` … `1005.jpg`, `haut.json` mit Lauf, Reglerstempel und Messung). Die Seite zeigt sie nur auf der Figur, für die sie gerechnet sind
(Stempel wie bei den Kleidern, `Mesh3daiprobenkleider`) — sonst Grundhaut und eine Zeile im Log.

    Mesh3daiprobenhaut.fuer(job, nr, figur_ergebnis) -> {'fototextur': {'1001': Adresse, …}, 'quelle': Text} | None
    Mesh3daiprobenhaut.datei(job, nr, name) -> Path | None
"""
import json
import logging
import re

from .mesh3daiprobenkleider import Mesh3daiprobenkleider

logger = logging.getLogger('core')

__all__ = ['Mesh3daiprobenhaut']


class Mesh3daiprobenhaut:
    NAME = re.compile(r'^100[1-5]\.jpg$')

    @staticmethod
    def ordner(job, nr):
        return Mesh3daiprobenkleider.ordner(job, nr) / 'haut'

    @classmethod
    def info(cls, job, nr):
        try:
            return json.loads((cls.ordner(job, nr) / 'haut.json').read_text(encoding='utf-8'))
        except (OSError, ValueError):
            return None

    @classmethod
    def fuer(cls, job, nr, figur_ergebnis):
        info = cls.info(job, nr)
        if not info:
            return None
        jetzt = Mesh3daiprobenkleider.stempel((figur_ergebnis or {}).get('regler'))
        if info.get('regler_stempel') != jetzt:
            logger.warning('Mesh3daiprobenhaut: %s Probe %s — Haut für Regler %s gerechnet, die Ergebnisfigur trägt %s; Grundhaut', job.get('id'), nr, info.get('regler_stempel'), jetzt)
            return None
        fassung = '%s_%s' % (info.get('lauf'), str(info.get('gerechnet', '')).replace(':', ''))
        kacheln = {str(k): '/api/mesh3dai/%s/haut/%d/%s?t=%s' % (job['id'], int(nr), name, fassung) for k, name in (info.get('kacheln') or {}).items() if cls.NAME.match(str(name))}
        if not kacheln:
            return None
        b = info.get('befund') or {}
        messung = (' Gegen die Haut des Ziels %.1f (Backen „nächster Eingangspunkt“: %.1f) von 255.' % (b['fehler_ki_alle'], b['fehler_naechster_punkt_alle'])
                   if 'fehler_ki_alle' in b and 'fehler_naechster_punkt_alle' in b else '')
        return {'fototextur': kacheln, 'quelle': 'Haut: vom Hautkopf %s ausgegeben (je Texel aus dem Eingang gelernt, nicht gebacken).%s' % (info.get('lauf'), messung)}

    @staticmethod
    def _test_ordner(job):
        """Tripo-Job (21.10.2026 nachts, Stufe 2 der Kleider-KI an OlesiaWalk): die Kacheln liegen beim Test seines Laufs, `_test/<kennung>/haut_<g>/` — oder None."""
        from .mesh3daidaten import Mesh3daidaten
        from .mesh3daiergebnisfigur import Mesh3daiergebnisfigur
        from .mesh3daitest import Mesh3daitest
        lauf = Mesh3daidaten.lauf(job['ordner'])
        try:
            e = json.loads((lauf / 'lauf_ergebnis.json').read_text(encoding='utf-8')).get('ergebnis_figur') or {} if lauf is not None else {}
        except (OSError, ValueError):
            return None
        p = Mesh3daitest.pfad(e.get('test')) if e.get('test') else None
        g = job.get('geschlecht') if job.get('geschlecht') in Mesh3daiergebnisfigur.GRUNDHAUT else 'weiblich'
        return None if p is None else p / ('haut_%s' % g)

    @classmethod
    def fuer_test(cls, job):
        """Hautkacheln der Stufe 2 eines Tripo-Jobs (eine Haut für alle Proben: dieselben Genesis-UV, die Stelle hängt nicht an der Form) → wie `fuer` oder None."""
        ordner = cls._test_ordner(job)
        try:
            info = json.loads((ordner / 'haut.json').read_text(encoding='utf-8')) if ordner is not None else None
        except (OSError, ValueError):
            return None
        if not info:
            return None
        fassung = '%s_%s' % (info.get('lauf'), str(info.get('gerechnet', '')).replace(':', ''))
        kacheln = {str(k): '/api/mesh3dai/%s/haut/0/%s?t=%s' % (job['id'], name, fassung) for k, name in (info.get('kacheln') or {}).items() if cls.NAME.match(str(name))}
        if not kacheln:
            return None
        b = info.get('befund') or {}
        messung = (' Gegen die Haut des Ziels %.1f (Mittel des Eingangs allein: %.1f) von 255, dieser Job ist im Training.' % (b['ki'], b['mittel_des_ausschnitts'])
                   if 'ki' in b and 'mittel_des_ausschnitts' in b else '')
        return {'fototextur': kacheln, 'quelle': 'Haut: von Stufe 2 der KI %s ausgegeben (je Texel aus dem Eingang gelernt, nicht gebacken).%s' % (info.get('lauf'), messung)}

    @classmethod
    def datei(cls, job, nr, name):
        if not cls.NAME.match(str(name)):
            return None
        pfad = cls.ordner(job, nr) / str(name)
        if not pfad.is_file() and int(nr) == 0:
            ordner = cls._test_ordner(job)
            pfad = ordner / str(name) if ordner is not None else pfad
        return pfad if pfad.is_file() else None
