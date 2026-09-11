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

from django.views.generic import TemplateView

from koerper.fpskette import Fpskette
from koerper.physik import Koerperphysik


class KoerperPhysik(TemplateView):
    u"""Baustellen, Kandidaten, Kette, Messwerte, Fallen, Stand."""

    template_name = 'hilfe/koerper_physik.html'

    def get_context_data(self, **kwargs):
        kontext = super().get_context_data(**kwargs)
        kontext.update({
            'aktiv': 'hilfe_koerper_physik',
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
        })
        return kontext

    @classmethod
    def ansicht(cls):
        u"""Die fertige Ansicht mit sprechendem Namen.

        `View.as_view()` liefert eine Funktion namens `view`; im Fehlerlog
        und in `manage.py show_urls` staende sonst mehrfach dasselbe.
        """
        ansicht = cls.as_view()
        ansicht.__name__ = 'hilfe_koerper_physik'
        return ansicht
