# -*- coding: utf-8 -*-
"""Dazgeograft — das Daz-Geograft „Anatomical Elements" als eigenes Stück der Garderobe (10.10.2026).

Edgar, 10.10.2026: „die sind jetzt installiert [Genesis 9 Starter Essentials Expansion] … baue die Morphs in das UI ein". Das Geograft gehört zur Daz-Bibliothek
(nur lesen); hier wird es in dasselbe Stückformat gewandelt wie der Genital-Anbau eines Blender-Imports (`Blendimportstuecke.scham_stueck`) — so laufen Loch,
Naht, Hautgewichte, `hoehe_mm` und die Regler des Penis (`G9penis`, `pen_*`) ohne neuen Weg im Browser:

    Quelle    Käfig des Geografts (+ Realism-Morph, Vorgabe 1) → Stufe 1 (Catmull-Clark) → Doppelgänger an UV-Nähten verschweißt   (`Dazgeograftquelle`)
    Loch      die verdeckten Käfigflächen der Figur als Dreiecke der Stufe 1                                                 (`Dazgeografthaut`)
    Naht      Ring des Lochs geglättet, Rand des Geografts genau auf dessen Ecken                                            (`Blendimportschamloch/-ring/-naht`)
    Schreiben OBJ → `.duf` mit den Hautgewichten der verdeckenden Hautpunkte, `.ersetzt.json` (anatomie, loch, hoehe_mm)    (`G9eigenstueck`, `G9stueckersatz`)

Die Knochen des Geografts (`Gen1`–`Gen6`, `Testes`) fallen weg: Neigung und Erektion rechnen die Regler selbst (`G9penismorphe`); Länge und Umfang sind dort
dieselben Griffe wie Dazs `Penile Length`/`Penile Width`. Eigene Regler für das, was nur Daz kennt: `Dazgeograftregler`.
"""
import logging

import numpy as np

logger = logging.getLogger('core')

__all__ = ['Dazgeograft']


