# -*- coding: utf-8 -*-
"""Meshgenesisanpassungsaugen — die Augäpfel zur eingepassten Genesis-Figur der Zeile 1 (19.11.2026, Edgar: „bau Augen in Zeile 1 ein“).

Die Einpassung (`meshgenesis_meshanpassung.py`, `Meshgenesistestanpassung`) liefert nur das Körpernetz (25.182 Punkte, dieselbe Folge wie `G9basisnetz`); ohne die
Augen von Genesis 9 (`G9anhang` „augen“, `Genesis9Eyes.dsf`) blieben die Augenhöhlen leer und sahen weiß aus. Gerechnet wird hier, nicht in der Kette: je Augapfel
die starre Abbildung mit Maßstab (`Kabsch.lage`, Umeyama) von den Körperpunkten, an denen der Augapfel hängt (`G9folger.projektion`, drei je Punkt), im Grundnetz auf
dieselben Punkte der eingepassten Figur — die steht in der Haltung des Netzes und in dessen Größe, eine reine Verschiebung (`G9folger.punkte_fuer`) ließe das Auge
ungedreht. Starr wie Daz (`G9anhang`: „ein verbeulter Augapfel ist schlimmer als einer, der 1 mm daneben sitzt“). Die Augenfeuchte (Glanzschicht ohne Bild) bleibt weg.

    bloecke, gruppen = Meshgenesisanpassungsaugen.bloecke(figur)   # {augen_punkte, augen_uv, augen_dreiecke}, [{name, index_ab, index_anzahl, albedo}] — oder (None, None)
"""

import logging

import torch
from KoerperKI_alle.torchfeld import Torchfeld

logger = logging.getLogger('core')

__all__ = ['Meshgenesisanpassungsaugen']


class Meshgenesisanpassungsaugen:
    BLOECKE = (('augen_punkte', 'f4'), ('augen_uv', 'f4'), ('augen_dreiecke', 'u4'))

    @classmethod
    def bloecke(cls, figur):
        try:
            from Genesis9.anhang import G9anhang
            from Genesis9.basisnetz import G9basisnetz
            from KoerperKI_alle.kabsch import Kabsch
            folger = G9anhang.folger('augen')
            bilder = G9anhang.bilder('augen')
            if folger is None or not bilder:
                return None, None
            basis = Torchfeld.feld(G9basisnetz.holen().punkte, dtype=torch.float64)
            ziel = Torchfeld.feld(figur, dtype=torch.float64).reshape(-1, 3)
            if ziel.shape != basis.shape:
                logger.warning('Augen der Zeile 1: Figur mit %d Punkten statt %d des Grundnetzes', len(ziel), len(basis))
                return None, None
            nachbar, _gewicht = folger.projektion()
            punkte = Torchfeld.feld(folger.punkte, dtype=torch.float64).clone()
            ursprung = Torchfeld.feld(folger.ursprung, dtype=torch.int64)
            dreiecke = Torchfeld.feld(folger.dreiecke, dtype=torch.int64).reshape(-1)
            teile, gruppen, ab = [], [], 0
            for g in folger.gruppen:
                albedo = (bilder.get(g['name']) or {}).get('albedo')
                if not albedo:                                   # Augenfeuchte: kein Bild
                    continue
                stueck = dreiecke[int(g['index_ab']):int(g['index_ab']) + int(g['index_anzahl'])]
                ecken = Torchfeld.unique(ursprung[stueck])
                koerper = Torchfeld.unique(Torchfeld.feld(nachbar, dtype=torch.int64)[ecken].reshape(-1))
                s, r, t = Kabsch.lage(basis[koerper], ziel[koerper], massstab=True)
                punkte[ecken] = s * punkte[ecken] @ r.T + t
                teile.append(stueck)
                gruppen.append({'name': g['name'], 'index_ab': ab, 'index_anzahl': int(len(stueck)), 'albedo': str(albedo), 'massstab': round(float(s), 4)})
                ab += len(stueck)
            if not teile:
                return None, None
            # nur die Punkte der Augäpfel: die der Augenfeuchte blieben sonst ungedreht im Grundnetz stehen und zögen die Hülle des Felds (Kamera) um 20 cm auf
            alle = Torchfeld.cat(teile)
            genutzt = Torchfeld.unique(alle)
            neu = Torchfeld.full(len(ursprung), -1, dtype=torch.int64)
            neu[genutzt] = Torchfeld.arange(len(genutzt))
            return {'augen_punkte': Torchfeld.astype(punkte[ursprung[genutzt]], torch.float32),
                    'augen_uv': Torchfeld.astype(Torchfeld.feld(folger.uv)[genutzt], torch.float32), 'augen_dreiecke': neu[alle]}, gruppen
        except (OSError, ValueError, KeyError, ImportError, RuntimeError) as fehler:
            logger.warning('Augen der Zeile 1 nicht gebaut: %s', fehler)
            return None, None
