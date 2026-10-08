# -*- coding: utf-8 -*-
"""Arpmodell — die Daten der Seite Hilfe → Architektur → ARP Modell (08.10.2026).

Edgar (08.10.2026): „mach eine neue Seite Hilfe - Architektur - ARP Modell mit diesen Infos und füge alle Infos zum Mesh
typ rein. Füge das Modell auch in die Seite …/andere-modelle/ ein". „Diese Infos" sind die Antworten zu: Was ist das
Ursprungsrig (Auto-Rig Pro)? Würde ein anderes Rig (HumanBody) „Mesh to 3D" umgehen? Was verliert „Mesh to 3D"? Was ist
Konzept C (das Original-Netz als eigene Figurart)?

Die Zahlen stehen hier, nicht in den Vorlagen — jede mit ihrer Messung (eine Zahl im HTML wäre eine Behauptung, die
niemand mehr nachprüft). Quelle ist, wo nichts anderes steht, `cute girl 5.0.blend`, gelesen mit Blender 5.2.2 im
Hintergrund (nur lesend) am 08.10.2026; die Skripte liegen unter `ProjektTemp/_wegwerf/cutegirl/`:

    mesh_probe.py        Polygonarten, Kanten, UV, Attribute, Modifier, Shape Keys, Gruppen je Netz (`mesh_steckbrief.json`)
    knochen_probe.py     alle 559 Knochen mit Eltern, Kopf, Schwanz, Deform-Flag (`knochen.json`)
    material_probe.py    Knotenweg vom Principled BSDF zu den Bildern; `haar_alpha_probe.py` das Haar im Einzelnen
    bildgroessen.py      Größe der Bilder an den Materialien (PIL)
    richtungen_vergleich.py  Richtung Gelenk zu Gelenk, Genesis (Genesis9.dsf) gegen ARP
"""

import re

from django.utils.html import escape
from django.utils.safestring import mark_safe

from .figurquellen import Figurquellen
from .figurquellenblender import Figurquellenblender
from .netzmasse import Netzmasse

__all__ = ['Arpmodell']


