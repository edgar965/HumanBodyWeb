# -*- coding: utf-8 -*-
"""Mesh3daitestfaelle — die Testfälle der Kleider-KI (Stufe 2) für die Test- und die Jobseite (22.10.2026).

Edgar: „schreibe immer rein, wieviel Fehler von wievielen insgesamt, für alle Prioritäten. Das soll auch in das UI kommen für die trainings und Testjobs. Evtl. auch den Namen der Tests die fehler
liefern, aber verständlich und kurzgefasst, in einer Tabelle“.
Der Rechenlauf (`ProjektTemp/_wegwerf/mesh3dai_stufe2_testfaelle.py`, `Stufe2testfaelle.ablegen`) legt nach jedem Einsatz `testfaelle.json` neben die Stücke, die er gemessen hat:
`3DObjects/mesh3dai/_test/<test>/kleider_<geschlecht>/g/testfaelle.json` — Lauf, Rolle (Training oder Test), je Priorität FEHLER von Prüfungen, je Testfall Name, Kurztext, FEHLER, Prüfungen, vorher,
Urteil, die ersten FEHLER-Texte, beim Training der Verlauf der Prio-1-Wache. Wird ein schlechterer Stand zurückgelegt, wandert die Datei mit dem Ordner `g` (`Stufe2sicherung`) — sie gehört also
immer zu den Stücken, die die Seite zeigt. Hier wird nur gelesen.

    Mesh3daitestfaelle.fuer_test('olesiawalk_neu', 'weiblich') -> dict | None
    Mesh3daitestfaelle.fuer_job('olesiawalk') -> [dict, …]   (die Trainingstests dieses Jobs, jüngster zuerst)
"""

import json
import logging

from .mesh3daitest import Mesh3daitest

logger = logging.getLogger('core')

__all__ = ['Mesh3daitestfaelle']


class Mesh3daitestfaelle:
    DATEI = 'testfaelle.json'

    @classmethod
    def _lesen(cls, datei):
        if not datei.is_file():
            return None
        try:
            return json.loads(datei.read_text(encoding='utf-8'))
        except (OSError, ValueError) as fehler:
            logger.warning('Mesh3daitestfaelle: %s nicht lesbar (%s)', datei, fehler)
            return None

    @classmethod
    def fuer_test(cls, kennung, geschlecht):
        """Die Testfälle der Stücke, die der Test für dieses Geschlecht zeigt — None ohne Datei (noch nie mit Ziel gemessen) oder bei unbekanntem Test."""
        ordner = Mesh3daitest.pfad(kennung)
        if ordner is None or geschlecht not in Mesh3daitest.GESCHLECHTER:
            return None
        kleider = ordner / ('kleider_%s' % geschlecht)
        # 23.10.2026: der Kostüm-Weg A legt seine Prüfung neben die Stücke von Weg k (`ProjektTemp/_wegwerf/mesh3dai_kostuem_pruefung.py`) — gilt, wenn kein Weg g gemessen ist
        return cls._lesen(kleider / 'g' / cls.DATEI) or cls._lesen(kleider / 'k' / cls.DATEI)

    @classmethod
    def fuer_job(cls, job):
        """Die Trainingstests eines Jobs (`rolle` Training, `job` = Datensatzordner des Jobs), jüngster zuerst — leer, wenn der Job nie Stufe 2 trainiert hat."""
        from .mesh3daiattrappe import Mesh3daiattrappe
        eintrag = next((j for j in Mesh3daiattrappe.stammdaten() if j['id'] == str(job).lower()), None)
        if eintrag is None:
            return []
        namen = {str(eintrag.get('ordner') or eintrag['name']).lower(), str(eintrag['name']).lower()}
        aus = []
        for datei in sorted(Mesh3daitest.ordner().glob('*/kleider_*/g/%s' % cls.DATEI)):
            d = cls._lesen(datei)
            if d and d.get('rolle') == 'Training' and str(d.get('job', '')).lower() in namen:
                aus.append(d)
        return sorted(aus, key=lambda d: d.get('gerechnet') or '', reverse=True)
