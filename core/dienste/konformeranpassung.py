# -*- coding: utf-8 -*-
u"""Konformeranpassung — ein fertiges Kleidungsnetz mit UMAs Konformer anlegen.

WARUM (09.09.2026, Edgar: „im Tab Assets - Garment Fit viele Assets, die nicht
auf das Modell fitten … Überlege, ob du die Logik von «Garment Code» anwenden
kannst für das Fitten")
=====================================================================
Der GarmentCode-Reiter legt seine Schnittteile mit
`UMA_Python.Kleidungskonformer` an den Körper — der Portierung von UMAs
`UMAClothingConformer`. Dessen Docstring nennt die Aufgabe wörtlich: **ein
fertiges Netz auf einer Körperoberfläche halten.** Genau das ist auch die
Aufgabe von Garment Fit, nur kommt das Netz dort aus der Kleiderbibliothek
statt aus einem Schnitt.

Die Logik ist ab dem Netz vollständig unabhängig von GarmentCode: In
`Assets/GarmentCode/vorschau3d.py` sind nur die ersten beiden Zeilen
schnittspezifisch (Spezifikation laden, Panels erzeugen), alles danach
rechnet mit `punkte`/`dreiecke`. Deshalb ist dieser Weg hier als DRITTES
Verfahren neben `fit_garment` und der Hüllen-Anpassung eingehängt, nicht als
Ersatz: Welcher besser sitzt, ist für die Kleiderbibliothek **nicht
gemessen** (`Assets/kleidung/verfahren.Kleidungsverfahren`, Zeile
`bibliothek`: „nicht gemessen"). Erst der Vergleich am selben Stück
entscheidet das, und dafür gibt es jetzt den Knopf.

ZWEI EINSTELLUNGEN ANDERS ALS IN DER SCHNITTVORSCHAU
====================================================
`vorschau3d` schaltet `glaetten` und `tangential_halten` AUS und überschreibt
den gemerkten Abstand mit der Stoffdicke — richtig für flache Zuschnitte, die
als Ebene im Raum stehen. Ein Bibliotheksstück ist aber ein bereits geformtes
Kleidungsstück: Seine Wölbung ist gewollt, sein Abstand zur Haut ist echte
Stoffdicke. Hier gelten deshalb UMAs Vorgaben (`glaetten=True`,
`tangential_halten=True`), und der Abstand bleibt, wie er gebunden wurde.
"""
import logging

import numpy as np

from .koerperhuelle import Koerperhuelle

logger = logging.getLogger('core')

__all__ = ['Konformeranpassung']


