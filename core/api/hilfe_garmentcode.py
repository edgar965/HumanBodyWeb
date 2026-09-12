# -*- coding: utf-8 -*-
u"""Hilfe -> Kleidung -> GarmentCode: Einzelheiten und Testfaelle.

Der GarmentCode-Weg ist der einzige, der Kleidung KONSTRUIERT statt sie
anzupassen — und der einzige, fuer den es eine vollstaendige Messreihe
gibt. Diese Seite zeigt beides: wie der Weg laeuft und was er auf 165
gemessenen Kombinationen liefert.

Die Messwerte kommen bei jedem Aufruf frisch aus den YAML-Dateien
(`Garmentcodemessung`). Fehlt eine, sagt die Seite das — statt eine leere
Tabelle zu zeigen, die wie „alles gut" aussieht.
"""

from .hilfeseite import Hilfeseite

from GarmentCode.messreihen import Garmentcodemessung


class KleidungGarmentcode(Hilfeseite):
    u"""Der GarmentCode-Weg mit allen Testfaellen."""

    template_name = 'hilfe/kleidung_garmentcode.html'
    AKTIV = 'hilfe_kleidung_garmentcode'

    #: Der Weg vom Koerper zum angezogenen Stueck. Je Schritt: was
    #: passiert, wo es steht, und was dabei schon schiefgegangen ist.
    SCHRITTE = [
        {'nr': 1, 'titel': 'Körper bereitstellen',
         'was': 'Das Figurnetz wird EINMAL gerechnet (CharacterState.compute '
                'über 18.210 bzw. 17.996 Punkte) und an Maßmessung, '
                'Drapierkörper und Verankerung durchgereicht.',
         'wo': 'core/dienste/garmentcode.py · garmentkoerper.py',
         'falle': 'Das Grundnetz war bis zum 07.09.2026 immer das '
                  'weibliche — eine männliche Figur ohne Regler wurde am '
                  'falschen Netz vermessen.'},
        {'nr': 2, 'titel': 'Segmentierung',
         'was': 'Aus den Skinning-Gewichten entsteht die Körperteil-'
                'Zuordnung (Rumpf, Arme, Beine, inneres Gesicht). Sie '
                'trennt die Arme bei der Messung und hält den Stoff von '
                'Zähnen und Zunge fern.',
         'wo': 'GarmentCode/segmentierung.py',
         'falle': '1.536 Punkte des männlichen Netzes hängen am '
                  'Steuerknochen corrective_smooth_inv und galten deshalb '
                  'als Rumpf — der Schritt rutschte um 37 cm nach unten.'},
        {'nr': 3, 'titel': 'Maße messen',
         'was': '26 Körpermaße am eigenen Netz: Umfänge über Hüllen, '
                'Rückenbreiten als Bogen, Messhöhen aus dem Profil '
                '(Hüfte = Maximum über dem Schritt, Taille = Minimum, '
                'Brust = Maximum darüber).',
         'wo': 'GarmentCode/koerpermasse.py · koerperprofil.py',
         'falle': 'Dünn besetzte Scheiben lieferten Scheinminima; die '
                  'Taille lag beim 195-cm-Mann bei 54 % statt 65 % der '
                  'Körperhöhe.'},
        {'nr': 4, 'titel': 'Schnittmuster konstruieren',
         'was': 'MetaGarment baut aus Maßen und Entwurf die 2D-Teile — '
                'Vorder- und Rückenteil, Ärmel, Kragen, Bund, Abnäher.',
         'wo': 'GarmentCode/entwurf.py · katalog.py (eigener Prozess)',
         'falle': 'Die Armlochtiefe kam aus der Vorlage, mit der '
                  'Körpergröße skaliert. Reicht sie bis zur Brustlinie, '
                  'entartet die Schulterecke und der Schnitt bricht ab.'},
        {'nr': 5, 'titel': 'Drapieren',
         'was': 'Die Teile werden vernäht und in einer Warp-XPBD-'
                'Simulation auf den Körper fallen gelassen. Der Körper '
                'liegt als OBJ in Metern mit Y oben, der Schnitt in '
                'Zentimetern.',
         'wo': 'GarmentCode/drapierung.py · drapierlauf.py (Python 3.10)',
         'falle': 'Der Körper wird ÜBERGEBEN, nicht geraten — ein '
                  'danebengegriffener Ordner drapiert stumm auf einem '
                  'fremden Körper.'},
        {'nr': 6, 'titel': 'Stoff korrigieren',
         'was': 'Die Simulation hält 2,5 mm Abstand; was spitzer aus dem '
                'Netz ragt, steht hindurch. Eingesunkene Punkte werden '
                'entlang der KÖRPERnormale herausgeschoben, der Weg auf '
                '15 mm gedeckelt.',
         'wo': 'GarmentCode/stoffkorrektur.py',
         'falle': 'Mit der Stoffnormale als Richtung schiebt die Korrektur '
                  'hinein statt heraus — aus 20 mm Einsinken wurden 35.'},
        {'nr': 7, 'titel': 'Anziehen',
         'was': 'Das Netz bekommt Knochengewichte vom nächsten '
                'Körperpunkt und eine Verankerung; der Versatz der Anker '
                'IST der Hautabstand.',
         'wo': 'GarmentCode/anziehen.py',
         'falle': 'Je Stück ein eigener Name an der Figur — mit einem '
                  'festen Namen nahm die Hose dem T-Shirt den Platz.'},
    ]

    #: Wie die drei Kennzahlen definiert sind. Ohne diese Angaben ist eine
    #: Prozentzahl nur eine Zahl (Regel: keine unbelegten Zahlen).
    KENNZAHLEN = [
        {'name': 'Durchstich',
         'frage': 'Wie viele STOFFpunkte stecken in der Haut?',
         'wie': 'Je Stoffpunkt der Abstand zum nächsten Körperdreieck '
                '(Punkt zu Dreieck, nicht Punkt zu Punkt); das Vorzeichen '
                'kommt aus der Körperflächennormale. Gezählt werden nur '
                'Punkte im Kontaktbereich unter 25 mm. Zähne, Zunge und '
                'Augen sind ausgenommen.',
         'warum': 'Umgekehrt gefragt — je Körperpunkt, ob Stoff dahinter '
                  'liegt — meldet der Messer an offenen Säumen Treffer, wo '
                  'kein Stoff in der Haut steckt: Der Fuß im Hosenbein '
                  'ergab 19,6 % für einen Jumpsuit, der einwandfrei sitzt. '
                  'Stoffseitig sind es 0,14 %.',
         'probe': '200 künstlich 15 mm eingedrückte Stoffpunkte müssen '
                  'gemeldet werden — sonst ist der Messer nur blind '
                  'geworden. Gemessen: genau 200 zusätzliche Treffer.'},
        {'name': 'Hautabstand',
         'frage': 'Wie weit liegt der Stoff im Median von der Haut?',
         'wie': 'Median des Abstands je Stoffpunkt zum nächsten '
                'Körperpunkt. Steht auch in der Rig-Datei als Versatz der '
                'Verankerung.',
         'warum': 'Die Probe darauf, dass überhaupt auf der richtigen '
                  'Figur drapiert wurde: Auf dem Durchschnittskörper des '
                  'Upstream lag derselbe Lauf bei 27,4 mm statt 13,2.',
         'probe': 'Über 40 mm heißt „sitzt nicht" — eine engere Schwelle '
                  'wäre falsch, eine weite Hose kommt legitim auf 21 mm.'},
        {'name': 'Knickflächen',
         'frage': 'Wie zerknittert ist das Ergebnis?',
         'wie': 'Anteil der Flächen, deren Winkel zur Nachbarfläche über '
                '60 Grad liegt (trimesh face_adjacency_angles).',
         'warum': 'Die Konfiguration wirkt hier sichtbar: gui_sim_props '
                  '(edge_ke 100) gegen default_sim_props (edge_ke 1) '
                  'halbiert die Knitter von 10,5–11,8 % auf 4,9–5,5 %.',
         'probe': 'Flach schattiert sieht JEDE Facette wie eine Falte aus. '
                  'Der Ärmel-Befund vom 06.09.2026 war zur Hälfte das '
                  'eigene Rendering, nicht die Simulation.'},
    ]

    #: Grenzen, die gemessen und NICHT behoben sind — mit dem Grund.
    GRENZEN = [
        {'was': 'FittedShirt oberhalb ~115 cm Brustumfang',
         'messung': 'mean_female, alle Umfänge skaliert: ×1,15 (Brust '
                    '112,0) baut, ×1,18 (114,9) bricht mit StitchingError '
                    'ab. Nur bust ×1,2 (116,9) baut, ×1,3 (126,6) nicht. '
                    'waist, hips und underbust vertragen ×1,3 problemlos.',
         'schluss': 'Die Grenze liegt bei GarmentCode selbst, nicht an '
                    'unserer Messung: Sie tritt auf dem Referenzkörper des '
                    'Werkzeugs genauso auf. Betrifft die fünf Stücke mit '
                    'FittedShirt (Trägertop, Hemd, Kleid, Abendkleid, '
                    'Jumpsuit).'},
        {'was': 'Die Brustlinie liegt bei den Männern hoch',
         'messung': 'Referenz: 22,4–23,0 cm unter der Schulterlinie. '
                    'Gemessen: hb1 14,2 cm, hb2 17,0 cm. Ursache ist das '
                    'Umfangsmaximum, das bei einem männlichen Netz in der '
                    'Achsel liegt statt auf Brusthöhe.',
         'schluss': 'Die Armlochtiefe folgt seit 07.09.2026 dem '
                    'Verhältnis der Vorlage (57 % des Schulter-Brust-'
                    'Abstands) und wandert damit mit. Die Brustlinie '
                    'selbst bleibt, wie sie gemessen wird — eine andere '
                    'Definition wäre geraten, nicht gemessen.'},
        {'was': 'Das Stück hängt starr an der Figur',
         'messung': 'Der Körper in der Szene ist ein Mesh, kein '
                    'SkinnedMesh — ein Skelett bekommt die Figur erst beim '
                    'Animieren.',
         'schluss': 'Die Bindung ist gebaut und greift, sobald ein Skelett '
                    'da ist; solange sagt die Meldung „aber unbeweglich".'},
    ]

    def kontext(self):
        return {
            'schritte': self.SCHRITTE,
            'kennzahlen': self.KENNZAHLEN,
            'grenzen': self.GRENZEN,
            'matrix_hb': Garmentcodemessung.matrix('humanbody'),
            'matrix_smpl': Garmentcodemessung.matrix('smpl'),
            'testkoerper': Garmentcodemessung.koerper(),
        }
