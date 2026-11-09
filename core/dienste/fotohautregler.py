# -*- coding: utf-8 -*-
"""Fotohautregler — die Haut-Regler des Renders für eine Figur mit eigener Haut (05.11.2026, `Exportleiste.optionen`).

Edgar zu Edgar_1: „im render Export ist das Genesis Modell nochmal anders, gesicht scheint anders, die Haut ist glänzend und ölig“. Die Vorgaben von `Figurfilm.Reglerhaut` sind die Werte von
Randys Film: Bräune `#f7c487` (Franks Unterarm gegen die blasse Daz-Haut), Klarlack 0,3 („Schweiß, Öl“), Rauheit 0,38. Sie sollen die Daz-Haut einfärben; auf Hautkacheln aus Fotos oder Netz
tönen sie eine schon richtige Haut noch einmal orange und legen Öl darüber — der Render von Edgar_1 (05.11.2026) zeigte genau das.

Darum gilt für jede Figur mit eigenen Kacheln (`Exportleistequelle.kacheln`): keine Tönung, kein Klarlack, Rauheit wie auf der Seite. `RAUHEIT` ist der Mittelwert der Mediane der Rauheitskarten,
die die Seite auf der Haut zeigt: 0,725–0,773 je Material, gemessen an der GLB der Seite von Edgar_1 (`ProjektTemp/_wegwerf/edgar1_textur/rauheit_seite.py`). `spekular` bleibt: die Seite rechnet
wie die Vorgabe 0,5 mit F0 = 0,04. Ohne eigene Kacheln (Daz-Haut, 2D3D Kleider, Feld „Mesh3D-AI“) bleibt alles wie bisher.

Kein Relief (05.11.2026, Edgar: „es gibt noch abweichungen zu dem genesis modell“): Die Normalenkarten sind Daz' Poren und Falten, nicht die der Person, die Seite zeichnet ohne sie (im Chrome
gelesen: keine `normalMap`). Den Sprenkel auf der Brust erklärt das nicht: Er ist Bildrauschen bei 96 Proben (`ProjektTemp/_wegwerf/edgar1_textur/sprenkel_probe.py`), mit Relief 0 unverändert.

Ein gespeicherter Wert, der der Vorgabe des Katalogs gleicht, gilt als nicht verstellt: `regler_werte.json` hält den ganzen Formularstand, auch nie berührter Regler — sonst behielte jeder schon
einmal gerenderte Test die Bräune. Wer genau die Katalogvorgabe will, stellt einen Nachbarwert ein.
"""

__all__ = ['Fotohautregler']


class Fotohautregler:
    GRUPPE = 'renderhaut'
    RAUHEIT = 0.75
    WERTE = {'material.haut.toenung': '#ffffff', 'material.arme.toenung': '#ffffff', 'material.haut.glanzlack': 0.0, 'material.haut.rauheit': RAUHEIT, 'material.arme.rauheit': RAUHEIT,
             'material.haut.normale_staerke': 0.0, 'material.arme.normale_staerke': 0.0}

    @classmethod
    def einsetzen(cls, optionen, kacheln):
        """`optionen` (`{gruppe: {schluessel: wert}}`, geprüft) mit den Werten für eigene Haut, wenn `kacheln` nicht leer ist → neues Wörterbuch (die Eingabe bleibt)."""
        if not kacheln:
            return optionen
        from Figurfilm.reglerhaut import Reglerhaut
        katalog = {e['schluessel']: e['vorgabe'] for e in Reglerhaut.REGLER}
        haut = dict(optionen.get(cls.GRUPPE) or {})
        for schluessel, wert in cls.WERTE.items():
            if haut.get(schluessel, katalog[schluessel]) == katalog[schluessel]:
                haut[schluessel] = wert
        return dict(optionen, **{cls.GRUPPE: haut})
