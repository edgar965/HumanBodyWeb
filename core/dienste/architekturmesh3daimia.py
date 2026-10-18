# -*- coding: utf-8 -*-
"""Architekturmesh3daimia — Hilfe → Architektur → Mesh3DAI, Abschnitt 1: was mit dem Schritt MIA anders ist als vorher (18.10.2026).

Edgar: „Ich verstehe aber noch nicht genau, wie du jetzt trainierst und berechnest mit dem A-Pose Zwischenschritt, update das auf der Hilfe Seite, schreibe einen neuen Absatz, was mit diesem MIA Schritt
anders ist als davor“. GELESEN beim Aufruf, nichts von Hand:
    `<Job>/_laeufe/<jüngster mit wege.json>/wege.json` und die Sicherungen `wege_vor_<Zeit>.json` daneben (die Kette legt die alte Fassung so ab, `Vorstufenkette.wege`) — je Job die jüngste
        Fassung des Wegs MIA (`kette.json` der Ablage: `weg = mia`) und die jüngste des alten Wegs (Mesh-3D „Nur Rig“)
    `<Ablage>/mia/pruefung.json`   MIAs Prüfung (gerissen, abgerissen, Gründe), `<Ablage>/kette.json` → `weg_grund` (erzwungen?)
    `_vorstufe/laeufe/*/lauf_ergebnis.json`   das Netz der Vorstufe je Weg: alter Weg = `gewaehlt.json` → `lauf`, Weg MIA = `lauf_mia`, sonst der jüngste mit `eingang: apose_v7…`
"""

from pathlib import Path

from .architekturmesh3daikette import Architekturmesh3daikette

__all__ = ['Architekturmesh3daimia']


class Architekturmesh3daimia:
    #: Wege der Trainingsdaten, die zum Weg MIA gehören (`mesh3dai_vorstufe_mia_daten.py`, Fassung 7 und 8).
    MIA_EINGAENGE = ('apose_v7', 'apose_v8', 'apose_v9')
    _json = staticmethod(Architekturmesh3daikette._json)

    @classmethod
    def _fassungen(cls, lauf):
        """[(Datei, wege, kette)] des Laufs, jüngste zuerst: `wege.json`, dann die Sicherungen nach ihrer Zeit im Namen."""
        dateien = [lauf / 'wege.json'] + sorted(lauf.glob('wege_vor_*.json'), key=lambda p: p.name, reverse=True)
        aus = []
        for d in dateien:
            wege = cls._json(d)
            if not wege or not wege.get('ablage'):
                continue
            aus.append((d, wege, cls._json(Path(wege['ablage']) / 'kette.json') or {}))
        return aus

    @staticmethod
    def _mm(wege):
        je = (wege.get('proben') or {}).get('1') or {}
        return {k: (je.get(k) or {}).get('mm') for k in ('direkt', 'vorstufe', 'rig')}

    @classmethod
    def jobs(cls, wurzel):
        aus = []
        for job in Architekturmesh3daikette.JOBS:
            ordner = wurzel / job
            laeufe = sorted(p for p in (ordner / '_laeufe').glob('*') if (p / 'wege.json').is_file()) if (ordner / '_laeufe').is_dir() else []
            if not laeufe:
                continue
            fassungen = cls._fassungen(laeufe[-1])
            mia = next(((d, w, k) for d, w, k in fassungen if k.get('weg') == 'mia'), None)
            alt = next(((d, w, k) for d, w, k in fassungen if k.get('weg') != 'mia'), None)
            if not mia or not alt:
                continue
            probe = next((p for p in cls._json(ordner / 'proben.json') or [] if p.get('nr') == 1), {})
            pruefung = cls._json(Path(mia[1]['ablage']) / 'mia' / 'pruefung.json') or {}
            grund = str(mia[2].get('weg_grund') or '')
            aus.append({'job': job, 'pose': probe.get('name', ''), 'direkt': cls._mm(alt[1])['direkt'],
                        'alt': {**cls._mm(alt[1]), 'netz': alt[1].get('netz_vorstufe'), 'ablage': Path(alt[1]['ablage']).name, 'datei': alt[0].name, 'aufgerichtet': bool(alt[2].get('aufgerichtet'))},
                        'mia': {**cls._mm(mia[1]), 'netz': mia[1].get('netz_vorstufe'), 'ablage': Path(mia[1]['ablage']).name, 'datei': mia[0].name,
                                'erzwungen': 'ERZWUNGEN' in grund, 'gruende': ((pruefung.get('pruefung') or {}).get('gruende') or []),
                                'gerissen': pruefung.get('gerissen_anteil'), 'abgerissen': pruefung.get('abgerissen_flaeche')}})
        return aus

    @classmethod
    def netz(cls, wurzel, lauf):
        """Ein Netz der Vorstufe: Prüfwolken je Figur (Fehler in Ruhe) und der Fehler des Rigs, mit dem die Wolken in die A-Pose kamen."""
        e = cls._json(wurzel / '_vorstufe' / 'laeufe' / lauf / 'lauf_ergebnis.json') if lauf else None
        if not e:
            return None
        figuren = [{'figur': f, 'pruefung': (w.get('pruefung') or {}).get('mm'), 'rig': (w.get('pruefung') or {}).get('rig_verfaelscht_mm')} for f, w in (e.get('je_figur') or {}).items()]
        return {'lauf': lauf, 'eingang': e.get('eingang'), 'proben': e.get('proben') or {}, 'ausgelassen': e.get('ausgelassen_pruefung'), 'figuren': figuren,
                'pruefung': round(sum(f['pruefung'] for f in figuren) / len(figuren), 1) if figuren else None,
                'rig': round(sum(f['rig'] for f in figuren) / len(figuren), 1) if figuren else None}

    @classmethod
    def netz_mia(cls, wurzel, wahl):
        if wahl.get('lauf_mia'):
            return wahl['lauf_mia']
        laeufe = sorted(p for p in (wurzel / '_vorstufe' / 'laeufe').glob('*') if (p / 'lauf_ergebnis.json').is_file()) if (wurzel / '_vorstufe' / 'laeufe').is_dir() else []
        return next((p.name for p in reversed(laeufe) if (cls._json(p / 'lauf_ergebnis.json') or {}).get('eingang') in cls.MIA_EINGAENGE), None)

    @classmethod
    def kontext(cls, wurzel):
        """`{jobs, mittel, netz_alt, netz_mia, netz_gewaehlt}` oder None (kein Job hat beide Wege gerechnet)."""
        jobs = cls.jobs(wurzel)
        if not jobs:
            return None

        def mittel(liste):
            werte = [x for x in liste if x is not None]
            return round(sum(werte) / len(werte), 1) if werte else None

        wahl = cls._json(wurzel / '_vorstufe' / 'gewaehlt.json') or {}
        return {'jobs': jobs,
                'mittel': {'direkt': mittel(j['direkt'] for j in jobs), 'alt': mittel(j['alt']['vorstufe'] for j in jobs), 'alt_rig': mittel(j['alt']['rig'] for j in jobs),
                           'mia': mittel(j['mia']['vorstufe'] for j in jobs), 'mia_rig': mittel(j['mia']['rig'] for j in jobs)},
                'netz_alt': cls.netz(wurzel, wahl.get('lauf')), 'netz_mia': cls.netz(wurzel, cls.netz_mia(wurzel, wahl)), 'mia_gewaehlt': bool(wahl.get('lauf_mia'))}
