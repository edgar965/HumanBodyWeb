# -*- coding: utf-8 -*-
"""Blendimportauftragsnutzer — wer außer einem Import noch an dessen Auftrag „Mesh to 3D“ hängt (13.10.2026).

Edgar (13.10.2026): „Fehler bei /mesh-3D/2026.10.11.00.10.00/, öffnet nicht" — die Seite zeigte einen roten 404 auf `/api/meshfigur/dacaa0bd…/zustand/`.
Gemessen: Der Import `…11.00.10.00` (Rosemary Winters) ist eine Kopie mit Daten von `…10.02.12.12`; beide nennen in `stand.ergebnis.figur.id` DENSELBEN
Auftrag „Mesh to 3D“ `2026.10.10.21.15.22`. Das Löschen des Originals am 11.10.2026 14:24 (`core.log`, „Blender-Import 2026.10.10.02.12.12 gelöscht … auftrag
2026.10.10.21.15.22, ordner_mb 542.5“) hat den gemeinsamen Auftrag samt Ordner mitgenommen — die Kopie zeigt seitdem eine Figur, die es nicht mehr gibt.

Die Stücke der Garderobe schützt `Blendimportloeschen.benutzer` schon vor genau diesem Fall; der Auftrag blieb ungeschützt.
"""

import logging

from ..daten.blendimportablage import Blendimportablage

logger = logging.getLogger('core')

__all__ = ['Blendimportauftragsnutzer']


class Blendimportauftragsnutzer:
    @staticmethod
    def figur_id(stand):
        """Die Kennung des Auftrags „Mesh to 3D“ im Stand eines Imports (`ergebnis.figur.id`) oder ''."""
        return str((((stand or {}).get('ergebnis') or {}).get('figur') or {}).get('id') or '')

    @classmethod
    def andere(cls, kennung, job):
        """Kennungen der ANDEREN Importe, deren Schritt „figur“ denselben Auftrag nennt (eine Kopie mit Daten teilt ihn mit dem Original)."""
        if job is None:
            return []
        gesucht = str(job.pk)
        return [k for k in Blendimportablage.alle() if k != kennung and cls.figur_id(Blendimportablage(k).stand()) == gesucht]

    @classmethod
    def frei(cls, kennung, job, still=False):
        """Der Auftrag, den ein Löschen von `kennung` mitnehmen darf — `None`, wenn es keinen gibt oder ein anderer Import ihn noch braucht
        (das steht im Protokoll, außer bei `still`: die Rückfrage im Browser fragt nur)."""
        nutzer = cls.andere(kennung, job)
        if nutzer:
            if not still:
                logger.info('Blender-Import %s: Auftrag „Mesh to 3D“ %s bleibt — ihn nennt auch der Import %s', kennung, job.kennung, ', '.join(nutzer))
            return None
        return job
