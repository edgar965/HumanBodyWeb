# -*- coding: utf-8 -*-
"""Bildablage — ein Bild aus dem Browser entgegennehmen und ablegen.

Zwei Endpunkte nehmen ein im Browser gerendertes Bild als Data-URL entgegen und
legen es unter `media/photo_analysis/<ordner>/<auftrag>.jpg` ab: das
3D-Vorschaubild (`Fotoauftraege.bild_sichern`) und die Silhouette
(`Fotoabgleich.projektion_sichern`). Beide taten das am 27.08.2026 mit
demselben Block — Praefix abschneiden, `b64decode`, Ordner anlegen, schreiben,
relativen Pfad zurueckgeben.

Die Rueckgabe von `bytes_aus_dataurl` unterscheidet drei Faelle, weil die
Endpunkte sie unterschiedlich beantworten:

    b''    — es kam gar kein Bild mit   -> 400 „No image data"
    None   — base64 kaputt              -> 400 „Invalid base64"
    bytes  — in Ordnung
"""

import base64
import logging
import os

from django.conf import settings

logger = logging.getLogger('core')


class Bildablage:
    """Ein Unterordner unter `media/photo_analysis/`."""

    #: Wo die Bilder liegen, relativ zu `BASE_DIR`.
    BASIS = ('media', 'photo_analysis')

    def __init__(self, unterordner):
        self.unterordner = unterordner

    @staticmethod
    def bytes_aus_dataurl(angabe):
        """Bytes aus einer Data-URL — `b''` wenn leer, `None` wenn kaputt."""
        if not angabe:
            return b''
        if ',' in angabe:
            angabe = angabe.split(',', 1)[1]
        try:
            return base64.b64decode(angabe)
        except Exception:                                        # noqa: BLE001
            logger.warning('Bilddaten nicht dekodierbar', exc_info=True)
            return None

    def ordner(self):
        pfad = os.path.join(str(settings.BASE_DIR), *self.BASIS,
                            self.unterordner)
        os.makedirs(pfad, exist_ok=True)
        return pfad

    def sichern_aus_dataurl(self, name, angabe):
        """Data-URL entgegennehmen, prüfen, ablegen.

        BEFUND `doppelcode` (29.08.2026): Diese drei Schritte standen in
        `Fotoabgleich.projektion_sichern` und `Fotoauftraege.bild_sichern`
        wortgleich — zehn Zeilen. Die beiden legen dasselbe Bild in zwei
        Unterordnern ab.

        Zurück kommt `(relativer Pfad, Fehlertext)`; genau einer von beiden
        ist gesetzt. Die HTTP-Antwort baut der Endpunkt — ein Dienst, der
        `JsonResponse` zurückgibt, ist nur noch aus einer Ansicht heraus
        benutzbar.
        """
        roh = self.bytes_aus_dataurl(angabe)
        if roh is None:
            return None, 'Invalid base64'
        if not roh:
            return None, 'No image data'
        return self.sichern(name, roh), None

    def sichern(self, name, roh):
        """Schreibt `<name>.jpg` und gibt den Pfad RELATIV zu `BASE_DIR`."""
        dateiname = '%s.jpg' % name
        with open(os.path.join(self.ordner(), dateiname), 'wb') as datei:
            datei.write(roh)
        return '/'.join(self.BASIS + (self.unterordner, dateiname))
