# -*- coding: utf-8 -*-
"""Ai2d3dlaeufe — die Läufe der Foto-Kette eines 2d-3d-AI-Jobs (25.10.2026; Edgar: „hier sehe ich keine aktuellen Läufe“ — die Läufe der Kette `nurfotos_kette.py` lagen nur in
`ProjektTemp/_wegwerf/ai2d3d/kopf/`, der Reiter „Test“ zeigte allein Messlatte A, also einen Mesh3D-AI-Test zum selben Netz).

Quelle: `<Job>/laeufe/<stand>.json`, geschrieben von der Kette (`nurfotos_laufeintrag.Laufeintrag`): `{stand, start, ende, status, stufe, stufen: [[name, s, code]], pid,
einpassung: {formrest_mm, kopf_mm_max, figur, dichte_kg_m3, …}, abnahme: {gruen, rot, gemessen}}`. Ein Lauf mit `status = läuft`, dessen Prozess nicht mehr lebt, heißt „abgebrochen“.
"""
import json
import logging
from datetime import datetime

logger = logging.getLogger('core')

__all__ = ['Ai2d3dlaeufe']


class Ai2d3dlaeufe:
    @staticmethod
    def alle(ordner):
        """Alle Läufe des Jobordners, der jüngste zuerst (nach `start`); unlesbare Dateien stehen im Log, nicht in der Liste."""
        aus = []
        for datei in sorted((ordner / 'laeufe').glob('*.json')) if ordner and (ordner / 'laeufe').is_dir() else []:
            try:
                aus.append(json.loads(datei.read_text(encoding='utf-8')))
            except (OSError, ValueError) as fehler:
                logger.warning('Ai2d3dlaeufe: %s nicht lesbar (%s)', datei, fehler)
        return sorted(aus, key=lambda lauf: str(lauf.get('start') or ''), reverse=True)

    @staticmethod
    def zeit(text):
        try:
            return datetime.fromisoformat(str(text)).timestamp() if text else None
        except ValueError:
            return None

    @staticmethod
    def lebt(lauf):
        import psutil
        pid = lauf.get('pid')
        return bool(pid) and psutil.pid_exists(int(pid))

    @classmethod
    def status(cls, lauf):
        if lauf.get('status') == 'läuft':
            return ('läuft: %s' % (lauf.get('stufe') or '…')) if cls.lebt(lauf) else 'abgebrochen in %s (Prozess beendet)' % (lauf.get('stufe') or '?')
        a = lauf.get('abnahme')
        if a:
            farbe = ' · Farbe %s/%s' % (a['farbe_gruen'], a['farbe_rot']) if a.get('farbe_gruen') is not None else ''
            return 'Abnahme %s grün · %s rot%s' % (a.get('gruen'), a.get('rot'), farbe)
        return '%s, Abnahme offen' % lauf.get('status') if str(lauf.get('status', '')).startswith('fertig') else str(lauf.get('status') or '—')

    @staticmethod
    def laufzeit(lauf):
        """`{sekunden, teile, quelle}` für `Mesh3daitabelle.laufzeit_zelle`; ohne fertige Stufe None."""
        teile = [(name, s) for name, s, _code in lauf.get('stufen') or [] if s is not None]
        return {'sekunden': sum(s for _n, s in teile), 'teile': teile, 'quelle': 'Foto-Kette nurfotos_kette.py, Stufen'} if teile else None

    @staticmethod
    def figur(lauf):
        e = lauf.get('einpassung') or {}
        teile = []
        if e.get('formrest_mm') is not None:
            teile.append('Formrest %s mm' % str(e['formrest_mm']).replace('.', ','))
        if e.get('kopf_mm_max') is not None:
            teile.append('Kopf ≤ %s mm' % str(e['kopf_mm_max']).replace('.', ','))
        if (e.get('figur') or {}).get('hoehe_m'):
            teile.append('%s m' % str(e['figur']['hoehe_m']).replace('.', ','))
        return ' · '.join(teile) or '—'

    @classmethod
    def verlauf(cls, laeufe):
        """Tooltip: alle Läufe mit Formrest und Abnahme, der jüngste zuerst."""
        return '\n'.join('%s  %s  %s  %s' % (str(lauf.get('start') or '').replace('T', ' ')[:16], lauf.get('stand'), cls.figur(lauf), cls.status(lauf)) for lauf in laeufe)