class Arpmodell:
    STAND = '08.10.2026'
    DATEI = 'cute girl 5.0.blend'

    #: Der Eintrag in der Rangliste der Seite „Andere Modelle".
    ORDNER = 'cute_girl_ARP'
    #: Zum Vergleich der Netzdichte neben diesem Modell.
    VERGLEICH = ('00_eigene_Renderings', '11_Daz_Genesis9', ORDNER)

    #: Je Netz (Reihenfolge der Datei): (Name, Rolle, Punkte, Dreiecke, Kanten, Kantenlänge mm „Median (p5 … p95, Max)",
    #: Fläche m², UV-Bereich, Gruppen „definiert / mit Gewicht", Material und Bild). Polygonarten: überall nur
    #: Dreiecke (0 Vierecke, 0 n-Ecke); `Dreiecke` = Polygone = Schleifendreiecke.
    NETZE = [
        ('body', 'Körper (mit Kopf, Händen, Füßen)', 54_369, 108_545, 162_890, '4,53 (0,88 … 13,06, max 24,6)', '1,884',
         '0,001|0,004 … 0,990|0,999', '136 / 133', 'body — Farbe, Rauheit, Normalen je 8192² (sRGB / Non-Color)'),
        ('hair', 'Haar (Karten)', 34_637, 33_379, 66_966, '11,54 (2,2 … 23,27, max 62,7)', '1,877',
         '0,027|0,011 … 0,960|0,965', '144 / 1 (nur head.x, Gewicht 0,77 … 0,85)',
         'hair — 1024² RGBA: Alpha ja, Farbe fest'),
        ('shirt', 'Hemd', 8_045, 15_806, 23_852, '10,78 (1,08 … 20,13, max 40,5)', '0,726',
         '0,020|0,020 … 0,906|0,987', '137 / 24', 'shirt — Farbe + Normalen 2048²'),
        ('jean', 'Shorts', 5_272, 10_332, 15_595, '9,00 (1,85 … 16,48, max 27,7)', '0,199',
         '0,004|0,006 … 0,969|0,995', '137 / 9', 'jean — Farbe + Normalen 2048²'),
        ('L_eyes / R_eyes', 'Augäpfel (je Seite)', 770, 1_536, 2_304, '2,05 (0,71 … 4,04, max 4,3)', '0,003',
         '0,178|0,076 … 0,921|0,819', '1 / 1 (c_eye)', 'eyes — Eye_BaseColor.tga 2048²'),
        ('teeth_upper', 'Zähne oben', 2_633, 5_200, 7_832, '0,91 (0,41 … 2,89, max 6,4)', '0,003',
         '0,012|0,004 … 0,517|0,726', '3 / 3', 'teeth — Mouth_* 2048²'),
        ('teeth_lower', 'Zähne unten', 2_532, 4_976, 7_508, '0,78 (0,36 … 2,57, max 6,9)', '0,002',
         '0,002|0,646 … 0,997|0,996', '3 / 3', 'teeth — Mouth_* 2048²'),
        ('tongue', 'Zunge', 601, 1_168, 1_768, '1,95 (0,73 … 3,04, max 3,7)', '0,002',
         '0,516|0,032 … 0,998|0,693', '3 / 3', 'teeth.001 — Mouth_* 2048²'),
    ]

    #: Eigenschaften des Mesh-Typs: (Merkmal, Befund, Wirkung auf den Import).
    MESHTYP = [
        ('Polygonart', 'In allen 9 Netzen nur Dreiecke: 0 Vierecke, 0 n-Ecke (Blender: Polygone = Schleifendreiecke).',
         'Kein Viereck-Nachbau nötig; für „Mesh to 3D" und die Stücke ohnehin Dreiecke.'),
        ('Geschlossenheit', 'Körper: 162.890 Kanten bei 54.369 Punkten = 2,996 Kanten je Punkt (geschlossene Dreiecksfläche '
                            'hat ≈ 3); 147 Randkanten, davon 138 über 1,54 m (Augen, Mund), je 3 an Hemd- und Shortsband.',
         'Der Rumpf unter der Kleidung ist geschlossen — der Körper lässt sich ohne Kleider anpassen.'),
        ('Haar', '34.637 Punkte, 33.379 Dreiecke, 1,93 Kanten je Punkt: offene Streifen (Haarkarten), keine Volumina; '
                 'Überblendung HASHED.', 'Wird ein Genesis-Haarstück (Karten), kein Körperteil; Alpha aus dem PNG.'),
        ('Normalen', 'Attribut `custom_normal` bei Körper, Haar, Hemd, Shorts und Augen; nicht bei Zähnen und Zunge.',
         'Geglättete Schattierung der Datei; Genesis rechnet seine eigenen Normalen.'),
        ('UV', 'Eine UV-Ebene `UVMap` je Netz, alle Werte in 0 … 1 (kein UDIM, keine Kacheln). Der Körper nutzt '
               '0,001 … 0,999 — eine 8192²-Textur für alles.', 'Genesis nutzt fünf UDIM-Kacheln (1001–1005): vier umbacken, die Nägel (1005) bleiben Genesis.'),
        ('Shape Keys', 'Körper, Haar, Hemd, Shorts, Augen: `Basis` + `V_None` (bewegt am Körper 6 Punkte um höchstens '
                       '0,59 mm); Zähne und Zunge keine.', 'Es gibt keine Morphs zu übernehmen — die Form kommt aus Genesis.'),
        ('Modifier', 'Je Netz genau einer: `ARMATURE` (Eltern: `rig`). Kein SubSurf, kein Displace.',
         'Die Punkte der Datei sind die Endpunkte; kein Hochrechnen nötig.'),
        ('Material', 'Ein Material je Netz (`body`, `hair`, `shirt`, `jean`, `eyes`, `teeth`, `teeth.001`), Überblendung '
                     'HASHED; der Körper hat Subsurface 0,674. Bilder liegen neben der Datei (`textures/`), nicht gepackt.',
         'Deshalb ein Pfadfeld im Importdialog und kein Hochladen.'),
        ('Maße', 'Körper 1,0474 × 0,3932 × 1,7544 m (Breite mit Armen × Tiefe × Höhe), Füße auf 0, Z oben, Maßstab 1,0; '
                 'Objekte liegen im Ursprung, nur die Augen sitzen bei (±0,030 | −0,108 | 1,647).',
         'Meter, Z oben → glTF (x, z, −y), wie `Blendimportkoerper.gltf`.'),
    ]

    #: Das Rig: (Merkmal, Befund).
    RIG = [
        ('Typ', 'Auto-Rig Pro (ARP): Namen `c_…` (Steuerknochen), `.x/.l/.r`, `c_traj`, `c_pos`, `root_master.x`; '
                'dazu das Rig-Bedienskript `sexy girl_rig_ui.py` (beim Lesen nicht ausgeführt).'),
        ('Knochen', '559 insgesamt, 144 deformierend (alle 144 tragen Gewicht); 149 Gruppen tragen Gewicht, 5 davon '
                    'deformieren nicht. Gewicht tragen: 62 im Gesicht (Lippen, Lider, Brauen, Wangen, Ohren, Nase, Kinn, '
                    'Zähne, Augen), 38 an den Fingern, 25 Stretch-/Twist-Knochen.'),
        ('Hierarchie', 'Die deformierenden Knochen hängen unter Steuerknochen und folgen über Constraints: '
                       '`arm_stretch.l` ← `arm_twist.l` ← `c_shoulder.l`; `forearm_stretch.l` und `leg_stretch.l` ← '
                       '`c_traj`; `foot.l` ← `leg_fk.l`; `head.x` ← `c_head.x`. Ihre eigene Kette ist keine Gelenkkette '
                       '— darum nimmt die Knochenkarte die Referenzknochen (`arm.l`, `forearm.l`, `thigh.l`, `leg.l`, '
                       '`foot.l`) als Gelenke.'),
        ('Haltung', 'A-Haltung, Oberarm rund 57° unter der Waagerechten; keine Aktion; ein Pose-Knochen weicht ab '
                    '(`forearm_ik.l`); die ausgewerteten Punkte der Datei stimmen mit der Ruhelage auf 0,02 mm überein.'),
        ('Morphs', 'Keine. Die Mimik läuft über die Gesichtsknochen, nicht über Shape Keys.'),
        ('Zweites Rig', 'Eine Rigify-Armatur `sexy girl_Rigify` (470 Knochen, 88 deformierend) liegt in der Datei, '
                        'aber kein Netz benutzt sie.'),
        ('Herkunft', 'Unbekannt. Vermutung (nicht geprüft): Die Lichter heißen `Key_cc3iid_2528` — ursprünglich aus '
                     'Reallusion Character Creator, danach auf Auto-Rig Pro umgebaut.'),
    ]

    #: Knochenkarte: (Segment, ARP-Gelenke, Genesis-Knochen, Abweichung Genesis↔ARP in Grad, Drehung beim Umposen in Grad).
    #: Abweichung = Winkel zwischen den Richtungen Gelenk zu Gelenk (links gemessen, `richtungen_vergleich.py`);
    #: Drehung = gerechnet im Import (`umposen.json`, Lauf 08.10.2026), links wie rechts gleich, nach der Bewegung des
    #: Elternsegments — darum kleiner als die Abweichung, wo der Elternteil schon mitgewandert ist.
    KNOCHENKARTE = [
        ('Schlüsselbein', 'shoulder → arm', 'shoulder → upperarm', '4,4', '4,4'),
        ('Oberarm', 'arm → forearm', 'upperarm → forearm', '10,0', '8,3'),
        ('Unterarm', 'forearm → hand', 'forearm → hand', '15,0', '9,4'),
        ('Hand', 'hand → middle1', 'hand → mid1', '—', '1,9'),
        ('Oberschenkel', 'thigh → leg', 'thigh → shin', '6,4', '6,4'),
        ('Unterschenkel', 'leg → foot', 'shin → foot', '4,2', '2,5'),
        ('Fuß', 'foot → toes_01', 'foot → toes', '12,0', '13,8'),
        ('Zehen', 'toes_01 (Kopf → Schwanz)', 'toes (Kopf → Schwanz)', '—', '8,1'),
        ('Finger (15 Glieder je Hand)', 'index1 … pinky3, thumb1 … thumb3 (Glied → nächstes Glied)',
         'index1 … pinky3, thumb1 … thumb3', '17,0 … 29,3 (Daumen 6,7 … 19,3)', '0,8 … 15,5 (im Test, siehe unten)'),
    ]
    KNOCHENKARTE_FEHLT = (
        'Nicht gedreht: Wirbelsäule (8,0°) und Hals (14,3°) — ARP und Genesis sind dort anders GEBAUT, niemand steht '
        'anders. Das Gesicht folgt dem Kopf. Die Fingerglieder kamen NACH dem ersten Lauf dazu: Der Lauf '
        '2026.10.08.11.28.06 lief ohne sie (Finger folgten der Hand).'
    )

    #: Folgen des Umposens (Lauf 08.10.2026, `umposen.json`): (Netz, größte Bewegung mm, Median mm, Kanten außerhalb
    #: 0,8 … 1,25 des Originals in %, größte Streckung).
    UMPOSEN = [
        ('body', '150,6', '36,5', '0,033', '1,878'),
        ('shirt', '58,7', '1,9', '0,113', '2,005'),
        ('jean', '12,2', '2,1', '0,18', '1,569'),
        ('hair, Augen, Zähne, Zunge', '0,0', '0,0', '0', '1,00'),
    ]

    #: Messung des Genesis-Wegs („Mesh to 3D" auf dem umposten nackten Körper), Auftrag 2026.10.08.11.34.04, fertig nach
    #: 958,8 s (`ergebnis` des Auftrags, Skript `auftrag_ende.py`): (Größe, Wert, was sie misst). Der erste Anlauf
    #: (2026.10.08.11.28.34) hielt am Körper-Tor an: 11 Regler am Anschlag (Soll ≤ 8) — der Import lässt das Tor jetzt
    #: nur melden (`Blendimportfigur.rechnen`), der Befund bleibt im Ergebnis.
    MESSUNG = [
        ('Abstand Körperkette, Figur → Netz', 'RMS 2,68 mm, p95 5,46 mm',
         'nach 152 freien Reglern, Runde 2; Netz → Figur RMS 2,64 mm, p95 5,36 mm'),
        ('Verlauf der Körperkette (Figur → Netz, RMS)', '13,55 → 6,06 → 4,71 → 2,72 mm',
         'Haltung → Größe → Körpertyp → Bereiche (Runde 1)'),
        ('Gesichtskette (Kopfpunkte), Figur → Netz', 'RMS 0,97 mm, p95 1,89 mm',
         'nach 286 freien Kopfreglern; Netz → Figur RMS 0,58 mm, p95 1,11 mm'),
        ('Eigenmorph (Rest)', 'Rest 2,32 mm → 0,80 mm, größte Verschiebung 10,7 mm',
         '15.305 Käfigpunkte, 14.377 getroffen, 730 Punkte der Augenpartie als Lücke'),
        ('Endfigur gegen das Original-Körpernetz, zugeordnete Punktpaare',
         'Figur → Netz RMS %s mm, p95 1,62 mm; Netz → Figur RMS %s mm, p95 1,68 mm' % Figurquellenblender.ENDABSTAND_RMS,
         'Schritt „vorschau": ganze Figur nach Regler und Eigenmorph; je Körperteil 0,53 … 1,10 mm RMS. ACHTUNG: Das Maß '
         'zählt nur Paare, die zusammenpassen (Normalen, Grenzabstand) — Ausreißer sind ausgeschlossen.'),
        ('Endfigur gegen ALLE Körperpunkte (Fläche der Figur)',
         'Median %s mm, p95 %s mm, %s %% der Punkte über 8 mm; größter Abstand 27,9 mm, RMS 5,74 mm'
         % Figurquellenblender.ALLE_PUNKTE,
         'Abstand jedes der 54.369 Körperpunkte (in Ruhe) zur Fläche der Figur Stufe 1 (104.480 Punkte), `haltung_diag.py`. '
         'Nach Höhe: Füße (0–0,12 m) Median 2,17 / p95 9,56 mm; 0,8–1,0 m (Schritt, Hüfte und die hängenden Hände) '
         '5,33 / 21,58 mm; Taille 0,65 / 7,30 mm; Brust 1,03 / 13,29 mm'),
        ('Fingersegmente (Test, kein neuer Lauf)',
         'Hand/Finger-Region (10.811 Punkte): RMS 8,10 → 6,99 mm, größter Abstand 27,4 → 20,1 mm, über 8 mm 28,9 → 22,7 %; '
         'ganzer Körper RMS 5,74 → 5,45 mm',
         'Median der Hand-Region 4,08 → 4,38 mm (minimal schlechter). `finger_test.py`: dieselbe Figur und Rückrechnung, nur '
         'der Körper an einer frischen Export-Kopie mit Fingersegmenten umpost; Kanten: 0,04 % außerhalb 0,8 … 1,25, '
         'größte Streckung unverändert 1,878'),
        ('Wo die Abweichungen sitzen',
         'Fingerspitzen und Finger, Brustwarzen, Lippen, Schritt (hier steht die Figur außerhalb des Originals), Zehen',
         'Wärmekarte `abstand_karte.py`: der Rest der Oberfläche liegt auf der Figurfläche. Deutung, nicht geprüft: '
         'Genesis hat dort andere Anatomie und eine andere Fingerhaltung; Finger zählen im Fit mit Gewicht 0, Hände mit 0,1.'),
        ('Höhe', 'Figur 175,0 … 175,4 cm', 'Original 175,44 cm (größter Z-Wert des Körpernetzes)'),
        ('Rumpftiefe Figur / Netz', 'kleinstes Verhältnis 0,957', 'Tor-Messung bei 55, 62, 70, 76 % der Höhe'),
        ('Regler am Anschlag', '12 (Soll ≤ 8); im ersten Lauf 11',
         "Im ersten Lauf namentlich: Brust (BreastsFullnessUpper, BreastsLargeHigh), Brustmuskel (PectoralsHeight, "
         "…HeightOuter, …UnderCurve, …Width), Brustbein (SternumHeight), Schulterblatt (ScapulaDepth, ScapulaSize), Hals "
         "(Under Neck Height), Bauch (NW Damira Abs I). Deutung, nicht geprüft: Die Brust ist größer, als Genesis' "
         "Regler hergeben."),
        ('Erkennung', '33 Körperpunkte (5,9 px), 478 Gesichtspunkte (3,4 px)', 'Median-Fehler der Triangulation, Auftrag 11.28.34'),
        ('Dauer', 'Erkennung 99 s, Körper 328 s, Gesicht 149 s, Rest 40 s, Textur 250 s, Vorschau 63 s',
         'gesamt 958,8 s auf der RTX PRO 4500 Blackwell'),
    ]

    @classmethod
    def vergleich(cls):
        """Die Zeilen von HumanBody, Genesis 9 und diesem Modell aus der Rangliste von „Andere Modelle"."""
        nach_ordner = {e['ordner']: e for e in Figurquellen.rangliste()}
        return [nach_ordner[o] for o in cls.VERGLEICH if o in nach_ordner]

    @staticmethod
    def auszeichnen(text):
        """Text maskieren und `so` Markiertes als `<code>` setzen — die Texte hier stehen in Rückticks wie im Code."""
        return mark_safe(re.sub(r'`([^`]+)`', r'<code>\1</code>', escape(text)))

    @classmethod
    def netze(cls):
        """`NETZE` mit deutschen Tausenderpunkten bei Punkten, Dreiecken und Kanten."""
        return [(n[0], n[1], Netzmasse.zahl(n[2]), Netzmasse.zahl(n[3]), Netzmasse.zahl(n[4])) + n[5:] for n in cls.NETZE]

    @classmethod
    def kontext(cls):
        return {
            'stand': cls.STAND, 'datei': cls.DATEI, 'netze': cls.netze(),
            'meshtyp': [(m, cls.auszeichnen(b), cls.auszeichnen(w)) for m, b, w in cls.MESHTYP],
            'rig': [(m, cls.auszeichnen(b)) for m, b in cls.RIG],
            'knochenkarte': cls.KNOCHENKARTE, 'knochenkarte_fehlt': cls.KNOCHENKARTE_FEHLT, 'umposen': cls.UMPOSEN,
            'messung': cls.MESSUNG, 'vergleich': cls.vergleich(),
        }
