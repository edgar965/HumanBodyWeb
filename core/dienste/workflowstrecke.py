# -*- coding: utf-8 -*-
"""Workflowstrecke — die Schritte eines Auftrags „2D3D Kleider" (seit 07.10.2026 elf, Kopf und Segmentierung sind optional) als Kette von Klassenkarten, mit ihren Optionen, ihrer
Zeit und der Zeitleiste eines vollständigen Auftrags (Hilfe → Architektur → 2D3D, 02.10.2026).

Die Schritte kommen aus `Architektur2d3d.LAUF` (= `Engine2d3dKleiderlauf.SCHRITTE`), die Optionen aus den Katalogen
(`Engine2d3dKleideroptionen.SICHTBAR`: nur was das Formular der Seite zeigt), die Zeiten aus `Workflowzeiten`. Die Zeitleiste zeigt (seit 06.10.2026)
den Auftrag 2026.10.06.14.10.22, einen vollen Lauf mit allen Schritten neu, von den Fotos bis zum Export: vorbereitung 55,9 s, netz 384,3 s, segmentierung 28,0 s,
koerper 877,0 s, grundfigur 1,7 s, kleiderstuecke 297,9 s, iterationen (eine Runde, Iteration 0) 154,2 s, export 2,1 s, film 357,7 s (300 Bilder) — zusammen 2.158,8 s;
speichern 0,0 s. Vorher stand hier der Auftrag 2026.10.01.20.10.04 (23 Runden, 1.826,3 s, ohne Film).
"""

from .workflowzeit import Workflowzeit
from .workflowzeiten import Workflowzeiten as W

__all__ = ['Workflowstrecke']


