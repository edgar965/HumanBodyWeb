# -*- coding: utf-8 -*-
"""Bildmodellablage — die Dateien eines Auftrags „Modell aus Bildern".

`<OBJECTS_ROOT>/modellauftraege/<kennung>/`
    original/     die hochgeladenen Dateien, unverändert
    zuschnitt/    ein JPG je Objekt (`Bildzuschnitt`), das die Sichtung und
                  die Schätzer bekommen — und die Auftragsseite zeigt
    schaetzung/   je Ausschnitt die Rohantwort des Schätzers (JSON) und
                  seine Netze (posed_vertices.npy, flame_vertices.npy)
    ergebnis/     ziel.npz, anpassung.json, vorschau_*.png, icon.png
    auftrag.log   Ausgabe des Arbeitsprozesses, auftrag.pid seine PID

`3DObjects/` steht in `.gitignore` (Edgar: sein Inhaltsordner). Nichts
davon liegt unter `media/` — die Bilder gehen über einen Endpunkt mit
Pfadprüfung heraus (`Bildmodellendpunkte.datei`), nicht als Statik.
"""

import os
import re
from pathlib import Path

from django.conf import settings

__all__ = ['Bildmodellablage']


class Bildmodellablage:
    ORDNER = 'modellauftraege'
    ORIGINAL = 'original'
    ZUSCHNITT = 'zuschnitt'
    SCHAETZUNG = 'schaetzung'
    ERGEBNIS = 'ergebnis'
    LOG = 'auftrag.log'
    PID = 'auftrag.pid'
    #: Was als Bild angenommen wird.
    ENDUNGEN = ('.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tif', '.tiff')
    #: … und was als Drehvideo (GVHMR, 19.09.2026).
    VIDEOENDUNGEN = ('.mp4', '.mov', '.webm', '.mkv', '.avi', '.m4v')
    _NAME = re.compile(r'[^A-Za-z0-9._-]+')

    def __init__(self, kennung):
        self.kennung = str(kennung)

    @classmethod
    def wurzel(cls):
        return Path(settings.OBJECTS_ROOT) / cls.ORDNER

    def ordner(self):
        return self.wurzel() / self.kennung

    def original(self):
        return self.ordner() / self.ORIGINAL

    def zuschnitt(self):
        return self.ordner() / self.ZUSCHNITT

    def schaetzung(self):
        return self.ordner() / self.SCHAETZUNG

    def ergebnis(self):
        return self.ordner() / self.ERGEBNIS

    def log(self):
        return self.ordner() / self.LOG

    def pid(self):
        return self.ordner() / self.PID

    def anlegen(self):
        for p in (self.original(), self.zuschnitt(), self.schaetzung(), self.ergebnis()):
            p.mkdir(parents=True, exist_ok=True)
        return self.ordner()

    # -------------------------------------------------------------- Dateien

    @classmethod
    def sauber(cls, name):
        """Dateiname ohne Pfadanteile und Sonderzeichen; leer → `bild`."""
        stamm, endung = os.path.splitext(os.path.basename(str(name or '')))
        stamm = cls._NAME.sub('_', stamm).strip('._') or 'bild'
        return stamm + endung.lower()

    @classmethod
    def ist_bild(cls, name):
        return os.path.splitext(str(name))[1].lower() in cls.ENDUNGEN

    @classmethod
    def ist_video(cls, name):
        return os.path.splitext(str(name))[1].lower() in cls.VIDEOENDUNGEN

    @classmethod
    def ist_eingang(cls, name):
        return cls.ist_bild(name) or cls.ist_video(name)

    def original_ablegen(self, hochgeladen):
        """Eine hochgeladene Datei (Django `UploadedFile`) ablegen; Pfad.
        Ein vorhandener Name bekommt eine Nummer."""
        self.anlegen()
        name = self.sauber(getattr(hochgeladen, 'name', 'bild'))
        ziel = self.original() / name
        stamm, endung = os.path.splitext(name)
        n = 1
        while ziel.exists():
            n += 1
            ziel = self.original() / ('%s_%d%s' % (stamm, n, endung))
        with open(ziel, 'wb') as f:
            for stueck in hochgeladen.chunks():
                f.write(stueck)
        return ziel

    def originale(self):
        if not self.original().is_dir():
            return []
        return sorted(p for p in self.original().iterdir() if self.ist_bild(p.name))

    def videos(self):
        if not self.original().is_dir():
            return []
        return sorted(p for p in self.original().iterdir() if self.ist_video(p.name))

    def videoordner(self, video):
        """Wo GVHMR zu einem Video rechnet: `schaetzung/gvhmr/`."""
        return self.schaetzung() / 'gvhmr'

    def datei(self, unterordner, name):
        """Pfad einer Datei im Auftrag — nur innerhalb des Auftragsordners."""
        wurzel = self.ordner().resolve()
        pfad = (self.ordner() / unterordner / os.path.basename(str(name))).resolve()
        if wurzel not in pfad.parents:
            raise ValueError('Pfad liegt außerhalb des Auftrags')
        return pfad

    def loeschen(self):
        import shutil

        if self.ordner().is_dir():
            shutil.rmtree(self.ordner(), ignore_errors=True)
