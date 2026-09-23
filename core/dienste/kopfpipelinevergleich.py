# -*- coding: utf-8 -*-
"""Kopfpipelinevergleich — alle Foto-zu-3D-Kopf-Verfahren, gemessen und recherchiert.

Edgar (22.09.2026): „mach seite Hilfe - Foto - 3D in der du alle Modell erwähnst … mach
mit was automatisches, recherchiere was von denen am besten ist, und was davon du
nachbauen kannst" — KeenTools FaceBuilder, Reallusion Headshot 3, Epic MetaHuman
Creator, Tripo3D, Meshy, Hyper3D Rodin.

**Zwei getrennte Gruppen, nicht eine Rangliste** — die beiden sind nicht vergleichbar:

    GEMESSEN   In diesem Projekt eingebaut UND getestet (`Bildmodellkopf`, Schritt
               „Kopf"): mica, mehrbild, pymafx_flame. Zahlen aus einem echten Lauf an
               Damiras Fotos, 22.09.2026 (Procrustes-Abstand zur PyMAF-X-Referenz).
    EXTERN     Kommerzielle/fremde Werkzeuge — nur RECHERCHIERT (Web, 22.09.2026),
               NICHT an unseren Fotos getestet. Jede Zeile trägt ihre Quelle; keine
               Zahl hier ist eine eigene Messung (`keine-unbelegten-zahlen.md`).

`nachbaubar` bei EXTERN: ob sich das Werkzeug ohne Handarbeit (Blender-Klicks,
Character-Creator-GUI) in `Bildmodellkopf` einbinden ließe — nicht, ob es gut ist.
"""


