# -*- coding: utf-8 -*-
"""Workflowdrapieren — der Entscheidungsbaum „Drapieren" im Inneren einer Runde von „2D3D Kleider" (Hilfe → Architektur → 2D3D).

Herausgelöst aus `Workflowrundebau` (06.10.2026, die Datei stand bei 310 Zeilen) und neu geordnet. Edgar, 06.10.2026: „Blender und Newton sind doch
nur Ausnahmen, oder? Standard ist Stoffsolver? Kennzeichne das". Gelesen und gemessen, nicht angenommen:

- **Der Standard ist: kein Drapieren.** Ein Lauf drapiert nur, wenn eine Rezeptzeile `m.kleid_drapieren(…)` es verlangt. In den 11 Aufträgen mit Runden
  (`ergebnis.iterationen[].aufrufe`, gelesen 06.10.2026, `ProjektTemp/_wegwerf/edgar/drapier_zaehlen.py`) steht sie zweimal: im Auftrag „Randy" und in dessen
  Kopie, Runde 59, von Hand, `motor='stoffsolver'`. In keinem Sapiens-Auftrag, in keiner automatischen Runde.
- **Die Vorgabe der Zeile ist `newton`** (`ModellFormMixin.kleid_drapieren(…, motor='newton')`); die Automatik schreibt die Zeile ohne `motor`
  (`IterationKleider.drapieren`, erst wenn der Stoffabstand drei Runden still steht). Gelaufen ist Newton bisher nie.
- **Blender und der Stoffsolver sind Ausnahmen**: nur per Rezeptzeile von Hand. Der einzige Motor, der je in einem Auftrag lief, ist der Stoffsolver (Randy, Runde 59).
"""

from .workflowbaum import Workflowbaum
from .workflowknoten import Workflowknoten as K
from .workflowzeiten import Workflowzeiten as W

__all__ = ['Workflowdrapieren']


