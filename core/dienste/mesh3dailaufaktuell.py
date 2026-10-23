# -*- coding: utf-8 -*-
"""Mesh3dailaufaktuell — der Stand für den Reiter „Lauf Aktuell“ auf /mesh-3D-AI/ (18.10.2026): was gerade rechnet, mit CPU, GPU und Fortschritt.

Edgar: „mach auch einen neuen Tab: ‚Lauf Aktuell‘, wo du den gerade laufenden Job listest, mit GPU, CPU-Verbrauch und Fortschrittsbalken“.
  * Rechner gesamt: djangoBase `SystemStats` (nvidia-smi + psutil, geglättet, dieselbe Messung wie die Auslastungsleiste anderer Projekte);
  * je Job: Prozessbaum (`Mesh3dailaufprozesse`), GPU je Prozess aus den Windows-Leistungszählern (`Mesh3daigpuprozesse`);
  * Fortschritt von der Platte: Training = Epoche von N des laufenden Laufordners (`Mesh3daiformtraining`), Datenlauf = Proben mit MIA bzw. Wolke Fassung 9 der Formvarianten,
    die der Befehl nennt (`Mesh3daiformvarianten`). Job, Schritt und Art des Fortschritts je Skript: `Mesh3dailaufbeschreibung` (seit 20.10.2026; vorher `REGELN` hier).
  * je Job der Ablauf (Kette und Schritt n von m), wenn die Warteschlange den laufenden Schritt diesem Prozess zuordnet; die Plätze der GPU-Sperre (`gpu.lock`, `gpu.lock.2`).
Gemessen wird im Hintergrund (djangoBase `HintergrundCache`, erneuert, wenn älter als `TAKT_S` − 1): eine Messung kostet rund 1 s (zwei Zählerabfragen im Abstand von 0,5 s beim ersten Mal),
die Anfrage bekommt sofort den zuletzt bekannten Stand.

  * Warteschlange: die Ketten mit ihren Schritten (fertig/läuft/wartet) aus `ProjektTemp/mia_daten/warteschlange.json` und den Logs (`Mesh3daiwarteschlange`).

    Mesh3dailaufaktuell.lesen() -> {zeit, takt_s, system, sperre, plaetze, jobs, laeufe_ohne_prozess, ketten, warteschlange, fremde_gpu, kerne}
"""

import time
from pathlib import Path

from django.conf import settings

from .mesh3daiformtraining import Mesh3daiformtraining
from .mesh3dailaufbeschreibung import Mesh3dailaufbeschreibung
from .mesh3daiformvarianten import Mesh3daiformvarianten
from .mesh3daigpuprozesse import Mesh3daigpuprozesse
from .mesh3dailaufprozesse import Mesh3dailaufprozesse
from .mesh3daiwarteschlange import Mesh3daiwarteschlange

__all__ = ['Mesh3dailaufaktuell']


