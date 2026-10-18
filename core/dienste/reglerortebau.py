# -*- coding: utf-8 -*-
"""Reglerortebau — die Zuordnungstabelle `G9reglerorte` bauen: jeden Regler des Bedienfelds an der Grundfigur messen (18.10.2026).

Auftrag Edgar (18.10.2026): „mach die Empfehlung“ (Konzept `Docu/konzepte/2026-10-18_genesis9-regler-vereinfachen-konzept.md`) und „Ich verstehe
nicht die ‚versteckten‘ Regler, die haben doch auch eine Wirkung? dann glieder die ein in die richtigen Kategorien“.

Je Regler aus `G9reglerplan.bereiche()` (ohne die Bereiche, deren Platz feststeht: Alter, Anhänge, Eigenes — `FEST`):
  1. beide Anschläge messen (`Reglerortemessung`), den stärkeren behalten: Wirkung, Ort (Dehnung je Region), Größenanteil;
  2. ohne eigene Wirkung: die TREIBER suchen — die Kanäle, mit denen Daz den Wert multipliziert (`stufe: mult`, `G9formeln.wert`: Wert = Summe ×
     Faktor). Eine Körpertyp-Korrektur `BodyHeavy_body_cbs_…` ist ohne `BodyHeavy` immer 0, egal was man stellt. Gemessen wird dann mit
     gestellten Treibern gegen die Figur mit Treibern allein (`bedingt`). Dazu die Knochendrehung (`dreht`, Augen/Zunge drehen ohne Käfig) und ob
     ein Anhang den Kanal mit eigenen Deltas rechnet (`anhang`, Wimpern, Zähne);
  3. Doppelte und Gegenstücke (`Reglerortedoppelte`).

Dauer gemessen an der Inventur: 2.406 Regler in 265 s (ein Anschlag ~0,1 s); dazu Treiber und Stützstellen. Läuft als Befehl
`manage.py genesis9_reglerorte` — rechenlastig, mit niedriger Priorität starten.
"""

import logging
import time

from Genesis9.reglergliederung import G9reglergliederung
from Genesis9.reglerorte import G9reglerorte

from .reglerortedoppelte import Reglerortedoppelte
from .reglerortemessung import Reglerortemessung

logger = logging.getLogger('core')

__all__ = ['Reglerortebau']


class Reglerortebau:
    #: Bereiche, deren Platz im Bedienfeld feststeht — nicht messen (die Eigenmorphe bauten sich beim ersten Zug sogar erst).
    FEST = G9reglergliederung.FEST

    def __init__(self, melden=None):
        self.melden = melden or (lambda text: None)
        self._grund = {}

    def bauen(self):
        from Genesis9.reglerplan import G9reglerplan

        beginn = time.perf_counter()
        self.messung = Reglerortemessung()
        self.treiberindex = self._treiberindex()
        self.anhang = self._anhangkanaele()
        regler, kandidaten, fehler = {}, [], 0
        alle = [r for b in G9reglerplan.bereiche() if b['schluessel'] not in self.FEST for r in b['regler']]
        for nummer, r in enumerate(alle, 1):
            try:
                eintrag, feld = self._regler(r)
            except (ValueError, KeyError, IndexError, RuntimeError) as grund:
                fehler += 1
                logger.warning('Reglerorte: %s nicht gemessen (%s)', r['name'], grund)
                continue
            regler[r['name']] = eintrag
            kandidaten.append({'name': r['name'], 'ende': eintrag['ende'], 'mm': eintrag['mm'], 'feld': feld})
            if nummer % 100 == 0:
                self.melden('%d/%d Regler gemessen (%.0f s)' % (nummer, len(alle), time.perf_counter() - beginn))
        aliase, paare, linear = Reglerortedoppelte(self.messung, self.melden).bauen(kandidaten)
        pfad = G9reglerorte.ablegen({'regler': regler, 'aliase': aliase, 'paare': paare, 'linear': linear,
                                     'orte': list(self._orte()), 'gebaut': time.strftime('%Y-%m-%d %H:%M'),
                                     'dauer_s': round(time.perf_counter() - beginn, 1), 'fehler': fehler})
        self.melden('%d Regler, %d Fehler, %.0f s → %s' % (len(regler), fehler, time.perf_counter() - beginn, pfad))
        return regler

    @staticmethod
    def _orte():
        from Genesis9.reglerregionen import G9reglerregionen

        return G9reglerregionen.ORTE

    # ------------------------------------------------------------- je Regler

    def _regler(self, r):
        name = r['name']
        bestes, feld = None, None
        for ende in (r.get('max'), r.get('min')):
            if not ende or abs(float(ende)) < 1e-9:
                continue
            m = self.messung.messen({name: float(ende)})
            if bestes is None or m['mm'] > bestes['mm']:
                bestes, feld = dict(m, ende=float(ende)), m['feld']
        if bestes is None:
            return {'mm': 0.0, 'ende': 1.0, 'skal': 0.0, 'anteile': {}}, None
        eintrag = {'mm': round(bestes['mm'], 3), 'ende': bestes['ende'], 'skal': bestes['skal'], 'anteile': bestes['anteile']}
        if name in self.anhang:
            eintrag['anhang'] = True
        if bestes['mm'] < G9reglerorte.WIRKUNG_MM:
            eintrag['dreht'] = round(float(self.messung.drehung({name: bestes['ende']})), 2)
            eintrag['bedingt'] = self._bedingt(name, bestes['ende'])
        return eintrag, feld

    def _bedingt(self, name, ende):
        """Wirkung mit gestellten Treibern (Multiplikatoren) gegen die Figur mit Treibern allein — None ohne Treiber."""
        treiber = sorted(self.treiberindex.get(name, ()))
        if not treiber:
            return None
        stellung = {t: self._treiberwert(t) for t in treiber}
        schluessel = tuple(sorted(stellung.items()))
        if schluessel not in self._grund:
            self._grund[schluessel] = self.messung.punkte(stellung)
        m = self.messung.messen(dict(stellung, **{name: ende}), grund=self._grund[schluessel])
        return {'treiber': treiber, 'mm': round(m['mm'], 3), 'anteile': m['anteile'], 'skal': m['skal']}

    def _treiberwert(self, kanal):
        from Genesis9.morphablage import G9morphablage

        angaben = G9morphablage.holen().kanaele.get(kanal) or {}
        oben = float(angaben.get('max') or 1.0)
        return oben if oben > 0 else 1.0

    @staticmethod
    def _treiberindex():
        """`{kanal: {treiber}}` — die Kanäle in den Produkt-Formeln (`stufe: mult`) eines Kanals."""
        from Genesis9.formeln import G9formeln
        from Genesis9.morphablage import G9morphablage

        eingaenge, _, _ = G9formeln.index(G9morphablage.holen())
        aus = {}
        for ziel, formeln in eingaenge.items():
            for f in formeln:
                if f.get('stufe') != 'mult':
                    continue
                aus.setdefault(ziel, set()).update(o['kanal'] for o in f['ops'] if 'kanal' in o and o['kanal'] != ziel)
        return aus

    @staticmethod
    def _anhangkanaele():
        """Die Kanäle, die ein Anhang (Wimpern, Augen, Zähne) mit eigenen Deltas rechnet — sie wirken, auch ohne Käfigverschiebung."""
        from Genesis9.anhang import G9anhang
        from Genesis9.kanalnamen import G9kanalnamen
        from Genesis9.morphablage import G9morphablage

        namen = G9kanalnamen.von(G9morphablage.holen())
        return {namen.aufloesen(k) for k in G9anhang.morphnamen()}
