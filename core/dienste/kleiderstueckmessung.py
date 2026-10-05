# -*- coding: utf-8 -*-
"""Kleiderstueckmessung — die Messung des Schritts „Kleiderstücke": Stücknote je Fotostück, Aufbau, Körper gegen nackte Haut und ein Bibliotheks-Anker (04.10.2026).

Edgar: „Dafür fehlt mir eine Messgröße. Überleg dir was." Die Messgröße steht in `Kleiderstuecknote` (Deckung, Treue, F-Wert gegen die Maskenflächen des Foto-Netzes in der Ruhelage, dazu der Aufbau
des Netzes); diese Klasse führt sie für alle Stücke eines Auftrags aus und fasst zusammen.

Der ANKER: eine Zahl ohne Maßstab sagt wenig. Dieselbe Messung für das Bibliotheksstück, das die Runden vor den Fotostücken anzogen (`Kleiderwahl`: Hemd, Shorts, kurze Socken), gegen DENSELBEN Bezug
— „Fotostück besser als Bibliotheksstück?" ist damit eine Messung. Gemessen am Auftrag 2026.10.04.11.11.44 (Abweichung = 1 − F, kleiner ist besser): Oberteil Foto 0,085 gegen Hemd 0,279; Hose Foto
0,264 gegen Shorts 0,610; Socken Foto 0,210 gegen 0,261.

`abweichung` (gesamt) ist der Mittelwert der Stückabweichungen, gewogen nach der Fläche der Stücke (cm²) — eine Zahl für den Auftrag, vergleichbar zwischen Läufen.
"""

import logging

import numpy as np

from .kleiderstueckobjekt import Kleiderstueckobjekt
from .kleiderstuecknote import Kleiderstuecknote

logger = logging.getLogger('core')

__all__ = ['Kleiderstueckmessung']


class Kleiderstueckmessung:
    #: Das Bibliotheksstück je Fotostück (`Kleiderwahl.OBERTEIL`, `SHORTS`, `SOCKEN`) — der Maßstab, kein Vorschlag.
    BIBLIOTHEK = {'oberteil': 'g9_base_shirt', 'hose': 'g9_base_shorts', 'socken': 'gc_crudelowsocks'}

    @staticmethod
    def _nummern():
        from .fotostuecke import Fotostuecke
        return {name: nummer for nummer, name in Fotostuecke.STUECKE.items()}

    @classmethod
    def messen(cls, bezug, stuecke):
        """`stuecke`: `{name: Garderobenkennung}` aus `Fotostuecke.holen()` → `{stuecke: {name: {kennung, note, aufbau}}, koerper, abweichung}`."""
        nummern = cls._nummern()
        aus, gewicht = {}, []
        for name, kennung in stuecke.items():
            objekt = Kleiderstueckobjekt.laden(kennung)
            if objekt is None or name not in nummern:
                aus[name] = {'kennung': kennung, 'fehler': 'Netz des Stücks nicht gefunden'}
                continue
            note = Kleiderstuecknote.vergleichen(bezug.stueck(nummern[name]), objekt)
            aufbau = Kleiderstuecknote.aufbau(*objekt)
            aus[name] = {'kennung': kennung, 'note': note, 'aufbau': aufbau}
            gewicht.append((note['abweichung'], aufbau['cm2']))
        gesamt = None
        if gewicht and sum(w for _, w in gewicht) > 0:
            gesamt = round(float(sum(a * w for a, w in gewicht) / sum(w for _, w in gewicht)), 4)
        return {'stuecke': aus, 'koerper': Kleiderstuecknote.haut_abstand(bezug.haut(), bezug.koerper_netz()), 'abweichung': gesamt,
                'nah_mm': round(Kleiderstuecknote.NAH_M * 1000.0, 1)}

    @classmethod
    def bibliothek(cls, job, bezug, namen):
        """`{name: {sorte, abweichung, f}}` — die Stücknote der Bibliotheksstücke für die Stücke `namen`, gegen denselben Bezug. Ein Stück, das sich nicht bauen lässt, fehlt."""
        from Genesis9.modellmitkleidern import ModellMitKleidern

        from .kleidermodellbau import Kleidermodellbau
        nummern = cls._nummern()
        aus = {}
        for name in namen:
            sorte = cls.BIBLIOTHEK.get(name)
            if sorte is None or name not in nummern:
                continue
            try:
                modell = ModellMitKleidern().kleid_nur(sorte)
                teile = [t for t in Kleidermodellbau(job.stellung(), None, koerper=modell.koerper).teile(modell)
                         if t.get('art') == 'kleidung' and t.get('sorte') == sorte]       # das Standardhemd bleibt bei `kleid_nur` sonst stehen
                if not teile:
                    continue
                punkte = np.vstack([np.asarray(t['punkte'], dtype=np.float64) for t in teile])
                flaechen, versatz = [], 0
                for t in teile:
                    flaechen.append(np.asarray(t['dreiecke'], dtype=np.int64).reshape(-1, 3) + versatz)
                    versatz += len(t['punkte'])
                note = Kleiderstuecknote.vergleichen(bezug.stueck(nummern[name]), (punkte, np.vstack(flaechen)))
                aus[name] = {'sorte': sorte, 'abweichung': note['abweichung'], 'f': note['f']}
            except Exception as fehler:  # noqa: BLE001 — der Anker ist Beiwerk, die Messung der Stücke zählt
                logger.warning('2D3D Kleider %s: Bibliotheksanker %s nicht gerechnet (%s)', job.kennung, sorte, fehler)
        return aus
