# -*- coding: utf-8 -*-
"""Dazgeograftangepasst — das Daz-Geograft als Stück „<Modell> Daz Scham": angepasst an die Scham eines Blender-Imports (10.10.2026).

Edgar: „im Blender-File war die Scham ja vorgegeben, die sollst du mit Hilfe der Scham aus Genesis nachbauen". Der Weg ist der von `Dazgeograft` (Käfig → Stufe 1 → Loch → Naht →
Stück), nur mit drei Änderungen an den Haken dort:

    figur        die Figur des gespeicherten Modells (`figur.regler` in `data/models/<Modell>.json`) statt der Grundfigur — das Loch und der Ring liegen auf IHRER Haut
    angleichen   das Geograft wird in den Raum dieser Figur verlegt und auf die Original-Scham angepasst (`Dazgeograftanpassung`)
    backen       Farbe, Rauheit und Normalen der Original-Scham werden auf das Geograft übertragen (`Dazgeograftbacken`); die UV des Geografts bleibt die von Daz
Die Daz-Formmorphe (`Dazgeograftmorphe`, Realism, Vorhaut) und die Charakter-Varianten gehören zur Grundform und entfallen hier; die Regler `sch_*` rechnen aus der Form des Stücks.
"""
import json
import logging

from .dazgeograft import Dazgeograft

logger = logging.getLogger('core')

__all__ = ['Dazgeograftangepasst']


class Dazgeograftangepasst(Dazgeograft):
    def __init__(self, modell, scham, name=None, aufloesung=1024, steifigkeit=None):
        """`modell`: Name des gespeicherten Modells (`cute girl`); `scham`: Anzeigename des Scham-Stücks seines Imports (`cute girl Scham`); `name`: des neuen Stücks."""
        from django.conf import settings

        super().__init__('frau')
        self.modell, self.scham, self.aufloesung, self.steifigkeit = modell, scham, int(aufloesung), steifigkeit
        daten = json.loads((settings.HUMANBODY_MODELS_DIR / (modell + '.json')).read_text(encoding='utf-8'))
        self.regler = dict((daten.get('figur') or {}).get('regler') or {})
        self.haut_ordner = settings.HUMANBODY_MODELS_DIR / 'Texturen' / modell
        self.anzeige = name or '%s Daz Scham' % modell
        self.gruppe = 'Genitalia %s' % modell
        self._anpassung = None

    def figur(self):
        from .dazgeografthaut import Dazgeografthaut

        return Dazgeografthaut.grundfigur(self.regler)

    def angleichen(self, punkte, dreiecke, figur, maske, bericht):
        from .blendimportschamloch import Blendimportschamloch
        from .dazgeograftanpassung import Dazgeograftanpassung
        from .dazgeografthaut import Dazgeografthaut
        from .dazgeograftziel import Dazgeograftziel

        haut = Blendimportschamloch(figur['punkte'], figur['dreiecke'])
        ring_punkte = haut.ringpunkte(haut.ring(maske))
        anpassung = Dazgeograftanpassung(Dazgeografthaut.grundfigur(), figur, ring_punkte, Dazgeograftziel(self.scham))
        verlegt = anpassung.verlegen(punkte)
        angepasst = anpassung.anpassen(verlegt, dreiecke, self.steifigkeit)
        bericht['anpassung'] = anpassung.bericht
        self._anpassung = anpassung
        return angepasst

    def backen(self, punkte, dreiecke, uv_ecken, figur, bericht):
        from Genesis9.eigenstueck import G9eigenstueck

        from .dazgeograftbacken import Dazgeograftbacken

        kennung, _anzeige = G9eigenstueck.kennung_und_name(self.anzeige)
        ausgabe = G9eigenstueck.arbeitsordner(kennung) / 'gebacken'
        dateien, zahlen = Dazgeograftbacken(self._anpassung.ziel, figur, self.haut_ordner, self.aufloesung).backen(punkte, dreiecke, uv_ecken, ausgabe)
        bericht['bake'] = zahlen
        return dateien

    def vorgabe(self):
        """Die Original-Scham des Imports (nur der Teil, den die Figur nicht trägt) mit ihrer Atlasfarbe."""
        ziel = self._anpassung.ziel
        return {'punkte': ziel.punkte, 'dreiecke': ziel.dreiecke, 'farbe_an': ziel.farbe_an, 'teil': True}

    def kachelbild(self):
        return lambda kachel: self.haut_ordner / ('haut_%d_farbe.klein.jpg' % kachel)

    def zusaetze(self, quelle, _kaefig, bilanz):
        """Nur die Regler des Katalogs (`sch_*`) — sie rechnen aus der Form des angepassten Stücks."""
        from Genesis9.anatomien import G9anatomien

        from .dazgeograftmorphe import Dazgeograftmorphe

        gebaut, gescheitert = Dazgeograftmorphe.katalog_bauen(bilanz['stueck'], G9anatomien.fuer(self.NAMEN[self.geschlecht][1]))
        bilanz['bericht']['regler_gebaut'], bilanz['bericht']['regler_gescheitert'] = len(gebaut), gescheitert
        logger.info('Daz-Geograft angepasst an %s: %d Regler', self.scham, len(gebaut))
