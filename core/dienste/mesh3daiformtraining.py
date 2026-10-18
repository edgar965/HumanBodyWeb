# -*- coding: utf-8 -*-
"""Mesh3daiformtraining — die Trainingsläufe der gemeinsamen Netze (Vorstufe und Formkopf) für den Reiter „Formtraining“ auf /mesh-3D-AI/ (18.10.2026).

Edgar: „ich brauche ein UI für alle Training Jobs … die gerade laufenden Jobs sehen, letztes Datum usw. Falls du einen neuen Job-Typ hast, dann mach einen neuen Tab ‚Formtraining‘“.
Ein Lauf ist ein Ordner `3DObjects/mesh3dai/_vorstufe/laeufe/<JJJJ.MM.TT.HH.MM>_<name>/`. Die Trainingsskripte (`ProjektTemp/_wegwerf/mesh3dai_vorstufe_form2.py` u. a.) legen ihn NACH dem Laden
der Daten an, schreiben `lauf.log` (Kopfzeile, dann alle 20 Epochen eine Zeile `Epoche  N  {…}  (S s)`) und erst am Ende `lauf_ergebnis.json` (Verlauf, Proben, Dauer); Formläufe dazu
`formen_ergebnis.json` (Fehler je Formvariante und Summen je Gruppe).

Zustand eines Laufs — nur von der Platte, ohne Blick auf Prozesse:
  * fertig:     `lauf_ergebnis.json` liegt da; Ende = seine Änderungszeit;
  * läuft:      ohne Ergebnis, und `lauf.log` hat sich vor kürzerer Zeit geändert als `FRIST_LAEUFT_S` (oder als das Dreifache eines Abschnitts von 20 Epochen, wenn der länger ist);
  * steht:      ohne Ergebnis und länger still — abgebrochen oder abgestürzt; aus der Platte nicht zu unterscheiden, darum heißt es so und nicht „abgebrochen“;
  * Probelauf:  Name endet auf `_probe` (zählt auch in `Mesh3daitrainingsdatum` nicht als Training).

    Mesh3daiformtraining.laeufe() -> [{name, kurz, art, probe, zustand, start, ende, letzte, epoche, epochen, dauer_s, jobs, formvarianten, proben, rig_mm, form_mm, kopf_mm, messung}]
    Mesh3daiformtraining.gpu()    -> None | {'name': Halter der GPU-Sperre, 'seit': Unix-Zeit}
"""

import ast
import json
import logging
import re
import time
from datetime import datetime
from pathlib import Path

from django.conf import settings

logger = logging.getLogger('core')

__all__ = ['Mesh3daiformtraining']


