# -*- coding: utf-8 -*-
"""MhMaterial — Farbe und Textur aus einer MakeHuman-.mhmat-Datei.

Aus `mh_proxy_fit` herausgeloest (Umbau 15.08.2026). Dort wurde die Datei ZWEIMAL
geoeffnet und zeilenweise durchsucht — einmal fuer `diffuseColor`, einmal fuer
`diffuseTexture` —, jedes Mal mit eigenem try/except. Einmal lesen genuegt.
"""
import glob
import logging
import os

logger = logging.getLogger('core')


class MhMaterial:
    """Liest die Materialangaben eines Kleidungsstuecks."""

    #: Kantenlaenge, auf die eine Textur zum Farbmitteln verkleinert wird.
    PROBE = 16

    def __init__(self, verzeichnis):
        self.verzeichnis = verzeichnis
        self.farbe = None            # (r, g, b) in 0..1
        self.texturname = None
        self.texturfarbe = None
        self._lesen()

    # ------------------------------------------------------------------ lesen

    def _lesen(self):
        dateien = glob.glob(os.path.join(self.verzeichnis, '*.mhmat'))
        if not dateien:
            return
        try:
            with open(dateien[0], encoding='utf-8', errors='replace') as f:
                for zeile in f:
                    self._zeile(zeile.strip())
        except OSError as e:
            logger.debug('Materialdatei nicht lesbar: %s', e)
            return
        if self.texturname:
            self._texturfarbe_mitteln()

    def _zeile(self, zeile):
        if zeile.startswith('diffuseColor'):
            teile = zeile.split()
            if len(teile) >= 4:
                try:
                    self.farbe = [float(teile[1]), float(teile[2]), float(teile[3])]
                except ValueError:
                    logger.debug('diffuseColor unlesbar: %r', zeile)
        elif zeile.startswith('diffuseTexture') and not self.texturname:
            name = zeile.split(None, 1)[1].strip() if ' ' in zeile else ''
            if name and self._ist_bild(os.path.join(self.verzeichnis, name)):
                self.texturname = name

    #: Die ersten Bytes eines echten PNG bzw. JPEG.
    BILDKENNUNGEN = (b'\x89PNG\r\n\x1a\n', b'\xff\xd8\xff')

    @classmethod
    def _ist_bild(cls, pfad):
        """Steht dort wirklich ein Bild — oder nur ein Git-LFS-Zeiger?

        GEFUNDEN AM 06.09.2026: `female_casualsuit01_diffuse.png` ist 135 Bytes
        gross und enthaelt Text::

            version https://git-lfs.github.com/spec/v1
            oid sha256:414d46af…
            size 3019656

        Der LFS-Inhalt wurde nie geholt. `os.path.isfile` sagt trotzdem ja, die
        Antwort meldete `has_texture`, und der Browser faerbt das Material
        daraufhin WEISS, damit die Textur nicht doppelt einfaerbt. Die Textur
        kam dann nie — das Kleidungsstueck blieb weiss, und die Farbe aus der
        `.mhmat` wurde nicht einmal versucht. Ein Fehler ohne Fehlermeldung.
        """
        try:
            with open(pfad, 'rb') as datei:
                kopf = datei.read(8)
        except OSError:
            return False
        return any(kopf.startswith(k) for k in cls.BILDKENNUNGEN)

    def _texturfarbe_mitteln(self):
        """Mittlere Farbe der Textur — fuer die Vorschau, wenn kein Bild geladen
        wird."""
        try:
            from PIL import Image
            pfad = os.path.join(self.verzeichnis, self.texturname)
            bild = Image.open(pfad).convert('RGB').resize((self.PROBE, self.PROBE))
            punkte = list(bild.getdata())
            self.texturfarbe = [round(sum(p[i] for p in punkte) / len(punkte) / 255.0,
                                      3)
                                for i in range(3)]
        except Exception as e:                                    # noqa: BLE001
            logger.debug('Texturfarbe nicht berechenbar: %s', e)

    # ----------------------------------------------------------------- ausgeben

    def in_antwort(self, antwort):
        """Die Materialangaben in die JSON-Antwort eintragen."""
        if self.farbe:
            antwort['mat_color'] = self.farbe
        if self.texturname:
            antwort['has_texture'] = True
            antwort['texture_name'] = self.texturname
            if self.texturfarbe:
                antwort['texture_color'] = self.texturfarbe
        return antwort