class Konformeranpassung:
    u"""Ein Kleidungsnetz über UMAs Konformer an einen Körper legen."""

    #: Ein Bibliotheksstück kann weiter von der Haut weg liegen als ein
    #: Schnittteil (Mantel, weiter Rock) - der Suchradius muss das hergeben.
    SUCHRADIUS_M = 0.35
    HOECHSTABSTAND_M = 1.0

    @classmethod
    def legen(cls, stoff_punkte, stoff_dreiecke, koerper_punkte,
              koerper_dreiecke, zusatzabstand_m=0.0):
        u"""Das Stück an den Körper legen.

        @param stoff_punkte    (N, 3) des Kleidungsnetzes
        @param stoff_dreiecke  (T, 3)
        @param koerper_punkte  (M, 3) im SELBEN Koordinatensystem
        @param koerper_dreiecke (S, 3)
        @param zusatzabstand_m zusätzlicher Abstand zur Haut
        @returns (dict, None) oder (None, Grund) - nie eine stille Nulländerung
        """
        from UMA_Python import (Einstellungen, Kleidungskonformer,
                                Netzgeometrie)

        stoff = np.asarray(stoff_punkte, dtype=np.float64).reshape(-1, 3)
        koerper = np.asarray(koerper_punkte, dtype=np.float64).reshape(-1, 3)
        # DER KOERPER KOMMT ALS VIERECKE (gemessen 09.09.2026: 17.288 Quads,
        # `mesh.faces.shape[1] == 4`). Ein `reshape(-1, 3)` darauf haette
        # stillschweigend Unsinn ergeben - dieselbe Zahl Werte, voellig andere
        # Flaechen. `Koerperhuelle.dreiecke` teilt sie richtig auf.
        flaechen = np.asarray(Koerperhuelle.dreiecke(koerper_dreiecke),
                              dtype=np.int64).reshape(-1, 3)
        stoff_flaechen = np.asarray(Koerperhuelle.dreiecke(stoff_dreiecke),
                                    dtype=np.int64).reshape(-1, 3)
        dreiecke = stoff_flaechen
        if not len(stoff) or not len(dreiecke):
            return None, u'Das Stück hat keine Flächen'
        if not len(koerper) or not len(flaechen):
            return None, u'Der Körper hat keine Flächen'

        konformer = Kleidungskonformer(
            koerper, flaechen,
            Einstellungen(zusatzabstand_m=float(zusatzabstand_m),
                          suchradius_m=cls.SUCHRADIUS_M,
                          hoechstabstand_m=cls.HOECHSTABSTAND_M))
        bindung = konformer.binden('garment_fit', stoff, dreiecke)
        taugt, grund = bindung.taugt()
        if taugt:
            cls._abstand_kappen(bindung, zusatzabstand_m)
        if not taugt:
            logger.warning('Konformer: Bindung untauglich - %s', grund)
            return None, grund

        gelegt = konformer.anwenden(bindung)
        bilanz = bindung.bilanz()
        return {
            'vertices': gelegt,
            'faces': dreiecke,
            'normals': Netzgeometrie.punktnormalen(gelegt, dreiecke),
            'gebunden': bilanz.get('gebunden'),
            'ungebunden': bilanz.get('ungebunden'),
            'hautabstand_mm': cls._hautabstand_mm(koerper, gelegt),
        }, None

    #: Weiter als das darf ein Stück nach dem Anlegen nicht von der Haut
    #: stehen. Gemessen (09.09.2026, Handschuhe): Ohne Kappung hielt der
    #: Konformer 108–141 mm Median — den Abstand, den die Vorlage in IHRER
    #: Ruhelage zum Zielkörper hatte. Er hält eine Passung, er stellt keine
    #: her; `fit_garment` kam auf 12–18 mm. Gekappt bleibt die Form dort
    #: erhalten, wo sie ohnehin nah ist.
    KAPPE_M = 0.02

    @classmethod
    def _abstand_kappen(cls, bindung, zusatzabstand_m):
        u"""Zu weite Bindungsabstände auf `KAPPE_M` ziehen, Vorzeichen behalten.

        Das VORZEICHEN bleibt (wie in `GarmentCode/vorschau3d.py`): Wer es
        mitkappt, klappt das Stück auf die Innenseite des Körpers.
        """
        grenze = cls.KAPPE_M + max(0.0, float(zusatzabstand_m))
        abstand = np.asarray(bindung.abstand, dtype=np.float64)
        vorzeichen = np.where(abstand >= 0, 1.0, -1.0)
        bindung.abstand = vorzeichen * np.minimum(np.abs(abstand), grenze)

    @staticmethod
    def _hautabstand_mm(koerper, gelegt):
        u"""Median-Abstand zum nächsten Körperpunkt, in Millimetern.

        Die Zahl macht den Vergleich der Verfahren überhaupt erst möglich -
        ohne sie bliebe „sitzt besser" eine Behauptung. Sie misst gegen die
        PUNKTE, nicht gegen die Flächen: gröber, aber ohne zweiten KD-Baum
        und für einen Vergleich zweier Wege am selben Stück ausreichend.
        """
        try:
            from scipy.spatial import cKDTree
        except ImportError:                                    # noqa: BLE001
            logger.info('Konformer: ohne scipy kein Hautabstand')
            return None
        abstand, _ = cKDTree(koerper).query(gelegt, workers=-1)
        return round(float(np.median(abstand)) * 1000.0, 1)
