# -*- coding: utf-8 -*-
"""Stoffsolverumfang — was der Stoffsolver von Blenders Cloth, Haar und UV schon kann und was nicht (02.10.2026).

Edgar: „was fehlt am Solver?" und dann „implementiere alles, was fehlt". Die Tabelle auf der Seite Hilfe → Architektur → 2D3D
(Reiter „Workflow") stellt je Blender-Funktion die Klasse im Solver und den STAND dar. Der Stand ist ehrlich in vier Stufen:

    blender  gegen einen echten Blender-Lauf gemessen (`Stoffsolver/README.md`, Abschnitt „Messungen")
    quelle   nach Blenders Quelltext gebaut und gegen Handrechnung, Finite Differenzen und Host/Gerät getestet — KEIN Blender-Lauf
    eigen    Eigenbau, den es in Blender so nicht gibt (UV-Prüfung, Fotoprojektion)
    teil     teilweise gebaut, die Anmerkung nennt was
    nein     nicht gebaut

Die Klassen werden beim Aufruf im Code gesucht (`Architektur2d3dklassen.zeile`): Fehlt eine, steht „fehlt" in der Zeile, statt dass
die Behauptung stehen bleibt.
"""

from .architektur2d3dklassen import Architektur2d3dklassen

__all__ = ['Stoffsolverumfang']

S = 'Stoffsolver/'


