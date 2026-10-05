# -*- coding: utf-8 -*-
"""Engine2d3dKleiderrezeptbestand — prüft, ob die Namen in einem Rezept im Bestand vorkommen (05.10.2026).

Anlass: Die erste Iteration der Nachbesserung schrieb `m.kleid_nur('oberteil')`, `m.kleid_nur('hose')`, `m.kleid_nur('schuhe')` und `m.koerper_regler_setzen(FBMHeavy=0.2, PBMBellySize=0.1)`. `G9rezept.pruefen`
prüft nur die FORM (erlaubte Funktion, lesbare Argumente); die Namen löst das Modell erst beim Bau auf — ein Name, den es nicht gibt, bewirkt dort nichts und meldet nichts. Die Runde rechnete Minuten und
änderte an den Kleidern nichts (gemessen: `teile` vor und nach der Runde gleich). Hier wird derselbe Text VOR der Runde gegen die Bibliothek gelesen: ein unbekanntes Stück oder ein unbekannter Körperregler
ist ein Fehler mit Zeilennummer und den ähnlichsten Namen — der Server antwortet 400, und die Nachbesserung gibt die Meldung einmal an die KI zurück (`Nachbesserungslauf`).

Geprüft werden Parameter, die ein Stück meinen (`kennung`, `sorte`, die Liste `kennungen`) gegen die Garderobe (Kleidung, Haar, Requisiten) und die Fotostücke dieses Auftrags, und die Namen der
Körperregler (`koerper_regler`, `koerper_regler_setzen`) gegen die Kanäle der Morphablage. Stücke, die ein `kleid_schnitt` im selben Rezept erst anlegt (`gc_…`), und eigene Morphe (`eigen…`) gelten als bekannt.
NUR auf Anforderung (`pruefen_bestand` im Rumpf): das Rezeptfeld der Seite und ältere Aufrufer bleiben, wie sie waren.
"""

import difflib
import inspect

__all__ = ['Engine2d3dKleiderrezeptbestand']


class Engine2d3dKleiderrezeptbestand:
    STUECK = ('kennung', 'sorte')
    REGLER_FUNKTIONEN = {'koerper_regler': 'name', 'koerper_regler_setzen': 'werte'}

    def __init__(self, job):
        self.job = job
        self._stuecke = None
        self._kanaele = None

    # ------------------------------------------------------------------ Bestand

    def stuecke(self):
        if self._stuecke is None:
            from Genesis9.garderobe import G9garderobe
            self._stuecke = {e['id'] for e in G9garderobe.liste()} | set((((self.job.ergebnis or {}).get('fotostuecke') or {}).get('stuecke') or {}).values())
        return self._stuecke

    def kanaele(self):
        if self._kanaele is None:
            from Genesis9.morphablage import G9morphablage
            self._kanaele = set(G9morphablage.holen().kanaele)
        return self._kanaele

    @staticmethod
    def _aehnlich(name, bekannt):
        treffer = difflib.get_close_matches(str(name), sorted(bekannt), n=3, cutoff=0.5)
        return ' (ähnlich: %s)' % ', '.join(treffer) if treffer else ''

    # ------------------------------------------------------------------ Prüfen

    def pruefen(self, text):
        """Nichts, wenn alle Namen bekannt sind; sonst `ValueError` mit einer Zeile je unbekanntem Namen."""
        from Genesis9.modellmitkleidern import ModellMitKleidern
        from Genesis9.modellrezept import G9rezept
        aufrufe = G9rezept.pruefen(text)
        legt_an = any(name == 'kleid_schnitt' for _zeile, name, _args, _kwargs in aufrufe)
        fehler = []
        for zeile, name, args, kwargs in aufrufe:
            try:
                gebunden = inspect.signature(getattr(ModellMitKleidern, name)).bind_partial(None, *args, **kwargs).arguments
            except TypeError:
                continue                    # falsche Argumente meldet `G9rezept.anwenden` mit seiner eigenen Meldung
            for parameter, wert in gebunden.items():
                if parameter in self.STUECK and isinstance(wert, str):
                    fehler += self._stueck(zeile, name, wert, legt_an)
                elif parameter == 'kennungen':
                    fehler += [f for k in wert for f in self._stueck(zeile, name, k, legt_an)]
                elif self.REGLER_FUNKTIONEN.get(name) == parameter:
                    fehler += [f for k in (wert if isinstance(wert, dict) else [wert]) for f in self._regler(zeile, name, k)]
        if fehler:
            raise ValueError('\n'.join(fehler))

    def _stueck(self, zeile, funktion, name, legt_an):
        if name in self.stuecke() or (legt_an and name.startswith('gc_')):
            return []
        return ['Zeile %d: %s — „%s" ist kein Stück der Bibliothek%s; die Namen stehen im Prompt unter „Was es gibt"' % (zeile, funktion, name, self._aehnlich(name, self.stuecke()))]

    def _regler(self, zeile, funktion, name):
        if name in self.kanaele() or str(name).startswith('eigen'):
            return []
        return ['Zeile %d: %s — „%s" ist kein Körperregler von Genesis 9%s (body_ctrl_…, body_bs_…, head_ctrl_…, head_bs_…)' % (zeile, funktion, name, self._aehnlich(name, self.kanaele()))]
