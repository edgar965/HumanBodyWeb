# -*- coding: utf-8 -*-
"""Architekturmesh3daikette — die Vorstufe „Rig → A-Pose → Netz" als Kette vor dem Netz, auf Hilfe → Architektur → Mesh3DAI (17.10.2026).

Edgar: „warum macht die Pipeline das nicht, als erstes das Mesh zu riggen und in die A-Pose zu übertragen??" → „baue das ein!". Die Kette steht in `ProjektTemp/_wegwerf/mesh3dai_vorstufe*.py`
(Lage → Mesh-3D „Nur Rig" → Figur → A-Pose → Netz der Vorstufe → zurück in die Haltung). GELESEN beim Aufruf, nichts von Hand:
    `<Job>/vorstufe/<nnnn>/kette.json`   Schritte, Zeiten, Mesh-3D-Auftrag, aufgerichtet ja/nein (je Prüfposen-Job; der Lauf, den `wege.json` nennt, sonst der jüngste)
    `wege.json` im jüngsten Lauf des Jobs   Fehler gegen das Ziel je Weg (Probe 1, Ø der 138 Gelenke)
    `_vorstufe/laeufe/*/lauf_ergebnis.json` mit `eingang: apose_*`   das Netz der Vorstufe (Training auf zurückgerechneten Wolken)
    `_test/*/test.json` mit `weg: vorstufe`   die Testnetze, gerechnet mit der Kette
"""

import json
from pathlib import Path

__all__ = ['Architekturmesh3daikette']


