# -*- coding: utf-8 -*-
"""Workflowlauf — die Entscheidungsbäume der acht Schritte eines Auftrags „2D3D Kleider" (Hilfe → Architektur → 2D3D, 02.10.2026).

Edgar: „den Workflow der 2D3D mit allen Klassen und allen Optionen (z. B. Blender)" — dieser Teil: wo ein Lauf beginnt, woher
Netz und Körper kommen, was nach den Iterationen folgt. Jede Verzweigung ist eine Option, die es im Code gibt
(`Engine2d3dKleideroptionen`, `Meshoptionen`, `Engine2d3dKleiderkoerperoptionen`, `Engine2d3dKleiderfilmoptionen`); die Kinder einer Frage sind
ihre Werte, am Blatt steht die gemessene Zeit (`Workflowzeiten`) oder „nicht gemessen". Die Bäume der einzelnen Runde baut
`Workflowrunde`.
"""

from .workflowbaum import Workflowbaum
from .workflowknoten import Workflowknoten as K
from .workflowzeiten import Workflowzeiten as W

__all__ = ['Workflowlauf']


class Workflowlauf:
    F, T, E, OFFEN = K.FRAGE, K.TAT, K.ENDE, K.OFFEN

    @classmethod
    def baeume(cls):
        return [cls.start(), cls.netz(), cls.textur(), cls.koerper(), cls.ende()]

    @classmethod
    def start(cls):
        wurzel = K(
            cls.F,
            'Wo beginnt der Lauf?',
            'POST /api/engine2d3dkleider/<id>/starten/ mit {ab, bis, optionen}; der Lauf rechnet in '
            'einem eigenen Prozess (manage.py engine2d3dkleider_fahren), den ein Neustart des Servers nicht mitreißt.',
            ('Engine2d3dKleiderarbeiter', 'Engine2d3dKleiderlauf'),
        ).mit(
            K(
                cls.T,
                'ab = vorbereitung („Neu berechnen")',
                'Alle acht Schritte: vorbereitung → netz → koerper → grundfigur → iterationen → export → '
                'film → speichern. Vorher werden die Dauern früherer Läufe aus dem Ergebnis gelöscht.',
                ('Engine2d3dKleiderlauf',),
                kante='ab fehlt oder vorbereitung',
                vorgabe=True,
            ).mit(
                K(
                    cls.E,
                    'Aufbau je Auftrag',
                    'netz + koerper + grundfigur, einmal je Auftrag (Auftrag …20.10.04).',
                    zeit=W.AUFBAU,
                )
            ),
            K(
                cls.T,
                'ab = iterationen, bis = iterationen',
                '„Weiter iterieren", „Runde rechnen", „Automatisch". Voraussetzung: '
                'arbeit/grundkoerper.glb — sonst bricht der Lauf mit „Keine Grundfigur" ab.',
                ('Engine2d3dKleiderlauf',),
                kante='ab = bis = iterationen',
            ).mit(
                K(
                    cls.E,
                    'ein Lauf mit einer Runde',
                    'Prozess und Teilevorrat sind dabei kalt.',
                    zeit=W.LAUF_EINE_RUNDE,
                )
            ),
            K(
                cls.T,
                'ab = export, film oder speichern',
                'Ab diesem Schritt bis zum Ende (oder bis `bis`); derselbe Grundfigur-Test.',
                ('Engine2d3dKleiderlauf',),
                kante='ab = ein späterer Schritt',
            ).mit(K(cls.E, 'Nachlauf', 'Export, Film und Speichern.', zeit=W.EXPORT)),
        )
        return Workflowbaum(
            'start',
            'Wo beginnt ein Lauf?',
            'Welche der acht Schritte rechnet ein Druck auf den Knopf?',
            wurzel,
            'Engine2d3dKleiderlauf.ausfuehren(ab, bis), Engine2d3dKleiderlauf.SCHRITTE',
        )

    @classmethod
    def netz(cls):
        # Das Formmodell ist hier immer TRELLIS.2 (Edgar, 02.10.2026: „ich brauche NUR trellis in dem Workflow, kein
        # Hunyan") — `Engine2d3dKleidernurtrellis` streicht Hunyuan3D aus dem Katalog dieses Bereichs.
        wurzel = K(
            cls.F,
            'Auflösung?',
            'mesh.aufloesung (Vorgabe hoch). Das Formmodell ist immer TRELLIS.2: 512³, 1024³, 1536³ Voxel. Eine hohe '
            'Auflösung will auch Textur 4096 und viele Flächen. Der Runner _run_mesh.py (VideoToBVH, eigene venv) '
            'rechnet; Engine2d3dKleidernetz startet ihn, liest seine Zeilen und meldet den Fortschritt.',
            ('Engine2d3dKleidernetz', 'Engine2d3dKleideroptionen'),
        ).mit(
            K(
                cls.E,
                'Netz',
                'Auftrag …21.02.25, Textur fotos_ki, 500.000 Flächen.',
                zeit=W.NETZ_SCHNELL,
                kante='schnell (512³)',
            ),
            K(cls.OFFEN, 'nicht gemessen', 'Kein Auftrag mit 1024³.', zeit=W.KEINE, kante='mittel (1024³)'),
            K(
                cls.E,
                'Netz',
                'Je nach Textur und Flächenzahl (Baum „Textur").',
                zeit=W.NETZ,
                kante='hoch (1536³, Vorgabe)',
                vorgabe=True,
            ),
        )
        return Workflowbaum(
            'netz',
            'Netz aus den Fotos (Schritt netz)',
            'In welcher Auflösung rechnet TRELLIS.2?',
            wurzel,
            'Engine2d3dKleidermeshoptionen.KATALOG (aufloesung), Engine2d3dKleidernurtrellis.ERLAUBT, Zeiten: ergebnis.dauer.netz',
        )

    @classmethod
    def textur(cls):
        wurzel = K(
            cls.F,
            'Textur des Netzes?',
            'netz.textur (Vorgabe fotos_ki; die Aufträge …19.21.30 und …20.10.04 nahmen ki). '
            '„fotos_ki" legte bei „schnell" Fotoränder auf Arme und Beine, „ki" war sauber (30.09.2026).',
            ('Meshoptionen',),
        ).mit(
            K(
                cls.E,
                'Fotos aufprojiziert, Lücken aus der Textur von TRELLIS.2',
                '',
                zeit=W.NETZ_FOTOSKI,
                kante='fotos_ki (Vorgabe)',
                vorgabe=True,
            ),
            K(cls.E, 'Nur Fotos', 'Lücken aufgefüllt.', zeit=W.NETZ_HOCH_FOTOS, kante='fotos'),
            K(cls.E, 'Textur von TRELLIS.2', 'PBR.', zeit=W.NETZ_HOCH_KI, kante='ki'),
            K(cls.OFFEN, 'grau', 'Keine Textur.', zeit=W.KEINE, kante='keine'),
        )
        return Workflowbaum(
            'textur',
            'Textur des Netzes',
            'Woher kommen die Farben des Netzes?',
            wurzel,
            'Engine2d3dKleidernurtrellis.ERLAUBT, Meshoptionen.KATALOG (textur); die Zeit ist die des ganzen Schritts netz, '
            'nicht der Textur allein',
        )

    @classmethod
    def koerper(cls):
        uebernehmen = K(
            cls.F,
            'Kennung eines Auftrags „Mesh to 3D" gesetzt?',
            'koerper.auftrag',
            ('Engine2d3dKleiderkoerperoptionen',),
            kante='uebernehmen (Vorgabe)',
            vorgabe=True,
        ).mit(
            K(
                cls.E,
                'Fit übernehmen',
                'Reglerstellung, Eigenmorph, Kacheln und das Netz des Fits (3D-Bezug der Iterationen) '
                'aus dem fremden Auftrag.',
                ('Engine2d3dKleiderkoerper',),
                zeit=W.KOERPER_UEBERNEHMEN,
                kante='ja',
            ),
            K(
                cls.E,
                'wird zu „rechnen"',
                'Ohne Kennung scheitert „übernehmen" immer; Engine2d3dKleiderkoerperoptionen.pruefen setzt '
                'rechnen (01.10.2026).',
                ('Engine2d3dKleiderkoerperoptionen',),
                zeit=W.KOERPER_RECHNEN,
                kante='nein',
            ),
        )
        rechnen = K(
            cls.T,
            'Kette von „Mesh to 3D" auf dem Netz dieses Auftrags',
            'Dieselben Schrittklassen, unverändert; Frühstopp bei Körper und Gesicht seit 02.10.2026.',
            ('Engine2d3dKleiderkoerperlauf',),
            zeit=W.KOERPER_RECHNEN,
            teile=W.koerper_teile(),
            kante='rechnen',
        )
        wurzel = K(
            cls.F,
            'Woher kommt die Figur?',
            'koerper.quelle. Danach baut Engine2d3dKleidergrundfigur aus der Stellung die Grundfigur mit Rig.',
            ('Engine2d3dKleiderkoerper', 'Engine2d3dKleidergrundfigur', 'Engine2d3dKleideroptionen'),
        ).mit(uebernehmen, rechnen)
        return Workflowbaum(
            'koerper',
            'Körper (Schritt koerper)',
            'Übernehmen oder rechnen?',
            wurzel,
            'Engine2d3dKleiderkoerper.ausfuehren, Engine2d3dKleiderkoerperoptionen.pruefen; Teile: ergebnis.dauer_koerper (…20.10.04)',
        )

    @classmethod
    def ende(cls):
        film = K(
            cls.F,
            'Option film.bvh?',
            'Vorgabe: der Tanz der Bibliothek (Daz/Dance.bvh), wenn die Datei da ist.',
            ('Engine2d3dKleiderfilm', 'Engine2d3dKleiderfilmoptionen'),
        ).mit(
            K(
                cls.E,
                'Film übersprungen',
                'ergebnis.film = „Keine BVH-Datei gewählt"; die Figur ist trotzdem fertig.',
                zeit=W.KEINE,
                kante='leer',
            ),
            K(
                cls.E,
                'Fehler',
                'RuntimeError „BVH-Datei nicht gefunden", wenn der Pfad keine .bvh-Datei ist.',
                zeit=W.KEINE,
                kante='Pfad ohne Datei',
            ),
            K(
                cls.T,
                'Retarget auf Genesis 9, dann rendert die Engine den Film',
                'Bewegung als film_bewegung.json — die Bühne spielt sie live ab; Video film_video.mp4.',
                ('Engine2d3dKleiderbewegung', 'Genesisengine2d3dkleider'),
                zeit=W.FILM,
                kante='Datei',
                vorgabe=True,
            ),
        )
        wurzel = K(
            cls.T,
            'Nach den Iterationen',
            'Die drei letzten Schritte eines Laufs.',
            ('Engine2d3dKleiderexport', 'Engine2d3dKleiderfilm', 'Engine2d3dKleiderspeichern'),
            teile=[
                ('export — Figur als GLB mit Rig', W.EXPORT),
                ('film — nur mit BVH-Datei', W.FILM),
                ('speichern — Ablage output/Export/Engine2d3dKleider', W.SPEICHERN),
            ],
        ).mit(film)
        return Workflowbaum(
            'ende',
            'Export, Film, Speichern',
            'Wird ein Film gerechnet?',
            wurzel,
            'Engine2d3dKleiderlauf.SCHRITTE, Engine2d3dKleiderfilm.ausfuehren; Zeiten: ergebnis.dauer',
        )
