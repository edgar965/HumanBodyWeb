# -*- coding: utf-8 -*-
"""Architekturmeshto3dzeiten — die Zeiten der Schritte von „Mesh to 3D", gelesen aus den fertigen Aufträgen (Reiter „MeshTo3D", 11.10.2026).

Edgar: „Zahlen immer mit Definition und Quelle". Darum steht hier keine Zeit von Hand: jeder fertige Auftrag trägt seine Dauer je Schritt in `ergebnis.dauer`
(Sekunden, `Meshfigurlauf.ausfuehren`: Wanduhr des Schritts einschließlich des Runners) und die Summe in `ergebnis.dauer_s`. Die Seite zeigt die jüngsten fertigen Aufträge, mit
Kennung und Name; ein Auftrag aus dem Blender-Import steht darin wie jeder andere. Die Zeiten hängen an der Last des Rechners (laufen nebenher Agenten oder eine zweite GPU-Last,
schwanken sie um mehr als den Faktor 1,5, `zeit-messen.md`) — sie sind Beispiele, keine Zusage. Ohne Datenbank oder ohne fertigen Auftrag bleibt die Tabelle leer und sagt es.
"""

import logging

__all__ = ['Architekturmeshto3dzeiten']

logger = logging.getLogger('core')


class Architekturmeshto3dzeiten:
    ANZAHL = 8

    @staticmethod
    def _sekunden(wert):
        try:
            return round(float(wert), 1)
        except (TypeError, ValueError):
            return None

    @classmethod
    def zeile(cls, job, schritte):
        """Eine Tabellenzeile: Kennung, Name, Datum, Summe und je Schritt die Sekunden (`None` = nicht gemessen)."""
        ergebnis = job.ergebnis or {}
        dauer = ergebnis.get('dauer') or {}
        ende = job.finished_at
        return {
            'kennung': job.kennung,
            'name': job.name,
            'datum': ende.astimezone().strftime('%d.%m.%Y %H:%M') if ende else '–',
            'summe': cls._sekunden(ergebnis.get('dauer_s')),
            'schritte': [cls._sekunden(dauer.get(s)) for s in schritte],
        }

    @classmethod
    def lesen(cls, schritte):
        """`{'zeilen': [...], 'hinweis': str}` — die jüngsten fertigen Aufträge, neuester zuerst."""
        try:
            from ..models import Meshfigurauftrag

            jobs = list(Meshfigurauftrag.objects.filter(status='fertig').order_by('-finished_at')[:cls.ANZAHL])
        except Exception as fehler:  # noqa: BLE001 — ohne Datenbank bleibt die Tabelle leer, die Seite fällt nicht
            logger.warning('Architektur MeshTo3D: Zeiten nicht lesbar: %s', fehler)
            return {'zeilen': [], 'hinweis': 'Die Aufträge sind nicht lesbar (Datenbank): %s' % str(fehler)[:120]}
        zeilen = [cls.zeile(j, schritte) for j in jobs]
        if not zeilen:
            return {'zeilen': [], 'hinweis': 'Es gibt keinen fertigen Auftrag — keine Zeit gemessen.'}
        return {'zeilen': zeilen, 'hinweis': ''}
