# -*- coding: utf-8 -*-
"""Dazgeograftverlegt — das Daz-Geograft in seiner Form, nur der Figur eines Modells angelegt (11.10.2026, „cute girl daz5").

Edgar, 11.10.2026, nach „Daz4 sind noch immer katastrophal": „Daz original ist doch exakt das was man haben möchte, mit ein paar Anpassungen in Richtung alt4. Nimm Daz original und baue
behutsam Anpassungen rein, die sich an den Code von alt4 richten."

Die Stücke „Daz1 … Daz4" (`Dazgeograftangepasst`) zogen das Geograft auf die Scham des Blender-Imports (Strahlen längs der Hautnormalen, Laplace, Baking vom Original): die Rundung des Geografts ging dabei
verloren (Querschnitte: Stufe bei y 900–915, zwei Ebenen; bei daz4 gefaltete Lagen im Spalt). Hier bleibt die FORM die von Daz; die Anpassungen sind die von alt4 (`Schamtiefenfeld`):

    Figur       die Haut des Modells (`figur.regler`, ohne Unterkleid) statt der Grundfigur — Loch und Ring liegen auf IHRER Haut
    verlegen    die Punkte des Geografts folgen der Verschiebung der Haut von der Grundfigur zur Figur (`Dazgeograftanpassung.verlegen`: 6 nächste Hautpunkte, Gewicht 1/d², über das Netz geglättet) — weich, ohne
                das Original zu kennen
    Loch        das eigene Loch des Geografts (die verdeckten Käfigflächen), nicht der Umriss eines Blender-Stücks
    Naht        Rand auf den Ring, Auslauf `Schamtiefenfeld.NAHT_BAND_MM`; die Lücke zur Haut läuft als weiches Feld ins Stück (`Schamtiefenfeld`), dann die Randseite
    Textur      Farbe, Rauheit und Normalen aus den Hautkacheln des Modells und dem Original (`Dazgeograftbacken`; die FORM bleibt die von Daz): bis 4 mm vom Original gilt dessen Atlas, zum Rand und weiter
                weg die gebackene Haut der Figur — das Stück hat die Farbe der Haut daneben. Der erste daz5-Stand trug die feste Farbe der Hautton-Variante (`FARBE`, 214 / 168 / 155) gegen die Haut
                (199 / 143 / 128, Median der Kacheln 1002/1003 um die Scham, gemessen 11.10.2026); Edgar: „die daz variante macht keine Texturangleichung". Ohne Scham-Stück des Imports oder ohne
                Hautkacheln bleibt es bei `FARBE`.

Keine Anpassung der FORM an ein Original (kein Strahl, keine Laplace): das Original liefert nur die Textur.
"""
from types import SimpleNamespace

import numpy as np

from .dazgeograft import Dazgeograft

__all__ = ['Dazgeograftverlegt']


