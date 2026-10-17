# -*- coding: utf-8 -*-
"""Architekturmesh3daivorstufe — die Vorstufe „Rig-Generierung“ auf Hilfe → Architektur → Mesh3DAI (16.10.2026).

Edgar (16.10.2026 vormittags): „mach doch einen Zwischenschritt, wo du nur das Rigging auf das Mesh machst?“; abends: „schreibe auch den Schritt Rig-Generierung als Vorstufe in die
Architektur-Seite, und was das hilft“. Die Rig-Generierung ist ein Mesh-3D-Auftrag mit Weg „netz“ und Umfang „Nur Rig“ (`.claude/rules/mesh-3d.md`): „Mesh to 3D“ passt eine Genesis-9-Figur
an das Netz an und hört nach der Körperkette auf (`Meshfigurlauf.RIG_BIS`); das Skelett dieser Figur ist das Rig. Kein Training, kein Netz von Mesh3D-AI.
GELESEN beim Aufruf, nichts von Hand:
    `Ursula1/_diagnose/autorig/NNNN.json` (`ProjektTemp/_wegwerf/mesh3dai_autorig_messen.py`): Fehler des Rigs gegen das Ziel je Probe und den Mesh-3D-Auftrag dazu
    `3DObjects/blendimport/<auftrag>/stand.json`: Dauer je Schritt des Auftrags
    `vorhersagen.npz` der Läufe in `LAEUFE` und des jüngsten Formlaufs: Fehler des Netzes auf DENSELBEN Proben (`<gruppe>_nr`, `<gruppe>_fehler_mm`, nach der Anpassung der Daz-Winkel)
"""

import json
from pathlib import Path

import numpy as np

__all__ = ['Architekturmesh3daivorstufe']


def _mittel(werte):
    w = [v for v in werte if v is not None]
    return round(float(np.mean(w)), 1) if w else None


class Architekturmesh3daivorstufe:
    #: Läufe des Netzes, gegen die das Rig gestellt wird: (Ablage unter Ursula1, Ordner, Beschriftung). Der jüngste Formlauf kommt dazu (`kontext(…, form_lauf)`).
    LAEUFE = (
        ('_laeufe', '2026.10.16.12.03_stimmen_aufmerk_dreh30_e480', 'Stimmen, nur Ursula1'),
        ('_laeufe', '2026.10.16.13.58_stimmen_alle4', 'Stimmen, vier Jobs'),
    )
    SCHRITTE = (('koerper', 'Netz auf Menschenhöhe'), ('segmentierung', 'Sapiens2: Kleidung, Haut, Haar je Fläche'), ('pose', 'SAM 3D Body am Rendering: 21 Gelenke'),
                ('figur', '„Mesh to 3D“ bis zur Körperkette: Form und Haltung der Genesis-Figur'))

    @staticmethod
    def _json(datei):
        try:
            return json.loads(Path(datei).read_text(encoding='utf-8'))
        except (OSError, ValueError, TypeError):
            return None

    @classmethod
    def _stand(cls, kennung):
        from django.conf import settings
        if not kennung:
            return {}
        return cls._json(Path(settings.OBJECTS_ROOT) / 'blendimport' / str(kennung) / 'stand.json') or {}

    @staticmethod
    def _fehler(lauf):
        """{Probe: mm} aus `vorhersagen.npz` (alle Gruppen) oder None, wenn der Lauf fehlt."""
        datei = Path(lauf) / 'vorhersagen.npz'
        if not datei.is_file():
            return None
        aus = {}
        with np.load(datei) as z:
            for g in ('training', 'pruefung', 'spagat'):
                if g + '_nr' in z.files and g + '_fehler_mm' in z.files:
                    aus.update({int(n): float(f) for n, f in zip(z[g + '_nr'], z[g + '_fehler_mm'], strict=False)})
        return aus

    @classmethod
    def kontext(cls, ordner, form_lauf=None):
        dateien = sorted((ordner / '_diagnose' / 'autorig').glob('*.json'))
        if not dateien:
            return None
        proben = {int(p['nr']): p for p in cls._json(ordner / 'proben.json') or []}
        quellen = [(ordner / a / n, text) for a, n, text in cls.LAEUFE]
        if form_lauf is not None:
            quellen.append((form_lauf, 'Stimmen + Formkopf, vier Jobs + 40 Formvarianten'))
        spalten = [{'lauf': p.name, 'text': text, 'werte': w} for p, text in quellen if (w := cls._fehler(p)) is not None]
        zeilen, dauer = [], {}
        for datei in dateien:
            a = cls._json(datei) or {}
            nr = int(a.get('nr', 0))
            p = proben.get(nr, {})
            je = a.get('autorig_je_gruppe_mm') or {}
            zeilen.append({'nr': nr, 'name': p.get('name', ''), 'gruppe': p.get('gruppe', ''), 'rig': a.get('autorig_mm'), 'median': a.get('autorig_median_mm'),
                           'arm': je.get('arm'), 'hand': je.get('hand'), 'finger': je.get('finger'), 'rumpf': je.get('rumpf'), 'bein': je.get('bein'),
                           'alt': ((a.get('netz') or {}).get('netz_kanaele_e2400') or {}).get('mm'), 'netze': [s['werte'].get(nr) for s in spalten]})
            stand = cls._stand(a.get('mesh3d'))
            if (stand.get('einstellungen') or {}).get('umfang') == 'rig':        # die A-Pose lief als ganze Figur (361 s) — sie gehört nicht in die Zeit der Rig-Generierung
                for schritt, sekunden in (stand.get('dauer') or {}).items():
                    dauer.setdefault(schritt, []).append(float(sekunden))
        pruef = [z for z in zeilen if z['gruppe'] == 'pruefung']
        mittel = {'proben': len(pruef), 'rig': _mittel(z['rig'] for z in pruef), 'alt': _mittel(z['alt'] for z in pruef),
                  'netze': [_mittel(z['netze'][i] for z in pruef) for i in range(len(spalten))],
                  'besser': [sum(1 for z in pruef if z['rig'] is not None and z['netze'][i] is not None and z['rig'] < z['netze'][i]) for i in range(len(spalten))]}
        schritte = [{'schritt': s, 'text': t, 'min': round(min(dauer[s]), 1), 'max': round(max(dauer[s]), 1), 'mittel': round(float(np.mean(dauer[s])), 1), 'auftraege': len(dauer[s])}
                    for s, t in cls.SCHRITTE if dauer.get(s)]
        return {'zeilen': zeilen, 'spalten': [{'lauf': s['lauf'], 'text': s['text']} for s in spalten], 'mittel': mittel, 'schritte': schritte,
                'gesamt_s': round(sum(s['mittel'] for s in schritte)) if schritte else None}
