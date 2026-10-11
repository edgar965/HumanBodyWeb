# -*- coding: utf-8 -*-
"""Blendimporthautlokal — backt die Haut-Kacheln eines Imports im Speicher auf der GPU (`core/dienste/hautbacken`), ohne Blender zu starten.

Die Einstellung Charakter → Backen = „Lokal" (`Blendimportbackenwahl`). Das Material kommt als Knotengraph aus dem Export (`blendmaterialgraph.py`, `graphen/*.json`) und wird mit denselben
Rechenwegen ausgewertet wie in Cycles (`hautbacken/graph`, aus dem Blender-Quelltext übernommen und im Hautbackenzoo gegen Blender geprüft: 296 Materialien, Mittel ≤ 0,05 von 255).
Was der lokale Weg nicht kennt, ist ein `Hautgraphfehler` mit dem Namen von Material und Knoten (alle Befunde auf einmal) — keine stille Näherung; Ausweg ist „Blender".

    lokal = Blendimporthautlokal(ablage, netz, npz, ruhe_blender, genesis, px, melden)
    lokal.vorbereiten()                  # Quelle (BVH), Schattungsdaten, Graphen — wirft Hautgraphfehler
    e = lokal.kachel(1001)               # {'farbe', 'rauheit', 'normalen': (px, px, 3) uint8 mit Rand, 'getroffen': Anteil in %, 'maske': getroffen}

Die Figur einer Kachel wird so gelesen, wie Blender das OBJ aus `Blendimportlage.genesis_objs` liest (Koordinaten und UV auf sechs Nachkommastellen, float32); Normalen und Tangenten der
Figur rechnet `Hautschattungbau` wie Blender beim Backen. Der Rand um die getroffenen Texel ist `Hautbackenrand` (Blender: 16 Texel, `ADJACENT_FACES`; hier der nächste getroffene Texel).
"""

import json
import logging

import numpy as np

from .blendimportlage import Blendimportlage
from .hautbacken import Hautbackenflaeche, Hautbackenquelle, Hautbackenrand, Hautbackenretri
from .hautbacken.graph import Hautbackengraph, Hautgraph, Hautgraphfehler, Hautschattungbau

logger = logging.getLogger('core')

__all__ = ['Blendimporthautlokal']