class Kopfpipelinevergleich:
    #: Ein Lauf an Damiras Fotos (2 Kopffotos, schwache Qualität — ein kleiner,
    #: entfernter Seitenausschnitt) — Procrustes-Abstand (Drehung/Verschiebung, kein
    #: Maßstab) zur PyMAF-X-Referenz desselben Auftrags. Kein Ground-Truth-Scan; eine
    #: Einordnung der beiden Verfahren zueinander, keine absolute Genauigkeitsaussage.
    MESSUNG = {
        'auftrag': 'Damira Silhouetten (2026.09.20.12.37.57)',
        'fotos': 2,
        'datum': '22.09.2026',
        'referenz': 'PyMAF-X-Kopf desselben Auftrags (Procrustes ohne Maßstab)',
    }

    GEMESSEN = [
        {
            'name': 'MICA', 'schluessel': 'mica',
            'automatisch': True,
            'fotos': 'ab 1 Foto (mehrere werden gemittelt)',
            'abstand_mm': 1.9, 'abstand_max_mm': 7.8,
            'dauer': '~8–17 s je Foto (ArcFace + Generator, einmal Modell laden)',
            'beschreibung': 'ArcFace-Identität → 300 FLAME-Formparameter (Zielon et al. 2022). '
                'Metrisch, ohne Ausdruck/Pose — braucht nicht mal ein frontales Foto.',
        },
        {
            'name': 'Mehrbild-Anpassung', 'schluessel': 'mehrbild',
            'automatisch': True,
            'fotos': 'mehrere gemeinsam (Bündelausgleichung) — Zweck verfehlt mit nur einem',
            'abstand_mm': 3.7, 'abstand_max_mm': 17.2,
            'dauer': '~76 s für 2 Fotos (steigt mit der Fotozahl)',
            'beschreibung': 'Eigener Ersatz für KeenTools FaceBuilder ohne Blender: insightface-'
                'Gesichtspunkte je Foto, EIN FLAME-Kopf gemeinsam angepasst. In diesem einen Test '
                'schlechter als MICA (schwache, kleine Fotos) — sollte mit mehreren guten Ansichten '
                '(vorn + Seite) aufholen, das ist hier noch nicht geprüft.',
        },
        {
            'name': 'PyMAF-X (FLAME)', 'schluessel': 'pymafx_flame',
            'automatisch': True,
            'fotos': 'je Foto einzeln, dann gemittelt',
            'abstand_mm': None, 'abstand_max_mm': None,
            'dauer': 'läuft mit der Körperschätzung mit',
            'beschreibung': 'Ist in der Messung oben die REFERENZ, kein eigener Abstandswert. '
                'Kommt aus dem Körperschätzer selbst, ohne eigenen Gesichtsdetektor.',
        },
    ]

    #: `nachbaubar`: (moeglich, grund) — ob eine Automatisierung ohne GUI realistisch ist.
    EXTERN = [
        {
            'name': 'KeenTools FaceBuilder', 'art': 'Blender-Plugin, kostenpflichtig',
            'nachbaubar': (None, 'Ungeklärt — nur mit Edgars Lizenz + Blender vor Ort zu prüfen, ob '
                'die Python-API eine Anpassung ganz ohne manuelle Pins headless hergibt'),
            'staerke': 'Sehr genau DURCH manuelle Pin-Korrektur (Lippen, Nasenkurven, Hautfalten '
                'einzeln nachziehbar) — das ist der Kern des Produkts, nicht die Automatik.',
            'einschaetzung': 'Die automatische Anpassung OHNE Pins (das, was ohne Handarbeit übrig '
                'bliebe) ist nicht das, was KeenTools auszeichnet — unklare Genauigkeit ungeprüft.',
            'quelle': 'https://keentools.io/integrations/fbb-mh',
        },
        {
            'name': 'Reallusion Headshot 3', 'art': 'Character-Creator-Plugin, kostenpflichtig',
            'nachbaubar': (False, 'Community fragt im Reallusion-Forum selbst danach — keine '
                'offizielle Automatisierung/Kommandozeile bekannt (Stand 22.09.2026)'),
            'staerke': '„Scan-Qualität" laut Hersteller, für Game-Ready-Charaktere in Character '
                'Creator (Kleidung, Haare, Export nach Unreal/Unity/Blender/Maya).',
            'einschaetzung': 'Reines GUI-Werkzeug — nicht automatisch in unsere Pipeline einbindbar.',
            'quelle': 'https://forum.reallusion.com/417157/Is-there-any-api-or-command-line-tool',
        },
        {
            'name': 'Epic MetaHuman Creator', 'art': 'Cloud-Portal / Unreal Engine, kostenlos',
            'nachbaubar': (False, 'Nimmt eher ein FERTIGES Kopfnetz entgegen („Mesh to MetaHuman") '
                'statt eins aus Fotos zu erzeugen — falsche Aufgabe für diesen Schritt'),
            'staerke': 'AAA-Rig für Unreal Engine (Gesichtsrig, Groom-Haare, LODs, Live-Link-Face) —'
                ' für Echtzeit-Digital-Humans, nicht für Genesis-9-Kopfform aus Fotos.',
            'einschaetzung': 'Löst eine andere Aufgabe (Rigging fürs Rendern in Unreal), kein Ersatz '
                'für den Schritt „Kopf" hier.',
            'quelle': 'https://medium.com/keentools/keentools-facebuilder-x-metahuman-guide-81bc193ef2a',
        },
        {
            'name': 'Tripo3D / Meshy / Hyper3D Rodin', 'art': 'Cloud-KI, kostenpflichtige HTTP-API',
            'nachbaubar': (True, 'Echte dokumentierte REST-APIs (Bearer-Auth, JSON) — $0,10–$0,40 '
                'je Bild, technisch ohne Weiteres als eigener Runner-Schritt andockbar'),
            'staerke': 'Allzweck-Bild-zu-3D (Produkte, Kreaturen, Charaktere); Rodin gilt laut '
                'Testberichten als am fotorealistischsten der drei.',
            'einschaetzung': 'NICHT auf Gesichts-Identität trainiert wie MICA (ArcFace) — liefert '
                'einen plausiblen, nicht zwingend zutreffenden Kopf; Ausgabe wäre kein FLAME-Netz, '
                'bräuchte einen zusätzlichen Anpassungsschritt wie bei „Mehrbild". Ungetestet an '
                'unseren Fotos — Edgars Freigabe + API-Key vorausgesetzt (Fotos gehen an Dritte).',
            'quelle': 'https://developer.hyper3d.ai/api-specification/rodin-generation',
        },
    ]

    @classmethod
    def gemessen(cls):
        return cls.GEMESSEN

    @classmethod
    def extern(cls):
        return cls.EXTERN
