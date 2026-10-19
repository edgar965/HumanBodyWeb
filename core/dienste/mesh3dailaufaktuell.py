# -*- coding: utf-8 -*-
"""Mesh3dailaufaktuell — der Stand für den Reiter „Lauf Aktuell“ auf /mesh-3D-AI/ (18.10.2026): was gerade rechnet, mit CPU, GPU und Fortschritt.

Edgar: „mach auch einen neuen Tab: ‚Lauf Aktuell‘, wo du den gerade laufenden Job listest, mit GPU, CPU-Verbrauch und Fortschrittsbalken“.
  * Rechner gesamt: djangoBase `SystemStats` (nvidia-smi + psutil, geglättet, dieselbe Messung wie die Auslastungsleiste anderer Projekte);
  * je Job: Prozessbaum (`Mesh3dailaufprozesse`), GPU je Prozess aus den Windows-Leistungszählern (`Mesh3daigpuprozesse`);
  * Fortschritt von der Platte: Training = Epoche von N des laufenden Laufordners (`Mesh3daiformtraining`), Datenlauf = Proben mit MIA bzw. Wolke Fassung 9 der Formvarianten,
    die der Befehl nennt (`Mesh3daiformvarianten`). Welches Skript welchen Fortschritt hat, steht in `REGELN` — ein unbekanntes Skript erscheint ohne Balken.
Gemessen wird im Hintergrund (djangoBase `HintergrundCache`, erneuert, wenn älter als `TAKT_S` − 1): eine Messung kostet rund 1 s (zwei Zählerabfragen im Abstand von 0,5 s beim ersten Mal),
die Anfrage bekommt sofort den zuletzt bekannten Stand.

  * Warteschlange: die Ketten mit ihren Schritten (fertig/läuft/wartet) aus `ProjektTemp/mia_daten/warteschlange.json` und den Logs (`Mesh3daiwarteschlange`).

    Mesh3dailaufaktuell.lesen() -> {zeit, takt_s, system, sperre, jobs, laeufe_ohne_prozess, ketten, warteschlange, fremde_gpu, kerne}
"""

import time

from .mesh3daiformtraining import Mesh3daiformtraining
from .mesh3daiformvarianten import Mesh3daiformvarianten
from .mesh3daigpuprozesse import Mesh3daigpuprozesse
from .mesh3dailaufprozesse import Mesh3dailaufprozesse
from .mesh3daiwarteschlange import Mesh3daiwarteschlange

__all__ = ['Mesh3dailaufaktuell']


