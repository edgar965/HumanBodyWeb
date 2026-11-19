# -*- coding: utf-8 -*-
"""Fotogesicht — das am Frontfoto gemessene Gesicht in die Genesis-Figur der Foto-Genesis-Seite (19.11.2026).

Edgar: „ja, bau das Gesicht“ (zusammen mit 3dtools-96, das am Frontfoto misst: Mediapipe-Gesichtspunkte und
Blendshapes). Ablage je Figur, geschrieben von der Mesh-Genesis-Kette: `<ordner>/gesicht_<g>/gesicht.json` =
{"augen": "augen.jpg", "brauen" oder "brauen_hex": "#rrggbb", "regler": {facs_ctrl_…: Wert}, "gemessen": {…}},
daneben das eingefärbte Augenbild. `<ordner>` ist der Testordner `_test/<k>/` (`Meshgenesistest.daten`)
bzw. der Figurordner eines Foto-Jobs `<Job>/figur/` (`Fotogenesisfigur.daten`).

In die Angabe für `Genesis9Modell` (`figur_genesis`) kommen:
  fototextur.augen   Adresse des Augenbilds (`Genesis9fototextur.anhang` legt es als Albedo auf die Augäpfel;
                     Bildname `AUGEN` an der Bildroute der Figur)
  brauen             die nächste fertige Brauenfarbe zum gemessenen Hex (`Fotogesichtbrauen`; die Figur
                     nimmt nur Kennungen fertiger Farben)
  regler             die Mimik-Regler über die Form-Regler gelegt
Ohne Datei bleibt die Angabe, wie sie war.

    Fotogesicht.figur(figur_genesis, ordner, g, adresse)   # adresse(bildname) -> Adresse an der Bildroute
    Fotogesicht.bild(ordner, g, name) -> Path | None        # für die Bildroute: nur `AUGEN`
"""
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

__all__ = ['Fotogesicht']


class Fotogesicht:
    DATEI = 'gesicht.json'
    #: Name des Augenbilds an der Bildroute der Figur — fällt mit keiner Hautkachel (`10??.jpg`) und keinem
    #: Bild des Anzeigenetzes zusammen
    AUGEN = 'gesicht_augen.jpg'

    @classmethod
    def lesen(cls, ordner, g):
        datei = Path(ordner) / ('gesicht_%s' % g) / cls.DATEI
        if not datei.is_file():
            return None
        try:
            d = json.loads(datei.read_text(encoding='utf-8'))
        except (OSError, ValueError) as fehler:
            logger.warning('Fotogesicht: %s nicht lesbar (%s)', datei, fehler)
            return None
        return d if isinstance(d, dict) else None

    @classmethod
    def figur(cls, figur, ordner, g, adresse):
        d = cls.lesen(ordner, g) if figur else None
        if not d:
            return figur
        from .fotogesichtbrauen import Fotogesichtbrauen
        aus = dict(figur)
        augen = cls._augenbild(ordner, g, d)
        if augen is not None:
            stand = int(augen.stat().st_mtime)
            augen_adresse = '%s?t=%d' % (adresse(cls.AUGEN), stand)
            aus['fototextur'] = dict(aus.get('fototextur') or {}, augen=augen_adresse)
        brauen_alt = str(d.get('brauen') or '')
        hex_wert = d.get('brauen_hex') or (brauen_alt if brauen_alt.startswith('#') else None)
        brauen = Fotogesichtbrauen.naechste(hex_wert, aus.get('brauenstil')) if hex_wert else None
        if brauen:
            aus['brauen'] = brauen
        regler = {k: float(v) for k, v in (d.get('regler') or {}).items()
                  if isinstance(v, (int, float)) and not isinstance(v, bool)}
        if regler:
            aus['regler'] = dict(aus.get('regler') or {}, **regler)
        return aus

    @classmethod
    def bild(cls, ordner, g, name):
        if str(name) != cls.AUGEN or ordner is None:
            return None
        d = cls.lesen(ordner, g)
        return cls._augenbild(ordner, g, d) if d else None

    @staticmethod
    def _augenbild(ordner, g, d):
        """Das Augenbild aus `gesicht.json` (`augen`: Dateiname im selben Ordner, ohne Pfad) — oder None."""
        name = str(d.get('augen') or '')
        if not name or Path(name).name != name or not name.lower().endswith(('.jpg', '.jpeg', '.png')):
            return None
        pfad = Path(ordner) / ('gesicht_%s' % g) / name
        return pfad if pfad.is_file() else None
