# -*- coding: utf-8 -*-
"""Meshgenesistestgenesisfigur — die Figur eines Mesh-Genesis-Tests als Genesis-Modell, wie Testseite und Ergebniskarte sie zeigen (23.11.2026).

EINE Angabe für die Seite (`Meshgenesistest.daten` → `figur_genesis`) und „Als Modell speichern“ (`Meshgenesistestmodell.figur_der_seite`). Bis dahin baute nur die Seite sie;
das gespeicherte Modell trug die Grundhaut ohne Haut der KI, ohne Gesicht aus dem Foto und ohne Haut-Korrekturen (Edgar 23.11.2026: „beim Speichern sollen zumindest Haare, Bart,
Haut mitgehen“). Bestandteile, wie sie seit Oktober/November in `daten` standen:
  * Grundfigur, Regler, Anatomie-Stück (`Meshgenesisergebnisfigur._figur`)
  * Haut der KI als `fototextur` (`Meshgenesistesthaut.kacheln`, 31.10.2026)
  * Gesicht aus dem Frontfoto: Augenbild, Brauenfarbe, Mimik (`Fotogesicht`, 19.11.2026)
  * Haut-Korrekturen als `hautausgleich` (`Meshgenesistesthautkorrektur`, 20.11.2026)

    Meshgenesistestgenesisfigur.fuer(kennung, geschlecht, regler) -> {figur, regler, kleidung, garmentcode, pose, fototextur, brauen?, hautausgleich?}
"""

__all__ = ['Meshgenesistestgenesisfigur']


class Meshgenesistestgenesisfigur:

    @staticmethod
    def adresse(kennung, geschlecht, name):
        """Adresse eines Bilds der Figur (`Meshgenesistestendpunkte.figurbild`; `Texturquelle.FIGUR_MESHGENESIS` löst sie beim Speichern auf)."""
        return '/api/meshgenesis/test/%s/figur/%s/bild/%s' % (kennung, geschlecht, name)

    @classmethod
    def fuer(cls, kennung, geschlecht, regler):
        from .fotogesicht import Fotogesicht
        from .meshgenesisergebnisfigur import Meshgenesisergebnisfigur
        from .meshgenesistest import Meshgenesistest
        from .meshgenesistesthaut import Meshgenesistesthaut
        from .meshgenesistesthautkorrektur import Meshgenesistesthautkorrektur
        figur = dict(Meshgenesisergebnisfigur._figur(geschlecht, regler), fototextur=Meshgenesistesthaut.kacheln(kennung, geschlecht))
        figur = Fotogesicht.figur(figur, Meshgenesistest.pfad(kennung), geschlecht, lambda name: cls.adresse(kennung, geschlecht, name))
        return Meshgenesistesthautkorrektur.figur(figur, kennung, geschlecht)