class Workflowstrecke:
    #: (Schritt, Klasse, Zeit, [(Option, Werte)], [Baumkennung]) — Reihenfolge wie `Engine2d3dKleiderlauf.SCHRITTE`.
    SCHRITTE = [
        (
            'vorbereitung',
            'Engine2d3dKleidervorbereitung',
            W.VORBEREITUNG,
            [
                ('vorbereitung.ausrichten', 'Häkchen, aus (Vorgabe) · angehakt = Mittelachse: Kopf, Rumpf und Hüfte der Seitenfotos auf eine senkrechte Achse, vorne und hinten um die Körperachse gedreht'),
                ('netz.freistellen, netz.licht', 'wie beim Schritt „netz" (die Vorbereitung liest dieselben Felder)'),
            ],
            [],
        ),
        (
            'netz',
            'Engine2d3dKleidernetz',
            W.NETZ,
            [
                ('textur', 'fotos_ki · fotos · ki · keine (Formmodell immer TRELLIS.2)'),
                ('freistellen', 'auto (BiRefNet) · alpha'),
                ('licht', '0–100 %'),
                ('mesh.aufloesung', 'schnell (512) · mittel (1024) · hoch (1536, Vorgabe) — Resolution des Space'),
                ('mesh.flaechen', 'Decimation Target, Vorgabe hier 100.000'),
                ('mesh.texturgroesse', 'Texture Size: 1024 · 2048 · 3072 · 4096'),
                (
                    'mesh.seed, mesh.seed_zufall, mesh.ss_*, mesh.form_*, mesh.tex_*',
                    'Seed, Randomize Seed und die drei Sampler (Stage 1–3) — wie im Space microsoft/TRELLIS.2',
                ),
            ],
            ['netz', 'textur'],
        ),
        (
            'kopf',
            'Engine2d3dKleiderkopf',
            W.KOPF,
            [
                ('kopf.rechnen', 'Häkchen, an (Vorgabe) · aus: der Schritt entfällt im vollen Lauf (ausdrücklich gestartet läuft er immer) und die Körper-Kette nimmt kein Kopfnetz'),
                ('kopf.modell', 'hunyuan3d_2mv (Vorgabe, die drei Ausschnitte gemeinsam) · hunyuan3d_2 (nur der vordere)'),
                ('kopf.flaechen', '100.000 · 200.000 · 300.000 (Vorgabe) · 500.000'),
                ('mesh.aufloesung, mesh.texturgroesse, mesh.seed', 'wie beim Schritt „netz" (der Kopflauf liest dieselben Felder)'),
            ],
            [],
        ),
        (
            'segmentierung',
            'Engine2d3dKleidersegmentierung',
            W.SEGMENTIERUNG,
            [
                ('segmentierung.verwenden', 'aus (Vorgabe: der Schritt entfällt im vollen Lauf, die Maske bleibt nach Farbe und Lage) · an (Sapiens zerlegt die Fotos, '
                                            'die Kleidungsmaske des Schritts „koerper" folgt den Etiketten); ausdrücklich gestartet läuft der Schritt immer'),
            ],
            [],
        ),
        (
            'koerper',
            'Engine2d3dKleiderkoerper',
            W.KOERPER_RECHNEN,
            [('quelle', 'uebernehmen · rechnen'), ('auftrag', 'Kennung eines Auftrags „Mesh to 3D"')],
            ['koerper'],
        ),
        (
            'grundfigur',
            'Engine2d3dKleidergrundfigur',
            W.GRUNDFIGUR,
            [('figur.basis', 'feminine · masculine · neutral'), ('figur.modell', 'aus (Vorgabe hier) · an')],
            [],
        ),
        ('kleiderstuecke', 'Engine2d3dKleiderstuecke', W.KLEIDERSTUECKE, [], []),
        (
            'iterationen',
            'Iterationskreislauf',
            W.RUNDE_ALLE,
            [
                ('modus', 'begutachtung · automatisch'),
                ('pruefki', 'aus · Ollama-Bildmodell'),
                ('bildbreite · stufe_stillstand', 'Start-Auflösung 128 px · 3 Runden'),
                ('tafelbreite · runden', '384 px · 20'),
                ('form', 'aus · an'),
                ('Renderer (Einstellungen)', 'mitsuba · pyrender'),
            ],
            [
                'modus',
                'rezeptweg',
                'automatik',
                'kleidung',
                'sitz',
                'drapieren',
                'haarknoten',
                'haardynamik',
                'bauen',
                'fotoprojektion',
                'renderer',
                'auswahl',
            ],
        ),
        ('export', 'Engine2d3dKleiderexport', W.EXPORT, [], ['ende']),
        (
            'film',
            'Engine2d3dKleiderfilm',
            W.FILM,
            [('bvh', 'Pfad · leer = übersprungen'), ('bilder · breite · hoehe', '300 · 960 · 960')],
            ['ende'],
        ),
        ('speichern', 'Engine2d3dKleiderspeichern', W.SPEICHERN, [], ['ende']),
    ]
    #: Auftrag 2026.10.06.14.10.22 (voller Lauf vom 06.10.2026, alle Schritte neu): (Schritt, Sekunden) — iterationen = Iteration 0, die einzige Runde dieses Laufs.
    LEITER = (
        'ergebnis.dauer (vorbereitung, netz, segmentierung, koerper, grundfigur, kleiderstuecke, iterationen, export, film; speichern 0,0 s) des Auftrags 2026.10.06.14.10.22 '
        '(Datenbank, gelesen 06.10.2026 nach dem Ende des Laufs)'
    )
    ZEITLEISTE = [
        ('vorbereitung', 55.9),
        ('netz', 384.3),
        ('segmentierung', 28.0),
        ('koerper', 877.0),
        ('grundfigur', 1.7),
        ('kleiderstuecke', 297.9),
        ('iterationen (1 Runde: Iteration 0)', 154.2),
        ('export', 2.1),
        ('film (300 Bilder)', 357.7),
    ]
    #: Die ersten sechs Einträge sind der Aufbau (einmal je Auftrag), danach kommen die Runden und der Export.
    AUFBAU_SCHRITTE = 6

    def __init__(self, zeichner, titel):
        """`zeichner`: `Workflowzeichner`, `titel`: Kennung → Überschrift der Bäume (für die Verweise)."""
        self.zeichner = zeichner
        self.titel = titel

    def schritte(self):
        aus = []
        for nr, (name, klasse, zeit, optionen, baeume) in enumerate(self.SCHRITTE, start=1):
            aus.append(
                {
                    'nr': nr,
                    'name': name,
                    'klasse': klasse,
                    'klasse_html': self.zeichner.klasse(klasse),
                    'zeit_html': self.zeichner.zeit(zeit),
                    'hinweis': zeit.hinweis,
                    'optionen': [{'name': n, 'werte': w} for n, w in optionen],
                    'baeume': [{'anker': 'baum-' + b, 'titel': self.titel[b]} for b in baeume],
                }
            )
        return aus

    def zeitleiste(self):
        """Der Auftrag als ein Streifen: je Schritt ein Segment, Breite = Anteil an der Gesamtzeit."""
        gesamt = sum(s for _n, s in self.ZEITLEISTE)
        aufbau = sum(s for _n, s in self.ZEITLEISTE[: self.AUFBAU_SCHRITTE])
        segmente = [
            {
                'name': n,
                'zeit_html': self.zeichner.zeit(Workflowzeit(s)),
                'sekunden': s,
                'prozent': '%.2f' % (100.0 * s / gesamt),
                'anteil': ('%.1f' % (100.0 * s / gesamt)).replace('.', ','),
            }
            for n, s in self.ZEITLEISTE
        ]
        return {
            'segmente': segmente,
            'gesamt': Workflowzeit(gesamt).text,
            'quelle': self.zeichner.quellen.nummer(self.LEITER),
            'aufbau': Workflowzeit(aufbau).text,
            'aufbau_prozent': ('%.1f' % (100.0 * aufbau / gesamt)).replace('.', ','),
        }
