# -*- coding: utf-8 -*-
"""Hilfe -> Kleidung -> GarmentCode: Einzelheiten und Testfaelle.

Der GarmentCode-Weg ist der einzige, der Kleidung KONSTRUIERT statt sie
anzupassen — und der einzige, fuer den es eine vollstaendige Messreihe
gibt. Diese Seite zeigt beides: wie der Weg laeuft und was er auf 165
gemessenen Kombinationen liefert.

Die Messwerte kommen bei jedem Aufruf frisch aus den YAML-Dateien
(`Garmentcodemessung`). Fehlt eine, sagt die Seite das — statt eine leere
Tabelle zu zeigen, die wie „alles gut" aussieht.
"""

from GarmentCode.messreihen import Garmentcodemessung

from .hilfeseite import Hilfeseite


class KleidungGarmentcode(Hilfeseite):
    """Der GarmentCode-Weg mit allen Testfaellen."""

    template_name = 'hilfe/kleidung_garmentcode.html'
    AKTIV = 'hilfe_kleidung_garmentcode'

    #: Der Weg vom Koerper zum angezogenen Stueck. Je Schritt: was
    #: passiert, wo es steht, und was dabei schon schiefgegangen ist.
    #: Nachgezogen 25.09.2026 gegen den Code (Edgar: „die Architektur von
    #: Garment Code update ggf."): Dateien umgezogen, Nacharbeit als eigener
    #: Schritt, Anziehen ueber Dreiecke, drei Figurarten.
    SCHRITTE = [
        {
            'nr': 1,
            'titel': 'Körper bereitstellen',
            'was': 'Das Figurnetz wird EINMAL gerechnet und an Maßmessung, '
            'Drapierkörper und Verankerung durchgereicht. Drei Figurarten: '
            'HumanBody (MorphData, 18.210 bzw. 17.996 Punkte), SMPL-X '
            '(A40, 6.890 Punkte) und Genesis 9 (Netz mit HD-Morphs, '
            'sichtbare Fläche, Haut, sechs Segmente, Schulterneigung).',
            'wo': 'GarmentCode/dienst.py · koerperdienst.py · koerperablage.py · '
            'core/dienste/g9garmentfigur.py',
            'falle': 'Das Grundnetz war bis zum 07.09.2026 immer das '
            'weibliche — eine männliche Figur ohne Regler wurde am '
            'falschen Netz vermessen.',
        },
        {
            'nr': 2,
            'titel': 'Segmentierung',
            'was': 'Aus den Skinning-Gewichten entsteht die Körperteil-'
            'Zuordnung (Rumpf, Arme, Beine, inneres Gesicht). Sie '
            'trennt die Arme bei der Messung und hält den Stoff von '
            'Zähnen und Zunge fern.',
            'wo': 'GarmentCode/segmentierung.py',
            'falle': '1.536 Punkte des männlichen Netzes hängen am '
            'Steuerknochen corrective_smooth_inv und galten deshalb '
            'als Rumpf — der Schritt rutschte um 37 cm nach unten.',
        },
        {
            'nr': 3,
            'titel': 'Maße messen',
            'was': '27 Körpermaße am eigenen Netz (dazu 16 Fußmaße für '
            'Schuhe): Umfänge über Hüllen, Rückenbreiten als Bogen, '
            'Messhöhen aus dem Profil (Hüfte = Maximum über dem Schritt, '
            'Taille = Minimum, Brust = Maximum darüber).',
            'wo': 'GarmentCode/koerpermasse.py · koerperprofil.py',
            'falle': 'Dünn besetzte Scheiben lieferten Scheinminima; die '
            'Taille lag beim 195-cm-Mann bei 54 % statt 65 % der '
            'Körperhöhe.',
        },
        {
            'nr': 4,
            'titel': 'Schnittmuster konstruieren',
            'was': 'MetaGarment baut aus Maßen und Entwurf die 2D-Teile — '
            'Vorder- und Rückenteil, Ärmel, Kragen, Bund, Abnäher.',
            'wo': 'GarmentCode/entwurf.py · katalog.py (eigener Prozess)',
            'falle': 'Die Armlochtiefe kam aus der Vorlage, mit der '
            'Körpergröße skaliert. Reicht sie bis zur Brustlinie, '
            'entartet die Schulterecke und der Schnitt bricht ab.',
        },
        {
            'nr': 5,
            'titel': 'Drapieren',
            'was': 'Die Teile werden vernäht und in einer Warp-XPBD-'
            'Simulation auf den Körper fallen gelassen. Der Körper '
            'liegt als OBJ in Metern mit Y oben, der Schnitt in '
            'Zentimetern.',
            'wo': 'GarmentCode/drapierung.py · drapierlauf.py (Python 3.10)',
            'falle': 'Der Körper wird ÜBERGEBEN, nicht geraten — ein '
            'danebengegriffener Ordner drapiert stumm auf einem '
            'fremden Körper.',
        },
        {
            'nr': 6,
            'titel': 'Stoff korrigieren',
            'was': 'Die Simulation hält 2,5 mm Abstand; was spitzer aus dem '
            'Netz ragt, steht hindurch. Eingesunkene Punkte werden '
            'entlang der KÖRPERnormale herausgeschoben, der Weg auf '
            '15 mm gedeckelt; seit 24.09.2026 auch Haut, die zwischen den '
            'Stoffpunkten durch ein Dreieck sticht (Lot ins Dreieck).',
            'wo': 'GarmentCode/stoffkorrektur.py · flaechendurchstich.py',
            'falle': 'Mit der Stoffnormale als Richtung schiebt die Korrektur '
            'hinein statt heraus — aus 20 mm Einsinken wurden 35.',
        },
        {
            'nr': 7,
            'titel': 'Nacharbeit',
            'was': 'Gegen die SICHTBARE Haut plus die schon getragenen Stücke '
            '(auch Daz-Stücke auf Genesis 9): Hosen hochziehen (Schritt '
            'an den Körperschritt), auf festen Hautabstand anlegen '
            '(„Eng anliegend", Leggings 2,0 mm), Faltenzone am Knöchel '
            'ohne Glättung; Daz-Stücke, deren Saum über dem Bund hängt, '
            'kommen danach außen darüber.',
            'wo': 'GarmentCode/stoffnacharbeit.py · stoffhochziehen.py · '
            'stoffanlegen.py · stofffalten.py · hautmitstoff.py · stofflagen.py',
            'falle': 'Gegen die nackte Haut gerechnet zog das Anlegen den Bund '
            'der Leggings durch das T-Shirt an die Haut — und die Harem-'
            'Hose 2 mm über der Haut in die Jeans.',
        },
        {
            'nr': 8,
            'titel': 'Anziehen',
            'was': 'Jeder Stoffpunkt wird am nächsten Körper-DREIECK '
            'verankert (Baryzentrik und Versatz im mitgedrehten '
            'Dreiecksrahmen), die Knochengewichte der drei Ecken im '
            'selben Verhältnis gemischt; dieselbe Projektion trägt den '
            'Stoff bei Reglerzügen mit. Der Träger (HumanBody oder '
            'Genesis 9) kommt in einer Form: Steuernetz, Gewichte, Knochen.',
            'wo': 'GarmentCode/stoffbindung.py · anziehen.py · gewichtsuebertragung.py',
            'falle': 'Mit dem nächsten Körperpunkt statt dem Dreieck sprangen '
            'die Gewichte an Dreiecksgrenzen (47 % andere Hauptknochen '
            'auf 3.000 Probepunkten) — der Stoff riss beim Armheben. Je '
            'Stück ein eigener Name, sonst nahm die Hose dem T-Shirt den Platz.',
        },
    ]

    #: Wie die drei Kennzahlen definiert sind. Ohne diese Angaben ist eine
    #: Prozentzahl nur eine Zahl (Regel: keine unbelegten Zahlen).
    KENNZAHLEN = [
        {
            'name': 'Durchstich',
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
            'geworden. Gemessen: genau 200 zusätzliche Treffer.',
        },
        {
            'name': 'Hautabstand',
            'frage': 'Wie weit liegt der Stoff im Median von der Haut?',
            'wie': 'Median des Abstands je Stoffpunkt zum nächsten '
            'Körperpunkt. Steht auch in der Rig-Datei als Versatz der '
            'Verankerung.',
            'warum': 'Die Probe darauf, dass überhaupt auf der richtigen '
            'Figur drapiert wurde: Auf dem Durchschnittskörper des '
            'Upstream lag derselbe Lauf bei 27,4 mm statt 13,2.',
            'probe': 'Über 40 mm heißt „sitzt nicht" — eine engere Schwelle '
            'wäre falsch, eine weite Hose kommt legitim auf 21 mm.',
        },
        {
            'name': 'Knickflächen',
            'frage': 'Wie zerknittert ist das Ergebnis?',
            'wie': 'Anteil der Flächen, deren Winkel zur Nachbarfläche über '
            '60 Grad liegt (trimesh face_adjacency_angles).',
            'warum': 'Die Konfiguration wirkt hier sichtbar: gui_sim_props '
            '(edge_ke 100) gegen default_sim_props (edge_ke 1) '
            'halbiert die Knitter von 10,5–11,8 % auf 4,9–5,5 %.',
            'probe': 'Flach schattiert sieht JEDE Facette wie eine Falte aus. '
            'Der Ärmel-Befund vom 06.09.2026 war zur Hälfte das '
            'eigene Rendering, nicht die Simulation.',
        },
    ]

    #: Grenzen, die gemessen und NICHT behoben sind — mit dem Grund.
    GRENZEN = [
        {
            'was': 'FittedShirt oberhalb ~115 cm Brustumfang',
            'messung': 'mean_female, alle Umfänge skaliert: ×1,15 (Brust '
            '112,0) baut, ×1,18 (114,9) bricht mit StitchingError '
            'ab. Nur bust ×1,2 (116,9) baut, ×1,3 (126,6) nicht. '
            'waist, hips und underbust vertragen ×1,3 problemlos.',
            'schluss': 'Die Grenze liegt bei GarmentCode selbst, nicht an '
            'unserer Messung: Sie tritt auf dem Referenzkörper des '
            'Werkzeugs genauso auf. Betrifft die fünf Stücke mit '
            'FittedShirt (Trägertop, Hemd, Kleid, Abendkleid, '
            'Jumpsuit).',
        },
        {
            'was': 'Die Brustlinie liegt bei den Männern hoch',
            'messung': 'Referenz: 22,4–23,0 cm unter der Schulterlinie. '
            'Gemessen: hb1 14,2 cm, hb2 17,0 cm. Ursache ist das '
            'Umfangsmaximum, das bei einem männlichen Netz in der '
            'Achsel liegt statt auf Brusthöhe.',
            'schluss': 'Die Armlochtiefe folgt seit 07.09.2026 dem '
            'Verhältnis der Vorlage (57 % des Schulter-Brust-'
            'Abstands) und wandert damit mit. Die Brustlinie '
            'selbst bleibt, wie sie gemessen wird — eine andere '
            'Definition wäre geraten, nicht gemessen.',
        },
        {
            'was': 'Reglerzüge nach dem Neuladen',
            'messung': 'Auf Genesis 9 folgt das Stück Reglerzügen über die '
            'Dreiecksbindung an den zuletzt gemerkten Körper '
            '(`Gcnachformung`; Ursula, BodyHeavy 1: Hose median 32 mm '
            'mitgewandert, Hautabstand 3,4 → 3,8 mm). Nach einem '
            'Neuladen der Szene steht wieder die Form vom Bau.',
            'schluss': 'Kein Fehler der Bindung, sondern ein fehlender '
            'Speicherstand des letzten Körpers; bis dahin hilft ein '
            'neuer Bau.',
        },
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
