# -*- coding: utf-8 -*-
u"""Kleidungsverfahren — die sechs Wege, wie ein Stueck an einen Koerper kommt.

Ueber die Jahre sind in diesem Projekt sechs verschiedene Verfahren
entstanden, und sie unterscheiden sich nicht in Kleinigkeiten, sondern im
Prinzip: Fuenf davon NEHMEN ein fertiges Netz und bringen es an einen
Koerper; eines KONSTRUIERT das Stueck aus Koerpermassen und laesst es dann
fallen.

Diese Tabelle ist die Stammdatenquelle der Hilfeseite „Kleidung —
Allgemein". Sie steht bewusst hier und nicht in der Vorlage: Eine Zahl im
HTML ist eine Behauptung, die niemand mehr nachrechnet.

WOHER DIE MESSWERTE STAMMEN
===========================
Jede Zahl in `messung` hat eine Quelle in `beleg`. Wo nichts gemessen ist,
steht das ausdruecklich da — eine leere Zelle sieht sonst aus wie eine Null.
"""


class Kleidungsverfahren:
    u"""Die Verfahren, ihre Prinzipien und was an ihnen gemessen ist."""

    #: Je Verfahren: Schluessel, Name, Herkunft des Stuecks, Prinzip,
    #: Anpassung an Morphs, Simulation, Messwerte, Code, Beleg.
    VERFAHREN = [
        {
            'schluessel': 'garmentcode',
            'name': 'GarmentCode',
            'traeger': 'HumanBody-Figur, SMPL-Referenzkörper, SMPL-Varianten',
            'herkunft': 'Kein fertiges Netz — ein Schnittmuster, aus 26 '
                        'Körpermaßen konstruiert',
            'prinzip': 'Zweidimensionale Schnittteile werden vernäht und in '
                       'einer Stoffsimulation (Warp XPBD) auf den Körper '
                       'fallen gelassen. Danach holt eine geometrische '
                       'Korrektur eingesunkene Punkte heraus.',
            'morphs': 'Vollständig: Ein anderer Körper ergibt einen anderen '
                      'Schnitt, nicht nur eine andere Verformung.',
            'simulation': 'Ja — rund 20 s je Stück (Median über 75 Läufe)',
            'messung': 'Hautabstand 17,3 mm Median, Durchstich unter 0,16 %',
            'code': 'GarmentCode/, core/dienste/garmentcode.py, '
                    'garmentdrapierung.py, garmentkoerper.py',
            'beleg': 'test/HumanBody_local/messung_alle_stuecke.yaml '
                     '(5 Körper × 15 Stücke)',
            'katalog': '15 Stücke (Katalog.STUECKE)',
        },
        {
            'schluessel': 'mh_eigen',
            'name': 'MakeHuman auf der MakeHuman-Figur',
            'traeger': 'MakeHuman-Basiskörper (19.158 Punkte)',
            'herkunft': '.mhclo aus der Kleiderbibliothek',
            'prinzip': 'Die .mhclo hängt jeden Stoffpunkt an drei '
                       'Körperpunkte: Punkt = w1·K[v1] + w2·K[v2] + w3·K[v3] '
                       '+ Versatz. Auf dem Körper, für den das Stück '
                       'entworfen wurde, ist das keine Näherung, sondern die '
                       'Definition.',
            'morphs': 'Vollständig: Jede Reglerbewegung rechnet Körper und '
                      'Kleidung neu.',
            'simulation': 'Nein',
            'messung': 'Hautabstand: Anzug 8,2 mm, Schuhe 7,5 mm, '
                       'Kleid 13,5 mm',
            'code': 'MakeHuman/kleidnetz.py, loeschmaske.py',
            'beleg': 'CLAUDE.md, Abschnitt „Kleidung auf der '
                     'MakeHuman-Figur" (06.09.2026)',
            'katalog': '181 Stücke mit .mhclo',
        },
        {
            'schluessel': 'mh_proxy',
            'name': 'MakeHuman auf der HumanBody-Figur',
            'traeger': 'MB-Lab/Rigify-Körper (18.210 bzw. 17.996 Punkte)',
            'herkunft': 'Dieselbe .mhclo wie oben',
            'prinzip': 'Dasselbe Verfahren, aber auf einem FREMDEN Körper. '
                       'Das braucht sieben Nacharbeitsschritte: glätten, '
                       'abrücken, skalieren, heben, von T- auf A-Pose, aus '
                       'dem Körper schieben — jeder mit einem Regler.',
            'morphs': 'Ja, über dieselbe Zuordnung — aber die Nacharbeit '
                      'muss dabei stehen bleiben.',
            'simulation': 'Nein',
            'messung': '14,3 % der Anker fallen auf EINEN Körpervertex; '
                       'Shrinkwrap liefert bis 36 % Punkte im Körper',
            'code': 'MakeHuman/proxy_anpassung.py, '
                    'static/viewer/…/mhproxy_anpassen.js',
            'beleg': 'core/dienste/garmentcode.py, Modulkopf (06.09.2026)',
            'katalog': 'dieselben 181 Stücke',
        },
        {
            'schluessel': 'bibliothek',
            'name': 'Kleiderbibliothek-Anpassung',
            'traeger': 'HumanBody-Figur',
            'herkunft': 'Netz aus der Kleiderbibliothek (7 Kategorien)',
            'prinzip': 'Zwei Wege: um den Körper oder um eine Hülle. Die '
                       'Knochengewichte kommen jeweils vom nächsten '
                       'Körperpunkt.',
            'morphs': 'Ja, über die Neuanpassung',
            'simulation': 'Nein',
            'messung': 'nicht gemessen',
            'code': 'core/dienste/kleidungsanpassung.py, '
                    'kleidungswerkzeuge.py',
            'beleg': 'Modulkopf kleidungsanpassung.py (15.08.2026)',
            'katalog': '181 Stücke (Kleiderbibliothek)',
        },
        {
            'schluessel': 'smpl',
            'name': 'SMPL-Garderobe',
            'traeger': 'SMPL-X-Netz, danach der Projektkörper',
            'herkunft': 'SmplGarmentLibrary',
            'prinzip': 'Das Kleidungsnetz wird mit Abstand und Steifigkeit '
                       'an den Projektkörper gebracht.',
            'morphs': 'Ja (Regler kommen mit der Anfrage)',
            'simulation': 'Nein',
            'messung': 'nicht gemessen',
            'code': 'core/api/smpl.py (kleid_anpassen)',
            'beleg': 'core/api/smpl.py, Zeile 162 ff.',
            'katalog': 'SmplGarmentLibrary',
        },
        {
            'schluessel': 'uma',
            'name': 'UMA-Garderobe',
            'traeger': 'UMA-Figur (Unity)',
            'herkunft': 'UMA-Rezepte aus den Text-Assets des '
                        'Unity-Projekts',
            'prinzip': 'Angezogen wird nicht im Browser, sondern in Unity: '
                       'Der Bauer bekommt die Rezeptnamen als Argument und '
                       'liefert eine fertige GLB zurück.',
            'morphs': 'Über die UMA-DNA (Knochen), nicht über Punkte',
            'simulation': 'Nein',
            'messung': 'nicht gemessen',
            'code': 'core/api/umakleidung.py, core/dienste/umabauer.py, '
                    'UMA/',
            'beleg': 'CLAUDE.md, Abschnitt „UMA-Figur auf Zuruf bauen"',
            'katalog': 'Rezepte je Rasse und Platz',
        },
    ]

    #: Was GarmentCode grundlegend von den anderen fuenf trennt. Jede
    #: Zeile: (Frage, die anderen fuenf, GarmentCode).
    UNTERSCHIED = [
        ('Was ist die Quelle?',
         'Ein fertiges 3D-Netz, von jemandem modelliert',
         'Ein Programm, das aus Maßen ein Schnittmuster konstruiert'),
        ('Wie kommt es an den Körper?',
         'Jeder Stoffpunkt wird an Körperpunkte gebunden oder auf die '
         'Oberfläche gezogen',
         'Die Schnittteile werden vernäht und fallen in einer Simulation '
         'auf den Körper'),
        ('Was passiert bei einem anderen Körper?',
         'Dasselbe Netz wird anders verformt — die Machart bleibt',
         'Ein anderes Schnittmuster entsteht; Nähte und Abnäher wandern mit'),
        ('Woran scheitert es?',
         'An Stellen, für die das Netz nie gedacht war (Anker fallen '
         'zusammen, Stoff sinkt ein)',
         'An Maßkombinationen, die sich nicht konstruieren lassen — '
         'sichtbar als Abbruch, nicht als schiefes Bild'),
        ('Wie lange dauert es?',
         'Millisekunden bis Sekunden',
         'Rund 20 Sekunden je Stück'),
        ('Was kann man einstellen?',
         'Sitz und Aussehen (Abstand, Glättung, Farbe)',
         'Die Machart selbst: Ärmellänge, Kragenform, Rockweite, '
         'Abnäher — plus Stoffparameter der Simulation'),
        ('Wovon hängt die Qualität ab?',
         'Davon, wie ähnlich der Träger dem Entwurfskörper ist',
         'Davon, wie gut die Körpermaße gemessen sind'),
    ]

    @classmethod
    def alle(cls):
        return list(cls.VERFAHREN)

    @classmethod
    def unterschied(cls):
        return list(cls.UNTERSCHIED)
