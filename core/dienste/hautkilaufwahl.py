# -*- coding: utf-8 -*-
"""Hautkilaufwahl — welcher Lauf der Haut-KI die Hautkacheln eines Foto-Genesis-Jobs schreibt (17.11.2026).

Edgar: „mach einen Job n1-HautKI als Kopie von n1, mit der neuen HautKI“, „Die Haut-KI ist doch einstellbar, passe die Einstellung an in dieser combo“. Bis dahin galt für alle
Jobs der Lauf in `ki_fassungen.json` → `hautki` (`Meshgenesiskifassungen`); das Häkchen „Haut-KI“ schaltet nur an oder aus. Jetzt wählt ein Job einen anderen Lauf, ohne dass
sich die übrigen ändern: job.json `pshuman.haut_ki_lauf` (`Fotogenesispshuman`), gelesen im Schritt „Haut“ (`meshgenesis/meshgenesis_hautki_einsatz.py`). Leer = der eingesetzte.

Angeboten werden der eingesetzte Lauf und die jüngeren unter `_hautki/laeufe/` mit `netz.pt` — die Kandidaten für den Einsatz; die älteren hat niemand gegen den heutigen Lader
(`KoerperKI_alle.hautki.HautKI.laden`) geprüft.
"""
from pathlib import Path

from django.conf import settings

__all__ = ['Hautkilaufwahl']


class Hautkilaufwahl:
    FELD = 'haut_ki_lauf'

    @staticmethod
    def ordner():
        return Path(settings.OBJECTS_ROOT) / '_Output' / 'MeshGenesisJobs' / '_hautki' / 'laeufe'

    @staticmethod
    def eingesetzt():
        """Der Lauf aus `ki_fassungen.json` → `hautki` ('' ohne)."""
        from .meshgenesiskifassungen import Meshgenesiskifassungen
        return str(Meshgenesiskifassungen.lesen().get('hautki') or '')

    @classmethod
    def laeufe(cls):
        """Wählbare Läufe, jüngster zuerst: der eingesetzte und die jüngeren (die Namen beginnen mit der Zeit, `JJJJ.MM.TT.hh.mm_`), je mit `netz.pt`."""
        eingesetzt = cls.eingesetzt()
        try:
            namen = sorted((p.name for p in cls.ordner().iterdir() if (p / 'netz.pt').is_file()), reverse=True)
        except OSError:
            return []
        return [n for n in namen if n >= eingesetzt]

    @staticmethod
    def kurz(name):
        """'2026.11.17.00.11_hautki_atlas53_fotojobs' → '17.11. atlas53_fotojobs'."""
        zeit, _, rest = name.partition('_')
        teile = zeit.split('.')
        if len(teile) < 3:
            return name
        return ('%s.%s. %s' % (teile[2], teile[1], rest.removeprefix('hautki_'))).strip()

    @classmethod
    def auswahl(cls):
        """[(Wert, Text)] der Combo: '' = der eingesetzte Lauf, danach die jüngeren."""
        eingesetzt = cls.eingesetzt()
        erste = ('', 'eingesetzt (%s)' % cls.kurz(eingesetzt) if eingesetzt else 'eingesetzt (keiner)')
        return [erste] + [(n, cls.kurz(n)) for n in cls.laeufe() if n != eingesetzt]

    @classmethod
    def gueltig(cls, name):
        return name == '' or name in cls.laeufe()
