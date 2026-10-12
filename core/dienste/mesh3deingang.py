# -*- coding: utf-8 -*-
"""Mesh3deingang — ein Netz (Datei oder Ordner) aus dem Browser entgegennehmen (11.10.2026).

Edgar: „den Import eines neuen Meshes vergessen“. Der Browser verrät den Pfad einer gewählten Datei nicht, das Feld „Pfad“ des Formulars nützt also nur, wer ihn kennt. Hier kommt die Datei selbst:
„Datei wählen“ (eine oder mehrere) und „Ordner wählen“ (alle Dateien des Ordners, `webkitdirectory`) laden nach `3DObjects/mesh3d_eingang/<Kennung>/…` — die Ordnerstruktur bleibt (eine OBJ
findet ihre MTL und ihre Bilder über relative Pfade wieder). Die Antwort nennt die Datei, die der Auftrag liest; sie kommt in das Feld „Pfad“, danach läuft alles wie mit einem getippten Pfad.

Angenommen werden die Endung des gewählten Formats und die Beilagen eines Netzes (`BEILAGEN`: MTL, Bilder, Puffer); alles andere wird still ausgelassen und in der Antwort gezählt. Pfade aus dem Browser
werden bereinigt (kein `..`, kein Laufwerk, keine Sonderzeichen) und müssen unter dem Zielordner bleiben. Eine Einzeldatei bekommt einen Ordner nach ihrem Namen — „Ordner wie die Datei“ ist die Vorgabe
für den Namen der Figur (`Blendimportquelle`). Hochgeladenes wird nie überschrieben (jeder Upload ein eigener Ordner) und nicht von selbst gelöscht.
"""

import logging
import re
from pathlib import Path

from django.conf import settings
from django.utils import timezone

from ..daten.auftragskennung import Auftragskennung
from ..daten.hochgeladen import Hochgeladen
from .blendimportformate import Blendimportformate
from .blendimportquelle import Blendimportquelle

logger = logging.getLogger('core')

__all__ = ['Mesh3deingang']


class Mesh3deingang:
    ORDNER = 'mesh3d_eingang'
    BEILAGEN = ('.mtl', '.png', '.jpg', '.jpeg', '.webp', '.tga', '.bmp', '.tif', '.tiff', '.dds', '.exr', '.hdr', '.bin')
    _UNGUELTIG = re.compile(r'[<>:"|?*\x00-\x1f]')

    def __init__(self, format):
        self.format = Blendimportformate.pruefen(format)
        self.endung = Blendimportformate.endung(self.format)

    @classmethod
    def wurzel(cls):
        return Path(settings.OBJECTS_ROOT) / cls.ORDNER

    def erlaubt(self):
        """Die Endungen, die `<input accept>` und der Server annehmen."""
        return (self.endung,) + self.BEILAGEN

    @classmethod
    def teile(cls, roh):
        """Der Weg aus dem Browser als Liste sauberer Namen: Trenner `/` und `\\`, kein `..`, keine Laufwerks- und Sonderzeichen."""
        teile = []
        for teil in re.split(r'[\\/]+', str(roh or '')):
            teil = cls._UNGUELTIG.sub('_', teil).strip().strip('.')
            if teil:
                teile.append(teil[:120])
        return teile

    def ablegen(self, dateien, pfade):
        """`dateien`: hochgeladene Dateien, `pfade`: ihr Weg im gewählten Ordner (oder leer) → `{pfad, ordner, anzahl, mb, ausgelassen}`; `ValueError` mit dem Grund."""
        eintraege, ausgelassen = [], 0
        for nummer, datei in enumerate(dateien):
            teile = self.teile(pfade[nummer] if nummer < len(pfade) and pfade[nummer] else datei.name)
            if teile and Path(teile[-1]).suffix.lower() in self.erlaubt():
                eintraege.append((datei, teile))
            else:
                ausgelassen += 1
        haupt = [teile for _, teile in eintraege if Path(teile[-1]).suffix.lower() == self.endung]
        if not haupt:
            raise ValueError('Keine %s-Datei in der Auswahl' % self.endung)
        if all(len(teile) == 1 for _, teile in eintraege):
            # Einzeldateien ohne Ordner: ein Ordner nach dem Namen der ersten Hauptdatei (ohne Fassung), sonst hieße die Figur wie die Kennung
            stamm = Blendimportquelle._FASSUNG.sub('', Path(haupt[0][-1]).stem).strip() or Path(haupt[0][-1]).stem
            eintraege = [(datei, self.teile(stamm)[:1] + teile) for datei, teile in eintraege]
        ziel = self.wurzel() / Auftragskennung.frei(timezone.now(), lambda k: (self.wurzel() / k).exists())
        gelesen, groesse = [], 0
        for datei, teile in eintraege:
            pfad = ziel.joinpath(*teile)
            if not pfad.resolve().is_relative_to(ziel.resolve()):
                raise ValueError('Ungültiger Pfad: %s' % '/'.join(teile))
            pfad.parent.mkdir(parents=True, exist_ok=True)
            Hochgeladen.ablegen(pfad, datei)
            groesse += pfad.stat().st_size
            if pfad.suffix.lower() == self.endung:
                gelesen.append(pfad)
        beste = max(gelesen, key=lambda p: (Blendimportquelle.fassung(p), p.stat().st_size))
        logger.info('Mesh-3D-Eingang: %d Dateien (%.1f MB) nach %s, gelesen wird %s', len(eintraege), groesse / 1e6, ziel, beste.name)
        return {'pfad': str(beste), 'ordner': str(ziel), 'anzahl': len(eintraege), 'mb': round(groesse / 1e6, 1), 'ausgelassen': ausgelassen,
                'hauptdateien': [p.name for p in sorted(gelesen)]}
