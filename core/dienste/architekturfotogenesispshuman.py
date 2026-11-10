# -*- coding: utf-8 -*-
"""Architekturfotogenesispshuman — die Grafiken der Abschnitte „Was wir heute tun“, „PSHuman“ und „Mehrere Fotos“ auf Hilfe → Architektur → Foto-Genesis (07.11.2026).

Edgar: „Erkläre mir die pshuman pipeline. Passe die seite … an mit dem was wir jetzt tun, und füge die Beschreibung der pshuman ein“, „Wo siehst du eine Möglichkeit, die anzupassen für mehrere Bilder?“.
Derselbe Zeichner wie die Foto-Kette (`Architekturfotogenesiskette.svg`), nur mit eigenen Marken. Inhalt aus dem Code gelesen: `pshuman_port14/fremd/original/pshuman/` (`inference.py`, `reconstruct.py`,
`configs/remesh.yaml`, `inference-768-6view.yaml`), `meshgenesis/meshgenesis_rechenlauf`. Kästen mit `stand: offen` sind Vorschlag, nicht gebaut.
Die Grafik „PSHuman“ zeigt seit dem Umbau vom 07.11.2026 unsere Kette: Genesis statt SMPL-X, Haltung aus SAM 3D Body (`pshuman_port14/genesiskoerper.py`, `startgelenke.py`, `remesh_genesis.py`); was das Original dort tut, steht im Kasten als „Original:“.
"""

from .architekturfotogenesiskette import Architekturfotogenesiskette

__all__ = ['Architekturfotogenesispshuman']