class Dazgeograftverlegt(Dazgeograft):
    #: Diffuse Farbe der Variante „Daz Anatomie Frau Hautton cute girl" (aus ihrem Preset gelesen, 11.10.2026): sRGB 214 / 168 / 155. Die Vorgabe des Geografts (160 / 121 / 104) ist die Mittelfarbe der Basishaut.
    #: Gilt nur noch, wenn nichts gebacken wird (kein Scham-Stück des Imports oder keine Hautkacheln).
    FARBE = (0.8392, 0.6588, 0.6078)

    def __init__(self, modell, name=None, farbe=None, scham=None, aufloesung=1024):
        """`modell`: Name des gespeicherten Modells, dessen Figur das Geograft bekommt (`figur.regler` in `data/models/<Modell>.json`); `name`: des neuen Stücks (Vorgabe „<Modell> Daz Scham");
        `scham`: Anzeigename des Scham-Stücks des Imports (Vorgabe „<Modell> Scham"; `False` = nichts backen) — das Original, von dem die Textur kommt; `aufloesung`: Kante der gebackenen Bilder."""
        import json

        from django.conf import settings

        super().__init__('frau', farbe=farbe or self.FARBE)
        daten = json.loads((settings.HUMANBODY_MODELS_DIR / (modell + '.json')).read_text(encoding='utf-8'))
        #: Das Unterkleid der Figur ist für Kleider gerechnet, die das Loch einer anderen Scham umgehen — es gehört nicht zur Haut, auf der das Geograft verschweißt wird.
        self.regler = {k: v for k, v in ((daten.get('figur') or {}).get('regler') or {}).items() if '_unterkleid' not in k}
        self.modell = modell
        self.anzeige = name or '%s Daz Scham' % modell
        self.gruppe = 'Genitalia %s' % modell
        self.scham = '%s Scham' % modell if scham is None else scham
        self.aufloesung = int(aufloesung)
        self.haut_ordner = settings.HUMANBODY_MODELS_DIR / 'Texturen' / modell
        self._ziel = None

    def figur(self):
        from .dazgeografthaut import Dazgeografthaut

        return Dazgeografthaut.grundfigur(self.regler)

    def angleichen(self, punkte, dreiecke, uv_ecken, figur, maske, bericht):
        """Das Geograft in den Raum der Figur verlegen — nichts weiter. → `(punkte, dreiecke, uv_ecken)`."""
        from .blendimportschamloch import Blendimportschamloch
        from .dazgeograftanpassung import Dazgeograftanpassung
        from .dazgeografthaut import Dazgeografthaut

        haut = Blendimportschamloch(figur['punkte'], figur['dreiecke'])
        ring_punkte = haut.ringpunkte(haut.ring(maske))
        # `Dazgeograftanpassung` verlangt ein Ziel (das Original); `verlegen` braucht es nicht — ein Platzhalter-Dreieck genügt.
        platzhalter = SimpleNamespace(punkte=np.zeros((3, 3)), dreiecke=np.array([[0, 1, 2]]))
        anpassung = Dazgeograftanpassung(Dazgeografthaut.grundfigur(), figur, ring_punkte, platzhalter, stufe=self.STUFE)
        verlegt = anpassung.verlegen(punkte, dreiecke)
        bericht['verlegen'] = anpassung.bericht
        return verlegt, dreiecke, uv_ecken

    def ziel(self):
        """Das Scham-Stück des Imports als Textur- und Formvorlage (`Dazgeograftziel`) — `None`, wenn es keines gibt oder `scham` aus ist (dann bleibt die feste Farbe)."""
        from .dazgeograftziel import Dazgeograftziel

        if self._ziel is None and self.scham:
            try:
                self._ziel = Dazgeograftziel(self.scham)
            except (OSError, KeyError, ValueError, IndexError):
                import logging

                logging.getLogger('core').warning('Daz-Geograft %s: Scham-Stück „%s" nicht lesbar — keine Textur vom Original', self.anzeige, self.scham, exc_info=True)
        return self._ziel

    def backen(self, punkte, dreiecke, uv_ecken, figur, bericht):
        """Farbe, Rauheit, Normalen aus Original und gebackener Haut auf das Stück (`Dazgeograftbacken`) → `{'farbe'|'normalen'|'rauheit': Pfad}`; leer, wenn es kein Original oder keine Kacheln gibt."""
        from Genesis9.eigenstueck import G9eigenstueck

        from .dazgeograftbacken import Dazgeograftbacken

        ziel = self.ziel()
        if ziel is None or not (self.haut_ordner / 'haut_1002_farbe.jpg').is_file():
            bericht['bake'] = {'aus': 'kein Scham-Stück des Imports oder keine Hautkacheln — feste Farbe'}
            return {}
        kennung, _anzeige = G9eigenstueck.kennung_und_name(self.anzeige)
        dateien, zahlen = Dazgeograftbacken(ziel, figur, self.haut_ordner, self.aufloesung).backen(punkte, dreiecke, uv_ecken, G9eigenstueck.arbeitsordner(kennung) / 'gebacken')
        bericht['bake'] = zahlen
        return dateien

    def vorgabe(self):
        """Das Original (nur der Teil, den die Figur nicht trägt) mit seiner Atlasfarbe — Bezug der Messung (`Schammessung`), nicht der Form: das Stück bleibt Daz."""
        ziel = self.ziel()
        return None if ziel is None else {'punkte': ziel.punkte, 'dreiecke': ziel.dreiecke, 'farbe_an': ziel.farbe_an, 'teil': True}

    def kachelbild(self):
        return lambda kachel: self.haut_ordner / ('haut_%d_farbe.jpg' % kachel)

    def zusaetze(self, _quelle, _kaefig, bilanz):
        """Nach dem Schreiben nur die Regler des Katalogs (`sch_*`), aus der Form des Stücks. Die Daz-Formmorphe (Realism aus) entfallen: sie übertragen ihre Deltas vom Geograft in Lage der Grundfigur auf das Stück
        (`Dazgeograftmorphe.MAX_ABSTAND_M` 10 mm), das verlegte Stück liegt aber bis 60 mm daneben (gemessen beim ersten Bau: 57,5 mm); Charakter-Varianten braucht ein Stück mit eigener Farbe nicht."""
        from Genesis9.anatomien import G9anatomien

        from .dazgeograftmorphe import Dazgeograftmorphe

        gebaut, gescheitert = Dazgeograftmorphe.katalog_bauen(bilanz['stueck'], G9anatomien.fuer(self.NAMEN[self.geschlecht][1]))
        bilanz['bericht']['regler_gebaut'], bilanz['bericht']['regler_gescheitert'] = len(gebaut), gescheitert

    def verschweissen(self, figur, maske, punkte, dreiecke, uv_ecken):
        """Wie `Dazgeograft.verschweissen`, dazu der Auslauf der Naht und das Tiefenfeld von alt4 (`Schamtiefenfeld`)."""
        from .blendimportschamloch import Blendimportschamloch
        from .blendimportschamnaht import Blendimportschamnaht
        from .blendimportschamring import Blendimportschamring
        from .schamtiefenfeld import Schamtiefenfeld

        haut = Blendimportschamloch(figur['punkte'], figur['dreiecke'])
        ring = haut.ring(maske)
        ring_punkte = haut.ringpunkte(ring)
        normalen = Blendimportschamring.normalen(haut.punkte, haut.dreiecke)[ring_punkte]
        lage0 = haut.lage(ring)
        lage, verschiebung = Blendimportschamring.ziehen(haut.punkte, haut.dreiecke, maske, ring_punkte, lage0, normalen)
        rand_vorher = punkte[Schamtiefenfeld.randpunkte(dreiecke)]
        einrasten = Blendimportschamnaht(lage)
        einrasten.BAND_MM = Schamtiefenfeld.NAHT_BAND_MM
        punkte, dreiecke, uv_ecken, naht = einrasten.anlegen(punkte, dreiecke, uv_ecken)
        if naht['rand_weg_max_mm'] > self.MAX_RAND_WEG_MM:
            raise ValueError('der Rand des Geografts liegt bis %.1f mm neben dem Ring (Grenze %.0f mm)' % (naht['rand_weg_max_mm'], self.MAX_RAND_WEG_MM))
        tiefenfeld = {}
        if Schamtiefenfeld.STAERKE > 0:
            punkte, tiefenfeld = Schamtiefenfeld.anwenden(punkte, dreiecke, rand_vorher)
        loch = {'dreiecke': np.flatnonzero(maske).astype(np.int64), 'von': int(len(figur['dreiecke'])), 'ring': lage,
                'ring_punkte': ring_punkte, 'verschiebung': verschiebung, 'ring_d': lage - lage0}
        return punkte, dreiecke, uv_ecken, loch, dict(haut.bericht(maske, ring), **naht, tiefenfeld=tiefenfeld)
