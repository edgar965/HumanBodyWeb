# -*- coding: utf-8 -*-
"""Mesh3daiwarteschlange — die Warteschlange des Reiters „Lauf Aktuell“ auf /mesh-3D-AI/ (18.10.2026): welche Ketten mit welchen Schritten fertig sind, laufen oder warten.

Edgar: „#aktuell soll die aktuelle Job queue enthalten, mit der Jobliste, und Spalte mit Fortschrittsbalken bei aktuellem Job“ → „die ‚Ketten im Hintergrund‘ ausführlicher“ → „statt Jobliste: Warteschlange“.
Die Ketten sind Git-Bash-Skripte (`ProjektTemp/_wegwerf/mesh3dai_*_kette.sh`), die auf eine Marke im Log einer anderen Kette warten und ihre Schritte nacheinander starten. Was sie tun werden,
steht nicht in einem Prozess — darum eine Beschreibung je Kette in `ProjektTemp/mia_daten/warteschlange.json` (Skript, Log, Wartemarke, Endmarke, Schritte mit der Marke, die die Kette beim
Beginn ins Log schreibt). Der Zustand kommt aus dem Log:
  * ein Schritt hat begonnen, wenn seine Marke im Log steht (gesucht in Reihenfolge, je Schritt hinter dem vorigen Fund); fertig, sobald ein späterer begonnen hat oder die Endmarke steht;
  * der letzte begonnene ohne Endmarke läuft, wenn das Skript als Prozess lebt (`Mesh3dailaufprozesse` „ketten“) — sonst „abgebrochen“;
  * ein Schritt ohne Marke, hinter dem ein späterer begonnen hat, ist „übersprungen“ (die Kette ging per `|| continue` weiter); eine Markenzeile mit „übersprungen“ ebenso;
  * Zeiten aus `HH:MM:SS` in der Markenzeile; das Datum ist das der letzten Änderung des Logs (eine Zeit nach ihr gehört zum Vortag).
Fortschritt nur beim laufenden Schritt: der Balken des Python-Jobs, dessen Befehl `prozess` enthält (`Mesh3dailaufaktuell`), sonst die gezählten Zeilen (`zaehlen`), sonst keiner.
Eine Kette, deren Endmarke steht und deren Log älter ist als `ALT_S`, fällt weg; ein laufendes Skript, das die Datei nicht nennt, steht unter `unbeschrieben`.

    Mesh3daiwarteschlange.lesen(ketten, jobs, jetzt) -> {'datei', 'fehler', 'ketten': [{skript, titel, zustand, …, 'schritte': [...]}], 'unbeschrieben': [...]}
"""

import json
import logging
import re
from datetime import datetime, timedelta
from pathlib import Path

from django.conf import settings

logger = logging.getLogger('core')

__all__ = ['Mesh3daiwarteschlange']