class Blendimporthautlokal:
    KANAELE = ('farbe', 'rauheit', 'normalen')

    def __init__(self, ablage, netz, npz, ruhe_blender, genesis, px, melden=None, geraet='cuda:0'):
        """`netz`: Eintrag des Körpers im Inventar; `npz`: seine Arrays (`dreiecke`, `uv_ecken`, `material`, …); `ruhe_blender`: die Körperpunkte in der Ruhelage der Figur (Blender-Achsen);
        `genesis`: `Blendimportlage.genesis()`; `px`: Seitenlänge der Kacheln."""
        self.ablage, self.netz = ablage, netz
        self.ruhe, self.genesis, self.px, self.geraet = ruhe_blender, genesis, int(px), geraet
        self.npz, self.retri = npz, None
        self.melden = melden or (lambda anteil, text: None)
        self.figur_blender = np.round(Blendimportlage.blender(genesis['punkte']), 6)
        self.quelle = self.schattung = self.treiber = None
        #: Glanz-Normalen-Korrektur von Cycles (`hautglanz`): `glanz_gerechnet` `{Material: Texel}` (das Closure-Modell hat die gebackene Normale gerechnet), `glanz_korrektur`
        #: `{Material: {'texel', 'grund'}}` (nicht gerechnet: dort gilt die Normale ohne die Korrektur).
        self.glanz_gerechnet = {}
        self.glanz_korrektur = {}
        #: Texel, deren Material keinen Principled BSDF hat (bleiben schwarz/flach, wie in Blender).
        self.ohne_graph = {}

    # ------------------------------------------------------------------ Vorbereitung

    def vorbereiten(self):
        """Quelle (BVH), Schattungsdaten und die Graphen aller Materialien; `Hautgraphfehler` mit allen Befunden, wenn ein Material etwas verlangt, das der lokale Weg nicht kennt."""
        if not all(k in self.npz for k in ('poly_start', 'poly_punkte', 'dreieck_poly')):
            raise Hautgraphfehler(['der Export enthält die Polygon-Daten des Körpers nicht (älterer Export) — den Schritt „export" neu laufen lassen'])
        # Blender bildet die Dreiecke der Vierecke aus den Punkten der Ruhelage, nicht der Exportlage (`Hautbackenretri`): hinako 1.328 Vierecke, seori 242.
        self.npz, self.retri = Hautbackenretri.neu(self.npz, self.ruhe)
        self.quelle = Hautbackenquelle(self.ruhe, self.npz['dreiecke'], self.npz['uv_ecken'], self.geraet)
        self.schattung = Hautschattungbau.aus_export(self.quelle.flaeche.punkte, self.npz, self.netz, self.geraet)
        texturen, graphen, gruende = {}, {}, []
        for i, m in enumerate(self.netz['materialien']):
            if not m.get('graph'):
                if 'graph_grund' not in m:
                    gruende.append('Material „%s": der Export enthält keinen Materialgraph (älterer Export) — den Schritt „export" neu laufen lassen' % m.get('name'))
                graphen[i] = None
                logger.info('Hautbacken lokal %s: Material „%s" ohne Graph (%s) — bleibt schwarz', self.ablage.kennung, m.get('name'), m.get('graph_grund'))
                continue
            try:
                spec = json.loads(self.ablage.export(m['graph']).read_text(encoding='utf-8'))
                graphen[i] = Hautgraph(m['name'], spec, self.geraet, texturen)
            except Hautgraphfehler as fehler:
                gruende += fehler.gruende
        if gruende:
            raise Hautgraphfehler(gruende)
        self.treiber = Hautbackengraph(self.schattung, graphen, self.px, self.geraet)
        return self

    # ------------------------------------------------------------------ Kacheln

    def figur(self, nummer):
        """Die Figur der Kachel (`Hautbackenflaeche`), so wie Blender das OBJ liest."""
        g = self.genesis
        dreiecke = g['dreiecke'][g['kachel'] == nummer]
        uv = np.round(g['uv'][dreiecke], 6).astype(np.float32)
        return Hautbackenflaeche(self.figur_blender.astype(np.float32), dreiecke, uv)

    def kachel(self, nummer):
        """`{'farbe', 'rauheit', 'normalen': (px, px, 3) uint8, 'maske': (px, px) getroffen, 'belegt': getroffen + Rand, 'getroffen': Anteil in %}`."""
        if self.treiber is None:
            self.vorbereiten()
        figur = self.figur(nummer)
        e = self.treiber.backen(self.quelle, figur, Hautschattungbau.figur_tangenten(figur), self.KANAELE)
        for name, anzahl in e['glanz_gerechnet'].items():
            self.glanz_gerechnet[name] = self.glanz_gerechnet.get(name, 0) + anzahl
        for name, eintrag in e['glanz_korrektur'].items():
            alt = self.glanz_korrektur.setdefault(name, {'texel': 0, 'grund': eintrag['grund']})
            alt['texel'] += eintrag['texel']
        if e['ohne_graph']:
            self.ohne_graph[str(nummer)] = e['ohne_graph']
        maske = e['maske']
        rand = Hautbackenrand(self.geraet)
        aus = {'maske': maske, 'getroffen': round(100.0 * float(maske.mean()), 1)}
        for kanal in self.KANAELE:
            aus[kanal], aus['belegt'] = rand.erweitern(e[kanal], maske)
        return aus

    def glanz_text(self):
        """Ein Satz über die Texel, an denen Cycles die Glanz-Normalen korrigiert und das Closure-Modell die gebackene Normale NICHT rechnen konnte (Grund je Material) — leer, wenn es keine gibt."""
        if not self.glanz_korrektur:
            return ''
        return ('Normalen: an %s neigt sich die Normale so stark, dass Cycles die Glanz-Normalen korrigiert (`ensure_valid_specular_reflection`, „Bump Map Correction"); '
                'das Modell rechnet das Material nicht — dort gilt die Normale ohne die Korrektur' % '; '.join(
                    '%d Texeln von „%s" (%s)' % (e['texel'], name, e['grund']) for name, e in sorted(self.glanz_korrektur.items())))
