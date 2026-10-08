# -*- coding: utf-8 -*-
"""Workflowrundebau — die Entscheidungsbäume im Inneren einer Runde von „2D3D Kleider": Kleidung (woher ein Stück kommt, wie es sitzt: `Workflowkleidung`),
Drapieren (`Workflowdrapieren`), Haar-Knoten (Blender), Bauen, Fotoprojektion, Renderer, Rundenauswahl; Haar-Dynamik: `Workflowhaardynamik`.

Edgar: „allen Optionen (z. B. Blender)". Blender kommt in der Pipeline an genau zwei Stellen vor, beide nur über den einen
Arbeiter `Engine2d3dKleiderblender` und nur per Rezeptzeile: `m.kleid_drapieren(…, motor='blender')`, `m.haar_knoten(…)`. Der Stoffsolver
(Blenders Rechnung auf der GPU) ist ein weiterer Weg, nur per Rezept: `motor='stoffsolver'`, `m.haar_dynamik(…)`. Beide sind Ausnahmen; der Standard eines
Laufs ist: kein Drapieren (06.10.2026, Baum `Workflowdrapieren`).
"""

from .workflowbaum import Workflowbaum
from .workflowdrapieren import Workflowdrapieren
from .workflowhaardynamik import Workflowhaardynamik
from .workflowkleidung import Workflowkleidung
from .workflowknoten import Workflowknoten as K
from .workflowzeiten import Workflowzeiten as W

__all__ = ['Workflowrundebau']


class Workflowrundebau:
    F, T, E, OFFEN = K.FRAGE, K.TAT, K.ENDE, K.OFFEN

    @classmethod
    def baeume(cls):
        return [
            *Workflowkleidung.baeume(),
            Workflowdrapieren.baum(),
            cls.haarknoten(),
            Workflowhaardynamik.baum(),
            cls.bauen(),
            cls.fotoprojektion(),
            cls.renderer(),
            cls.auswahl(),
        ]

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