class Mesh3daiformtraining:
    ERGEBNIS = 'lauf_ergebnis.json'
    FORMEN = 'formen_ergebnis.json'
    LOG = 'lauf.log'
    FRIST_LAEUFT_S = 3600.0
    PRUEFFORMEN = 'Prüfformen (nie trainiert)'
    #: die Sperre, unter der jeder GPU-Lauf dieses Projekts rechnet (`projekt.md`, Edgars Vorgaben); `gib` löscht die Datei
    SPERRE = ('ProjektTemp', '_wegwerf', 'recherche_human3d', 'umsetzung', 'gpu.lock')
    _EPOCHEN = re.compile(r'(\d+) Epochen')
    _EPOCHE = re.compile(r'^Epoche\s+(\d+)\s+(\{.*\})\s+\((\d+) s\)\s*$')
    _FORMVARIANTEN = re.compile(r'Formvarianten (\d+)')
    _TRAINING = re.compile(r'Training (\d+)')
    _PRUEFUNG = re.compile(r'Prüf(?:ung|posen) (\d+)')
    _REGLER = re.compile(r'\bRegler \d+')

    @staticmethod
    def ordner():
        return Path(settings.OBJECTS_ROOT) / 'mesh3dai' / '_vorstufe' / 'laeufe'

    @classmethod
    def laeufe(cls, jetzt=None):
        """Alle Läufe, der jüngste zuerst."""
        jetzt = time.time() if jetzt is None else jetzt
        wurzel = cls.ordner()
        if not wurzel.is_dir():
            return []
        aus = [cls.lauf(p, jetzt) for p in wurzel.iterdir() if p.is_dir() and ((p / cls.LOG).is_file() or (p / cls.ERGEBNIS).is_file())]
        return sorted(aus, key=lambda x: (x['start'] or 0, x['name']), reverse=True)

    @classmethod
    def lauf(cls, p, jetzt):
        e = cls._json(p / cls.ERGEBNIS)
        log = cls._log(p / cls.LOG)
        start = cls._start(p.name)
        kurz = p.name[17:] if start else p.name
        verlauf = (e or {}).get('verlauf') or []
        formen = cls._json(p / cls.FORMEN) or {}
        if e is not None:
            zustand, ende = 'fertig', (p / cls.ERGEBNIS).stat().st_mtime
        else:
            abschnitt = 20.0 * log['s'] / log['epoche'] if log['epoche'] else 0.0
            zustand, ende = ('läuft' if jetzt - log['zeit'] <= max(cls.FRIST_LAEUFT_S, 3 * abschnitt) else 'steht'), None
        e = e or {}
        pruef = (formen.get('zusammen') or {}).get(cls.PRUEFFORMEN) or {}
        return {
            'name': p.name, 'kurz': kurz, 'probe': kurz.endswith('_probe'), 'zustand': zustand,
            'art': 'Formkopf' if ('formkopf' in e or formen or cls._REGLER.search(log['kopf'])) else 'Vorstufe',
            'start': start, 'ende': ende, 'letzte': max(log['zeit'], ende or 0.0) or None,
            'epoche': len(verlauf) if verlauf else log['epoche'], 'epochen': e.get('epochen') or log['epochen'],
            'dauer_s': e.get('dauer_s') if e.get('dauer_s') is not None else (log['s'] or None),
            'jobs': list(e.get('training_daten') or []),
            'formvarianten': e.get('formvarianten') if e.get('formvarianten') is not None else cls._zahl(cls._FORMVARIANTEN, log['kopf']),
            'proben': cls._proben(e, log['kopf']),
            'rig_mm': cls._rig(verlauf or [log['messung']]),
            'form_mm': pruef.get('form_mm'), 'kopf_mm': pruef.get('kopf_form_mm'),
            'messung': verlauf[-1] if verlauf else log['messung'],
        }

    @classmethod
    def je_variante(cls):
        """Je Formvariante der jüngste FERTIGE Formlauf (ohne Probeläufe), der sie trainiert oder gemessen hat — aus `formen_ergebnis.json` → `varianten`:
        `{name: {lauf, zeit, gruppe, form_mm, kopf_mm}}`; `gruppe` 'training' heißt trainiert, 'pruefung' nur gemessen (Prüfform)."""
        aus = {}
        wurzel = cls.ordner()
        if not wurzel.is_dir():
            return aus
        for p in wurzel.iterdir():
            ergebnis = p / cls.ERGEBNIS
            if not p.is_dir() or p.name.endswith('_probe') or not ergebnis.is_file() or not (p / cls.FORMEN).is_file():
                continue
            zeit = ergebnis.stat().st_mtime
            for name, v in ((cls._json(p / cls.FORMEN) or {}).get('varianten') or {}).items():
                if not isinstance(v, dict) or (name in aus and aus[name]['zeit'] >= zeit):
                    continue
                gruppe = v.get('gruppe')
                form = v.get('form') or {}
                werte = form.get(gruppe) or next(iter(form.values()), {}) or {}
                aus[name] = {'lauf': p.name, 'zeit': zeit, 'gruppe': gruppe, 'form_mm': werte.get('form_mm'), 'kopf_mm': (v.get('kopf') or {}).get('kopf_form_mm')}
        return aus

    @classmethod
    def gpu(cls):
        """Wer die GPU-Sperre hält — `None`, wenn sie frei ist (die Datei fehlt). Andere Programme auf der Karte (Ollama, Chrome) sieht die Sperre nicht."""
        d = cls._json(Path(settings.TOOLS_ROOT).joinpath(*cls.SPERRE))
        if not isinstance(d, dict) or not d.get('name'):
            return None
        try:
            return {'name': str(d['name']), 'seit': float(d['seit'])}
        except (KeyError, TypeError, ValueError):
            return {'name': str(d['name']), 'seit': None}

    @staticmethod
    def _start(name):
        try:
            return datetime.strptime(name[:16], '%Y.%m.%d.%H.%M').timestamp()
        except ValueError:
            return None

    @classmethod
    def _log(cls, datei):
        """Kopfzeile, letzte Epochenzeile (Nummer, Messwerte, Sekunden) und Änderungszeit von `lauf.log`."""
        aus = {'kopf': '', 'epochen': None, 'epoche': 0, 'messung': {}, 's': 0.0, 'zeit': 0.0}
        try:
            aus['zeit'] = datei.stat().st_mtime
            zeilen = datei.read_text(encoding='utf-8', errors='replace').splitlines()
        except OSError:
            return aus
        aus['kopf'] = zeilen[0] if zeilen else ''
        aus['epochen'] = cls._zahl(cls._EPOCHEN, aus['kopf'])
        for zeile in reversed(zeilen):
            m = cls._EPOCHE.match(zeile)
            if m:
                aus['epoche'], aus['s'] = int(m.group(1)), float(m.group(3))
                try:
                    aus['messung'] = ast.literal_eval(m.group(2))
                except (ValueError, SyntaxError):
                    aus['messung'] = {}
                break
        return aus

    @classmethod
    def verlauf_aus_log(cls, zeilen):
        """ALLE Epochenzeilen eines `lauf.log` als Verlauf `[{epoche, …, 's': Sekunden}]` — während des Laufs die einzige Quelle (`lauf_ergebnis.json` kommt erst am Ende)."""
        aus = []
        for zeile in zeilen:
            m = cls._EPOCHE.match(zeile)
            if not m:
                continue
            try:
                werte = ast.literal_eval(m.group(2))
            except (ValueError, SyntaxError):
                continue
            if isinstance(werte, dict):
                aus.append({**werte, 'epoche': int(m.group(1)), 's': float(m.group(3))})
        return aus

    @classmethod
    def _proben(cls, e, kopf):
        p = e.get('proben_alle') or e.get('proben')
        if isinstance(p, dict):
            return {'training': p.get('training'), 'pruefung': p.get('pruefung')}
        return {'training': cls._zahl(cls._TRAINING, kopf), 'pruefung': cls._zahl(cls._PRUEFUNG, kopf)}

    @staticmethod
    def _rig(verlauf):
        """Gelenkfehler der Prüfung bei der letzten Zwischenmessung: `pruefung_mm` (Vorstufe, Formtraining 1) oder `pruefung_gelenke_mm` (Formtraining 2)."""
        for zeile in reversed(verlauf):
            for schluessel in ('pruefung_mm', 'pruefung_gelenke_mm'):
                if isinstance(zeile, dict) and zeile.get(schluessel) is not None:
                    return zeile[schluessel]
        return None

    @staticmethod
    def _zahl(muster, text):
        m = muster.search(text or '')
        return int(m.group(1)) if m else None

    @staticmethod
    def _json(datei):
        if not datei.is_file():
            return None
        try:
            return json.loads(datei.read_text(encoding='utf-8'))
        except (OSError, ValueError):
            logger.warning('Mesh3daiformtraining: %s nicht lesbar (wird gerade geschrieben?)', datei)
            return {}
