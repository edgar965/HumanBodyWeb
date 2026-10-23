# -*- coding: utf-8 -*-
"""Mesh3daistufe2wahl — Einstellungen der Stufe 2 der Kleider-KI von Mesh3D-AI (21.10.2026).

Edgar: „reicht unser Netz für 8 Mio Punkte? Mach das einstellbar unter Einstellungen - Mesh3d-AI. Die erste Stufe bleibt so wie sie jetzt ist. Mach eine zweite Stufe“ → „Form der Kleider 1 cm
Abtastung ist zu grob … sonst sieht man keine Kleiderschnallen oder keine Schnürsenkel“ → „mach es“.
Stufe 1 (Schichtkopf: Form je Käfigpunkt, 1–1,5 cm; Farbkopf: Farbe je Punkt aus 262.144 Eingangspunkten) bleibt fest. Stufe 2 bekommt das Tripo-Netz dicht abgetastet als EINGANG und gibt je Punkt
des feiner geteilten Stücks eine Höhe und je Texel eine Farbkorrektur aus, trainiert gegen das Ziel (`ProjektTemp/_wegwerf/mesh3dai_stufe2_*.py`).
Die Werte liegen in `AppSettings.ui_prefs` (Formular als JSON an `/api/ui-prefs/`, wie `Mesh3daitexturwahl`); Unbekanntes heißt Vorgabe. Ein Lauf der Stufe 2 trägt die Werte, mit denen er
gerechnet wurde (`fassung`) — der Einsatz nimmt ihn nur bei denselben Werten.
"""

import logging

logger = logging.getLogger('core')

__all__ = ['Mesh3daistufe2wahl']


class Mesh3daistufe2wahl:
    FELDER = {
        'mesh3dai_stufe2_punkte': ((0, 'aus — nur Stufe 1'), (1_000_000, '1 Mio. (etwa 1 Punkt je 2 mm²)'), (2_000_000, '2 Mio. (etwa 1 Punkt je mm², Abstand 1 mm)'),
                                   (4_000_000, '4 Mio. (Abstand 0,7 mm)'), (8_000_000, '8 Mio. (Abstand 0,5 mm)')),
        'mesh3dai_stufe2_nachbarn': ((32, '32'), (64, '64')),
        'mesh3dai_stufe2_textur': ((1024, '1024 × 1024'), (2048, '2048 × 2048')),
        'mesh3dai_stufe2_teilungen': ((2, '2 — wie Stufe 1, Punkte alle 3–4 mm'), (3, '3 — Punkte alle 1–2 mm'), (4, '4 — Punkte alle 0,5–1 mm (viermal so viele Dreiecke)')),
    }
    VORGABE = {'mesh3dai_stufe2_punkte': 2_000_000, 'mesh3dai_stufe2_nachbarn': 64, 'mesh3dai_stufe2_textur': 1024, 'mesh3dai_stufe2_teilungen': 3}
    BESCHREIBUNG = {
        'mesh3dai_stufe2_punkte': 'So dicht wird das Tripo-Netz für Stufe 2 abgetastet (jeder Punkt mit seiner Texturfarbe); das Ziel genauso dicht. Das Netz wird dadurch nicht größer — '
                                  'es sieht je Stelle nur deren Nachbarn —, nur Daten und Nachbarsuche.',
        'mesh3dai_stufe2_nachbarn': 'So viele nächste Tripo-Punkte sieht Stufe 2 je Stelle des Stücks.',
        'mesh3dai_stufe2_textur': 'Bild je Kleidungsstück für die Farbe der Stufe 2 (1024 passt zu 2 Mio. Punkten, 2048 zu 8 Mio.).',
        'mesh3dai_stufe2_teilungen': 'So oft wird jedes Stück geteilt, bevor Stufe 2 je Punkt die Höhe setzt — mehr Teilungen zeigen feinere Form (Schnürsenkel, Schlaufen, Nieten), '
                                     'jede Stufe vervierfacht die Dreiecke.',
    }
    TITEL = {'mesh3dai_stufe2_punkte': 'Punkte vom Tripo-Netz', 'mesh3dai_stufe2_nachbarn': 'Nachbarn je Stelle', 'mesh3dai_stufe2_textur': 'Texturgröße je Stück',
             'mesh3dai_stufe2_teilungen': 'Teilungen der Form'}

    @classmethod
    def aus(cls, prefs):
        """Die vier Werte aus einem `ui_prefs`-Dict; was keiner der erlaubten Werte ist, ist die Vorgabe."""
        prefs = prefs or {}
        werte = {}
        for schluessel, erlaubt in cls.FELDER.items():
            try:
                w = int(str(prefs.get(schluessel, cls.VORGABE[schluessel])).strip())
            except ValueError:
                w = cls.VORGABE[schluessel]
            werte[schluessel] = w if w in dict(erlaubt) else cls.VORGABE[schluessel]
        return werte

    @classmethod
    def gewaehlt(cls):
        """Die gespeicherten Werte — ohne lesbare Einstellungen die Vorgabe, mit Warnung."""
        try:
            from ..models import AppSettings
            return cls.aus(AppSettings.load().ui_prefs)
        except Exception as fehler:  # noqa: BLE001 — Rechenläufe sollen auch ohne Datenbank laufen, mit der Vorgabe
            logger.warning('Mesh3daistufe2wahl: Einstellung nicht lesbar (%s) — Vorgabe', fehler)
            return dict(cls.VORGABE)

    @staticmethod
    def fassung(werte):
        """Name der Fassung für Ablagen: `p2000000_n64_t1024_s3`."""
        return 'p%d_n%d_t%d_s%d' % (werte['mesh3dai_stufe2_punkte'], werte['mesh3dai_stufe2_nachbarn'], werte['mesh3dai_stufe2_textur'], werte['mesh3dai_stufe2_teilungen'])

    @classmethod
    def felder(cls, werte):
        """Für die Vorlage: je Feld Schlüssel, Titel, Wert, Auswahl, Vorgabetext, Beschreibung."""
        return [{'schluessel': s, 'titel': cls.TITEL[s], 'wert': werte[s], 'werte': erlaubt, 'vorgabe': dict(erlaubt)[cls.VORGABE[s]], 'beschreibung': cls.BESCHREIBUNG[s]}
                for s, erlaubt in cls.FELDER.items()]
