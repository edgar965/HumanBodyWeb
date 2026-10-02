# -*- coding: utf-8 -*-
"""Workflowhaardynamik — der Entscheidungsbaum der Haar-Dynamik in „2D3D Kleider": `m.haar_dynamik(…)` rechnet das Stranghaar
einer Frisur mit Blenders Haar-Dynamik als Warp-Löser (Stoffsolver, 02.10.2026). Eigene Datei, weil `Workflowrundebau` die
Grenze von 300 Zeilen erreicht hat.

Der Weg ist nur per Rezeptzeile von Hand: Die Automatik (`Iteration*`, `Rundenauswahl`) schreibt ihn nie, die Prüf-KI darf ihn
nicht (`Begutachtungskritik.VERBOTEN`). Die Zeiten sind NICHT in der Pipeline gemessen, sondern in einer Probe an der Bibliothek
(Frisur Pixie und Hime Cut, Käfig auf der Bühne, `Haardynamik.simulieren` mit abgefangenem `G9kleidmorphe.ablegen`, Skript
`ProjektTemp/_wegwerf/stoff_ausbau/k7/haardynamik_zeit.py`, 02.10.2026, warmer Warp-Cache).
"""

from .workflowbaum import Workflowbaum
from .workflowknoten import Workflowknoten as K
from .workflowzeit import Workflowzeit as Z

__all__ = ['Workflowhaardynamik']


class Workflowhaardynamik:
    F, T, E = K.FRAGE, K.TAT, K.ENDE
    PROBE = ('nicht in der Pipeline gemessen: Probe haardynamik_zeit.py (ProjektTemp/_wegwerf/stoff_ausbau/k7), 02.10.2026, '
             'warmer Warp-Cache, Wanduhrzeit des Aufrufs Haardynamik.simulieren, 2–3 Läufe')
    PIXIE_24 = Z(5.7, 8.8, PROBE, 'Pixie (21.755 Strähnen, 236.136 Punkte), 24 Bilder: 5,7 s ab dem zweiten Lauf im Prozess, '
                 '8,8 s im ersten (Käfig, Körper, Kopfhaut werden erst geladen); davon der Solver-Prozess 5,1 s, die '
                 'Zeitschritte 2,2 s')
    HIME_24 = Z(4.4, 7.5, PROBE, 'Hime Cut (2.292 Strähnen, 182.276 Punkte), 24 Bilder: 4,4–4,5 s ab dem zweiten Lauf, '
                '7,5 s im ersten; davon der Solver-Prozess 4,0 s, die Zeitschritte 1,6 s')
    PIXIE_12 = Z(4.7, 7.5, PROBE, 'Pixie, 12 Bilder (erster Lauf 7,5 s, zweiter 4,7 s); Zeitschritte 1,1 s')
    HIME_12 = Z(3.6, 6.6, PROBE, 'Hime Cut, 12 Bilder (erster Lauf 6,6 s, zweiter 3,6 s); Zeitschritte 0,8 s')

    @classmethod
    def baum(cls):
        wurzel = K(
            cls.F,
            'm.haar_dynamik(sorte, bilder, name, wert, material, mindestabstand_mm)',
            'Eine Rezeptzeile von Hand, keine Vorgabe: die Automatik schreibt sie nie, die Prüf-KI darf sie nicht '
            '(Begutachtungskritik.VERBOTEN). Ergebnis: Morph <sorte>.eigen.dynamik, linear stellbar 0…1. Braucht eine '
            'Runde (Rezeptumgebung) — der Arbeiter kommt aus Begutachtungswerkzeug.haardynamik.',
            ('Rezeptumgebung', 'Begutachtungswerkzeug', 'Haardynamik'),
        ).mit(
            K(
                cls.E,
                'ValueError: Kartenhaar',
                'Die Frisur hat kein Stranghaar (Teile ohne G9strang): Hinweis auf haar_trim, haar_clump, haar_noise … '
                '(G9haarops). Es wird nichts abgelegt.',
                ('Haardynamik',),
                kante='Kartenhaar (kein Strang)',
            ),
            K(
                cls.E,
                'RuntimeError: keine CUDA-GPU',
                'Die Haarkollision gibt es nur auf dem Gerät. Haarsimulation bricht den Aufbau mit dem Grund ab, statt '
                'das Haar durch den Kopf laufen zu lassen; der Host-Weg (NumPy) wird nicht benutzt.',
                ('Haardynamik', 'Haarsimulation'),
                kante='keine CUDA-GPU',
            ),
            K(
                cls.T,
                'Haardynamik → Haarauftrag → Haarsimulation',
                'Je Strang-Teil ein Prozess in python14 (haar_lauf.py): Haarstraehnen macht aus den Ketten der Segmente '
                'Strähnen mit der Wurzel zuerst (an der echten Geometrie gemessen: Pixie und Hime Cut liefern sie so) und '
                'die Kopfhautnormale je Wurzel; Körper ist die ganze Grundfigur, Schwerkraft −Y, Mindestabstand 2 mm. '
                'Blenders Regel psys_hair_use_simulation friert Strähnen mit einem sehr kurzen Segment ein (Probe: Pixie '
                '14.108 von 21.755, Hime Cut 464 von 2.292). Die Wurzeln bleiben (Delta genau 0); das Delta je Käfigpunkt '
                'wird atomar als Morph abgelegt.',
                ('Haardynamik', 'Haarstraehnen', 'Haarauftrag', 'Haarsimulation', 'G9kleidmorphe'),
                kante='Stranghaar und CUDA-GPU',
                teile=[
                    ('Pixie, 24 Bilder', cls.PIXIE_24),
                    ('Hime Cut, 24 Bilder', cls.HIME_24),
                    ('Pixie, 12 Bilder', cls.PIXIE_12),
                    ('Hime Cut, 12 Bilder', cls.HIME_12),
                ],
            ),
        )
        return Workflowbaum(
            'haardynamik',
            'Haar-Dynamik: Stoffsolver auf Stranghaar',
            'Was geschieht bei m.haar_dynamik, und wann wird abgelehnt?',
            wurzel,
            'Haardynamik, Haarstraehnen, Stoffsolver/haarauftrag.py; Zeiten: Probe an der Bibliothek, nicht aus der Pipeline',
        )
