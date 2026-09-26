# -*- coding: utf-8 -*-
"""Meshablage — die Dateien eines Mesh-Auftrags (Reiter „Mesh", 26.09.2026).

`<OBJECTS_ROOT>/meshauftraege/<kennung>/`
    eingang/      die hochgeladenen Fotos, unverändert
    vorbereitet/  je Foto das freigestellte RGBA-PNG (quadratisch, Objekt mittig) und
                  die Maske — das bekommt das Formmodell
    arbeit/       Zwischenstände des Laufs (Rohnetz, Kameras, Texturschichten)
    ergebnis/     mesh.glb, mesh.obj/.mtl/_textur.png, mesh.ply, vorschau_*.png, icon.png,
                  bericht.json
    auftrag.log   Ausgabe des Arbeitsprozesses, auftrag.pid seine PID

`3DObjects/` ist nicht versioniert (Edgars Inhaltsordner); die Dateien gehen über einen
Endpunkt mit Pfadprüfung heraus (`Meshendpunkte.datei`), nicht als Statik.
"""

import os
import re
import shutil
import time
from pathlib import Path

from django.conf import settings

__all__ = ['Meshablage']


class Meshablage:
    ORDNER = 'meshauftraege'
    EINGANG = 'eingang'
    VORBEREITET = 'vorbereitet'
    ARBEIT = 'arbeit'
    ERGEBNIS = 'ergebnis'
    LOG = 'auftrag.log'
    PID = 'auftrag.pid'
    #: Welche Unterordner über den Datei-Endpunkt lesbar sind.
    LESBAR = (EINGANG, VORBEREITET, ERGEBNIS)
    ENDUNGEN = ('.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tif', '.tiff')
    _NAME = re.compile(r'[^A-Za-z0-9._-]+')

    def __init__(self, kennung):
        self.kennung = str(kennung)

    @classmethod
    def wurzel(cls):
        return Path(settings.OBJECTS_ROOT) / cls.ORDNER

    def ordner(self):
        return self.wurzel() / self.kennung

    def unter(self, name):
        return self.ordner() / name

    def log(self):
        return self.ordner() / self.LOG

    def pid(self):
        return self.ordner() / self.PID

    def anlegen(self):
        for name in (self.EINGANG, self.VORBEREITET, self.ARBEIT, self.ERGEBNIS):
            self.unter(name).mkdir(parents=True, exist_ok=True)
        return self.ordner()

    # -------------------------------------------------------------- Dateien

    @classmethod
    def ist_bild(cls, name):
        return os.path.splitext(str(name or ''))[1].lower() in cls.ENDUNGEN

    @classmethod
    def sauber(cls, name):
        """Dateiname ohne Pfadanteile und Sonderzeichen; leer → `bild`."""
        stamm, endung = os.path.splitext(os.path.basename(str(name or '')))
        stamm = cls._NAME.sub('_', stamm).strip('._') or 'bild'
        return stamm[:80] + endung.lower()

    def eingang_ablegen(self, hochgeladen):
        """Eine hochgeladene Datei unter freiem, sauberem Namen in `eingang/` legen."""
        self.anlegen()
        name = self.sauber(hochgeladen.name)
        ziel = self.unter(self.EINGANG) / name
        stamm, endung = os.path.splitext(name)
        n = 2
        while ziel.exists():
            ziel = self.unter(self.EINGANG) / ('%s_%d%s' % (stamm, n, endung))
            n += 1
        with open(ziel, 'wb') as aus:
            for stueck in hochgeladen.chunks():
                aus.write(stueck)
        return ziel.name

    def eingaenge(self):
        ordner = self.unter(self.EINGANG)
        if not ordner.is_dir():
            return []
        return sorted(p.name for p in ordner.iterdir() if p.is_file() and self.ist_bild(p.name))

    def datei(self, unterordner, name):
        """Pfad einer Datei im Auftrag — nur in `LESBAR`, nur ein Name ohne Pfad."""
        if unterordner not in self.LESBAR:
            raise ValueError('Unterordner %s' % unterordner)
        rein = os.path.basename(str(name or ''))
        if not rein or rein != name or rein in ('.', '..'):
            raise ValueError('Name %s' % name)
        pfad = (self.unter(unterordner) / rein).resolve()
        if not pfad.is_relative_to(self.unter(unterordner).resolve()):
            raise ValueError('Pfad außerhalb: %s' % name)
        return pfad

    def loeschen(self):
        """Den ganzen Auftragsordner entfernen — mit kurzem Nachversuch, weil Windows eine
        eben ausgelieferte Datei (GLB im Browser) kurz sperrt."""
        ordner = self.ordner()
        for _ in range(6):
            if not ordner.exists():
                return True
            try:
                shutil.rmtree(ordner)
                return True
            except OSError:
                time.sleep(0.25)
        return not ordner.exists()