class Stoffsolverumfang:
    STAENDE = {
        'blender': 'gegen Blender gemessen',
        'quelle': 'nach Quelltext gebaut und getestet, kein Blender-Lauf',
        'eigen': 'Eigenbau, nicht aus Blender',
        'teil': 'teilweise',
        'nein': 'nicht gebaut',
    }
    QUELLE = ('Stoffsolver/README.md (Messungen, Bausteine) und Stoffsolver/LUECKEN.md; Blender-Läufe nur für den Kern '
              '(Federn, Kollision, Druck, Haar ohne Kollision), alle Bausteine des Ausbaus vom 02.10.2026 sind nicht gegen Blender gelaufen')
    #: (Bereich, Blender-Funktion, [(Datei, Klasse)], Stand, Anmerkung)
    ZEILEN = [
        ('Kleid', 'Federn (Struktur, Scherung), Winkelbiegung, Dämpfung',
         [(S + 'federn.py', 'Federn'), (S + 'federkraefte.py', 'Federkraefte'), (S + 'winkelbiegung.py', 'Winkelbiegung')],
         'blender', 'Oberteil im Mittel 2 mm von Blenders Ergebnis; die Hose ist chaotisch, ein Ensemble trennt beide nicht.'),
        ('Kleid', 'Kollision Körper und Selbst (Dreieck gegen Dreieck), Reibung',
         [(S + 'kollisionsablauf.py', 'Kollisionsablauf')], 'blender', 'Impulse, Runden und Reibung wie `collision.cc`.'),
        ('Kleid', 'Implizites Verfahren (Baraff–Witkin, Blenders CG)',
         [(S + 'implizitesverfahren.py', 'ImplizitesVerfahren')], 'blender',
         'Ein Schritt gleicht Blender; der Rest ist die float32-Rundung.'),
        ('Kleid', 'Innendruck mit Volumenterm', [(S + 'aussenkraefte.py', 'Aussenkraefte')], 'blender',
         'Der Volumenterm gilt nur bei Ausgangsvolumen über 1e-6 m³ (geschlossenes Stück).'),
        ('Kleid', 'Vertexgruppen für Struktur, Scherung, Biegung, Innenfedern',
         [(S + 'federgewichte.py', 'Federgewichte'), (S + 'federsteifigkeit.py', 'Federsteifigkeit')], 'quelle',
         'Steifigkeit = Wert + Gewicht · |Maximum − Wert|.'),
        ('Kleid', 'Schrumpfen (shrink_min, shrink_max, Gruppe)', [(S + 'schrumpfen.py', 'Schrumpfen')], 'quelle',
         'Vor dem Lauf auf Host und GPU. Zeitabhängiges Schrumpfen: Host; auf der GPU nur von Hand (`federn_hochladen`).'),
        ('Kleid', 'Innenfedern (use_internal_springs)', [(S + 'innenfedern.py', 'Innenfedern')], 'quelle',
         'Zielpunkt wie im Quelltext (erste Ecke), Zufallsfolge nach `rand.cc` nachgebaut, nicht mit einer Blender-Ausgabe verglichen.'),
        ('Kleid', 'Nähte (use_sewing_springs)', [(S + 'naehte.py', 'Naehte')], 'quelle',
         'Lose Kanten als Zugfedern der Länge 0. Zum Rechenzeitpunkt trägt die Naht `tension`, nicht `max_tension` (Quelltext-Befund).'),
        ('Kleid', 'Anheften hart und weich (pin_stiffness), bewegte Pins',
         [(S + 'zielfedern.py', 'Zielfedern'), (S + 'pinbewegung.py', 'Pinbewegung')], 'quelle',
         'Gewicht⁴, ab 0,999 fest; Interpolation je Teilschritt wie `SIM_mass_spring.cc`, auf der GPU im Graph.'),
        ('Kleid', 'Wind und Kraftfelder', [(S + 'windkraft.py', 'Windkraft'), (S + 'kraftfeld.py', 'Kraftfeld')], 'teil',
         'Wind und Punktkraft. Wirbel, Magnet, Turbulenz, Luftwiderstand, Textur- und Fluid-Felder fehlen. Rauschen auf der GPU '
         'bitgleich nur, solange der Abfall überall größer 0 ist.'),
        ('Kleid', 'Hydrostatik, Druck-Vertexgruppe', [(S + 'hydrostatik.py', 'Hydrostatik'), (S + 'druckgruppe.py', 'Druckgruppe')],
         'quelle', 'Dreiecke mit einer Null-Ecke der Gruppe fallen aus Volumen und Druck.'),
        ('Kleid', 'time_scale', [(S + 'stoffmaterial.py', 'StoffMaterial')], 'quelle', 'Skaliert dt, nicht die Schrittzahl; 0 rechnet nichts.'),
        ('Körper', 'Mehrere Kollisionsobjekte', [(S + 'koerperantwort.py', 'Koerperantwort')], 'quelle',
         'Jeder Körper mit eigener Dicke, Reibung, Culling; die Impulse eines Durchgangs wirken zusammen.'),
        ('Körper', 'collision_quality, Impuls-Klammern, Gruppen „Object/Self Collisions"',
         [(S + 'kollisionseinstellungen.py', 'Kollisionseinstellungen')], 'quelle', 'Host und GPU lesen dieselben Einstellungen.'),
        ('Körper', 'Bewegter Körper', [(S + 'warpkoerpersatz.py', 'WarpKoerpersatz')], 'quelle',
         'Im CUDA-Graph. Tuch auf steigendem Quader: Gerät gegen Host 4,5e-7 m; ein seitlich fahrender Quader weicht bis 1,2 mm ab.'),
        ('Haar', 'Haar-Dynamik (Federn, Biegung, Wurzeln, Kopfkollision)', [(S + 'haarsimulation.py', 'Haarsimulation')], 'teil',
         'Ohne Kollision 0,006 mm von Blender; mit Kopfkollision 5–13 mm, die Ursache ist nicht geklärt (`Stoffsolver/README.md`).'),
        ('Haar', 'Haar-Kontinuum (Dichte, innere Reibung)', [(S + 'haarkontinuum.py', 'Haarkontinuum')], 'quelle',
         'Bei `dichte_ziel` 0 rechnet der Zielterm nach dem Quelltext mit NaN; ob Blenders Build das tut, ist nicht geprüft.'),
        ('Haar', 'bending_random', [(S + 'haarzufall.py', 'Haarzufall')], 'quelle', 'Zufallsfolge von `psys_frand`.'),
        ('Haar', 'Wind, weiches Halten, bewegte Kopfhaut',
         [(S + 'haarpin.py', 'Haarpin'), (S + 'haarkopf.py', 'Haarkopf')], 'quelle',
         'Wurzeln und Kopfkollision folgen einem bewegten Kopf, auf der GPU im Graph.'),
        ('Haar', 'Haare erzeugen und kämmen (Emitter, Comb)',
         [(S + 'haarverteilung.py', 'Haarverteilung'), (S + 'haarkamm.py', 'Haarkamm')], 'quelle',
         'Zufallsfolge, Jitter-Tabelle und Dreieckszuordnung bitgleich; nicht Strähne für Strähne wie Blender (Wurzelrahmen, Kamm im 3D-Raum).'),
        ('Haar', 'Kinder, Clump, Rauheit, Kink', [(S + 'kinderpfade.py', 'Kinderpfade')], 'quelle',
         'Interpolierte und einfache Kinder; Effektoren und Führungskurven auf den Pfaden fehlen.'),
        ('Haar', 'Anschluss an die Pipeline', [('HumanBodyWeb/core/dienste/haardynamik.py', 'Haardynamik')], 'quelle',
         'Rezeptzeile `m.haar_dynamik(sorte)`, nur von Hand, nie von der Automatik; Ergebnis ist ein Regler `<sorte>.eigen.dynamik_…`. '
         'Mindestabstand 2 mm: Hime Cut (Segmente von 2 mm) divergiert mit Blenders 15 mm Kontaktabstand; ob Blender das auch tut, ist nicht geprüft.'),
        ('UV und Textur', 'UV abwickeln (Smart UV Project, LSCM, ABF++)', [(S + 'uvabwicklung.py', 'Uvabwicklung')], 'quelle',
         'Nicht übernommen: Symmetrie-Pins, SLIM, die Streck-Minimierung.'),
        ('UV und Textur', 'Inseln packen', [(S + 'uvpacker.py', 'Uvpacker')], 'quelle', 'Alpaca und Boxpack; kein xatlas, kein optimal_pack.'),
        ('UV und Textur', 'UV prüfen (Überlappung, Dehnung, Rand)', [(S + 'uvpruefung.py', 'Uvpruefung')], 'eigen',
         'Gegenprobe der Abwicklung; Blender hat keine solche Prüfung.'),
        ('UV und Textur', 'Texturen backen (Farbe, Fotos)', [(S + 'texturbacker.py', 'Texturbacker')], 'eigen',
         'Lochkamera mit Verdeckung und Randauffüllung. Die Orthokamera der Pipeline ist nachgebildet, nicht erprobt.'),
        ('Nicht gebaut', 'Lineares und Polygon-Biegemodell, Cache/Bake, rest_shape_key', [], 'nein',
         'Blenders Vorgabe ist das Winkelmodell; die Pipeline füttert Dreiecke.'),
        ('Nicht gebaut', 'Szene: Modifier-Stapel, Keyframes, Materialien', [], 'nein',
         'Bewusst: Netz, UV und Textur bleiben am Genesis-Stück, der Solver liefert Verschiebungen je Punkt.'),
        ('Nicht gebaut', 'Körperanpassung (Shrinkwrap, Armature, Lattice, Sculpt)', [], 'nein',
         'Nicht im Solver, sondern in der Pipeline schon in Python (Genesis9: Ortsmorph, Hülle, Haltung).'),
    ]

    @classmethod
    def zeilen(cls):
        """Die Tabelle: je Zeile Bereich, Blender-Funktion, `klassen` ({klasse, anker, fehlt}), Stand-Kennung und -Text, Anmerkung."""
        aus = []
        for bereich, blender, klassen, stand, hinweis in cls.ZEILEN:
            gefunden = []
            for modul, klasse in klassen:
                z = Architektur2d3dklassen.zeile(modul, klasse)
                gefunden.append({'klasse': klasse, 'anker': 'k-' + klasse, 'fehlt': z['fehlt']})
            aus.append({'bereich': bereich, 'blender': blender, 'klassen': gefunden, 'stand': stand,
                        'stand_text': cls.STAENDE[stand], 'hinweis': hinweis})
        return aus

    @classmethod
    def zaehlung(cls):
        """[{stand, text, anzahl}] in der Reihenfolge der Stufen — gezählt aus den Zeilen, nicht geschrieben."""
        return [{'stand': s, 'text': t, 'anzahl': sum(1 for z in cls.ZEILEN if z[3] == s)} for s, t in cls.STAENDE.items()]
