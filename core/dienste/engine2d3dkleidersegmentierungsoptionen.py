# -*- coding: utf-8 -*-
"""Engine2d3dKleidersegmentierungsoptionen — die Gruppe `segmentierung` der Optionen von „2D3D Kleider" (04.10.2026; Einstellungen 05.10.2026).

Der Schritt „Segmentierung" (`Engine2d3dKleidersegmentierung`) steht nach dem Netz und ist OPTIONAL (Edgar, 04.10.2026: „baue das ein in den 2d3dKleider jobs — optional nach der Mesh
erzeugung"). Bis 05.10.2026 gab es EINE Option (`verwenden`); alles andere stand fest im Code. Edgar (05.10.2026): „was für andere Sapiens Klassen gibt es noch? Noch anderen Einstellungen, die du
mir bisher verschwiegen hast? Baue diese alle ein und zeige mir die Optionen in der Oberfläche." Jetzt ist jede Stellgröße ein Feld; die Vorgaben sind die Werte, mit denen gemessen wurde:

    verwenden     Kleidungsmaske aus den Etiketten (an) oder Farbe und Lage (aus, Vorgabe) — im vollen Lauf läuft der Schritt nur bei „an" oder `haar` ≠ „farbe"
    haar          woher die Haarmaske kommt: Farbe des Netzes (Vorgabe) · Sapiens-Klasse Hair · beides (`Sapienshaar`)
    modell        Familie und Größe: Sapiens 0.3b · 0.6b · 1b (Vorgabe) · Sapiens2 sapiens2-0.4b (gemessen 09.10.2026) · sapiens2-0.8b — `Sapiensgewichte.GROESSEN`
    schuhe        Klassen Left/Right_Shoe: zu „Socken / Schuhe" (Vorgabe) · zu Zubehör · Haut          (`Sapienszuordnung`)
    socken        Klassen Left/Right_Sock: zu „Socken / Schuhe" (Vorgabe) · Haut
    zubehoer      Klasse Apparel: Zubehör (Vorgabe) · zum Oberteil · Haut
    min_stimmen   so viele Pixel Stimme braucht eine Fläche, um als gesehen zu gelten (`Sapiensmaske.MIN_STIMMEN`)
    glaettung     Gewicht der Nachbarstimmen (`Sapiensmaske.GLAETTUNG`)
    nah_mm        so nah muss eine gesehene Fläche liegen, damit eine ungesehene ihr Stück übernimmt (`Sapiensmaske.NAH_M`)
    raster        Kantenlänge des Flächenbildes in px (`Sapiensflaechen.RASTER`)
    kante         px, auf die das Foto vor dem Modell verkleinert wird (`Sapiensfoto.KANTE`)
    rand          Rand um das Motiv vor dem Modell in % (`Sapiensfoto.RAND`)

`modell`, `raster`, `kante` und `rand` ändern, WAS Sapiens rechnet (`rechenoptionen`: stehen im Stand der Ablage; andere Werte → „passt nicht mehr", die Schritte danach nehmen die Stimmen nicht).
Alle anderen wirken erst bei der Entscheidung (CPU, `Sapiensmaske`, `Sapienshaar`) und brauchen keinen neuen Sapiens-Lauf.
"""

__all__ = ['Engine2d3dKleidersegmentierungsoptionen']


