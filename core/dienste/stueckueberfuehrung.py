# -*- coding: utf-8 -*-
"""Stueckueberfuehrung — ein Bibliotheksstück als GarmentCode-Schnitt.

WARUM (09.09.2026, Edgar: „überlege, wie diese Assets verbessert werden können,
so dass sie fitten. Kannst du die in das GarmentCode Modell überführen?")
=====================================================================
Gemessen über den ganzen Bestand (179 Stücke, `_wegwerf/passungsbefund.py` und
`_wegwerf/formverlust.py`) sitzt das Problem NICHT dort, wo man es vermutet:

    Durchstich    tiefster Fall über alle 179 Stücke: 38 mm bei 0,07 % der
                  Punkte. Median je Kategorie 0,00–0,14 %. Kein Befund.
    Form          Kleider verlieren beim Anpassen im Median 16 % ihrer
                  Saumweite, der schlimmste Fall 72 %
                  (`toigo_halter_dress_with_fluted_skirt`).
    Saumluft      über alle Kategorien Median 11–19 mm. Ein Rock, der fällt,
                  hat am Saum ein Vielfaches davon.

Ein Shrinkwrap zieht jeden Punkt auf die Haut. Bei einem T-Shirt ist das
richtig, bei einem Glockenrock nicht: Aus dem weiten Rock werden zwei
Beinröhren — im Bild sieht das aus wie eine Hose (`_wegwerf/silhouettenbild.py`).

DIESER WEG DREHT DIE RICHTUNG UM. Statt das Netz zu ziehen, wird es VERMESSEN
(`GarmentCode.stueckmasse`) und aus den Maßen ein Schnitt KONSTRUIERT
(`GarmentCode.schnittdeutung`). Was ankommt, ist die Silhouette: Länge, Weite,
Ärmel, trägerlos ja/nein. Was zurückbleibt, sind Muster, Rüschen und Schnallen
— das Ergebnis ist ein neues Kleidungsstück nach demselben Vorbild, nicht
dasselbe Netz an anderer Stelle. Deshalb heißt der Knopf „als Schnitt deuten"
und nicht „übernehmen".

BELEGT AN EINEM KLEID (`toigo_camisole_dress_with_full_skirt`, 09.09.2026):

    Weg                        Durchstich   Saumweite   Saumluft
    Garment Fit (heute)            0,00 %      1,67        15 mm
    GarmentCode, drapiert          0,59 %      1,76        73 mm

Die Saumluft ist die Zahl, die zählt: 15 mm heißt „klebt am Bein", 73 mm heißt
„fällt". Der Schnitt kostet 2,9 s, die Drapierung 48 s.
"""
import logging

import numpy as np

logger = logging.getLogger('core')

__all__ = ['Stueckueberfuehrung']


