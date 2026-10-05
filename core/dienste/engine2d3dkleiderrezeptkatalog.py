# -*- coding: utf-8 -*-
"""Engine2d3dKleiderrezeptkatalog — was ein Rezept von „2D3D Kleider" beim Namen nennen darf, gelesen aus den Bibliotheken dieses Rechners (05.10.2026).

Edgar (nach der ersten Iteration, in der die KI `kleid_nur('oberteil')` und `koerper_regler_setzen(FBMHeavy=…)` schrieb — Namen, die es nicht gibt): „dann reicht der Prompt nicht aus — wir müssen im Prompt
sagen, welche Funktionen es in den Klassen gibt, und ggf. welche Morphs es gibt für Kleider, Personen, welche Kleider und Haare es gibt". Die Funktionen liefert `GET …/funktionen/`; hier der Rest, damit der Prompt nichts
raten lässt (`GET /api/engine2d3dkleider/<id>/rezeptkatalog/`, Text daraus: `Edgar.rezeptkatalog.Rezeptkatalog`):

    auftrag      die Fotostücke des Schritts „Kleiderstücke" (oberteil/hose/socken → Kennung), die gewählte Frisur und ihre Kandidaten, die Frisur des Startmodells (`Begutachtungsrunde._start`), das Standardhemd
    startrezept  die Figur des Stands vor den Iterationen als Rezeptzeilen (`Standvorabkleider.rezept`) — die Ausgangslage der ersten Runde
    garderobe    Kleidung (Daz, ohne `eigen_`/`gc_`), eigene Stücke (`eigen_…`, ohne die Fotostücke FREMDER Aufträge), Haar, Requisiten — nur Kennungen
    regler       je Stück dieses Auftrags (Fotostücke, Frisur, Standardhemd, Teile der letzten Runde) die Regler der Garderobe: Name, Grenzen — `kleid_morph(kennung, kanal, wert)`
    koerper      die Genesis-9-Regler der Person: `body_ctrl_`, `body_bs_`, `head_ctrl_`, `head_bs_` mit Grenzen — `koerper_regler(name, wert)`
    schnitt      je GarmentCode-Vorlage die Formen (`form=`) und, für die Vorlagen, die ein Rezept üblicherweise braucht, die Regler (`regler={pfad: wert}`) mit Bereich und Vorgabe

Jeder Abschnitt fängt seinen Fehler selbst (`fehler`): ein Abschnitt, der nicht lesbar ist, kostet nicht den ganzen Katalog.
"""

import logging

logger = logging.getLogger('core')

__all__ = ['Engine2d3dKleiderrezeptkatalog']


