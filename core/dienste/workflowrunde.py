# -*- coding: utf-8 -*-
"""Workflowrunde — die Entscheidungsbäume des Schritts „iterationen" von „2D3D Kleider": wer die Runden treibt, wer das Rezept
schreibt und wie die Automatik entscheidet (Hilfe → Architektur → 2D3D, 02.10.2026).

Bedingungen und Schwellen stehen so im Code: `Iterationsoptionen` (Modus, Prüf-KI), `Begutachtungsrunde.ausfuehren` und
`_automatisch` (Stufe, leeres Rezept, Ende), `Aufloesungsstufe.faellig/naechste`, `Begutachtungskritik.faellig`. Was die Runde
innen tut (Bauen, Rendern, Auswahl, Blender), baut `Workflowrundebau`.
"""

from .workflowbaum import Workflowbaum
from .workflowknoten import Workflowknoten as K
from .workflowzeiten import Workflowzeiten as W

__all__ = ['Workflowrunde']


class Workflowrunde:
    F, T, E, OFFEN = K.FRAGE, K.TAT, K.ENDE, K.OFFEN

    @classmethod
    def baeume(cls):
        return [cls.modus(), cls.rezeptweg(), cls.automatik()]

    @classmethod
    def modus(cls):
        begutachtung = K(
            cls.F,
            'Rezept von Hand oder Automatik?',
            'POST /api/engine2d3dkleider/<id>/begutachtung/ mit {aufrufe, kommentar} '
            'oder {automatisch: true, runden: N}.',
            ('Engine2d3dKleiderbegutachtungsendpunkte', 'Begutachtungsrunde'),
            kante='begutachtung (Vorgabe)',
            vorgabe=True,
        ).mit(
            K(
                cls.E,
                'Eine Runde, dann „Wartet auf Begutachtung"',
                'Der Server prüft das Rezept (G9rezept.pruefen), bevor er '
                'rechnet. Fable sieht die Vergleichstafel an und schreibt das nächste.',
                ('G9rezept',),
                zeit=W.LAUF_EINE_RUNDE,
                kante='Rezept von Hand',
                vorgabe=True,
            ),
            K(
                cls.E,
                'N Runden in einem Lauf (höchstens 50), dann „Fertig"',
                'Rezept aus IterationModell; die erste Runde '
                'rechnet kalt, die weiteren warm. Keine Prüfung durch Fable.',
                ('IterationModell',),
                zeit=W.RUNDE_ALLE,
                kante='automatisch: true',
            ),
        )
        wurzel = K(
            cls.F,
            'Wer treibt die Iterationen?',
            'Option iterationen.modus (Vorgabe begutachtung). Engine2d3dKleiderlauf ruft '
            'Iterationskreislauf; der verzweigt.',
            ('Iterationskreislauf', 'Iterationsoptionen'),
        ).mit(
            begutachtung,
            K(
                cls.OFFEN,
                'Die frühere Optimierer-Schleife',
                'Kandidaten je Runde (Vorgabe 4, 1–8 Prozesse parallel) und Prüf-KI '
                'über die Haarparameter. In keinem der 8 Aufträge gewählt.',
                ('Iterationsoptimierer', 'Iterationswahl', 'Iterationskritik'),
                zeit=W.KEINE,
                kante='automatisch',
            ),
        )
        return Workflowbaum(
            'modus',
            'Wer treibt die Iterationen?',
            'Begutachtung oder die alte Schleife — und dann?',
            wurzel,
            'Iterationsoptionen.KATALOG (modus), Iterationskreislauf, Begutachtungsrunde.ausfuehren; '
            'Zeiten: ergebnis.iterationen[].sekunden und auftrag.log',
        )

    @classmethod
    def rezeptweg(cls):
        pruefki = K(
            cls.F,
            'Option iterationen.pruefki?',
            'Vorgabe „aus" (Edgar, 01.10.2026: „keine Prüfung über lokale KI"). '
            'Die Automatik liest nur Messwerte: IterationModell schreibt die Zeilen nach festen Regeln.',
            ('Iterationsoptionen',),
            kante='Automatik (Regeln)',
        ).mit(
            K(
                cls.E,
                'Rezept der Automatik allein',
                'Feinstellen von Farben und Längen; das Bild sieht niemand an.',
                ('IterationModell', 'IterationKleider', 'IterationTextur', 'IterationHaare'),
                kante='aus (Vorgabe)',
                vorgabe=True,
                zeit=W.REZEPT,
            ),
            K(
                cls.F,
                'Fällig? alle 5 Runden oder 3 Runden ohne Besserung',
                'iterationen.pruefki_alle und pruefki_stillstand.',
                ('Begutachtungskritik',),
                kante='Ollama-Modell, z. B. qwen3.8:27b (Q4_K_M)',
            ).mit(
                K(cls.E, 'nur die Automatik', '', kante='nein', zeit=W.REZEPT),
                K(
                    cls.T,
                    'Bildmodell bekommt die Vergleichstafel',
                    'Antwort als JSON: Urteil, Ähnlichkeit 1–10, höchstens 8 '
                    'Rezeptzeilen. Jede Zeile wird einzeln geprüft und HINTER das Rezept der Automatik gehängt; „fertig" bei '
                    'Ähnlichkeit ≥ 8 beendet den Lauf.',
                    ('Begutachtungskritik', 'Begutachtungsprompt', 'Ollamamodelle'),
                    kante='ja',
                    zeit=W.PRUEFKI,
                ),
            ),
        )
        wurzel = K(
            cls.F,
            'Wer schreibt das Rezept der nächsten Runde?',
            'Nach jeder Runde. Ein Rezept ist Text, eine Zeile je '
            'Aufruf m.xxx(…) an ModellMitKleidern, geprüft über den Syntaxbaum (kein exec).',
            ('G9rezept', 'ModellMitKleidern'),
        ).mit(
            K(
                cls.T,
                'Fable sieht die Vergleichstafel an',
                'Verbessert die Klassen, die den Fehler erzeugen, oder schreibt ein '
                'Rezept und startet genau eine Runde — die Vorgabe (Edgar, 02.10.2026).',
                ('Engine2d3dKleiderbegutachtungsendpunkte',),
                kante='Fable (Vorgabe)',
                vorgabe=True,
                zeit=W.LAUF_EINE_RUNDE,
            ),
            pruefki,
        )
        return Workflowbaum(
            'rezeptweg',
            'Wer schreibt das Rezept?',
            'Fable, die Regeln oder eine Prüf-KI?',
            wurzel,
            'Architektur2d3d.WEGE, Begutachtungsrunde._automatisch, Begutachtungskritik.faellig; '
            'Prüf-KI-Zeit: Optionstext, nicht gemessen',
        )

    @classmethod
    def automatik(cls):
        stufe_hoch = K(
            cls.E,
            'Messrunde statt Ende',
            'Kein Rezept: die beste Runde wird in doppelter Auflösung neu benotet '
            'und ist die neue Bezugsnote.',
            ('Aufloesungsstufe',),
            zeit=W.KEINE,
            kante='ja',
        )
        ende = K(
            cls.E,
            'Lauf endet „Fertig · beste Runde N, Note x"',
            'Begutachtungskritik.beenden.',
            ('Begutachtungskritik',),
            zeit=W.KEINE,
            kante='nein',
        )
        leer = K(
            cls.F,
            'Gibt es eine höhere Auflösungsstufe?',
            'Bis zur Auflösung der Figur im Foto (…20.10.04: 2485 px). '
            'Auch ein „fertig" der Prüf-KI führt erst dorthin.',
            ('Aufloesungsstufe',),
            kante='ja',
        ).mit(stufe_hoch, ende)
        rezept = K(
            cls.T,
            'Rezept der Automatik schreiben, gesperrte Zeilen streichen',
            'IterationModell liest den Befund der '
            'letzten Runde; Zeilen, die aus dieser Lage schon verworfen sind, entfallen. Die Prüf-KI hängt, wenn fällig, '
            'ihre Zeilen an (Baum „Wer schreibt das Rezept?").',
            ('IterationModell', 'Begutachtungsstand'),
            kante='nein',
            zeit=W.REZEPT,
        ).mit(
            K(cls.F, 'Ist das Rezept leer?', '', ('Begutachtungsrunde',)).mit(
                leer, K(cls.E, 'Runde mit diesem Rezept', '', kante='nein', zeit=W.RUNDE_ALLE)
            )
        )
        wurzel = K(
            cls.F,
            'Läuft gerade eine Probe?',
            'kreislauf.weiter — ein Umbau darf bis zu 3 Runden weiterlaufen.',
            ('Begutachtungsrunde', 'Rundenauswahl'),
        ).mit(
            K(
                cls.E,
                'Die Runde geht von der Probe aus',
                'Kein Stufenwechsel während einer Probe.',
                zeit=W.RUNDE_ALLE,
                kante='ja',
            ),
            K(
                cls.F,
                'Steht die Stufe still? 3 Runden ohne „besser"',
                'iterationen.stufe_stillstand; Start 128 px Breite, jede Stufe × 2.',
                ('Aufloesungsstufe',),
                kante='nein',
            ).mit(
                K(
                    cls.E,
                    'Messrunde in der nächsten Stufe',
                    'Wenn es eine höhere gibt; sonst weiter wie bei „nein".',
                    ('Aufloesungsstufe',),
                    zeit=W.KEINE,
                    kante='ja',
                ),
                rezept,
            ),
        )
        return Workflowbaum(
            'automatik',
            'Automatische Runde: was entscheidet?',
            'Probe, Stufenwechsel, Ende — in welcher Reihenfolge?',
            wurzel,
            'Begutachtungsrunde.ausfuehren, Aufloesungsstufe.faellig/naechste, Begutachtungsrunde._automatisch',
        )