class Mesh3daiwarteschlange:
    DATEI = ('ProjektTemp', 'mia_daten', 'warteschlange.json')
    ALT_S = 24 * 3600
    ZEILE_MAX = 200
    _ZEIT = re.compile(r'\b(\d{2}):(\d{2}):(\d{2})\b')

    @classmethod
    def pfad(cls):
        return Path(settings.TOOLS_ROOT).joinpath(*cls.DATEI)

    @classmethod
    def lesen(cls, ketten, jobs, jetzt):
        pfad = cls.pfad()
        aus = {'datei': str(pfad), 'fehler': None, 'ketten': [], 'unbeschrieben': []}
        try:
            plan = json.loads(pfad.read_text(encoding='utf-8'))
        except FileNotFoundError:
            aus['fehler'] = 'Die Beschreibung der Ketten fehlt.'
            return aus
        except (OSError, ValueError) as f:
            logger.warning('Mesh3daiwarteschlange: %s nicht lesbar (%s)', pfad, f)
            aus['fehler'] = 'Die Beschreibung der Ketten ist nicht lesbar: %s' % f
            return aus
        prozesse = {}
        for k in ketten or ():
            prozesse.setdefault(k['name'], []).append(k)
        eintraege = [e for e in plan.get('ketten', ()) if isinstance(e, dict) and e.get('skript') and e.get('log')]
        titel_je_log = {e['log']: e.get('titel') or e['skript'] for e in eintraege}
        beschrieben, nr = set(), 0
        for e in eintraege:
            beschrieben.update([e['skript'], *e.get('teilskripte', ())])
            kette = cls._kette(e, pfad.parent, prozesse, jobs or [], jetzt, titel_je_log)
            if kette is None:
                continue
            for s in kette['schritte']:
                nr += 1
                s['nr'] = nr
            aus['ketten'].append(kette)
        aus['unbeschrieben'] = [k for name, liste in prozesse.items() if name not in beschrieben for k in liste]
        return aus

    @classmethod
    def _kette(cls, e, ordner, prozesse, jobs, jetzt, titel_je_log):
        zeilen, geaendert = cls._log(ordner / e['log'])
        eigene = prozesse.get(e['skript'], [])
        lebt = bool(eigene)
        ende = cls._suchen(zeilen, e.get('ende'), 0) if e.get('ende') else None
        if ende is not None and not lebt and geaendert is not None and jetzt - geaendert > cls.ALT_S:
            return None
        bezug = datetime.fromtimestamp(geaendert if geaendert is not None else jetzt)
        schritte, pos = [], 0
        for s in cls._schritte(e, zeilen):
            i = cls._suchen(zeilen, s['marke'], pos)
            if i is not None:
                pos = i + 1
            schritte.append({'titel': s.get('titel') or s['marke'].strip('= '), 'marke': s['marke'], 'zeile': i, 'quelle': s})
        gefunden = [n for n, s in enumerate(schritte) if s['zeile'] is not None]
        letzter = gefunden[-1] if gefunden else None
        for n, s in enumerate(schritte):
            s.update(cls._zustand(n, s, schritte, letzter, ende, lebt, zeilen, bezug))
            if s['zustand'] == 'läuft':
                s.update(cls._fortschritt(s, cls._abschnitt(zeilen, s['zeile'], ende), jobs, jetzt))
            s.pop('zeile')
            s.pop('quelle')
        warten = e.get('wartet_auf') or {}
        warten_aus = None
        if warten.get('log') and warten.get('marke'):
            andere, _ = cls._log(ordner / warten['log'])
            warten_aus = {'titel': titel_je_log.get(warten['log'], warten['log']), 'marke': warten['marke'], 'erreicht': cls._suchen(andere, warten['marke'], 0) is not None}
        if ende is not None:
            zustand = 'fertig'
        elif gefunden:
            zustand = 'läuft' if lebt else 'abgebrochen'
        else:
            zustand = 'wartet' if lebt else 'nicht gestartet'
        return {'skript': e['skript'], 'titel': e.get('titel') or e['skript'], 'log': e['log'], 'zustand': zustand,
                'ende': cls._zeit(zeilen[ende], bezug) if ende is not None else None, 'wartet_auf': warten_aus,
                'prozesse': [{'pid': k['pid'], 'start': k['start']} for k in eigene], 'doppelt': len(eigene) > 1, 'schritte': schritte}

    @classmethod
    def _schritte(cls, e, zeilen):
        """Die Schritte in Reihenfolge; mit `je` wiederholt sich die ganze Liste je Wert (`{je}` in Marke und Titel)."""
        schritte = [s for s in e.get('schritte', ()) if isinstance(s, dict) and s.get('marke')]
        je = e.get('je') or {}
        if not any('{je}' in s['marke'] for s in schritte):
            return schritte
        werte = list(je.get('werte') or ())
        if je.get('zeile'):
            muster = re.compile(je['zeile'])
            treffer = next((m for m in map(muster.search, zeilen) if m), None)
            if treffer:
                werte = [w for w in treffer.group(1).split(',') if w]
        return [{**s, 'marke': s['marke'].replace('{je}', w), 'titel': (s.get('titel') or '').replace('{je}', w)} for w in werte for s in schritte]

    @classmethod
    def _zustand(cls, n, s, schritte, letzter, ende, lebt, zeilen, bezug):
        i = s['zeile']
        start = cls._zeit(zeilen[i], bezug) if i is not None else None
        if i is None:
            return {'zustand': 'übersprungen' if (letzter is not None and n < letzter) or ende is not None else 'wartet', 'start': None, 'dauer_s': None}
        naechste = next((x['zeile'] for x in schritte[n + 1:] if x['zeile'] is not None), ende)
        if 'übersprungen' in zeilen[i]:
            zustand = 'übersprungen'
        elif naechste is not None:
            zustand = 'fertig'
        else:
            zustand = 'läuft' if lebt else 'abgebrochen'
        schluss = cls._zeit(zeilen[naechste], bezug) if naechste is not None else None
        return {'zustand': zustand, 'start': start, 'dauer_s': schluss - start if start is not None and schluss is not None else None}

    @classmethod
    def _fortschritt(cls, s, abschnitt, jobs, jetzt):
        """Balken des Jobs, der den Schritt rechnet (der letzte mit Fortschritt > 0 — beim Datenlauf Phase C, sobald sie begonnen hat), sonst gezählte Zeilen; dazu die letzte Zeile des Abschnitts."""
        q = s['quelle']
        aus = {'fortschritt': None, 'job': None, 'lauf': None, 'seit_s': jetzt - s['start'] if s['start'] else None,
               'abschnitt': next((z.strip() for z in reversed(abschnitt[1:]) if z.startswith('== ')), None),
               'letzte_zeile': next((z.strip()[:cls.ZEILE_MAX] for z in reversed(abschnitt[1:]) if z.strip()), None)}
        job = next((j for j in jobs if q.get('prozess') and q['prozess'] in ' '.join([j.get('skript', ''), *j.get('argumente', ())])), None)
        if job is not None:
            aus['job'], aus['lauf'] = job.get('pid'), job.get('lauf')
            balken = job.get('fortschritt') or []
            if balken:
                aus['fortschritt'] = next((b for b in reversed(balken) if b.get('fertig')), balken[0])
                return aus
        if q.get('zaehlen'):
            try:
                zahl = sum(1 for z in abschnitt if re.search(q['zaehlen'], z))
            except re.error:
                return aus
            gesamt = q.get('gesamt')
            aus['fortschritt'] = {'name': q.get('einheit') or 'Zeilen', 'fertig': zahl, 'gesamt': gesamt, 'rest_s': None,
                                  'text': '%d%s %s' % (zahl, ' von %d' % gesamt if gesamt else '', q.get('einheit') or 'Zeilen'),
                                  'hinweis': 'Gezählt im Log der Kette: Zeilen „%s“ seit dem Beginn des Schritts.' % q['zaehlen']}
        return aus

    @staticmethod
    def _abschnitt(zeilen, i, ende):
        return zeilen[i:ende] if ende is not None and ende > i else zeilen[i:]

    @staticmethod
    def _suchen(zeilen, marke, ab):
        return next((j for j in range(ab, len(zeilen)) if zeilen[j].startswith(marke)), None)

    @staticmethod
    def _log(pfad):
        try:
            text = pfad.read_text(encoding='utf-8', errors='replace')
            return text.splitlines(), pfad.stat().st_mtime
        except OSError:
            return [], None

    @classmethod
    def _zeit(cls, zeile, bezug):
        m = cls._ZEIT.search(zeile)
        if not m:
            return None
        h, mi, se = map(int, m.groups())
        if h > 23 or mi > 59 or se > 59:
            return None
        t = bezug.replace(hour=h, minute=mi, second=se, microsecond=0)
        if t > bezug + timedelta(minutes=2):
            t -= timedelta(days=1)
        return t.timestamp()
