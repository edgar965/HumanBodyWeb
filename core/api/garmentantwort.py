# -*- coding: utf-8 -*-
"""Garmentantwort — die Antwort eines langen Laufs, abgelegt für den Fall,
dass sie den Browser nicht erreicht.

    POST …/erzeugen|drapieren|gemeinsam/  mit Feld `anfrage=<Kennung>`
    GET  /api/garmentcode/antwort/<Kennung>/  -> die abgelegte Antwort,
                                                 404 solange keine da ist

WARUM (20.09.2026, Edgar: „von einem Bug zum anderen! Stoff drapieren —
Failed to fetch"): Der Dev-Server lädt neu, sobald eine importierte Datei
sich ändert — an diesem Abend 109-mal, weil eine zweite Sitzung nebenan
am Bildmodell arbeitet. Eine Drapierung dauert 25 bis 65 s. Fällt ein
Neustart hinein, rechnet der alte Prozess ZU ENDE und schreibt das Rig
(Log 21:42:31 drapiere … 21:42:46 reloading … 21:43:01 angezogen) — nur die
HTTP-Antwort kommt nie an, der Browser sieht „Failed to fetch", und ein
Klick auf „3D" rechnet 30 s neu. Dreimal an einem Abend (21:23, 21:24,
21:42).

DER WEG: Der Browser gibt jeder Anfrage eine Kennung mit. Der Endpunkt legt
seine fertige Antwort unter dieser Kennung ab, bevor er sie sendet. Bricht
die Verbindung, fragt der Browser die Kennung ab, bis die Antwort da ist
(`gemeinsam/antwortnachholen.js`), und macht weiter, als wäre nichts
gewesen. Die Ablage liegt im Projekt (`ausgabe/_antworten/`, Regel
`systemtemp`), eine Datei je Kennung, älter als einen Tag wird geräumt.
Ohne Kennung (alte Aufrufer, Tests) wird nichts abgelegt.
"""

import json
import logging
import os
import re
import time

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_GET

logger = logging.getLogger('core')

__all__ = ['Garmentantwort']


class Garmentantwort:
    """Ablage und Abruf der Antworten langer GarmentCode-Läufe."""

    ORDNER = os.path.join(str(settings.ASSETS_ROOT), 'GarmentCode', 'ausgabe', '_antworten')
    #: So sieht eine Kennung aus (`crypto.randomUUID()` im Browser, oder ein
    #: eigener Name). Alles andere wird nicht abgelegt — sie wird ein Dateiname.
    KENNUNG = re.compile(r'^[A-Za-z0-9_-]{8,64}$')
    #: Älter als so wird eine abgelegte Antwort geräumt (Sekunden).
    HALTEN_S = 24 * 3600

    @classmethod
    def ablegen(cls, kennung, antwort):
        """Die Antwort unter ihrer Kennung ablegen — still, wenn keine gültige da ist.

        @returns Pfad der Datei oder None
        """
        if not kennung or not cls.KENNUNG.match(str(kennung)):
            return None
        try:
            os.makedirs(cls.ORDNER, exist_ok=True)
            cls.aufraeumen()
            pfad = cls._pfad(kennung)
            with open(pfad + '.neu', 'w', encoding='utf-8') as datei:
                json.dump(antwort, datei)
            os.replace(pfad + '.neu', pfad)      # nie eine halbe Datei lesen
            return pfad
        except Exception:                        # noqa: BLE001
            logger.exception('GarmentCode: Antwort %s nicht abgelegt', kennung)
            return None

    @classmethod
    def lesen(cls, kennung):
        """Die abgelegte Antwort — oder None."""
        if not kennung or not cls.KENNUNG.match(str(kennung)):
            return None
        pfad = cls._pfad(kennung)
        if not os.path.isfile(pfad):
            return None
        with open(pfad, encoding='utf-8') as datei:
            return json.load(datei)

    @classmethod
    def aufraeumen(cls):
        """Antworten älter als `HALTEN_S` löschen; gibt die Zahl zurück."""
        if not os.path.isdir(cls.ORDNER):
            return 0
        grenze = time.time() - cls.HALTEN_S
        geloescht = 0
        for name in os.listdir(cls.ORDNER):
            pfad = os.path.join(cls.ORDNER, name)
            try:
                if os.path.isfile(pfad) and os.path.getmtime(pfad) < grenze:
                    os.remove(pfad)
                    geloescht += 1
            except OSError:
                logger.warning('GarmentCode: Antwort %s nicht geräumt', name)
        return geloescht

    @classmethod
    def _pfad(cls, kennung):
        return os.path.join(cls.ORDNER, '%s.json' % kennung)

    @staticmethod
    @require_GET
    def holen(request, kennung):
        """GET /api/garmentcode/antwort/<kennung>/ — 404, solange nichts da ist."""
        if not Garmentantwort.KENNUNG.match(kennung or ''):
            return JsonResponse({'fehler': 'Ungültige Kennung'}, status=400)
        antwort = Garmentantwort.lesen(kennung)
        if antwort is None:
            return JsonResponse({'fehler': 'Noch keine Antwort'}, status=404)
        return JsonResponse(antwort)