class Architekturmesh3daikette:
    JOBS = ('UrsulaSpagat', 'DamiraSitzen', 'MattLiegen', 'MannLaufen')
    WEGE = (('direkt', 'Netz direkt'), ('vorstufe', 'Rig → A-Pose → Netz'), ('rig', 'Rig allein'))
    SCHRITTE = (('mia_stapel', 'Make-It-Animatable v2 auf der Datei: Gelenke, Hautgewichte, Pose je Knochen (GPU, mit Laden der Modelle) — seit 18.10.2026 der erste Schritt'),
                ('mia', 'MIAs Ruhelage, Oberarme auf die Genesis-A-Pose, Inselregel, Lochfüllung, Prüfung — durchgefallen: weiter mit „lage“'),
                ('lage','Lage: liegt das Netz? dann aufrichten (Wirbelsäule aus dem Netz direkt, über 45° schräg)'), ('rig', 'Mesh-3D „Nur Rig“ (ein fertiger Auftrag auf derselben Datei wird genommen)'),
                ('figur', 'Käfig, Gelenke und Drehungen der Rig-Figur'), ('apose', 'Netz mit der Rig-Figur in die A-Pose, gerissene Dreiecke und abgerissene Stücke weg, 16.384 Punkte'),
                ('netz', 'Netz der Vorstufe auf der Wolke, mit den Drehungen des Rigs zurück in die Haltung, Daz-Winkel'))

    @staticmethod
    def _json(datei):
        try:
            return json.loads(Path(datei).read_text(encoding='utf-8'))
        except (OSError, ValueError, TypeError):
            return None

    @classmethod
    def _wege(cls, ordner):
        """`wege.json` des jüngsten Laufs, der eine trägt."""
        laeufe = sorted(p for p in (ordner / '_laeufe').glob('*') if (p / 'wege.json').is_file()) if (ordner / '_laeufe').is_dir() else []
        return (cls._json(laeufe[-1] / 'wege.json'), laeufe[-1].name) if laeufe else (None, None)

    @staticmethod
    def _ablage(ordner):
        """Der jüngste Lauf der Kette (`vorstufe/0001`, `0002` …) — für `wege.json` ohne Feld `ablage` (Fassung vom 17.10.2026 früh)."""
        laeufe = sorted(p for p in (ordner / 'vorstufe').glob('[0-9][0-9][0-9][0-9]') if (p / 'kette.json').is_file()) if (ordner / 'vorstufe').is_dir() else []
        return laeufe[-1] if laeufe else ordner / 'vorstufe' / '0001'

    @classmethod
    def kontext(cls, wurzel):
        """`{posen: [...], mittel, zeiten, netz, tests}` oder None, wenn kein Job eine Kette gerechnet hat."""
        posen, zeiten = [], {}
        for job in cls.JOBS:
            ordner = wurzel / job
            wege, lauf = cls._wege(ordner)
            kette = cls._json(Path((wege or {}).get('ablage') or cls._ablage(ordner)) / 'kette.json')
            if not kette or not wege:
                continue
            probe = next((p for p in cls._json(ordner / 'proben.json') or [] if p.get('nr') == 1), {})
            je = (wege.get('proben') or {}).get('1') or {}
            posen.append({'job': job, 'pose': probe.get('name', ''), 'abstand': probe.get('naechste_trainingspose_mm'), 'aufgerichtet': kette.get('aufgerichtet'),
                          'mesh3d': kette.get('mesh3d'), 'netz': wege.get('netz_vorstufe') or Path(kette.get('netz_lauf', '')).name, 'lauf': lauf,
                          'mm': {k: (je.get(k) or {}).get('mm') for k, _t in cls.WEGE}, 'gruppen': {k: (je.get(k) or {}).get('je_gruppe_mm') or {} for k, _t in cls.WEGE},
                          # in der Folge von WEGE, für die Vorlage (sie kennt keinen Zugriff über einen Schlüssel aus einer Schleife)
                          'werte': [{'schluessel': k, 'mm': (je.get(k) or {}).get('mm')} for k, _t in cls.WEGE]})
            for schritt, s in (kette.get('zeiten_s') or {}).items():
                zeiten.setdefault(schritt, []).append(float(s))
        if not posen:
            return None
        mittel = {k: round(sum(p['mm'][k] for p in posen if p['mm'][k] is not None) / max(1, sum(1 for p in posen if p['mm'][k] is not None)), 1) for k, _t in cls.WEGE}
        schritte = [{'schritt': s, 'text': t, 'min': round(min(zeiten[s]), 1), 'max': round(max(zeiten[s]), 1)} for s, t in cls.SCHRITTE if zeiten.get(s)]
        return {'posen': posen, 'wege': [{'schluessel': k, 'text': t} for k, t in cls.WEGE], 'mittel': mittel, 'mittel_liste': [mittel[k] for k, _t in cls.WEGE], 'schritte': schritte, 'netz': cls.netz(wurzel), 'tests': cls.tests(wurzel)}

    @classmethod
    def netz(cls, wurzel):
        """Der jüngste Lauf des Netzes der Vorstufe (auf zurückgerechneten Wolken)."""
        laeufe = sorted(p for p in (wurzel / '_vorstufe' / 'laeufe').glob('*') if (p / 'lauf_ergebnis.json').is_file()) if (wurzel / '_vorstufe' / 'laeufe').is_dir() else []
        wahl = cls._json(wurzel / '_vorstufe' / 'gewaehlt.json') or {}
        # Das GEWÄHLTE Netz (dasselbe, das `mesh3dai_vorstufe.py` nimmt) zuerst, sonst das jüngste.
        laeufe.sort(key=lambda p: p.name == wahl.get('lauf'))
        for p in reversed(laeufe):
            e = cls._json(p / 'lauf_ergebnis.json') or {}
            if str(e.get('eingang', '')).startswith('apose'):
                je = e.get('je_figur') or {}
                return {'lauf': p.name, 'gewaehlt': wahl.get('grund') if p.name == wahl.get('lauf') else None, 'farbe': e.get('farbe', 'fest'), 'eingang': e.get('eingang'), 'epochen': e.get('epochen'), 'dauer_s': e.get('dauer_s'), 'start': Path(e['start']).name if e.get('start') else None, 'proben': e.get('proben') or {},
                        'k': e.get('k_training'), 'stoerung': e.get('stoerung_pruefung_mm'), 'parameter': e.get('parameter'),
                        'figuren': [{'figur': f, 'training': (w.get('training') or {}).get('mm'), 'pruefung': (w.get('pruefung') or {}).get('mm'),
                                     'stoerung': (w.get('pruefung') or {}).get('rig_verfaelscht_mm')} for f, w in je.items()],
                        # Fassung 3 (17.10.2026): Prüfposen je Kleid (weite Stücke, Textur) und die Kleider des Datensatzes mit Teilfarbe
                        'je_kleid': [{'kleid': k, 'mm': mm} for k, mm in (e.get('je_kleid_pruefung_mm') or {}).items()], 'teilfarbe': e.get('pruefung_grund_teilfarbe_mm')}
        return None

    @classmethod
    def tests(cls, wurzel):
        """Alle Testnetze, die die Kette gerechnet hat — mit dem Weg, den die Sicherheitsregel wählte (`Vorstufentest.GRENZE_MM`), und dem Abstand, an dem sie entschied."""
        aus = []
        for p in sorted((wurzel / '_test').glob('*')) if (wurzel / '_test').is_dir() else []:
            t = cls._json(p / 'test.json') or {}
            if t.get('weg') in ('vorstufe', 'rig'):
                aus.append({'name': t.get('name', p.name), 'figur': t.get('figur'), 'rest': t.get('ik_rest_mm'), 'mesh3d': t.get('mesh3d'), 'aufgerichtet': t.get('aufgerichtet'),
                            'weg': t.get('weg'), 'abweichung': t.get('abweichung_netz_rig_mm'), 'zeiten': (t.get('vorstufe') or {}).get('zeiten_s') or {}})
        return aus
