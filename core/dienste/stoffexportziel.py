# -*- coding: utf-8 -*-
"""Stoffexportziel — wohin das Kleider-Export-Video geschrieben wird.

Herausgelöst aus `cloth_export_api.export_cloth` (93 Zeilen). Der Zielpfad ist
der Teil, in dem die Sicherheitsprüfungen stecken — und der einzige, der ohne
Blender und Grafikkarte prüfbar ist.

DREI QUELLEN, DREI PRÜFUNGEN
============================
* **`output_dir`** aus dem Rumpf: geht durch `SafePath.fuer_ausgabe()`. Vorher
  wurde nur „existiert als Verzeichnis" geprüft — ein `..\\..\\x` landete
  außerhalb.
* **`filename`** aus dem Rumpf: `SafePath.dateiname(..., '.mp4')`, dann wird der
  Motorname eingefügt (`rock.mp4` -> `rock_warp_only.mp4`). Zwei Motoren
  schreiben so nicht in dieselbe Datei.
* **`scene_name`** als Rückfall: wird BEREINIGT, nicht abgelehnt. Er kommt aus
  einem Textfeld und darf Leerzeichen und Umlaute enthalten; ein Export soll
  daran nicht scheitern. Positivliste (`isalnum`, `-`, `_`), alles andere wird
  ein Unterstrich — Verbotslisten haben hier schon zweimal einen Fall übersehen
  (nur `/`, nicht `\\`).
"""

import logging
import os
import time
import uuid

from django.conf import settings

from ..safe_paths import SafePath


logger = logging.getLogger('core')


class Stoffexportziel:
    """Ordner und Dateiname für ein Export-Video."""

    HOECHSTLAENGE = 60
    ERSATZNAME = 'scene'
    ENDUNG = '.mp4'
    #: Zufälliger Anhang, damit zwei Exporte derselben Szene sich nicht
    #: überschreiben (Zeitstempel allein reicht bei Sekundengenauigkeit nicht).
    ZUFALLSLAENGE = 6

    def __init__(self, rumpf, motor, jetzt=None):
        self.rumpf = rumpf or {}
        self.motor = motor
        self.jetzt = jetzt

    # ------------------------------------------------------------------ Ordner

    def ordner(self, vorgabe):
        """Der geprüfte Zielordner. Wirft `PfadAbgelehnt`, wenn er ausbricht."""
        gewuenscht = (self.rumpf.get('output_dir') or '').strip()
        if not gewuenscht:
            return vorgabe
        return str(SafePath.fuer_ausgabe().pruefe(gewuenscht))

    # ---------------------------------------------------------------- Dateiname

    def dateiname(self):
        """Der geprüfte Dateiname — mit Motornamen darin."""
        gewuenscht = (self.rumpf.get('filename') or '').strip()
        if gewuenscht:
            geprueft = SafePath.dateiname(gewuenscht, self.ENDUNG)
            stamm, endung = os.path.splitext(geprueft)
            return '%s_%s%s' % (stamm, self.motor, endung)
        return '%s_%s_%d_%s%s' % (self.namensstamm(), self.motor,
                                  int(self.jetzt or time.time()),
                                  uuid.uuid4().hex[:self.ZUFALLSLAENGE],
                                  self.ENDUNG)

    def namensstamm(self):
        """Szenenname -> unbedenklicher Namensstamm (siehe Modul-Docstring)."""
        text = str(self.rumpf.get('scene_name') or '').strip()
        stamm = ''.join(z if (z.isalnum() or z in '-_') else '_' for z in text)
        return stamm.strip('_')[:self.HOECHSTLAENGE] or self.ERSATZNAME

    # -------------------------------------------------------------------- URL

    @staticmethod
    def adresse(pfad):
        """Öffentliche URL — nur wenn die Datei unter `MEDIA_ROOT` liegt.

        Ein Export in einen eigenen Ordner (Studio-Ausgabe) hat keine URL; der
        Browser bekommt dann nur den Pfad zur Anzeige. Eine erfundene URL wäre
        ein toter Link.
        """
        wurzel = str(settings.MEDIA_ROOT)
        if not pfad.startswith(wurzel):
            return None
        rest = pfad[len(wurzel):].replace('\\', '/').lstrip('/')
        return settings.MEDIA_URL.rstrip('/') + '/' + rest

    # ------------------------------------------------------------- Auflösung

    def aufloesung(self, vorgabe=(1920, 1080), mindestens=64):
        """Breite und Höhe aus dem Rumpf — nie kleiner als `mindestens`."""
        try:
            breite = int(self.rumpf.get('width') or vorgabe[0])
            hoehe = int(self.rumpf.get('height') or vorgabe[1])
        except (TypeError, ValueError):
            # Nicht stumm: Der Nutzer bekommt sonst still 1920x1080, obwohl er
            # etwas anderes eingestellt hat — und sucht den Fehler im Renderer.
            logger.warning('Auflösung der Anfrage unbrauchbar (%r x %r) — es '
                           'gilt %dx%d', self.rumpf.get('width'),
                           self.rumpf.get('height'), *vorgabe)
            return vorgabe
        return max(mindestens, breite), max(mindestens, hoehe)