class Mesh3dailaufaktuell:
    TAKT_S = 5
    #: so viele neue Proben braucht das Tempo, bevor eine Restzeit genannt wird
    MIN_PROBEN = 5
    _speicher = None

    @classmethod
    def lesen(cls):
        if cls._speicher is None:
            from djangobase.hintergrund_cache import HintergrundCache
            cls._speicher = HintergrundCache('mesh3dai-lauf-aktuell', cls.messen, cls.TAKT_S - 1)
        return cls._speicher.holen()

    @classmethod
    def messen(cls):
        from djangobase.system_stats import SystemStats

        jetzt = time.time()
        prozesse = Mesh3dailaufprozesse.lesen(Mesh3daigpuprozesse.lesen())
        laufend = [lf for lf in Mesh3daiformtraining.laeufe(jetzt) if lf['zustand'] == 'läuft']
        varianten = Mesh3daiformvarianten.alle(jetzt)
        jobs = []
        namen = Mesh3dailaufbeschreibung.namen()
        for job in prozesse['jobs']:
            beschreibung = Mesh3dailaufbeschreibung.beschreiben(job, namen)
            fortschritt = beschreibung.pop('fortschritt_art')
            job = {**job, **beschreibung, 'fortschritt': [], 'lauf': None, 'ablauf': None, 'befehl_kurz': cls._kurz(job['argumente'])}
            if fortschritt == 'training':
                lf = next((x for x in laufend if (x['start'] or 0) >= job['start'] - 90), None)
                if lf is not None:
                    laufend.remove(lf)
                    job['lauf'] = {'name': lf['name'], 'kurz': lf['kurz'], 'adresse': '/mesh-3D-AI/formtraining/%s/' % lf['name']}
                job['fortschritt'] = cls._training(lf)
            elif fortschritt == 'daten':
                job['fortschritt'] = cls._daten(job, varianten, jetzt)
            jobs.append(job)
        warteschlange = Mesh3daiwarteschlange.lesen(prozesse['ketten'], jobs, jetzt)
        cls._ablauf(jobs, warteschlange)
        return {'zeit': jetzt, 'takt_s': cls.TAKT_S, 'system': SystemStats.lesen(), 'sperre': Mesh3daiformtraining.gpu(), 'plaetze': cls._plaetze(), 'jobs': jobs,
                'laeufe_ohne_prozess': [{'name': lf['name'], 'kurz': lf['kurz'], 'adresse': '/mesh-3D-AI/formtraining/%s/' % lf['name'], 'fortschritt': cls._training(lf)}
                                        for lf in laufend],
                'ketten': prozesse['ketten'], 'warteschlange': warteschlange,
                'fremde_gpu': prozesse['fremde_gpu'], 'kerne': prozesse['kerne']}

    @staticmethod
    def _ablauf(jobs, warteschlange):
        """Je Job die Kette, deren laufender Schritt ihm gehört (`job` = PID, `Mesh3daiwarteschlange._fortschritt`): Titel, Schritt n von m. Ohne Eintrag in der Warteschlange
        die Kette aus den Vorfahren des Prozesses (`kette`, Dateiname) — Git-Bash trennt die Elternkette oft, dann bleibt es leer."""
        je_pid = {j['pid']: j for j in jobs}
        for k in warteschlange.get('ketten') or ():
            for n, s in enumerate(k['schritte'], 1):
                job = je_pid.get(s.get('job'))
                if job is not None and s.get('zustand') == 'läuft':
                    job['ablauf'] = {'titel': k['titel'], 'schritt': n, 'von': len(k['schritte']), 'schritt_titel': s['titel']}
        for job in jobs:
            if job['ablauf'] is None and job.get('kette'):
                name = job['kette'][0]
                job['ablauf'] = {'titel': name.removeprefix('mesh3dai_').removesuffix('.sh').replace('_', ' '), 'schritt': None, 'von': None, 'schritt_titel': name}

    @staticmethod
    def _plaetze():
        """Die zwei Plätze der GPU-Sperre (`gpu_sperre.py`: `gpu.lock`, `gpu.lock.2`) — je Platz `{platz, name, seit}` oder `{platz}` (frei)."""
        ordner = Path(settings.TOOLS_ROOT).joinpath(*Mesh3daiformtraining.SPERRE).parent
        aus = []
        for platz, datei in ((1, 'gpu.lock'), (2, 'gpu.lock.2')):
            d = Mesh3daiformtraining._json(ordner / datei)
            if isinstance(d, dict) and d.get('name'):
                try:
                    seit = float(d.get('seit'))
                except (TypeError, ValueError):
                    seit = None
                aus.append({'platz': platz, 'name': str(d['name']), 'seit': seit})
            else:
                aus.append({'platz': platz})
        return aus

    @staticmethod
    def _training(lf):
        if lf is None:
            return [{'name': 'Fortschritt', 'fertig': 0, 'gesamt': None, 'text': 'lädt die Beispielfiguren', 'rest_s': None, 'hinweis': ''}]
        rest = lf['dauer_s'] / lf['epoche'] * (lf['epochen'] - lf['epoche']) if lf['epoche'] and lf['epochen'] and lf['dauer_s'] else None
        return [{'name': 'Fortschritt', 'fertig': lf['epoche'] or 0, 'gesamt': lf['epochen'],
                 'text': 'Durchgang %d von %s' % (lf['epoche'] or 0, lf['epochen'] or '?') if lf['epoche'] else 'hat gerade angefangen', 'rest_s': rest,
                 'hinweis': 'Ein Durchgang zeigt der KI jede Beispielfigur einmal. Der Stand wird alle 20 Durchgänge gemeldet; die Restzeit folgt dem bisherigen Tempo.'}]

    @classmethod
    def _daten(cls, job, varianten, jetzt):
        """Proben mit MIA bzw. Wolke Fassung 9 der Formvarianten, die der Befehl nennt (sonst aller); Restzeit aus den Proben, die seit dem Start des Prozesses neu dazukamen."""
        genannt = set(job['argumente'])
        gewaehlt = [v for v in varianten if v['name'] in genannt] or varianten
        geplant = sum(v['geplant'] for v in gewaehlt)
        aus = []
        for name, zahl, zeiten, hinweis in (
                ('1. In Grundhaltung bringen', 'mia', 'mia_zeiten', 'Haltungen, die schon in die Grundhaltung gebracht sind. Eine Haltung, bei der das nicht gelingt, fällt weg — '
                 'der Balken kann darum vor 100 % enden.'),
                ('2. Trainingsbilder ablegen', 'wolken', 'wolken_zeiten', 'Haltungen, deren Punktwolke für das Training fertig ist. Dieser Teil beginnt, wenn Teil 1 fertig ist.')):
            fertig = sum(v[zahl] for v in gewaehlt)
            neu = sum(1 for v in gewaehlt for t in v.get(zeiten, ()) if t >= job['start'])
            dauer = jetzt - job['start']
            tempo = neu / dauer if neu >= cls.MIN_PROBEN and dauer > 60 else None
            aus.append({'name': name, 'fertig': fertig, 'gesamt': geplant, 'text': '%s von %s Haltungen (%d Figuren)' % (cls._zahl(fertig), cls._zahl(geplant), len(gewaehlt)),
                        'rest_s': (geplant - fertig) / tempo if tempo and fertig < geplant else None,
                        'hinweis': hinweis + (' Seit dem Start %s fertig (%s je Stunde); die Restzeit rechnet mit diesem Tempo.' % (cls._zahl(neu), cls._zahl(round(tempo * 3600)))
                                              if tempo else '')})
        return aus

    @staticmethod
    def _kurz(argumente, n=10):
        return ' '.join(argumente[:n]) + (' … (+%d)' % (len(argumente) - n) if len(argumente) > n else '')

    @staticmethod
    def _zahl(wert):
        return f'{int(wert):,}'.replace(',', '.')
