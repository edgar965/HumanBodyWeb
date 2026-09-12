# -*- coding: utf-8 -*-
u"""Animationseffekte — Mimik, Haare, Kleidung, Wind: die Stammdaten der Seite.

WARUM (Edgar, 12.09.2026: „wie machen die Animationsstudios diese
Sondereffekte, mit Mimik, Wind in den Haaren, bewegung der Kleider / Haare
wenn sich die Person bewegt? gibt es open Source dinger, die ich testen /
anwenden koennte?" — „schreibe schon mal alles hinein in Hilfe -
Animationseffekte")

Die Seite beantwortet drei Fragen: Wie machen es die Studios, was davon
liegt hier schon, und welcher offene Code kaeme fuer den Rest in Frage.
Die Texte stehen in Python und nicht in der Vorlage — dieselbe Regel wie
bei `Kleiderphysik` und `Koerperphysik`: Eine Aussage im HTML prueft
niemand mehr nach.

WAS HIER GEPRUEFT IST UND WAS NICHT
===================================
    Bestand       im Code nachgesehen (12.09.2026): `Gesichtskontur`,
                  `CharmorphBestand.frisuren`, `Kleiderphysik`, `Koerperphysik`,
                  `effekte/blender/kleidwind.py` (gelaufen, Zahlen in `effekte()`)
    Kandidaten    Lizenz und Stand aus den Adressen in
                  `Effektkandidaten.quellen()` (Web, 12.09.2026); KEINER
                  davon lief auf dieser Maschine
    Studios       Fachwissen ohne Messung — als Erklaerung gekennzeichnet
"""

__all__ = ['Animationseffekte']


