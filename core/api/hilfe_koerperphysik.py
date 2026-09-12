# -*- coding: utf-8 -*-
u"""Hilfe -> Kleidung -> Koerperphysik: was sich am Koerper selbst bewegt.

WARUM (Edgar, 10.09.2026): „schreibe alle Erkenntnisse und das ganze Know how
der Koerperphysik auf in Hilfe - Kleidung - Koerperphysik. auch wie ich das
bedienen kann, performance usw"

Die Seite beantwortet drei Fragen: Was kann lineares Blend-Skinning nicht,
welcher offene Code kann es, und wie bedient man den Weg, der hier gebaut ist.
Die Daten kommen aus `koerper.physik` und `koerper.fpskette`, nicht aus der
Vorlage — dieselbe Regel wie bei der Kleiderphysik.
"""

from .hilfeseite import Hilfeseite

from koerper.fpskette import Fpskette
from koerper.physik import Koerperphysik


class KoerperPhysik(Hilfeseite):
    u"""Baustellen, Kandidaten, Kette, Messwerte, Fallen, Stand."""

    template_name = 'hilfe/koerper_physik.html'
    AKTIV = 'hilfe_koerper_physik'

    def kontext(self):
        return {
            'baustellen': Koerperphysik.baustellen(),
            'kandidaten': Koerperphysik.kandidaten(),
            'nicht': Koerperphysik.nicht(),
            'quellen': Koerperphysik.quellen(),
            'armverlust': Koerperphysik.LBS_ARMVERLUST_PROZENT,
            'armumfang_ruhe': Koerperphysik.LBS_ARMUMFANG_RUHE_CM,
            'aufloesung_mm': Koerperphysik.AUFLOESUNG_MM,
            'aufloesung_fein_mm': Koerperphysik.AUFLOESUNG_UNTERTEILT_MM,
            'schritte': Fpskette.schritte(),
            'pruefen': Fpskette.pruefen(),
            'fallen': Fpskette.fallen(),
            'aenderungen': Fpskette.aenderungen(),
            'stand': Fpskette.stand(),
            'offen': Fpskette.offen(),
            'punkte': Fpskette.PUNKTE,
            'dreiecke': Fpskette.DREIECKE,
            'punkte_voll': Fpskette.PUNKTE_VOLL,
            'gelenke': Fpskette.GELENKE,
            'gelenke_finger': Fpskette.GELENKE_MIT_FINGERN,
            'sekunden_60': Fpskette.SEKUNDEN_60_BILDER,
            'sekunden_je_bild': Fpskette.sekunden_je_bild(),
            'minuten_je_10s': Fpskette.minuten_je_10s(),
            'kb_je_bild': Fpskette.kb_je_bild(),
            'ordner': Fpskette.ORDNER,
            'klon': Fpskette.KLON,
        }