class Engine2d3dKleiderrezeptkatalog:
    KOERPER = ('body_ctrl_', 'body_bs_', 'head_ctrl_', 'head_bs_')
    #: Vorlagen, deren Regler im Prompt stehen (die Kleider, die ein Foto-Auftrag meistens braucht); Kleid, Anzug und Rock haben 38–104 Felder, ihre Formen stehen trotzdem da.
    SCHNITT_MIT_REGLERN = ('oberteil', 'hose', 'shorts', 'unterwaesche', 'schuh')
    REGLER_JE_STUECK = 24

    def __init__(self, job):
        self.job = job
        self.ergebnis = job.ergebnis or {}
        self.fehler = []

    # ------------------------------------------------------------------ Abschnitte

    def auftrag(self):
        from Genesis9.haargenerisch import G9haargenerisch
        from iterationen2d3d.kleiderwahl import Kleiderwahl
        stuecke = ((self.ergebnis.get('fotostuecke') or {}).get('stuecke')) or {}
        frisur = self.ergebnis.get('frisur') or {}
        wahl = frisur.get('wahl') or {}
        kandidaten = list(dict.fromkeys(str(k['kennung']) for k in frisur.get('kandidaten') or [] if k.get('kennung')))
        return {'fotostuecke': dict(stuecke), 'hemd': Kleiderwahl.OBERTEIL, 'startfrisur': (kandidaten[0] if kandidaten else G9haargenerisch.VORGABE),
                'kandidaten': kandidaten[:8], 'frisur': {'kennung': wahl.get('kennung'), 'regler': dict(wahl.get('regler') or {}), 'farbe': wahl.get('farbe')}}

    def startrezept(self):
        """Die Figur, die der Stand vor den Iterationen zeigt (Fotostücke, Frisur, Farben), als Rezeptzeilen — die Ausgangslage, auf der die erste Runde der Nachbesserung aufbaut."""
        from .standvorabkleider import Standvorabkleider
        return Standvorabkleider.rezept(self.job)

    def garderobe(self, eigene_fotostuecke):
        from Genesis9.garderobe import G9garderobe
        liste = [e for e in G9garderobe.liste() if not (e['id'].startswith('eigen_foto_') and e['id'] not in eigene_fotostuecke)]

        def ids(art, ohne=()):
            return [e['id'] for e in liste if e['art'] == art and not e['id'].startswith(ohne)]

        return {'kleidung': ids('kleidung', ('eigen_', 'gc_')), 'eigene': [e['id'] for e in liste if e['id'].startswith('eigen_') and e['art'] != 'haar'],
                'haar': ids('haar'), 'requisiten': ids('requisit')}

    def regler(self, kennungen):
        from Genesis9.garderobe import G9garderobe
        aus = {}
        for kennung in dict.fromkeys(k for k in kennungen if k):
            eintrag = G9garderobe.eintrag(kennung)
            if eintrag:
                aus[kennung] = [{'name': r['name'], 'min': r.get('min'), 'max': r.get('max')} for r in (eintrag.get('regler') or [])[:self.REGLER_JE_STUECK]]
        return aus

    def koerper(self):
        from Genesis9.morphablage import G9morphablage
        kanaele = G9morphablage.holen().kanaele
        return {praefix: [{'name': n, 'min': k.get('min'), 'max': k.get('max')} for n, k in sorted(kanaele.items())
                          if n.startswith(praefix) and k.get('sichtbar', True) and '-0x' not in n] for praefix in self.KOERPER}

    @staticmethod
    def _felder(bloecke):
        aus = []
        for gruppe in bloecke:
            aus += [{'pfad': f.get('pfad'), 'typ': f.get('typ'), 'bereich': f.get('bereich'), 'wert': f.get('wert')} for f in gruppe.get('felder') or []]
            aus += Engine2d3dKleiderrezeptkatalog._felder(gruppe.get('untergruppen') or [])
        return aus

    def schnitt(self):
        from GarmentCode.formpresets import Formpresets
        from GarmentCode.katalog import Katalog
        from GarmentCode.regler import Regler
        aus = {}
        for name in Katalog.STUECKE:
            felder = self._felder(Regler.fuer(Katalog.entwurf(name), Katalog.varianten(name))) if name in self.SCHNITT_MIT_REGLERN else []
            aus[name] = {'formen': [{'schluessel': f['schluessel'], 'titel': f['titel']} for f in Formpresets.fuer(name)], 'regler': felder}
        return aus

    # ------------------------------------------------------------------ Gesamt

    def _abschnitt(self, name, aufruf, vorgabe):
        try:
            return aufruf()
        except Exception as fehler:  # noqa: BLE001 — ein Abschnitt, der sich nicht lesen lässt, darf den Katalog nicht kosten
            logger.warning('Rezeptkatalog %s: Abschnitt %s nicht lesbar: %s', self.job.kennung, name, fehler, exc_info=True)
            self.fehler.append('%s: %s' % (name, fehler))
            return vorgabe

    def _teile_der_letzten_runde(self):
        runden = [r for r in self.ergebnis.get('iterationen') or [] if isinstance(r, dict)]
        return [k for k, v in ((runden[-1].get('teile') or {}).items() if runden else []) if v]

    def daten(self):
        auftrag = self._abschnitt('auftrag', self.auftrag, {'fotostuecke': {}, 'hemd': None, 'startfrisur': None, 'kandidaten': [], 'frisur': {}})
        meine = set(auftrag['fotostuecke'].values())
        stuecke = [auftrag.get('hemd'), *auftrag['fotostuecke'].values(), auftrag['frisur'].get('kennung') or auftrag.get('startfrisur'), *self._teile_der_letzten_runde()]
        return {'auftrag': auftrag, 'startrezept': self._abschnitt('startrezept', self.startrezept, []),
                'garderobe': self._abschnitt('garderobe', lambda: self.garderobe(meine), {}),
                'regler': self._abschnitt('regler', lambda: self.regler(stuecke), {}), 'koerper': self._abschnitt('koerper', self.koerper, {}),
                'schnitt': self._abschnitt('schnitt', self.schnitt, {}), 'fehler': self.fehler}