class Animationseffekte:
    u"""Die Tabellen der Seite „Hilfe — Animationseffekte"."""

    #: Der Blender, den `ui/settings/pfade.py` kennt — und der, in dem die
    #: neue Haar- und Stoffdynamik liegt (Geometry Nodes, XPBD).
    BLENDER_HIER = '5.0'
    BLENDER_MIT_HAARDYNAMIK = '5.2 LTS (Juli 2026)'

    #: MediaPipe Face Landmarker: so viele Verformungswerte je Bild liefert
    #: er, nach dem Modellblatt (Blendshape V2).
    MIMIK_WERTE = 52
    MIMIK_PUNKTE = 478

    @staticmethod
    def schichten():
        u"""Wie die Studios es machen — eine Schicht je Zeile."""
        return [
            {'schicht': 'Körper',
             'verfahren': 'Keyframe-Animation oder Motion Capture; das Skelett '
                          'bewegt das Netz (Skinning). Alles Weitere setzt '
                          'darauf auf.',
             'eingabe': 'Animator oder Aufnahme',
             'werkzeuge': 'Maya, Blender; MoCap-Anzüge, Kamerasysteme',
             'hier': 'Video to BVH (14 Pipelines), Theatre spielt das BVH ab'},
            {'schicht': 'Mimik',
             'verfahren': 'Das Gesicht ist ein eigenes Rig aus hunderten '
                          'Verformungszielen (Blendshapes) nach FACS: Braue '
                          'hoch, Mundwinkel links, Kiefer auf. Gestellt von '
                          'Hand (Pixar, Disney) oder aus einer Helmkamera vor '
                          'dem Gesicht (Performance Capture, Weta/Avatar). '
                          'Körper und Gesicht sind fast immer zwei getrennte '
                          'Aufnahmen.',
             'eingabe': 'Regler oder Gesichtsvideo',
             'werkzeuge': 'Maya-Rigs, Faceware, hauseigene Löser',
             'hier': 'MocapNET v4 liefert Gesichtsgelenke im BVH (2D und '
                     'Hybrid); Verformungsziele gibt es nicht'},
            {'schicht': 'Haare',
             'verfahren': 'Nicht animiert, sondern simuliert: einige hundert '
                          'Leitsträhnen als biegsame Stäbe mit Kollision gegen '
                          'den Körper; die übrigen Zehntausende werden '
                          'dazwischen interpoliert. Der bewegte Körper ist die '
                          'Kollisionsfläche — die Haare folgen von selbst.',
             'eingabe': 'Frisur (Ruhelage) + Körperbewegung',
             'werkzeuge': 'Houdini Vellum, Maya XGen/nHair, hauseigene Löser',
             'hier': 'Frisuren als starres Netz (CharMorph `hairstyles/*.npz`, '
                     'UMA); keine Dynamik gefunden'},
            {'schicht': 'Kleidung',
             'verfahren': 'Stoff als Dreiecksnetz mit Dehnung, Biegung und '
                          'Kollision; geschneidert in Ruhelage, dann auf dem '
                          'bewegten Körper gerechnet. Falten entstehen aus der '
                          'Bewegung, niemand zeichnet sie.',
             'eingabe': 'Schnitt (Ruhelage) + Körperbewegung',
             'werkzeuge': 'Marvelous Designer/CLO (Schnitt), Houdini Vellum, '
                          'Maya nCloth',
             'hier': 'GarmentCode (Ruhelage) + Newton SolverStyle3D (Dynamik) '
                     '— siehe Kleiderphysik'},
            {'schicht': 'Wind',
             'verfahren': 'Kein eigener Effekt: ein Kraftfeld (Richtung, '
                          'Stärke, Turbulenz) in derselben Simulation, das je '
                          'Punkt an Haaren und Stoff zieht. Böen sind Rauschen '
                          'auf der Stärke.',
             'eingabe': 'Richtung, Stärke, Turbulenz',
             'werkzeuge': 'Force Fields in Houdini/Maya/Blender',
             'hier': 'Windfeld der Effekte-Pipeline (Blender); im Theatre nichts'},
            {'schicht': 'Reihenfolge',
             'verfahren': 'Körper zuerst (Bild für Bild fertig), dann Kleidung '
                          'auf dem Körper, dann Haare auf beidem; jede Stufe '
                          'wird als Bildfolge abgelegt („gebacken"), nie live '
                          'gerechnet. Rendern zuletzt.',
             'eingabe': '—',
             'werkzeuge': 'Pipeline-Caches (Alembic, USD)',
             'hier': 'Kleiderphysik-Kette legt je Bild ab, Theatre spielt es'},
        ]

    @staticmethod
    def bestand():
        u"""Was im Projekt schon liegt — im Code nachgesehen (12.09.2026)."""
        return [
            {'was': 'Körperbewegung aus Video',
             'wo': 'VideoToBVH, Seite „Process Videos — 3D"',
             'stand': 'läuft',
             'bemerkung': 'Vergleich aller Pipelines unter Hilfe → Video to BVH'},
            {'was': 'Gesichtsgelenke im BVH',
             'wo': 'MocapNET v4 (2D-Pipeline, GVHMR-Hybrid)',
             'stand': 'läuft, ungemessen',
             'bemerkung': 'Gelenke, keine Verformungsziele — die Figur muss '
                          'sie erst auf ihr Gesicht übersetzen'},
            {'was': 'MediaPipe Face Landmarker',
             'wo': '`core/dienste/gesichtskontur.py`, Modell '
                   '`VideoToBVH/MocapNET_v4/…/models/face_landmarker.task`',
             'stand': 'läuft — nur für den Gesichtsumriss (Foto → 3D)',
             'bemerkung': 'Derselbe Erkenner liefert je Bild die '
                          'Verformungswerte; `Gesichtskontur` fragt sie nicht '
                          'ab (`output_face_blendshapes` nicht gesetzt)'},
            {'was': 'Frisuren',
             'wo': 'CharMorph-Bestand (`hairstyles/*.npz`), UMA-Figuren',
             'stand': 'starr',
             'bemerkung': 'Im Theatre als Netz mit der Figur bewegt, keine '
                          'Strähnen-Dynamik'},
            {'was': 'Stoffdynamik (Theatre)',
             'wo': 'Newton SolverStyle3D auf dem GarmentCode-Stück',
             'stand': 'gemessen, Kette geplant',
             'bemerkung': 'Alles dazu unter Hilfe → Kleidung → Kleiderphysik; '
                          'Blender Cloth ist dort ausdrücklich nicht gewählt'},
            {'was': 'Effekte-Pipeline „Kleid + Wind" (Video)',
             'wo': 'Process Videos → Effekte; `effekte/blender/kleidwind.py`',
             'stand': 'läuft (12.09.2026)',
             'bemerkung': 'BVH → MPFB-Figur (CMU-MB-Rig, BVH Retargeter) → '
                          'MakeHuman-Kleid aus der Kleiderbibliothek als Blender-Cloth '
                          'mit Windfeld → Workbench-MP4. Offline, für die Beurteilung '
                          'der Stoffbewegung — nicht die Theatre-Kette'},
            {'was': 'Effekte-Pipeline „HumanBody-Figur (DEF-Skelett)" (Video)',
             'wo': 'Process Videos → Effekte; `effekte/figur/figurfilm.py`',
             'stand': 'läuft (12.09.2026)',
             'bemerkung': 'Gespeichertes Modell der Szene (Körpertyp, Morphs, '
                          'GarmentCode-Stücke, Frisur) + BVH → Retarget der Web-App '
                          'auf die 176 DEF-Knochen → LBS → GarmentCode-Stücke als '
                          'Stoff in Newton SolverStyle3D (GPU, Apache-2.0; Körper je '
                          'Teilschritt als Kollider, Wind als Staudruck je Stoffpunkt '
                          'über `State.particle_f`) → pyrender-MP4 (H.264). Kein '
                          'Blender. Female1 + Rock (deutung_toigo_long_full_skirt) + '
                          '001_ShyrinKurz, 148 Bilder 720×900, 22.781 Stoffpunkte: '
                          '1,5 s je Bild Stoff, Einlauf 20 s; Shirt 9,6 mm von der Haut, '
                          '0 % im Körper. Ohne Stoff (Schalter) folgt die Kleidung dem '
                          'Körper starr; die Frisur hängt immer starr am Kopfknochen. '
                          'Modell über den Figurwahldialog der Szene, Animation über '
                          'den Animationsbrowser (Aufträge + Bibliothek)'},
            {'was': 'Körperphysik (Muskeln, Nachschwingen)',
             'wo': 'FastProjectiveSkinning, Kommandozeile',
             'stand': 'Arme zerreißen noch',
             'bemerkung': 'Hilfe → Kleidung → Körperphysik'},
            {'was': 'Wind',
             'wo': 'Effekte-Pipeline: Blender-Windfeld (MPFB) oder Staudruck je '
                   'Stoffpunkt in Newton (HumanBody-Figur), Stärke, Böen und '
                   'Richtung als Parameter',
             'stand': 'läuft im Video, nicht im Theatre',
             'bemerkung': 'Newton nimmt äußere Kräfte je Punkt an '
                          '(`State.particle_f`, von `SolverStyle3D` gelesen — im '
                          'Code nachgesehen 12.09.2026); damit ist Wind auch in der '
                          'Kleiderphysik-Kette des Theatre möglich'},
        ]

    @classmethod
    def weg(cls):
        u"""Der Weg, der zu diesem Projekt passt — je Schicht ein Vorschlag."""
        return [
            ('Mimik aus demselben Video',
             'Face Landmarker über das Video laufen lassen, das schon den '
             'Körper liefert: %d Werte je Bild (ARKit-Namen: jawOpen, '
             'eyeBlinkLeft …). Die Werte sind Verformungsziele — die Figur '
             'braucht die passenden %d Ziele auf ihrem Gesicht. Welche der '
             'Figuren (CharMorph, UMA, MakeHuman) sie hat, ist die offene '
             'Frage; MPFB-Figuren bringen eigene Ausdrucksziele mit.'
             % (cls.MIMIK_WERTE, cls.MIMIK_WERTE)),
            ('Mimik aus der Sprache',
             'Wo kein Gesicht im Bild ist (Rücken, Weitwinkel), rechnet '
             'Audio2Face die Lippen und den Ausdruck aus der Tonspur — auch '
             'als Verformungsziele. Modelle unter NVIDIA Open Model License, '
             'SDK MIT.'),
            ('Haare als Strähnen',
             'Die Frisur als Leitsträhnen mit Kollision gegen den bewegten '
             'Körper rechnen und je Bild ablegen — dieselbe Bauform wie die '
             'Kleiderphysik-Kette. Fertiger offener Löser: Blender %s '
             '(Hair Dynamics, XPBD); installiert ist hier %s.'
             % (cls.BLENDER_MIT_HAARDYNAMIK, cls.BLENDER_HIER)),
            ('Wind',
             'Ein Kraftfeld in der Simulation, die schon läuft — kein '
             'eigener Schritt. In Blender „Wind" plus „Turbulence"; für '
             'Newton ist zu prüfen, ob der Style3D-Löser äußere Kräfte je '
             'Punkt annimmt.'),
            ('Reihenfolge',
             'Körper (BVH) → Kleidung → Haare → Ablage je Bild → Theatre. '
             'Jede Stufe liest die vorige aus der Ablage; nichts wird live '
             'gerechnet. Zittern im BVH wird im Stoff und in den Haaren '
             'sichtbar — die Glättung (σ) der Pipelines steht davor.'),
        ]

    #: Der Lauf, aus dem die Zahlen unten stammen: 002_Dance (GEM-SMPL-BVH,
    #: 1.004 Bilder bei 60 fps), Kleid `toigo_halter_dress_knee_length`,
    #: 300 Bilder, 1280x720, Unterteilung 1, Wind 2, Selbstkollision an
    #: (`ProjektTemp/effekte/dance300c/dance300c.json`, 12.09.2026).
    EFFEKTLAUF = '002_Dance, 300 Bilder, 1280×720, Unterteilung 1 (12.09.2026)'

    @staticmethod
    def effekte():
        u"""Die Effekte-Pipeline, gemessen — je Zeile ein Befund."""
        return [
            ('Stoffnetz', '7.999 Punkte nach einer Unterteilung (Kleid: 2.031 '
             'Punkte, 1.968 Flächen); Anker: 375 Punkte fest, 746 teilweise'),
            ('Figur + Kleid', '1,1 s (MPFB-Figur, CMU-MB-Rig, Kleid anziehen)'),
            ('Retarget', '6,2 s für 300 Bilder — 33,1 s, wenn der Retargeter '
             'alle 1.004 Bilder liest; seither liest er nur die gebrauchten'),
            ('Simulation', '670,7 s für 300 Bilder (2,2 s je Bild) mit Körper- '
             'und Selbstkollision; ruhige Bilder 0,4 s, hohe Beinschwünge bis '
             '9 s je Bild'),
            ('Rendern', '40,6 s für 300 Bilder Workbench 1280×720 als H.264'),
            ('Falle 1: die Delete-Maske', 'MPFB versteckt die Haut unter dem '
             'Kleid (MASK `Delete.<kleid>`). Der Kollider ist das Netz nach '
             'allen Modifiern — ohne Hüfte und Oberschenkel fiel der Rock nach '
             'innen und zerknüllte. Die Maske kommt in der Pipeline weg.'),
            ('Falle 2: Selbstkollisionsabstand', 'Blenders 6 mm auf dem '
             'unterteilten Netz (Flächen ~1 cm) ließ Nachbarflächen als Kontakt '
             'gelten: Saum +7,5 cm in 30 Bildern, fünffache Rechenzeit. Mit '
             '3 mm (Abstand je Stufe halbiert) blieb der Saum (−1,1 cm).'),
            ('Falle 3: Windstärke', 'Bei 6 (Blender-Einheit) wickelte sich der '
             'Rock in 100 Bildern um die Hüfte; Vorgabe jetzt 2.'),
            ('Falle 4: Reibung', 'Blenders Vorgabe 5 hält den Rock am Bein, '
             'wenn das Knie hochkommt: Bild 120 von 002_Dance, Saum 1,6 cm '
             'unter der Hüfte; mit Reibung 1 sind es 7,8 cm (0,2: 4,3 cm). '
             'Vorgabe der Pipeline: 1.'),
            ('Was bleibt', 'Bei hohen Beinschwüngen rutscht ein knielanger Rock '
             'hoch und kräuselt — das ist teils Physik, teils Netz (2.031 '
             'Punkte, einmal unterteilt). Feiner unterteilen kostet Zeit; die '
             'Parameter der Seite sind dafür da.'),
        ]

    @staticmethod
    def nicht():
        u"""Was ausdruecklich nicht vorgeschlagen wird — und warum."""
        return [
            ('Blender Cloth für das Theatre', 'Edgar, 10.09.2026: „blenderCloth '
             'nutze ich nicht". Für Stoff im Theatre bleibt Newton '
             '(Kleiderphysik); die Effekte-Pipeline nutzt Blender Cloth nur für '
             'das Offline-Video (Auftrag 12.09.2026).'),
            ('MetaHuman / Unreal 5', 'Gesichts-Capture per iPhone, Chaos '
             'Cloth, Groom-Haare — kostenlos, aber nicht offen (Epic-EULA). '
             'Nichts davon lässt sich in die eigene Kette einbauen.'),
            ('Haare aus dem Video rekonstruieren', 'Gaussian Haircut, '
             'Im2Haircut: Forschungscode, CC BY-NC-SA — liefert eine '
             'Frisur, keine Bewegung. Die Frisur kommt hier aus dem Bestand.'),
            ('Gesicht in 3D aus dem Bild (FLAME, DECA, EMOCA, SMIRK)',
             'MPI-Lizenz, nur nicht-kommerziell — dieselbe Lage wie bei SMPL. '
             'Für die Mimik reichen die Werte des Face Landmarkers.'),
        ]

    @staticmethod
    def offen():
        u"""Entscheidungen, die noch niemand getroffen hat."""
        return [
            ('Welche Figur bekommt die Mimik?', 'Die 52 Werte brauchen 52 '
             'Ziele auf dem Gesicht der Figur. CharMorph führt eigene '
             'Ausdrucks-Morphs, UMA eigene — keine davon ist die ARKit-Menge. '
             'Entweder eine Übersetzungstabelle oder eine Figur, die die '
             'Ziele mitbringt (MPFB).'),
            ('Blender 5.0 → 5.2 LTS', 'Die neue Haar- und Stoffdynamik liegt '
             'erst in 5.2. Ob der Umstieg die übrigen Blender-Schritte des '
             'Projekts (CharMorph, Rigging) stört, ist nicht geprüft.'),
            ('Gelenke oder Verformungsziele?', 'MocapNET schreibt das Gesicht '
             'als Gelenke ins BVH, der Face Landmarker liefert '
             'Verformungsziele. Zwei Darstellungen für dieselbe Sache; eine '
             'muss die Hauptsache werden.'),
            ('Liefert das Modell hier die Werte?', 'Die Datei '
             '`face_landmarker.task` aus MocapNET v4 enthält den Umriss; ob '
             'sie auch das Blendshape-Modell bündelt, sagt erst ein Aufruf '
             'mit `output_face_blendshapes=True`.'),
            ('Stoff auf Stoff', 'Style3D behandelt Shirt und Rock in EINEM Netz; '
             'wo die Drapierungen einander durchdringen (Bund unter dem Saum), '
             'entscheidet der Kontakt je Teilschritt. Gemessen ist nur, dass es '
             'nicht kippt — nicht, wie es aussieht.'),
        ]
