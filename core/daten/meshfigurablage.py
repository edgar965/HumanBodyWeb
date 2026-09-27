# -*- coding: utf-8 -*-
"""Meshfigurablage — die Dateien eines Auftrags „Mesh to 3D" (27.09.2026).

`<OBJECTS_ROOT>/meshfigurauftraege/<kennung>/`
    eingang/     das hochgeladene Netz, unverändert (GLB, OBJ + MTL + Texturen, PLY, STL, OFF)
    arbeit/      auftrag.json, Lage des Netzes, Landmarken, Genesis-Dateien je Runde,
                 Zustand (Haltung), Rest, Texelfarben — Zwischenstände der Schritte
    ergebnis/    Übersichtsbilder der Erkennung, Vergleichsbild, Vorschauen, Icon,
                 Texturkacheln (`meshfigur_<kachel>.jpg`), bericht.json
    auftrag.log  Ausgabe des Arbeitsprozesses, auftrag.pid seine PID

`3DObjects/` ist nicht versioniert; die Dateien gehen über einen Endpunkt mit Pfadprüfung
heraus (`Meshfigurendpunkte.datei`), nicht als Statik — wie `Meshablage`.
"""

import os
import re
import shutil
import time
from pathlib import Path

from django.conf import settings

__all__ = ['Meshfigurablage']


class Meshfigurablage:
    ORDNER = 'meshfigurauftraege'
    EINGANG = 'eingang'
    ARBEIT = 'arbeit'
    ERGEBNIS = 'ergebnis'
    LOG = 'auftrag.log'
    PID = 'auftrag.pid'
    LESBAR = (EINGANG, ERGEBNIS)
    #: Netzformate, die trimesh liest; OBJ darf seine MTL und Bilder mitbringen.
    NETZE = ('.glb', '.gltf', '.obj', '.ply', '.stl', '.off')
    BEILAGEN = ('.mtl', '.png', '.jpg', '.jpeg', '.bin', '.webp', '.tga', '.bmp')
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

    def arbeit(self, name=''):
        return self.unter(self.ARBEIT) / name if name else self.unter(self.ARBEIT)

    def ergebnis(self, name=''):
        return self.unter(self.ERGEBNIS) / name if name else self.unter(self.ERGEBNIS)

    def anlegen(self):
        for name in (self.EINGANG, self.ARBEIT, self.ERGEBNIS):
            self.unter(name).mkdir(parents=True, exist_ok=True)
        return self.ordner()

    # -------------------------------------------------------------- Dateien

    @classmethod
    def ist_netz(cls, name):
        return os.path.splitext(str(name or ''))[1].lower() in cls.NETZE

    @classmethod
    def ist_beilage(cls, name):
        return os.path.splitext(str(name or ''))[1].lower() in cls.BEILAGEN

    @classmethod
    def sauber(cls, name):
        """Dateiname ohne Pfadanteile und Sonderzeichen — Endung klein, Stamm ASCII."""
        stamm, endung = os.path.splitext(os.path.basename(str(name or '')))
        stamm = cls._NAME.sub('_', stamm).strip('._') or 'netz'
        return stamm[:80] + endung.lower()

    def ablegen(self, hochgeladen, name=None):
        """Eine hochgeladene Datei in `eingang/` legen. OBJ-Beilagen (MTL, Bilder) behalten ihren
        Namen, weil die MTL sie so nennt — deshalb hier nur säubern, nicht umbenennen."""
        self.anlegen()
        ziel = self.unter(self.EINGANG) / self.sauber(name or hochgeladen.name)
        with open(ziel, 'wb') as aus:
            for stueck in hochgeladen.chunks():
                aus.write(stueck)
        return ziel.name

    def netzdatei(self):
        """Pfad des Netzes im Eingang (das erste mit Netzendung) — oder None."""
        ordner = self.unter(self.EINGANG)
        if not ordner.is_dir():
            return None
        for p in sorted(ordner.iterdir()):
            if p.is_file() and self.ist_netz(p.name):
                return p
        return None

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
        """Den Auftragsordner entfernen — mit Nachversuch (Windows sperrt eben ausgelieferte Dateien)."""
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