class Stueckueberfuehrung:
    """Aus einer Bibliothekskennung ein Katalogstück mit Reglern."""

    @classmethod
    def deuten(cls, garment_id, koerper, masse):
        """(dict, None) oder (None, Grund) — nie eine stille Vermutung.

        @param garment_id  Kennung aus der Kleiderbibliothek
        @param koerper     Körperzustand (Netz im Projektraum)
        @param masse       die GarmentCode-Maße dieser Figur, in Zentimetern
        """
        from GarmentCode.schnittdeutung import Schnittdeutung, Unuebersetzbar
        from GarmentCode.stueckmasse import Stueckmasse

        punkte, kategorie, fehler = cls._vorlagenpunkte(garment_id)
        if punkte is None:
            return None, fehler
        gemessen = Stueckmasse(punkte, koerper.vertices)
        werte = gemessen.als_dict(masse['shoulder_w'], cls._achsel_cm(masse),
                                  cls._huefte_cm(masse))
        try:
            if cls._ist_schuh(gemessen, masse, kategorie):
                stueck, regler, bericht = cls._schuh(punkte, masse)
            else:
                stueck, regler, bericht = Schnittdeutung(werte, masse,
                                                         kategorie).deuten()
        except (Unuebersetzbar, ValueError) as grund:
            logger.info('Deutung %s abgelehnt: %s', garment_id, grund)
            return None, str(grund)
        logger.info('Deutung %s -> %s (%d Regler)',
                    garment_id, stueck, len(regler))
        return {'garment_id': garment_id, 'vorlage': stueck,
                'regler': regler, 'bericht': bericht}, None

    #: Wann ein Stück den Schuhweg nimmt (11.09.2026) — die Kategorie führt,
    #: die Geometrie springt ein, wie bei Hose/Rock in `Schnittdeutung`:
    #:
    #: * Ordner `shoes`: alles, was unter diesem Anteil der Körperhöhe endet.
    #:   Der höchste Stiefel (`heroine_boots_1`) endet bei 85 cm (0,51);
    #:   `elvs_crude_bootyshorts` liegt fälschlich in `shoes` und endet bei
    #:   94 cm (0,56) — die Grenze trennt beide.
    #: * Jeder andere Ordner: nur, was unter `SCHUH_FREMD_BIS` endet. Drei
    #:   Ballerinas (6 cm) und die Wasserstiefel (44 cm) stehen unter
    #:   `tops`; Strümpfe reichen bis zur Hüfte und bleiben Kleidung. Ein
    #:   einheitlicher Wert von 0,55 zog 22 Miniröcke und Shorts mit.
    SCHUH_BIS_ANTEIL = 0.55
    SCHUH_FREMD_BIS = 0.40

    @classmethod
    def _ist_schuh(cls, gemessen, masse, kategorie=''):
        grenze = (cls.SCHUH_BIS_ANTEIL if (kategorie or '').lower() == 'shoes'
                  else cls.SCHUH_FREMD_BIS)
        return gemessen.oben_cm < grenze * float(masse['height'])

    @classmethod
    def _schuh(cls, punkte, masse):
        u"""Der Schuhweg (`GarmentCode.schuhdeutung`, seit 11.09.2026).

        Die Fussmasse kommen mit den Körpermassen (`Koerpermasse` misst sie
        seit demselben Tag); `Fussvorgabe` fällt ohne sie auf Anteile der
        Körperhöhe zurück und sagt das im Bericht.
        """
        from GarmentCode.schuh.fussvorgabe import Fussvorgabe
        from GarmentCode.schuhdeutung import Schuhdeutung
        fuss = Fussvorgabe(masse)
        deutung = Schuhdeutung(punkte, fuss)
        deutung.hinweise.extend(fuss.hinweise)
        stueck, regler, bericht = deutung.deuten()
        # Dieselben Schlüssel wie bei `Schnittdeutung`, damit der Messlauf
        # (`werkzeug/vorbilder_messen.py`) beide gleich behandelt.
        bericht['stueck'].setdefault('unten_cm', 0.0)
        bericht['stueck'].setdefault('oben_cm', bericht['stueck']['schaft_cm'])
        return stueck, regler, bericht

    @staticmethod
    def _achsel_cm(masse):
        """Höhe der Achsel über dem Boden — die Grenze zwischen Rumpf und Arm."""
        return (masse['height'] - masse['head_l'] - masse['armscye_depth'])

    @staticmethod
    def _huefte_cm(masse):
        """Höhe der Hüftlinie über dem Boden — GarmentCodes `_leg_length`.

        Unterhalb davon zählt kein Stoff als „am Arm": In der A-Pose stehen
        die Beine breiter als die Schultern.
        """
        return (masse['height'] - masse['head_l'] - masse['waist_line']
                - masse['hips_line'])

    @staticmethod
    def _vorlagenpunkte(garment_id):
        """(Punkte in Körperlage, Kategorie, Fehler) — Meter, Z oben.

        Die Bibliotheksstücke liegen als `makehuman-assets` in Dezimetern mit
        Y oben. `Stueckmasse` erwartet die Blender-Lage; die Verschiebung auf
        den Boden macht sie selbst.
        """
        from core.dienste.kleiderbibliothek import Kleiderbibliothek
        from GarmentFitter.fitter.koordinaten import Quellsystem

        vorlage = Kleiderbibliothek.holen().get_template(garment_id)
        if vorlage is None or vorlage.vertices is None:
            return None, '', 'Kleidungsstück %s hat kein Netz' % garment_id
        kategorie = getattr(vorlage, 'category', '') or ''
        punkte = np.asarray(vorlage.vertices, dtype=np.float64)
        system = ('makehuman' if vorlage.source == 'makehuman-assets'
                  else Quellsystem.erkennen(punkte))
        if system != 'blender':
            punkte = Quellsystem.nach_blender(punkte, system)
        return punkte, kategorie, None