class Engine2d3dKleidersegmentierungsoptionen:
    HAAR_QUELLEN = ('farbe', 'sapiens', 'beide')
    KLASSEN = ('Background, Apparel, Face_Neck, Hair, Left_Foot, Left_Hand, Left_Lower_Arm, Left_Lower_Leg, Left_Shoe, Left_Sock, Left_Upper_Arm, Left_Upper_Leg, Lower_Clothing, '
               'Right_Foot, Right_Hand, Right_Lower_Arm, Right_Lower_Leg, Right_Shoe, Right_Sock, Right_Upper_Arm, Right_Upper_Leg, Torso, Upper_Clothing, Lower_Lip, Upper_Lip, '
               'Lower_Teeth, Upper_Teeth, Tongue')
    KATALOG = [
        {'schluessel': 'verwenden', 'titel': 'Kleidung aus der Segmentierung (Sapiens)', 'art': 'wahl', 'vorgabe': 'aus', 'werte': [
            ('aus', 'Aus — Kleidung nach Farbe und Lage (Vorgabe)'),
            ('an', 'An — Sapiens zerlegt die Fotos, die Kleidungsmaske folgt den Etiketten'),
        ], 'hinweis': 'Sapiens (Meta, Körperteil-Modell, nicht kommerziell: CC BY-NC 4.0) zerlegt jedes vorbereitete Foto in 28 Klassen: ' + KLASSEN + '. Daraus werden Oberteil, Hose, Socken/Schuhe, '
                      'Zubehör, Haar und Haut; die Etiketten werden mit derselben Projektion wie die Fotofarbe auf die Flächen des Netzes gelegt, verdeckte Flächen stimmen nicht ab. Wo kein Foto hinsieht '
                      '(Innenseiten, Schritt, Achseln), gilt weiter die Regel nach Farbe und Lage. Gemessen im Probelauf an Edgars Fotos (04.10.2026): die Regel hatte Ärmel 2–4 cm zu kurz und Socken 3–9 cm '
                      'zu niedrig, Hosensaum und Shirt/Shorts-Grenze stimmten innerhalb ± 2 cm. Die Maske wirkt erst, wenn der Schritt „Körper“ mit Quelle „rechnen“ danach läuft (übernommene Körper '
                      'haben keine eigene Maske).'},
        {'schluessel': 'haar', 'titel': 'Haar aus der Segmentierung (Sapiens-Klasse Hair)', 'art': 'wahl', 'vorgabe': 'farbe', 'werte': [
            ('farbe', 'Farbe des Netzes — Helligkeit gegen Hautton, Gesichtszone geschützt (bisher)'),
            ('sapiens', 'Sapiens — wo ein Foto die Fläche sieht gilt die Klasse „Hair", sonst die Farbe'),
            ('beide', 'Beides — Haar ist, was die Farbe oder Sapiens als Haar sieht'),
        ], 'hinweis': 'Die Haarmaske trennt das Netz in „ohne Haar" und „nur Haar" (das Haar-Objekt `haar.glb`), gibt dem Schritt „Frisur" die Fläche zum Messen und färbt die Frisur. Bisher entschied die '
                      'Farbe allein — ein Foto mit grauem Haar und Hautton in der Nähe, Bart und Schatten bringen sie durcheinander. Sapiens kennt das Haar als eigene Klasse. Das Gesicht (Augen, Brauen, '
                      'Nase, Mund), die Bartzone und der Rumpf bleiben in jedem Fall geschützt. Der Schritt „Segmentierung“ läuft bei „Sapiens“ und „Beides“ im vollen Lauf mit. Ob Sapiens das Haar '
                      'besser trifft als die Farbe, ist an Edgars Fotos noch nicht gemessen — der Bericht „Haar“ zeigt beide Flächen und ihre Überschneidung.'},
        {'schluessel': 'modell', 'titel': 'Sapiens-Modell (Familie und Größe)', 'art': 'wahl', 'vorgabe': '1b', 'werte': [
            ('1b', 'Sapiens 1B — 4,7 GB, mIoU 79,94 laut Dateiname (Vorgabe)'),
            ('0.6b', 'Sapiens 0.6B — 2,7 GB, mIoU 77,77 laut Dateiname (nicht gelaufen)'),
            ('0.3b', 'Sapiens 0.3B — 1,4 GB, mIoU 76,73 laut Dateiname (nicht gelaufen)'),
            ('sapiens2-0.4b', 'Sapiens2 0.4B — 1,6 GB, gemessen 09.10.2026: auch bunte und gerenderte Kleidung'),
            ('sapiens2-0.8b', 'Sapiens2 0.8B — 3,3 GB (nicht gelaufen)'),
        ], 'hinweis': 'Kleinere Modelle brauchen weniger Grafikspeicher und Zeit, der Hersteller nennt dafür eine niedrigere mIoU auf seinem Goliath-Datensatz (Zahl im Dateinamen, nicht von uns gemessen). '
                      'Eine 2B-Segmentierung ist auf Hugging Face nicht öffentlich. Beim ersten Lauf einer Größe lädt der Schritt ihre Gewichte (SHA-256 geprüft). '
                      'Sapiens2 (Meta, 2026, Sapiens2 License — verbietet u. a. biometrische Verarbeitung und Deepfakes) ist der Nachfolger mit denselben Klassen und dazu „Eyeglass“ '
                      '(hier Zubehör). Gemessen am 09.10.2026 auf 19 vorbereiteten Fotos: bei Edgars Fotos gleich wie Sapiens 1B (Säume innerhalb 1 cm), bei Randy (Hawaiihemd, '
                      'gerendert) blieben mit Sapiens 1B 35 % der freigestellten Person ohne Etikett — das Hemd fehlte in 5 von 8 Ansichten —, mit Sapiens2 0.4B 1,7 %; beim Zauberer '
                      '(Robe, gerendert) 97 % gegen 5 %. Grafikspeicher 2,7 statt 5,9 GB.'},
        {'schluessel': 'schuhe', 'titel': 'Schuhe (Left/Right_Shoe) werden …', 'art': 'wahl', 'vorgabe': 'fuesse', 'werte': [
            ('fuesse', 'Socken / Schuhe — ein Stück (Vorgabe)'),
            ('zubehoer', 'Zubehör'),
            ('haut', 'nicht Kleidung (Haut)'),
        ], 'hinweis': 'Ein Fuß in einer schwarzen Socke kommt bei Sapiens als „Shoe“ heraus (gemessen an Edgars Fotos, 04.10.2026) — deshalb gehören Schuhe und Socken in der Vorgabe zusammen.'},
        {'schluessel': 'socken', 'titel': 'Socken (Left/Right_Sock) werden …', 'art': 'wahl', 'vorgabe': 'fuesse', 'werte': [
            ('fuesse', 'Socken / Schuhe — ein Stück (Vorgabe)'),
            ('haut', 'nicht Kleidung (Haut)'),
        ]},
        {'schluessel': 'zubehoer', 'titel': 'Zubehör (Klasse Apparel) wird …', 'art': 'wahl', 'vorgabe': 'zubehoer', 'werte': [
            ('zubehoer', 'Zubehör (Vorgabe)'),
            ('oberteil', 'Teil des Oberteils'),
            ('haut', 'nicht Kleidung (Haut)'),
        ], 'hinweis': 'Apparel fasst bei Sapiens Kleidung zusammen, die weder Ober- noch Unterteil ist (Jacke, Mütze, Schal, Uhr …).'},
        {'schluessel': 'min_stimmen', 'titel': 'Mindeststimmen je Fläche (Pixel)', 'art': 'zahl', 'vorgabe': 4, 'min': 1, 'max': 50, 'schritt': 1, 'fein': True,
         'hinweis': 'So viele Pixel Stimme (nach dem Glätten) braucht eine Netzfläche, um als gesehen zu gelten; das Flächenbild hat rund 1,7 mm je Pixel. Mehr = weniger, dafür sicherere Flächen; die übrigen '
                    'folgen der Nachbarschaft oder der Regel.'},
        {'schluessel': 'glaettung', 'titel': 'Gewicht der Nachbarstimmen', 'art': 'zahl', 'vorgabe': 0.5, 'min': 0, 'max': 2, 'schritt': 0.1, 'fein': True,
         'hinweis': 'Die Stimmen der Kantennachbarn zählen mit diesem Gewicht gegen die eigenen — einzelne Flächen am Kragen oder Saum folgen ihrer Umgebung. 0 = jede Fläche allein.'},
        {'schluessel': 'nah_mm', 'titel': 'Reichweite für ungesehene Flächen (mm)', 'art': 'zahl', 'vorgabe': 15, 'min': 0, 'max': 60, 'schritt': 1, 'fein': True,
         'hinweis': 'So nah muss eine gesehene Fläche liegen, damit eine ungesehene (Innenwand der doppelwandigen Schale) ihr Stück übernimmt — die Wandstärke des Netzes. Weiter weg gilt die Regel.'},
        {'schluessel': 'raster', 'titel': 'Flächenbild (Kantenlänge in Pixeln)', 'art': 'zahl', 'vorgabe': 1600, 'min': 800, 'max': 2400, 'schritt': 100, 'fein': True,
         'hinweis': 'Das Netz wird je Ansicht als Flächennummern-Bild gezeichnet (Verdeckung); die Person ist darin rund 1.000 Pixel hoch. Größer = feiner, langsamer. Ändert, was gerechnet wird.'},
        {'schluessel': 'kante', 'titel': 'Foto vor dem Modell verkleinern auf (Pixel)', 'art': 'zahl', 'vorgabe': 2048, 'min': 1024, 'max': 4096, 'schritt': 256, 'fein': True,
         'hinweis': 'Die vorbereiteten Fotos haben 5.500–6.200 Pixel; das Modell sieht ohnehin nur 1024 × 768. Ändert, was gerechnet wird.'},
        {'schluessel': 'rand', 'titel': 'Rand um das Motiv vor dem Modell (%)', 'art': 'zahl', 'vorgabe': 5, 'min': 0, 'max': 20, 'schritt': 1, 'fein': True,
         'hinweis': 'Das Foto wird auf den Motivkasten zugeschnitten, bevor das Modell es sieht (die Person füllt im Quadrat nur 7–11 %); so viel Luft bleibt rundum. Ändert, was gerechnet wird.'},
    ]
    #: Was die Etiketten ändert (`Sapiensstand.RECHENOPTIONEN`, Wrapper-Seite) — ein Test hält die beiden gleich.
    RECHENOPTIONEN = ('modell', 'raster', 'kante', 'rand')

    @classmethod
    def vorgaben(cls):
        return {e['schluessel']: e['vorgabe'] for e in cls.KATALOG}

    @classmethod
    def katalog(cls):
        aus = []
        for e in cls.KATALOG:
            werte = [{'wert': w, 'text': t} for w, t in e.get('werte', [])]
            aus.append(dict(e, werte=werte, fein=bool(e.get('fein'))))
        return {'optionen': aus, 'fein_titel': 'Feineinstellungen der Segmentierung (Schwellen, Auflösung)'}

    @classmethod
    def pruefen(cls, roh):
        """Nur bekannte Schlüssel mit erlaubten Werten (Zahlen auf den Bereich geklemmt, ganzzahlig bei ganzem Schritt) — der Rest wird Vorgabe."""
        roh = roh if isinstance(roh, dict) else {}
        aus = cls.vorgaben()
        for e in cls.KATALOG:
            wert = roh.get(e['schluessel'])
            if wert is None:
                continue
            if e['art'] == 'wahl':
                if str(wert) in [w for w, _ in e['werte']]:
                    aus[e['schluessel']] = str(wert)
            elif e['art'] == 'zahl':
                try:
                    zahl = float(min(e['max'], max(e['min'], float(wert))))     # `float`: an einer ganzzahligen Grenze (max 2) bliebe sonst ein int übrig
                except (TypeError, ValueError):
                    continue
                aus[e['schluessel']] = int(round(zahl)) if isinstance(e['schritt'], int) and isinstance(e['vorgabe'], int) else round(zahl, 3)
        return aus

    @classmethod
    def rechenoptionen(cls, optionen):
        """Aus einer (geprüften) Gruppe nur das, was die Etiketten ändert — dieselbe Form, die der Runner im Stand ablegt (`Sapiensstand.rechenoptionen`)."""
        o = cls.pruefen(optionen)
        return {'modell': str(o['modell']), 'raster': int(o['raster']), 'kante': int(o['kante']), 'rand': float(o['rand'])}