class Architekturfotogenesispshuman(Architekturfotogenesiskette):
    MARKEN = {'Stable Diffusion': '#7a5a8c', 'SAM 3D Body': '#b85450', 'rembg': '#a06a00', 'Remeshing': '#4f74a8', 'Unique3D': '#5f8a45', 'UP2You': '#2f7f7a', 'MIA': '#8a5a3c', 'Sapiens2': '#9673a6',
              'SAM 3': '#a06a00', 'Genesis': '#777777'}

    @classmethod
    def heute(cls):
        kaesten = [
            {'titel': 'Fotos', 'skript': '3DObjects/fotogenesis/<Job>/job.json', 'kis': [],
             'zeilen': ['Foto „vorn“ ist Pflicht,', 'Winkel je Foto,', 'Körpergröße, Geschlecht']},
            {'titel': 'Netz', 'skript': 'pshuman_port14/pshuman_job_rechnen.py', 'kis': [('Stable Diffusion', 'PSHuman: 1 Foto'), ('UP2You', 'oder alle Fotos, A-Pose')],
             'zeilen': ['ein farbiges Netz,', 'seine Rückseite ist erfunden', 'Ablage <Job>/pshuman/']},
            {'titel': 'Rig und Haltung', 'skript': 'Schritte rig, haltung, figur, anpassen', 'kis': [('MIA', 'Gelenke im Netz')],
             'zeilen': ['Make-It-Animatable riggt', 'das Netz, A-Pose,', 'Figur in die Haltung']},
            {'titel': 'Erkennen', 'skript': 'Schritte segmentierung, zerlegung, foto', 'kis': [('Sapiens2', 'Körperteile'), ('SAM 3', 'Stücke')],
             'zeilen': ['Haut, Haar, Kleider je Punkt,', 'Gelenke am Foto', '(SAM 3D Body)']},
            {'titel': 'Genesis einpassen', 'skript': 'Schritte meshanpassung, zeile1', 'kis': [('Genesis', 'Regler, Haltung, Versatz')],
             'zeilen': ['IPNet-Port: Figur ins Netz,', 'Start an MIAs Gelenken,', 'Kopf, Glieder, Finger eigen']},
            {'titel': 'Haut, Kleider, Haar', 'skript': 'Schritte haut, fotohaut, kleider', 'kis': [('Genesis', 'Kacheln und Stücke')],
             'zeilen': ['Haut aus dem Netz,', 'Rücken aus weiteren Fotos,', 'Kleider ausgeschnitten', 'und neu gebunden']},
            {'titel': 'Prüfen', 'skript': 'Schritt pruefung', 'kis': [],
             'zeilen': ['69 Prüfungen am Stand', 'und im Tanz,', 'Ergebnis auf der Testseite']},
        ]
        return cls.svg('a2d-heute', 'Was heute läuft: Foto → Netz → Mesh-Genesis → Genesis-Modell', kaesten)

    @classmethod
    def pshuman(cls):
        kaesten = [
            {'titel': 'Freistellen', 'skript': 'inference.py', 'kis': [('rembg', 'Person ausschneiden')],
             'zeilen': ['Person 740 px hoch', 'in 768 × 768 Pixeln']},
            {'titel': 'Haltung schätzen', 'skript': 'startgelenke.py', 'kis': [('SAM 3D Body', 'Gelenke aus dem Foto')],
             'zeilen': ['nur für Schritt 4:', 'die Diffusion sieht es nicht', '(with_smpl false)', 'Original: PIXIE, Mask R-CNN']},
            {'titel': 'Ansichten erfinden', 'skript': 'mvdiffusion/, 40 Schritte', 'kis': [('Stable Diffusion', 'SD 2.1 unCLIP, angepasst')],
             'zeilen': ['6 Ansichten + Gesicht,', 'je Farbe und Normale:', '14 Bilder, 768 px', 'Ansichten sehen einander', '(Aufmerksamkeit aus Era3D)']},
            {'titel': 'Genesis anpassen', 'skript': 'genesiskoerper.py, 100 Schritte', 'kis': [('Genesis', 'Regler, Haltung, Lage')],
             'zeilen': ['Form, Haltung, Lage', 'an Normalen und Umrisse', 'der 6 Ansichten', 'Original: SMPL-X']},
            {'titel': 'Netz formen', 'skript': 'remesh_genesis.py, 700 Schritte', 'kis': [('Remeshing', 'Continuous Remeshing')],
             'zeilen': ['Start: die Genesis-Figur,', 'Verlust: Normalen, Umriss,', 'Gewicht je Ansicht', '1 · 0,4 · 0,8 · 1 · 0,8 · 0,4']},
            {'titel': 'Schließen', 'skript': 'Poisson, Tiefe 10', 'kis': [],
             'zeilen': ['Löcher zu, Hände der Figur', 'nur mit Schalter', 'bei uns poissontorch', 'auf der Karte']},
            {'titel': 'Textur', 'skript': 'multiview_color_projection', 'kis': [('Unique3D', 'Farbprojektion')],
             'zeilen': ['Farbe der 6 Ansichten', 'auf die Punkte,', 'Ungesehenes ergänzt', 'bei uns wahlweise Fototextur']},
        ]
        return cls.svg('a2d-pshuman', 'PSHuman: ein Foto wird zu sechs erfundenen Ansichten, daraus wird ein Netz geformt', kaesten)

    @classmethod
    def master(cls):
        kaesten = [
            {'titel': 'Master', 'skript': 'gebaut', 'kis': [('Stable Diffusion', 'PSHuman: Foto vorn')],
             'zeilen': ['bestimmt Haltung, Gesicht,', 'Vorderseite und Kleider', 'bleibt unverändert']},
            {'titel': 'Je Foto ein Netz', 'skript': 'Vorschlag', 'stand': 'offen', 'kis': [('Stable Diffusion', 'PSHuman: jedes Foto')],
             'zeilen': ['jedes Netz ist nur dort', 'echt, wo sein Foto', 'hinschaut']},
            {'titel': 'Erfindungskarte', 'skript': 'Vorschlag', 'stand': 'offen', 'kis': [],
             'zeilen': ['je Punkt: gesehen oder', 'erfunden, aus Kamera', 'und Verdeckung', 'dazu Streuung über Saaten']},
            {'titel': 'Genesis in jedes Netz', 'skript': 'Vorschlag, Schritt meshanpassung', 'stand': 'offen', 'kis': [('Genesis', 'gleiche Punkte in allen')],
             'zeilen': ['andere Armhaltung fällt', 'weg: Vergleich in Ruhe,', 'Punkt für Punkt']},
            {'titel': 'Form verschmelzen', 'skript': 'Vorschlag', 'stand': 'offen', 'kis': [],
             'zeilen': ['je Punkt der Versatz aus', 'dem Foto, das ihn sah;', 'erfundene Teile zählen nicht']},
            {'titel': 'Textur übernehmen', 'skript': 'Haut gebaut (fotohaut), Kleider offen', 'stand': 'offen', 'kis': [],
             'zeilen': ['Fotos auf die Figur legen,', 'Haut gibt es schon,', 'Kleider fehlen']},
            {'titel': 'Prüfen', 'skript': 'gebaut', 'kis': [],
             'zeilen': ['Gegenprobe: ein Foto', 'zurückhalten und aus', 'seinem Winkel vergleichen']},
        ]
        return cls.svg('a2d-master', 'Vorschlag für mehrere Fotos: ein Master, die anderen Fotos ergänzen nur, was sie wirklich gesehen haben (gestrichelt = nicht gebaut)', kaesten)