class Dazgeograft:
    #: Anzeigename je Geschlecht und die Anatomie, die das Stück trägt (`G9stueckersatz.ANATOMIEN`).
    NAMEN = {'mann': ('Daz Anatomie Mann', 'penis'), 'frau': ('Daz Anatomie Frau', 'vagina')}
    KATEGORIE = ('Follower/Accessory', '/Default/Accessories')
    #: Materialgruppe des Stücks. Im Daz-Geograft heißt sie `Genitalia` (`Dazgeograftvarianten.GRUPPE`); je Stück eine eigene, sonst zählte die Variantensuche der Garderobe
    #: (`G9garderobeeintrag.varianten`: jedes Preset im Ordner, das eine Gruppe des Stücks belegt) die Texturen der Frau auch beim Mann (gesehen 10.10.2026).
    GRUPPEN = {'mann': 'Genitalia Mann', 'frau': 'Genitalia Frau'}
    #: Ohne Charaktertextur: Mittelfarbe der Basishaut `G9 Feminine|Masculine Skin 01` (sRGB, Median der Beine-Karte, gemessen 10.10.2026: 160/121/104 bzw. 159/120/102).
    FARBEN = {'mann': (159 / 255.0, 120 / 255.0, 102 / 255.0), 'frau': (160 / 255.0, 121 / 255.0, 104 / 255.0)}
    #: Vorgabe des Formmorphs „Realism HD" im Produkt (`current_value` 1): er gehört zur Grundform.
    REALISM = 'body_bs_GenitalRealism_HD3'
    #: Punkte, die um weniger als das (m) auseinanderliegen, sind derselbe Punkt (UV-Nähte teilen sie).
    LAGE_M = 1e-7
    #: Liegt der Rand des Geografts im Bau weiter (mm) vom Ring, bricht der Bau ab (die Naht zöge Keile).
    MAX_RAND_WEG_MM = 30.0

    def __init__(self, geschlecht='mann', farbe=None, rauheit=0.6):
        self.geschlecht = geschlecht
        self.farbe = tuple(float(f) for f in (farbe or self.FARBEN[geschlecht]))
        self.rauheit = float(rauheit)
        #: Anzeigename und Materialgruppe des Stücks (Unterklassen setzen eigene), Bilder aus `backen`.
        self.anzeige, self.gruppe, self.bilder = self.NAMEN[geschlecht][0], self.GRUPPEN[geschlecht], {}
        self._stufe = None

    def bauen(self, realism=1.0):
        """Das Stück in die eigene Bibliothek schreiben; gibt die Bilanz (`G9eigenstueck.schreiben`) mit `bericht` zurück."""
        from .dazgeografthaut import Dazgeografthaut
        from .dazgeograftquelle import Dazgeograftquelle

        quelle = Dazgeograftquelle(self.geschlecht)
        kaefig = quelle.punkte + float(realism) * quelle.morph(self.REALISM)
        punkte, dreiecke, uv_ecken = self.stufe1(quelle, kaefig)
        figur = self.figur()
        maske, loch_bericht = Dazgeografthaut.loch(figur, quelle.versteckt)
        if loch_bericht['ohne'] or not maske.any():
            raise ValueError('Loch unvollständig: %s' % loch_bericht)
        bericht = {'quelle_punkte': int(len(quelle.punkte)), 'loch': loch_bericht}
        punkte = self.angleichen(punkte, dreiecke, figur, maske, bericht)
        punkte, dreiecke, uv_ecken, loch, naht = self.verschweissen(figur, maske, punkte, dreiecke, uv_ecken)
        self.bilder = self.backen(punkte, dreiecke, uv_ecken, figur, bericht)
        bilanz = self.schreiben(figur, punkte, dreiecke, uv_ecken, loch)
        bilanz['bericht'] = dict(bericht, naht=naht, messung=self.messen(figur, punkte, dreiecke, uv_ecken, loch))
        self.zusaetze(quelle, kaefig, bilanz)
        logger.info('Daz-Geograft %s: %s', self.geschlecht, bilanz['bericht'])
        return bilanz

    # Haken für `Dazgeograftangepasst` (ein Geograft auf die Scham eines Blender-Imports): hier die Grundfigur, keine Anpassung, keine Bilder.

    def figur(self):
        """Die Figur, auf der das Loch geschnitten und das Geograft verschweißt wird."""
        from .dazgeografthaut import Dazgeografthaut

        return Dazgeografthaut.grundfigur()

    def angleichen(self, punkte, _dreiecke, _figur, _maske, _bericht):
        """Die Punkte des Geografts vor dem Verschweißen anpassen → neue Punkte (hier unverändert)."""
        return punkte

    def backen(self, _punkte, _dreiecke, _uv_ecken, _figur, _bericht):
        """Bilder des Stücks nach dem Verschweißen → `{'farbe'|'normalen'|'rauheit': Pfad}` (hier keine)."""
        return {}

    def vorgabe(self):
        """Das Original, gegen das gemessen wird: `{punkte, dreiecke[, farbe_an, teil]}` — hier keines (das Geograft allein hat kein Vorbild)."""
        return None

    def kachelbild(self):
        """`k → Pfad` der Hautkachel `k` für die Farbe am Ring — hier keine."""
        return None

    def messen(self, figur, punkte, dreiecke, uv_ecken, loch):
        """Die Scham-Messung (`Schammessung`) — bei jedem Bau, ohne Schalter; Ergebnis liegt als `messung.json` im Arbeitsordner und im Bericht (`messung`)."""
        from Genesis9.eigenstueck import G9eigenstueck

        from .schammessung import Schammessung

        kennung, _anzeige = G9eigenstueck.kennung_und_name(self.anzeige)
        return Schammessung.sicher(ordner=G9eigenstueck.arbeitsordner(kennung), punkte=punkte, dreiecke=dreiecke, uv_ecken=uv_ecken, figur=figur, loch=loch,
                                   vorgabe=self.vorgabe(), farbe_pfad=self.bilder.get('farbe'), kachelbild=self.kachelbild())

    def zusaetze(self, quelle, kaefig, bilanz):
        """Nach dem Schreiben: die Charakter-Texturen als Varianten, die Daz-Formmorphe und alle Regler des Katalogs (`bilanz['bericht']` ergänzt)."""
        from Genesis9.anatomien import G9anatomien

        from .dazgeograftmorphe import Dazgeograftmorphe
        from .dazgeograftvarianten import Dazgeograftvarianten

        stueck = bilanz['stueck']
        bericht = bilanz['bericht']
        if self.geschlecht == 'mann':                  # die Knochenkette des Penis: gerade Form und Marken für die Regler (`G9stueckgerade`)
            from .dazgeograftgerade import Dazgeograftgerade
            bericht['marken'] = Dazgeograftgerade.ablegen(self, quelle, kaefig, bilanz['roh'], bilanz['duf'])
        bericht['varianten'] = Dazgeograftvarianten.schreiben(bilanz['duf'], self.geschlecht, self.GRUPPEN[self.geschlecht])
        bericht['daz_morphe'] = Dazgeograftmorphe.ablegen(self, quelle, kaefig, stueck)
        gebaut, gescheitert = Dazgeograftmorphe.katalog_bauen(stueck, G9anatomien.fuer(self.NAMEN[self.geschlecht][1]))
        bericht['regler_gebaut'], bericht['regler_gescheitert'] = len(gebaut), gescheitert

    def _stufe_von(self, quelle):
        """Das Stufe-1-Netz des Geografts (Topologie hängt nur an den Käfigflächen und UV, nicht an den Punkten), einmal je Bau."""
        from Genesis9.netzstufe import G9netzstufe

        if self._stufe is None:
            self._stufe = G9netzstufe('dazgraft_%s' % self.geschlecht, quelle.polys, quelle.materialnamen, quelle.uvs, quelle.ueber, None, 1)
        return self._stufe

    def stufe_punkte(self, quelle, kaefig):
        """`(P, 3)` Punkte der Stufe 1 (UV-Nähte doppelt) für den Käfig `kaefig` (m) in Dazs Default Pose (`Dazgeograftquelle.gepostet`) — gleiche Reihenfolge für jeden Käfig."""
        return np.asarray(self._stufe_von(quelle).punkte(quelle.gepostet(kaefig)), dtype=np.float64)

    def stufe1(self, quelle, kaefig):
        """`(punkte, dreiecke, uv_ecken)`: der Käfig `kaefig` (m) auf Stufe 1, an UV-Nähten verschweißt, UV je Ecke `(T, 3, 2)`."""
        stufe = self._stufe_von(quelle)
        roh = self.stufe_punkte(quelle, kaefig)
        dreiecke = np.asarray(stufe.dreiecke, dtype=np.int64).reshape(-1, 3)
        uv_ecken = np.asarray(stufe.uv, dtype=np.float64)[dreiecke]
        schluessel = np.round(roh / self.LAGE_M).astype(np.int64)
        _, erste, rep = np.unique(schluessel, axis=0, return_index=True, return_inverse=True)
        return roh[erste], rep.ravel()[dreiecke], uv_ecken

    def verschweissen(self, figur, maske, punkte, dreiecke, uv_ecken):
        """Wie `Blendimportschamgeograft.verschweissen`, aber mit dem bekannten Loch: Ring glätten, Rand des Geografts darauf legen."""
        from .blendimportschamloch import Blendimportschamloch
        from .blendimportschamnaht import Blendimportschamnaht
        from .blendimportschamring import Blendimportschamring

        haut = Blendimportschamloch(figur['punkte'], figur['dreiecke'])
        ring = haut.ring(maske)
        ring_punkte = haut.ringpunkte(ring)
        normalen = Blendimportschamring.normalen(haut.punkte, haut.dreiecke)[ring_punkte]
        lage0 = haut.lage(ring)
        lage, verschiebung = Blendimportschamring.ziehen(haut.punkte, haut.dreiecke, maske, ring_punkte, lage0, normalen)
        punkte, dreiecke, uv_ecken, naht = Blendimportschamnaht(lage).anlegen(punkte, dreiecke, uv_ecken)
        if naht['rand_weg_max_mm'] > self.MAX_RAND_WEG_MM:
            raise ValueError('der Rand des Geografts liegt bis %.1f mm neben dem Ring (Grenze %.0f mm)' % (naht['rand_weg_max_mm'], self.MAX_RAND_WEG_MM))
        loch = {'dreiecke': np.flatnonzero(maske).astype(np.int64), 'von': int(len(figur['dreiecke'])), 'ring': lage,
                'ring_punkte': ring_punkte, 'verschiebung': verschiebung, 'ring_d': lage - lage0}
        return punkte, dreiecke, uv_ecken, loch, dict(haut.bericht(maske, ring), **naht)

    def schreiben(self, figur, punkte, dreiecke, uv_ecken, loch):
        """OBJ → Stück: Gewichte der verdeckenden Hautpunkte, Höhe über der Haut, Loch — wie `Blendimportstuecke.scham_stueck`."""
        import trimesh
        from Genesis9.eigenstueck import G9eigenstueck
        from Genesis9.objleser import G9objleser
        from Genesis9.stueckersatz import G9stueckersatz

        from .blendimportbilder import Blendimportbilder
        from .blendimportscham import Blendimportscham
        from .blendimportschamgewichte import Blendimportschamgewichte
        from .blendimportschamhoehe import Blendimportschamhoehe
        from .blendimportstuecke import Blendimportstuecke

        anatomie = self.NAMEN[self.geschlecht][1]
        kennung, anzeige = G9eigenstueck.kennung_und_name(self.anzeige)
        ordner = G9eigenstueck.arbeitsordner(kennung)
        ordner.mkdir(parents=True, exist_ok=True)
        material = {'name': self.gruppe, 'farbe': self.farbe, 'bild': None, 'shininess': 1.0 - self.rauheit, 'opacity': None}
        if self.bilder:            # gebackene Bilder: die Farbe ist dann das Bild, kein Faktor mehr
            material.update(farbe=(1.0, 1.0, 1.0), bild=str(self.bilder['farbe']), normalen=str(self.bilder['normalen']),
                            rauheit_bild=str(self.bilder['rauheit']), shininess=None)
        netz = G9objleser.lesen(str(Blendimportbilder.obj(ordner, punkte, dreiecke, uv_ecken, material)))
        roh = np.asarray(netz['punkte'], dtype=np.float64)
        gewichte = Blendimportschamgewichte.fuer_figur(figur).gewichte(roh, np.asarray(netz['flaechen'], dtype=np.int64),
                                                                       ring=(loch['ring'], loch['ring_punkte']))
        bilanz = G9eigenstueck.schreiben(roh, netz, kennung, anzeige, self.KATEGORIE, material, heben=False, wicklung=False, gewichte=gewichte)
        flaeche = trimesh.Trimesh(figur['punkte'], figur['dreiecke'], process=False)
        hoehe = np.round(Blendimportschamhoehe.ueber_figur(roh, flaeche), 1).tolist()
        G9stueckersatz.schreiben(bilanz['duf'], [], haut_tiefe_mm=Blendimportscham.HAUT_TIEFE_MM, anatomie=anatomie, eigene_gewichte=True,
                                 loch=Blendimportstuecke.loch_angabe(loch), hoehe_mm=hoehe)
        bilanz['roh'] = roh                      # die Punkte des Stücks in Dateireihenfolge (für gerade Form und Morphe), kein Teil der Bilanz auf der Platte
        return bilanz
