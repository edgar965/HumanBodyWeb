# -*- coding: utf-8 -*-
"""Workflowkleidung — zwei Entscheidungsbäume zur Kleidung in einer Runde von „2D3D Kleider": woher ein Stück kommt (Genesis-Bibliothek, Fotostück aus dem
Netz mit Sapiens-Etiketten, GarmentCode) und wie es sitzt (Bau, Kollision, Haltung der Fotos, Haltungsabstand) (Hilfe → Architektur → 2D3D, 06.10.2026).

Edgar, 06.10.2026: „Mach mehr Infos dazu, wo Sapiens, die Genesis-Dinger, GarmentCode und deine neue Drapierung da hineinkommt." Alles hier ist aus dem Code und
den Aufträgen gelesen: `Kleiderwahl`, `Standvorabkleider`, `Fotostuecke`, `G9stoff`, `G9haltungshaut`, `G9haltungsabstand`, und die Zählung der Quellen in den Rezepten
(`ergebnis.iterationen[].aufrufe` aller 11 Aufträge mit Runden, 06.10.2026, `ProjektTemp/_wegwerf/edgar/kleid_quellen_zaehlen.py`).
"""

from .workflowbaum import Workflowbaum
from .workflowknoten import Workflowknoten as K

__all__ = ['Workflowkleidung']