class Workflowdrapieren:
    F, T, E = K.FRAGE, K.TAT, K.ENDE
    #: Quelle der Zählung im Text (06.10.2026).
    ZAEHLUNG = 'in 0 von 11 Aufträgen mit Runden gelaufen (gelesen 06.10.2026)'

    @classmethod
    def baum(cls):
        keins = K(
            cls.E,
            'Kein Drapieren — so läuft ein Auftrag ohne Eingriff',
            'Die Kleider sitzen durch die Bindung an die Figur und die Kollision (G9kollision, 3 mm Abstand zur Haut) im Bau in der A-Pose; danach häutet '
            'G9haltungshaut sie in die Haltung der Fotos, und G9haltungsabstand hebt sie wieder 3 mm über die Haut (06.10.2026: vorher stand die Haut am Armloch '
            'bis 1,3 mm vor dem Hemd, im Render eine orange Linie). Das ist keine Stoffsimulation: der Stoff fällt nicht, Falten entstehen nicht. '
            'Woher die Stücke kommen und wie sie sitzen: die Bäume „Kleidung" und „Sitz".',
            ('Kleidermodellbau', 'G9kollision', 'G9haltungshaut', 'G9haltungsabstand'),
            kante='nein (der Standard)',
            vorgabe=True,
        )
        newton = K(
            cls.T,
            'Kleiddrapierung → Stoffnewton',
            'Die Vorgabe der Zeile (motor ohne Angabe), auch der Motor, den die Automatik wählt. Bisher %s. Eigener GPU-Löser (Newton SolverStyle3D, Warp): '
            'Z oben ↔ Y oben umgerechnet, oberes Band 8 %% fest, Grundfigur als stehender Kollider, ohne Druck.' % cls.ZAEHLUNG,
            ('Kleiddrapierung', 'Stoffnewton'),
            kante='newton (Vorgabe der Zeile)',
            vorgabe=True,
            teile=[
                ('erster Aufruf (Warp-Kernel übersetzen)', W.NEWTON_ERST),
                ('weitere Aufrufe, 24 Bilder', W.NEWTON_WARM),
            ],
        )
        blender = K(
            cls.T,
            'Engine2d3dKleiderblender.drapieren → Blender Cloth',
            'Mit Druck (Pressure), ein Blender-Aufruf je Stück; Netze per from_pydata, damit die Punktreihenfolge bleibt. Seit 02.10.2026 fällt der Stoff entlang −Y '
            '(vorher −Z, quer zur Figur: gemessen 533 mm in 11 Bildern) und das obere Band bleibt fest wie bei Newton. Nur per Rezept von Hand. Bisher %s.' % cls.ZAEHLUNG,
            ('Engine2d3dKleiderblender', 'Rezeptumgebung'),
            kante='blender (nur von Hand)',
            ausnahme=True,
            teile=[
                ('Blender-Start je Aufruf', W.BLENDER_START),
                ('Cloth: Hose, 3.123 Punkte, 24 Bilder', W.BLENDER_HOSE),
                ('Cloth: Oberteil, 17.552 Punkte, 24 Bilder', W.BLENDER_OBERTEIL),
            ],
        )
        solver = K(
            cls.T,
            'Stoffsolverdrapierung → Stoffsolver (Blenders Cloth auf der GPU)',
            'Dieselbe Rechnung wie Blender Cloth (Federn, Biegung, Druck mit Volumenterm, Kollision Dreieck gegen Dreieck, dazu Wind und Kraftfelder mit Texturen und '
            'bewegten Feldobjekten, Vertexgruppen, Schrumpfen, Nähte, weiches und bewegtes Anheften, mehrere und bewegte Körper — die Tabelle „Der Stoffsolver gegen '
            'Blender" unten führt jede Funktion mit Stand) als Warp-Löser in python14, ein Prozess je Stück, derselbe Auftrag. Braucht eine CUDA-GPU; ohne sie wird abgelehnt. '
            'Gleiche Schwerkraft und festes Band wie die anderen Motoren. Nur per Rezept von Hand. Der EINZIGE Motor, der in einem Auftrag lief: „Randy", Runde 59, '
            'Hose gc_hose_schlank, 24 Bilder. Oberteil 24 Bilder im Mittel 2,7 mm von Blender (Blenders eigenes Rauschen 2,3 mm), bei der rutschenden Hose nicht unterscheidbar '
            '(200 Blender- gegen 500 Solver-Läufe: Streuung 44,3 gegen 45,2 mm). Die Zeiten sind am 02.10.2026 vor dem Ausbau des Solvers gemessen und danach nicht neu.',
            ('Stoffsolverdrapierung', 'Drapierauftrag', 'Stoffsimulation', 'Rezeptumgebung'),
            kante='stoffsolver (nur von Hand)',
            ausnahme=True,
            teile=[
                ('Hose, 3.123 Punkte, 24 Bilder (Blender: 19,5 s)', W.SOLVER_HOSE),
                ('Oberteil, 17.552 Punkte, 24 Bilder (Blender: 55,0 s)', W.SOLVER_OBERTEIL),
                ('ohne CUDA-GPU (Host, 12 Bilder) — wird abgelehnt', W.SOLVER_OHNE_GPU),
            ],
        )
        motor = K(
            cls.F,
            'Welcher Motor?',
            'Parameter motor der Zeile: %s. Die Automatik schreibt die Zeile ohne motor, sobald der Stoffabstand drei Runden lang innerhalb 2 mm bleibt '
            '(IterationKleider.drapieren); die Prüf-KI darf sie nicht (Begutachtungskritik.VERBOTEN). Ergebnis: Morph <kennung>.eigen.drapiert, linear stellbar 0…1.'
            % ' | '.join(('newton', 'blender', 'stoffsolver')),
            ('Rezeptumgebung', 'IterationKleider', 'G9kleidmorphe'),
            kante='ja (Rezeptzeile m.kleid_drapieren)',
        ).mit(newton, blender, solver)
        wurzel = K(
            cls.F,
            'Steht im Rezept eine Zeile m.kleid_drapieren?',
            'Das Drapieren ist ein Sonderweg, kein Schritt jeder Runde. Gelesen 06.10.2026 in ergebnis.iterationen[].aufrufe aller 11 Aufträge mit Runden: 2 Zeilen, '
            'beide in „Randy" und dessen Kopie, Runde 59, von Hand, motor=\'stoffsolver\'; in keinem Sapiens-Auftrag und in keiner automatischen Runde.',
            ('ModellFormMixin', 'Rezeptumgebung'),
        ).mit(keins, motor)
        return Workflowbaum(
            'drapieren',
            'Drapieren: kein Drapieren (Standard), Newton, Blender oder Stoffsolver',
            'Wird gedrapt — und mit welchem Löser?',
            wurzel,
            'ModellFormMixin.kleid_drapieren, Rezeptumgebung.MOTOREN, Begutachtungswerkzeug.drapierer, IterationKleider.drapieren; Zählung: ProjektTemp/_wegwerf/edgar/drapier_zaehlen.py '
            '(06.10.2026); Zeiten: ortsmorphe.md (Newton) und Stoffsolver/README.md, Abschnitt „Messungen" (Blender und Stoffsolver, 02.10.2026, nicht aus der Pipeline)',
        )
