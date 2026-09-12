# -*- coding: utf-8 -*-
u"""Hilfe -> Kleidung -> Kleiderphysik: Stoffdynamik auf dem bewegten Koerper.

WARUM (Edgar, 10.09.2026): „Kleiderphysik - schreib das rein in eine neuen
Seite Hilfe - Kleider - Kleiderphysik. blenderCloth nutze ich nicht,
garmentCode ist bisher am besten, passen den Vorschlag dafuer an."

Die Seite beantwortet, welcher offene Code Stoff auf einem GEHENDEN Koerper
rechnen kann — fuer den MP4-Export des Theatre-Moduls — und was davon auf
dieser Maschine gemessen wurde. Die Daten kommen aus
`kleidung.physik.Kleiderphysik`, nicht aus der Vorlage.
"""

from .hilfeseite import Hilfeseite

from kleidung.physik import Kleiderphysik


class KleidungPhysik(Hilfeseite):
    u"""Bestand, Kandidaten, Messung, Kette."""

    template_name = 'hilfe/kleidung_physik.html'
    AKTIV = 'hilfe_kleidung_physik'

    def kontext(self):
        return {
            'bestand': Kleiderphysik.bestand(),
            'kandidaten': Kleiderphysik.kandidaten(),
            'messaufbau': Kleiderphysik.messaufbau(),
            'messung': Kleiderphysik.messung(),
            'deutung': Kleiderphysik.deutung(),
            'kette': Kleiderphysik.kette(),
            'nicht': Kleiderphysik.nicht(),
            'offen': Kleiderphysik.offen(),
            'quellen': Kleiderphysik.quellen(),
            'kernelbau_s': Kleiderphysik.KERNELBAU_S,
            'style3d_ms': Kleiderphysik.STYLE3D_MS_JE_BILD,
            'minuten_je_10s': Kleiderphysik.minuten_je_10s(),
            'kb_je_bild': Kleiderphysik.KB_JE_BILD,
        }