class Workflowkleidung:
    F, T, E = K.FRAGE, K.TAT, K.ENDE

    @classmethod
    def baeume(cls):
        return [cls.kleidung(), cls.sitz()]

    @classmethod
    def kleidung(cls):
        sapiens = K(
            cls.T,
            'Sapiens zerlegt die Fotos — die Etiketten gehen auf die Netzflächen',
            'Sapiens-1B (Schritt „segmentierung") etikettiert die vorbereiteten Fotos: Oberteil, Hose, Socken/Schuhe, Zubehör, Haut. Die Etiketten gehen mit der Fotoprojektion und '
            'der Verdeckung auf die Flächen des Netzes (verdeckte Flächen stimmen nicht ab; ungesehene übernehmen von den sichtbaren Nachbarn); der Schritt „kleidung" der '
            'Körper-Kette nimmt sie für die Kleidungsmaske. Gemessen am Auftrag …20.10.04 (04.10.2026): 23–30 s, die Hose von 0 auf 2.284 cm². In 8 der 11 Aufträge '
            'mit Runden gesetzt, darunter alle Sapiens-Aufträge.',
            ('Engine2d3dKleidersegmentierung', 'Engine2d3dKleidersegmentierungsoptionen'),
            kante='an (alle Sapiens-Aufträge)',
        )
        farbe_lage = K(
            cls.T,
            'Maske nach Farbe und Lage',
            'Die Kleidungsmaske des Schritts „kleidung" aus der Farbe der Netzflächen und ihrer Lage am Körper, ohne Sapiens. Läuft in test4, in „Randy" und dessen Kopie (3 von 11).',
            ('Engine2d3dKleiderkoerper',),
            kante='aus (Vorgabe der Option)',
            vorgabe=True,
        )
        foto = K(
            cls.F,
            'Wer sagt, welche Netzflächen zum Stück gehören?',
            'Hose und Socken (und das Oberteil, wenn koerper.oberteil = foto): `Fotostuecke` schneidet sie aus dem Netz der Fotos — Form UND Textur aus den Fotos. Der Schritt '
            '„kleidung" teilt das Netz (arbeit/kleidung_maske.npz, `stueck` je Fläche), `Kleidungsentposen` rechnet es in die Ruhelage zurück, daraus entsteht ein eigenes '
            'Genesis-Stück eigen_foto_<TTHHMMSS der Kennung>_<name>_f<Fassung> (Gewichte der 3 nächsten Hautpunkte; das Stück trägt die Kennung des Auftrags, der es BAUT — eine Kopie '
            'nimmt die Stücke ihrer Quelle weiter). Fotostücke gelten als starr (G9stoff.STARR) — Baum „Sitz".',
            ('Fotostuecke', 'Kleiderwahl'),
            kante='Hose und Socken: Fotostück',
            vorgabe=True,
        ).mit(sapiens, farbe_lage)
        hemd = K(
            cls.T,
            'Genesis-Hemd g9_base_shirt aus der Bibliothek',
            'Mit Saum, Ausschnitt und Ärmelabschlüssen; es bekommt die mittlere Farbe des Fotostücks (die Farbe des Hemds im Foto). Option koerper.oberteil = bibliothek (Vorgabe); in '
            'den Sapiens-Aufträgen nicht gesetzt, also die Vorgabe. Warum nicht das Fotostück: Edgar, 04.10.2026, zum dritten Mal: „T-shirt verfranst am Anfang und am Ende, zu weit '
            'abstehend vom Körper, kein Saum. Nimmst du ein Genesis T-Shirt oder GC? die sind doch viel besser". GarmentCode-Hemden sind Crop-Tops (engine2d3dkleider-kleiderstuecke.md).',
            ('Kleiderwahl', 'Engine2d3dKleiderkoerperoptionen', 'Standvorabkleider'),
            kante='Oberteil: bibliothek',
            vorgabe=True,
        )
        garderobe = K(
            cls.T,
            'Genesis-Stück der Garderobe (m.kleid_nur)',
            'Ohne Fotostücke zieht Kleiderwahl.soll nach den Farben der Körperbänder an (Haut ja oder nein): Shirt g9_base_shirt, Shorts g9_base_shorts, Jeans angie_jeans, kurze Socken '
            'gc_crudelowsocks (ein GarmentCode-Stück der Bibliothek). In den Aufträgen steht außer dem Hemd kein Bibliotheksstück im Rezept (Randy: 1 Nennung).',
            ('Kleiderwahl',),
            kante='Stück der Bibliothek, von Hand oder ohne Fotostücke',
            ausnahme=True,
        )
        garmentcode = K(
            cls.T,
            'GarmentCode-Schnitt (m.kleid_schnitt) — Stücke gc_…',
            '„Ein NEUES Stück aus einem GarmentCode-Schnitt: vorlage oberteil|hose|shorts|rock|kleid|anzug|unterwaesche|schuh, form, regler, farbe — gebaut, drapiert, als Genesis-Stück '
            'abgelegt (≈ 25 s) und mit anteil angezogen" (ModellFormMixin.kleid_schnitt). Das Drapieren dort ist GarmentCodes eigenes (Warp-Fork, python10_Garment), nicht der Baum „Drapieren". '
            'Gemessen: 31 Zeilen m.kleid_schnitt in „Randy" (und dessen Kopie), in keinem Sapiens-Auftrag. Neu seit 06.10.2026 (Parallelsitzung): `G9gcausfoto` macht aus einem Foto-Design '
            '(Design2GarmentCode, params.json) die Werte für ein GC-Oberteil; die Hose bleibt das Fotostück („die Foto-Kette liegt beim Unterteil in drei von vier Fällen falsch").',
            ('G9gceigenes', 'G9gcausfoto'),
            kante='GarmentCode-Schnitt, von Hand',
            ausnahme=True,
        )
        wurzel = K(
            cls.F,
            'Woher kommt ein Kleidungsstück?',
            'Das Rezept nennt die Stücke (m.kleid_nur(…)). Das Startrezept der Iteration 0 trägt in den Sapiens-Aufträgen: g9_base_shirt, eigen_foto_04111144_hose_f25, '
            'eigen_foto_04111144_socken_f25, eigen_uhr_l (gelesen im Rezept von „Edgar - Sapiens 4"; 04111144 = 04.10., 11:11:44, die Kennung des Auftrags, der die Stücke baute). Vor Runde 1 zeigt die Bühne dieselben Stücke (Standvorabkleider).',
            ('Standvorabkleider', 'Kleiderwahl'),
        ).mit(hemd, foto, garderobe, garmentcode)
        return Workflowbaum(
            'kleidung',
            'Kleidung: woher kommt ein Stück? (Genesis, Sapiens, GarmentCode)',
            'Bibliothek, Foto oder GarmentCode?',
            wurzel,
            'Kleiderwahl, Standvorabkleider, Fotostuecke, ModellFormMixin.kleid_schnitt; Zählung der Quellen in den Rezepten: ProjektTemp/_wegwerf/edgar/kleid_quellen_zaehlen.py (06.10.2026)',
        )

    @classmethod
    def sitz(cls):
        simuliert = K(
            cls.E,
            'dynamisch — wird in der Bewegung simuliert',
            'Das Stück bekommt `folger.dynamik` aus dem dForce-Modifikator seines Netzdokuments (G9stoff.entscheiden).',
            ('G9stoff',),
            kante='ja: dForce-Modifikator und p90 ≥ 5 cm',
        )
        gehaeutet = K(
            cls.E,
            'gehäutet, nicht simuliert',
            'Das Stück folgt den Knochen mit seinen Gewichten, in der Runde wie im Film. Im Log: „liegt eng an (p90 2,1 cm) — gehaeutet, nicht simuliert" '
            '(GC_Crudelowsocks_Shape, Lauf 14:37 am 06.10.2026).',
            ('G9stoff', 'G9haltungshaut'),
            kante='nein: eng (ENG_M 5 cm, ENG_ANTEIL 90 %) oder kein dForce',
            vorgabe=True,
        )
        weich = K(
            cls.F,
            'Hat das Stück einen dForce-Modifikator und liegt es weit?',
            'G9stoff.entscheiden: ein Stück der Garderobe ist dynamisch, wenn sein Netzdokument einen dForce-Simulationsmodifikator trägt UND das 90-%-Perzentil seines Abstands zur Haut '
            'mindestens ENG_M = 5 cm beträgt; ein enges Stück ist nie dynamisch.',
            ('G9stoff',),
            kante='nein: Bibliothek oder GarmentCode',
        ).mit(gehaeutet, simuliert)
        starr = K(
            cls.E,
            'Bleibt, wie gebaut',
            'Starre Stücke nehmen weder an der Simulation noch an der Passform noch an der Mischung teil (G9stoff.STARR: eigen_foto_*, Uhr, Hut, Brille, Gürtel, Ohrstecker, '
            'Armband, Manschette, Kette, Randy-Zubehör) und der Haltungsabstand fasst sie nicht an.',
            ('G9stoff', 'G9haltungsabstand'),
            kante='ja: Fotostück, Uhr, Hut …',
        )
        wurzel = K(
            cls.F,
            'Ist das Stück starr?',
            'Der Bau (Kleidermodellbau, immer in der A-Pose) bindet jedes Stück an die Figur und hält mit G9kollision mindestens 3 mm Abstand zur Haut (Hub über die 6 nächsten Punkte gemittelt, '
            'zwei Durchgänge). Für Render, Note, Befund und Fotoprojektion häutet G9haltungshaut danach Körper, Kleider und Haar mit ihren Gewichten in die Haltung der Fotos (lineare '
            'Hautmischung). Dort setzt die Neuerung vom 06.10.2026 an: G9haltungsabstand hebt nicht starre Kleidung wieder 3 mm über die gehäutete Haut — ein Punkt, der tiefer als 2 cm '
            'im Körper steckt, bleibt (gewollt oder falsch gemessen). Gemessen am Armloch von „Edgar - Sapiens", Seitenansicht: die Haut stand bis 1,3 mm VOR dem Hemd, 48 Pixel zu 1 mm — '
            'die orange Linie an jeder Ärmelecke, in Iteration 0 und 1 gleich: Geometrie, nicht Textur.',
            ('Kleidermodellbau', 'G9kollision', 'G9haltungshaut', 'G9haltungsabstand'),
        ).mit(starr, weich)
        return Workflowbaum(
            'sitz',
            'Sitz: wie liegt ein Stück an, und was geschieht in der Haltung der Fotos?',
            'Starr, gehäutet oder simuliert — und wer hebt es aus der Haut?',
            wurzel,
            'G9kollision.ABSTAND (0,003), G9haltungshaut, G9haltungsabstand.TIEFE_MAX (0,02), G9stoff.STARR/ENG_M/ENG_ANTEIL/entscheiden; Messung am Armloch: armloch_zpuffer2.py (06.10.2026)',
        )
