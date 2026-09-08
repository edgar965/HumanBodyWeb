# -*- coding: utf-8 -*-
u"""Hilfe -> Kleidung -> Neu: fuenf Welten, eine Figur.

WARUM (Edgar, 08.09.2026): Die Analyse, die am selben Tag als Artefakt
entstand, gehoert ins Projekt — dort steht sie neben den Seiten, deren
Zahlen sie benutzt, und veraltet mit ihnen zusammen.

Die Frage dahinter war: „Jetzt haben wir mindestens 3 Methoden: MakeHuman,
GarmentCode, UMA. mach doch einen Vorschlag wie du das beste aus allen
holst? Evtl. neuer AssetTyp bei Tab Assets: Unified?"

Die Antwort in einem Satz: Zusammenfuehrbar sind die fuenf Welten nicht
ueber ein gemeinsames NETZ (vier unvertraegliche Topologien), sondern ueber
die Schicht darueber — und seit dem 08.09.2026 auch ueber die darunter,
weil UMAs Konformer in Python vorliegt.

Die Daten kommen aus `kleidung.vergleich.Vergleich`, nicht aus der Vorlage.
"""

from django.views.generic import TemplateView

from kleidung.vergleich import Vergleich


class KleidungNeu(TemplateView):
    u"""Analyse der fuenf Systeme und der Stufenplan fuer „Unified"."""

    template_name = 'hilfe/kleidung_neu.html'

    def get_context_data(self, **kwargs):
        kontext = super().get_context_data(**kwargs)
        kontext.update({
            'aktiv': 'hilfe_kleidung_neu',
            'welten': Vergleich.welten(),
            'knochen_morph': Vergleich.knochen_gegen_morph(),
            'wege': Vergleich.wege(),
            'schicht': Vergleich.schicht(),
            'beschreibung': Vergleich.beschreibung(),
            'stufen': Vergleich.stufen(),
            'nicht': Vergleich.nicht(),
            'unsicher': Vergleich.unsicher(),
        })
        return kontext

    @classmethod
    def ansicht(cls):
        u"""Die fertige Ansicht mit sprechendem Namen.

        `View.as_view()` liefert eine Funktion namens `view`; im Fehlerlog
        und in `manage.py show_urls` staende sonst mehrfach dasselbe.
        """
        ansicht = cls.as_view()
        ansicht.__name__ = 'hilfe_kleidung_neu'
        return ansicht