class Mesh3dailaufaktuell:
    TAKT_S = 5
    #: (Teil des Befehls, Art, Titel, was passiert — in Worten ohne Technik, Fortschritt) — die erste passende Zeile gilt.
    #: Edgar, 18.10.2026: „der laufende Job ist völlig gaga, und unverständlich. Was läuft denn?? Lass deine blöden Technik infos weg … und sage verständlich was da läuft“ —
    #: die Seite zeigt Titel und Satz, nicht mehr Skript und Befehl (die stehen nur noch im Tooltip).
    REGELN = (
        ('form2_kurz30', 'Probe', 'Probe: Reichen 30 Durchgänge statt 120?',
         'Dasselbe Körperform-Training wie der lange Lauf, aber nur 30 Durchgänge — um zu sehen, ob kurze Läufe für Vergleiche reichen. Diese KI wird nicht verwendet.', 'training'),
        ('formtraining_netz_messen', 'Probe', 'Probe: Wo rechnet die Grafikkarte beim Training?',
         'Ein paar Trainingsschritte mit Zeitmessung, um zu sehen, welche Rechnungen am längsten dauern — es entsteht keine KI.', None),
        ('form2_tempo_probe', 'Probe', 'Probe: Wie schnell ist das Training jetzt?',
         'Zwei Durchgänge Körperform-Training mit dem schnelleren Ablauf, nur um die Zeit zu messen — es entsteht keine neue KI.', 'training'),
        ('tempoprobe', 'Probe', 'Probe: Rechnet der schnellere Weg in die Grundhaltung genauso?',
         'Acht Figuren werden auf dem alten und auf dem schnellen Weg in die Grundhaltung gebracht und verglichen. Nur wenn alles gleich herauskommt, wird der schnelle Weg eingeschaltet.', None),
        ('mesh3dai_vorstufe_mia_daten_lauf', 'Daten', 'Trainingsdaten erzeugen',
         'Die Beispielfiguren werden in die Grundhaltung (A-Pose) gebracht, so wie später jedes neue 3D-Modell vorbereitet wird. Aus diesen Figuren lernt die KI danach.', 'daten'),
        ('mesh3dai_vorstufe_form', 'Training', 'Die KI lernt die Körperform',
         'Die KI sieht viele Beispielfiguren in Grundhaltung und lernt, daraus die Körperregler von Genesis abzulesen: Größe, Proportionen, Kopf und Gesicht. '
         'Am Ende steht eine neue KI, die anschließend an Figuren geprüft wird, die sie nie gesehen hat.', 'training'),
        ('mesh3dai_vorstufe_netz', 'Training', 'Die KI lernt das Skelett', 'Die KI lernt, in einer Figur in Grundhaltung die Gelenke zu finden.', 'training'),
        ('mesh3dai_stimmen', 'Training', 'Die KI lernt das Skelett', 'Die KI lernt, in einer Figur die Lage der Gelenke zu finden.', 'training'),
        ('mesh3dai_kopffehler_messen', 'Prüfung', 'Prüfung: Wie gut trifft die neue KI Kopf und Körper?',
         'Für Figuren, die die KI nie gesehen hat, wird die vorhergesagte Figur gebaut und mit der echten verglichen — Kopf, Gesicht und Körper, neben der bisherigen KI.', None),
        ('mesh3dai_form_pruefen', 'Prüfung', 'Prüfung der Körperform', 'Die vorhergesagten Figuren werden gebaut und mit den echten verglichen.', None),
        ('mesh3dai_paar', 'Testfigur', 'Echte Testfigur durchrechnen', 'Ein Tripo-Modell, dessen richtige Lösung wir kennen (Genesis-Export), läuft durch die ganze Erkennung; danach wird verglichen.', None),
        ('mesh3dai_test', 'Testfigur', 'Testfiguren neu berechnen', 'Die Testmodelle laufen mit der aktuellen KI durch: Körperform, Figur und Kleider.', None),
    )
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
        for job in prozesse['jobs']:
            # Der ganze Befehl, nicht nur das erste Skript: ein GPU-Lauf startet über `mesh3dai_stimmen_lauf.py <Trainingsskript> …` (Sperre), das Trainingsskript steht in den Argumenten.
            befehl = ' '.join([job['skript'], *job['argumente']])
            art, titel, was, fortschritt = next(((a, t, w, f) for teil, a, t, w, f in cls.REGELN if teil in befehl),
                                                ('Mesh3D-AI', 'Unbekannter Lauf (%s)' % job['skript'], 'Für dieses Skript ist keine Beschreibung hinterlegt.', None))
            job = {**job, 'art': art, 'titel': titel, 'was': was, 'fortschritt': [], 'lauf': None, 'befehl_kurz': cls._kurz(job['argumente'])}
            if fortschritt == 'training':
                lf = next((x for x in laufend if (x['start'] or 0) >= job['start'] - 90), None)
                if lf is not None:
                    laufend.remove(lf)
                    job['lauf'] = {'name': lf['name'], 'kurz': lf['kurz'], 'adresse': '/mesh-3D-AI/formtraining/%s/' % lf['name']}
                job['fortschritt'] = cls._training(lf)
            elif fortschritt == 'daten':
                job['fortschritt'] = cls._daten(job, varianten, jetzt)
            jobs.append(job)
        return {'zeit': jetzt, 'takt_s': cls.TAKT_S, 'system': SystemStats.lesen(), 'sperre': Mesh3daiformtraining.gpu(), 'jobs': jobs,
                'laeufe_ohne_prozess': [{'name': lf['name'], 'kurz': lf['kurz'], 'adresse': '/mesh-3D-AI/formtraining/%s/' % lf['name'], 'fortschritt': cls._training(lf)}
                                        for lf in laufend],
                'ketten': prozesse['ketten'], 'warteschlange': Mesh3daiwarteschlange.lesen(prozesse['ketten'], jobs, jetzt),
                'fremde_gpu': prozesse['fremde_gpu'], 'kerne': prozesse['kerne']}

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
