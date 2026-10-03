# -*- coding: utf-8 -*-
"""Workflowrundebau — die Entscheidungsbäume im Inneren einer Runde von „2D3D Kleider": Drapieren (Newton, Blender oder
Stoffsolver), Haar-Knoten (Blender), Bauen, Fotoprojektion, Renderer, Rundenauswahl; Haar-Dynamik: `Workflowhaardynamik`.

Edgar: „allen Optionen (z. B. Blender)". Blender kommt in der Pipeline an genau zwei Stellen vor, beide nur über den einen
Arbeiter `Engine2d3dKleiderblender` und nur per Rezeptzeile: `m.kleid_drapieren(…, motor='blender')`, `m.haar_knoten(…)`. Der Stoffsolver
(Blenders Rechnung auf der GPU) ist ein weiterer Weg, nur per Rezept: `motor='stoffsolver'`, `m.haar_dynamik(…)`.
"""

from .workflowbaum import Workflowbaum
from .workflowhaardynamik import Workflowhaardynamik
from .workflowknoten import Workflowknoten as K
from .workflowzeiten import Workflowzeiten as W

__all__ = ['Workflowrundebau']


class Workflowrundebau:
    F, T, E, OFFEN = K.FRAGE, K.TAT, K.ENDE, K.OFFEN

    @classmethod
    def baeume(cls):
        return [
            cls.drapieren(),
            cls.haarknoten(),
            Workflowhaardynamik.baum(),
            cls.bauen(),
            cls.fotoprojektion(),
            cls.renderer(),
            cls.auswahl(),
        ]

    @classmethod
    def drapieren(cls):
        wurzel = K(
            cls.F,
            'm.kleid_drapieren(kennung, bilder, druck, motor)',
            'Eine Rezeptzeile, Vorgabe motor=newton. Die Automatik '
            'schreibt sie, wenn die Form steht (Stoffabstand drei Runden innerhalb 2 mm, IterationKleider.drapieren); '
            'die Prüf-KI darf sie nicht (Begutachtungskritik.VERBOTEN). Ergebnis: Morph <kennung>.eigen.drapiert, '
            'linear stellbar 0…1.',
            ('Rezeptumgebung', 'IterationKleider', 'G9kleidmorphe'),
        ).mit(
            K(
                cls.T,
                'Kleiddrapierung → Stoffnewton',
                'Eigener GPU-Löser (Newton SolverStyle3D, Warp): Z oben ↔ Y oben umgerechnet, '
                'oberes Band 8 % fest, Grundfigur als stehender Kollider, ohne Druck.',
                ('Kleiddrapierung', 'Stoffnewton'),
                kante='newton (Vorgabe)',
                vorgabe=True,
                teile=[
                    ('erster Aufruf (Warp-Kernel übersetzen)', W.NEWTON_ERST),
                    ('weitere Aufrufe, 24 Bilder', W.NEWTON_WARM),
                ],
            ),
            K(
                cls.T,
                'Engine2d3dKleiderblender.drapieren → Blender Cloth',
                'Mit Druck (Pressure), ein Blender-Aufruf je Stück; Netze per from_pydata, damit die Punktreihenfolge '
                'bleibt. Seit 02.10.2026 fällt der Stoff entlang −Y (vorher −Z, quer zur Figur: gemessen 533 mm in '
                '11 Bildern) und das obere Band bleibt fest wie bei Newton. Nur per Rezept von Hand.',
                ('Engine2d3dKleiderblender', 'Rezeptumgebung'),
                kante='blender',
                teile=[
                    ('Blender-Start je Aufruf', W.BLENDER_START),
                    ('Cloth: Hose, 3.123 Punkte, 24 Bilder', W.BLENDER_HOSE),
                    ('Cloth: Oberteil, 17.552 Punkte, 24 Bilder', W.BLENDER_OBERTEIL),
                ],
            ),
            K(
                cls.T,
                'Stoffsolverdrapierung → Stoffsolver (Blenders Cloth auf der GPU)',
                'Dieselbe Rechnung wie Blender Cloth (Federn, Biegung, Druck mit Volumenterm, Kollision Dreieck gegen '
                'Dreieck, dazu Wind und Kraftfelder mit Texturen und bewegten Feldobjekten, Vertexgruppen, Schrumpfen, Nähte, '
                'weiches und bewegtes Anheften, mehrere und bewegte Körper — die Tabelle „Der Stoffsolver gegen Blender" unten '
                'führt jede Funktion mit Stand) als Warp-Löser in python14, ein Prozess je Stück, derselbe Auftrag. Braucht eine '
                'CUDA-GPU; ohne sie wird abgelehnt. Gleiche Schwerkraft und festes Band wie die anderen Motoren. Nur per Rezept von '
                'Hand; Oberteil 24 Bilder im Mittel 2,7 mm von Blender (Blenders eigenes Rauschen 2,3 mm), bei der rutschenden '
                'Hose nicht unterscheidbar (200 Blender- gegen 500 Solver-Läufe: Streuung 44,3 gegen 45,2 mm). Die Zeiten sind '
                'am 02.10.2026 vor dem Ausbau des Solvers gemessen und danach nicht neu.',
                ('Stoffsolverdrapierung', 'Drapierauftrag', 'Stoffsimulation', 'Rezeptumgebung'),
                kante='stoffsolver',
                teile=[
                    ('Hose, 3.123 Punkte, 24 Bilder (Blender: 19,5 s)', W.SOLVER_HOSE),
                    ('Oberteil, 17.552 Punkte, 24 Bilder (Blender: 55,0 s)', W.SOLVER_OBERTEIL),
                    ('ohne CUDA-GPU (Host, 12 Bilder) — wird abgelehnt', W.SOLVER_OHNE_GPU),
                ],
            ),
        )
        return Workflowbaum(
            'drapieren',
            'Drapieren: Newton, Blender oder Stoffsolver',
            'Mit welchem Löser fällt der Stoff?',
            wurzel,
            'Rezeptumgebung.MOTOREN, Begutachtungswerkzeug.drapierer; Zeiten: ortsmorphe.md (Newton) und Stoffsolver/README.md, '
            'Abschnitt „Messungen" (Blender und Stoffsolver, 02.10.2026, nicht aus der Pipeline)',
        )

    @classmethod
    def haarknoten(cls):
        wurzel = K(
            cls.F,
            'm.haar_knoten(sorte, name, knoten)',
            'Nur Stranghaar (Kartenhaar nimmt haar_trim, haar_clump, …). Blenders '
            'Hair-Node-Gruppen rechnen in Blender ohne Fenster; die Automatik ruft sie nicht, nur ein Rezept von Hand.',
            ('Engine2d3dKleiderblender', 'Haarknotenauftrag'),
        ).mit(
            K(
                cls.T,
                'Verformende Knoten → Morph',
                'trim, clump, curl, frizz, noise, straighten, roll, smooth, braid, displace, rotate, '
                'shrinkwrap, attach. Delta je Punkt, Ortsgewicht als Mask, Ergebnis <sorte>.eigen.<name>.',
                ('Engine2d3dKleiderblender', 'G9kleidmorphe'),
                zeit=W.BLENDER_HAAR,
                kante='verformend',
            ),
            K(
                cls.T,
                'Erzeugende Knoten → Zusatzsträhnen',
                'duplicate, interpolate, generate. Ergebnis <sorte>.str.<name>. Attach, '
                'Interpolate und Generate brauchen eine Kopfhaut mit eindeutiger UV; ein unbrauchbares Ergebnis wird zurückgewiesen.',
                ('Engine2d3dKleiderblender', 'Haarknotenauftrag', 'G9haarzusatz'),
                zeit=W.KEINE,
                kante='erzeugend',
            ),
        )
        return Workflowbaum(
            'haarknoten',
            'Haar-Knoten in Blender',
            'Welche der 16 Hair-Node-Gruppen — und was entsteht?',
            wurzel,
            'Engine2d3dKleiderblender.KNOTEN, Haarknotenauftrag.ZUSATZ; Zeit: ortsmorphe.md (Pixie, nur Rechnung)',
        )

    @classmethod
    def bauen(cls):
        wurzel = K(
            cls.F,
            'Ist der Bauplan gleich geblieben?',
            'Stellung, Werte der Stücke, getragene Stücke — nicht die Farben. Der '
            'Teilevorrat hält je Prozess und Art (Kleidung, Haar) einen Eintrag.',
            ('Teilevorrat', 'Kleidermodellbau'),
        ).mit(
            K(
                cls.E,
                'Antwort aus dem Vorrat',
                'Im selben Prozess, Folgerunde eines Laufs (Abschnitt „Modell bauen" insgesamt).',
                zeit=W.BAUEN_WARM,
                kante='ja, im selben Prozess',
                vorgabe=True,
            ),
            K(
                cls.E,
                'Neu rechnen',
                'Bindung der Stücke an die Figur (Oberflaechenbindung, folgernetz) und Kollision der Lagen '
                '(kleidmischung, kollision). Jeder Lauf ist ein neuer Prozess — der Vorrat ist dort leer.',
                ('Kleidermodellbau',),
                zeit=W.BAUEN_KALT,
                kante='nein oder neuer Prozess',
            ),
        )
        return Workflowbaum(
            'bauen',
            'Modell bauen: Vorrat warm oder kalt?',
            'Wird gebaut oder aus dem Teilevorrat geholt?',
            wurzel,
            'Teilevorrat.antwort; Zeiten: auftrag.log, Abschnitt „Modell bauen"',
        )

    @classmethod
    def fotoprojektion(cls):
        wurzel = K(
            cls.F,
            'Ist die Haut schon projiziert, und ist kein Stück gewünscht?',
            'Haut einmal je Körper aus den Fotos, Haarzonen messen, Stücke auf Wunsch (m.kleid_fototextur).',
            ('Koerperfotoprojektion', 'Kleidfotoprojektion', 'Haarzonen'),
        ).mit(
            K(cls.E, 'Übersprungen', '', zeit=W.FOTOPROJEKTION_NICHT, kante='ja', vorgabe=True),
            K(
                cls.E,
                'Stück projizieren',
                'Kennfarben in 512 × 768, Farbe je Texel unter der Teilmaske.',
                zeit=W.FOTOPROJEKTION_STUECK,
                kante='ein Stück',
            ),
            K(cls.OFFEN, 'Haut erstmals projizieren', 'Einmal je Körper.', zeit=W.KEINE, kante='Haut fehlt'),
        )
        return Workflowbaum(
            'fotoprojektion',
            'Fotoprojektion',
            'Wird projiziert oder übersprungen?',
            wurzel,
            'Begutachtungswerkzeug.fototextur; Zeiten: auftrag.log, Abschnitt „Fotoprojektion"',
        )

    @classmethod
    def renderer(cls):
        wurzel = K(
            cls.F,
            'Welcher Renderer?',
            'Einstellungen → 2D3D Kleider (kleider2d3d_renderer). Gilt für die Runden-Bilder, die '
            'Kennbilder, den Kopf der Gesichtsmaße, die Fotoprojektion und den Film; eine laufende Runde übernimmt die Wahl ab '
            'der nächsten. Noten zweier Renderer sind nicht vergleichbar.',
            ('Renderwahl', 'Genesishaarrender'),
        ).mit(
            K(
                cls.T,
                'Mitsuba 3',
                'Pfadverfolgung auf der Grafikkarte wie Cycles, Strähnen als Kurven. Traf die Fotos besser: '
                'Abweichung 1,725 gegen 1,820. Fehlt Mitsuba oder CUDA: Rückfall auf pyrender, Warnung im Log.',
                ('Mitsubaszene',),
                zeit=W.RENDER_MITSUBA,
                kante='mitsuba (Vorgabe)',
                vorgabe=True,
            ),
            K(
                cls.T,
                'pyrender (OpenGL)',
                'Der schnelle Weg; Stranghaar bleibt unsichtbar.',
                ('Genesishaarrender',),
                zeit=W.RENDER_PYRENDER,
                kante='pyrender',
            ),
        )
        return Workflowbaum(
            'renderer',
            'Renderer',
            'Mitsuba oder pyrender?',
            wurzel,
            'Renderwahl.WAHLEN, Genesishaarrender; Zeit: Hilfetext der Einstellung (eine Runde, vor den '
            'Beschleunigungen vom 02.10.2026)',
        )

    @classmethod
    def auswahl(cls):
        probe = K(
            cls.F,
            'Probe schon 3 Runden alt?',
            'Rundenauswahl.PROBE_RUNDEN.',
            ('Rundenauswahl',),
            kante='ja',
        ).mit(
            K(cls.E, 'probe — weiterrechnen', '', kante='nein', zeit=W.RUNDE_ALLE),
            K(
                cls.F,
                'Pflichtzeile in der Probe?',
                'Fotostücke aus dem Netz, die erkannte Uhr, der Bart.',
                kante='ja',
            ).mit(
                K(cls.E, 'besser', 'Belegt: die Probe gilt, nicht die Note.', kante='ja'),
                K(
                    cls.E,
                    'probe_verworfen',
                    'Die Zeilen der Probe werden für diese Lage gesperrt.',
                    kante='nein',
                ),
            ),
        )
        umbau = K(
            cls.F,
            'Baut das Rezept um?',
            'Stück an/aus, Frisur, umfärben, Fototextur, Drapieren, Hülle, Decal, Falten, '
            'Haltung (Rundenauswahl.STRUKTUR).',
            ('Rundenauswahl',),
            kante='nein',
        ).mit(
            K(
                cls.E,
                'probe beginnt',
                'Bis zu 3 Runden von der neuen Lage aus: ein schwarzes Shirt ist erst nach dem Umfärben '
                'besser als keins.',
                kante='ja',
            ),
            K(
                cls.E,
                'verworfen',
                'Zurück zur besten Runde; die Zeilen sind für diese Lage gesperrt (Farbzeilen in Gesellschaft '
                'nicht).',
                kante='nein',
            ),
        )
        wurzel = K(
            cls.F,
            'Besser als die beste Runde?',
            'Gesamtnote kleiner als die beste − 0,002 (Toleranz) — oder eine Pflichtzeile '
            '— oder ein reiner Farbschritt, der nicht schlechter ist (+ 0,0005 Rauschen).',
            ('Rundenauswahl', 'Gesamtnote', 'Begutachtungsstand'),
        ).mit(
            K(
                cls.E,
                'besser',
                'Neue beste Runde; von ihr geht die nächste aus (kreislauf.modell, Export, Film).',
                kante='ja',
            ),
            K(
                cls.F,
                'Läuft gerade eine Probe?',
                'Ein Umbau darf bis zu 3 Runden weiterlaufen, bevor er gewertet wird (Rundenauswahl.probe).',
                ('Rundenauswahl',),
                kante='nein',
            ).mit(probe, umbau),
        )
        return Workflowbaum(
            'auswahl',
            'Rundenauswahl: welche Runde bleibt?',
            'Übernehmen, Probe oder verwerfen?',
            wurzel,
            'Rundenauswahl.nach_runde; reine Logik über Rundennummern und Noten, gehört zum Abschnitt „ablegen"',
        )
