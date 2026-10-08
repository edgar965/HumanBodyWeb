# -*- coding: utf-8 -*-
"""Architekturgenesis — die Daten der Seite Hilfe → Architektur → Genesis (08.10.2026).

Edgar (08.10.2026): „schreibe das hinein in eine neue Seite Hilfe - Architektur - Genesis" — gemeint ist das Konzept
„Blender-Modell als Genesis-Figur importieren" (`Docu/konzepte/2026-10-08_blend-import-als-genesis-figur-konzept.md`).
Der Text der Seite steht von Hand in den Vorlagen `hilfe/architektur_genesis*.html`; hier steht nur, was gegen den
Code geprüft wird: die BAUSTEINE, auf die das Konzept aufsetzt. Je Baustein werden Datei und Klasse beim Aufruf der
Seite gesucht — fehlt eine, steht das in der Tabelle (und der Test `test_hilfe_architektur_genesis` wird rot), statt
dass die Seite eine Klasse nennt, die es nicht mehr gibt.
"""

import logging
import re

from django.conf import settings

logger = logging.getLogger(__name__)

__all__ = ['Architekturgenesis']


class Architekturgenesis:
    #: Stand des Konzepts und der Messungen an `cute girl 5.0.blend`.
    STAND = '08.10.2026'

    #: (Pfad relativ zu `TOOLS_ROOT`, Klasse, Rolle im Konzept) — die Bausteine, die es heute schon gibt.
    BAUSTEINE = [
        ('HumanBodyWeb/static/viewer/charakter/szene_dialoge.js', '',
         'Datei → Modell importieren: liest heute nur JSON im Browser; bekommt die Wahl .blend'),
        ('HumanBodyWeb/core/dienste/meshfigurlauf.py', 'Meshfigurlauf',
         'Mesh to 3D: Vorbild für den Auftrag mit Schritten; seine Erkennung wird NICHT übernommen'),
        ('VideoToBVH/wrappers/meshfigur_modell.py', 'Meshfigurmodell',
         'Regler-Fit (Größe → Körpertyp → Bereiche, Gesichtskette) gegen den umgeposten Körper'),
        ('Genesis9/direktmorph.py', 'G9direktmorph',
         'Eigenmorph je Käfigpunkt — hier auf den ganzen Körper, weil Haltung und Haut stimmen'),
        ('Genesis9/restmorph.py', 'G9restmorph', 'Rest-Eigenmorph (Weg von Mesh to 3D)'),
        ('Genesis9/eigenmorphe.py', 'G9eigenmorphe', 'Ablage eigen:<kennung>, Wert 0…2'),
        ('HumanBodyWeb/core/dienste/meshfigurende.py', 'Meshfigurende', 'Rest und Textur am Ende von Mesh to 3D'),
        ('HumanBodyWeb/core/dienste/meshfigurspeichern.py', 'Meshfigurspeichern',
         'Modell <Name> in data/models (quelle genesis9)'),
        ('HumanBodyWeb/core/dienste/modelltexturen.py', 'Modelltexturen',
         'Fotohaut beim Modell (data/models/Texturen/<Modell>/)'),
        ('HumanBodyWeb/static/viewer/gemeinsam/genesis9fototextur.js', 'Genesis9fototextur',
         'ersetzt heute nur die Albedo — muss Normalen und Rauheit mitnehmen'),
        ('Genesis9/eigenstueck.py', 'G9eigenstueck', 'schreibt ein Netz als Genesis-Stück in die eigene Bibliothek'),
        ('Genesis9/dsonschreiber.py', 'G9dsonschreiber', '.duf, .dsf (Netz, UV, Haut), Texturen, .dsx (Kategorie)'),
        ('HumanBodyWeb/core/dienste/fotostuecke.py', 'Fotostuecke',
         'Vorbild: roh schreiben, Ruhelage der Grundfigur zurückrechnen, neu schreiben'),
        ('HumanBodyWeb/core/dienste/herrenhaarstueck.py', 'Herrenhaarstueck',
         'Vorbild für die Frisur: alles an head, Art Hair'),
        ('Genesis9/folger.py', 'G9folger', 'Stück folgt den Körpermorphs (Projektion auf 3 Körperpunkte)'),
        ('Genesis9/koerperhaut.py', 'G9koerperhaut', 'Häutung des Stücks vom Körper statt der ARP-Gewichte'),
        ('Genesis9/passform.py', 'G9passform', 'Regler Länge −20…20 cm, Weite −3…6 cm für Art kleidung'),
        ('Genesis9/haarachsen.py', 'G9haarachsen', 'Regler der Frisuren'),
        ('Genesis9/dazkategorien.py', 'G9dazkategorien', 'Kategorie aus der .dsx (Shorts/Oberteile nach dem Namen)'),
        ('Genesis9/garderobekategorien.py', 'G9garderobekategorien',
         'Edgars Zuordnung über der Vorgabe (garderobe_kategorien.json)'),
        ('Genesis9/texturverkleinerung.py', 'G9texturverkleinerung', 'Browser-Grenze 4096 px je Kante'),
        ('Genesis9/browserbilder.py', 'G9browserbilder', 'schwere Bilder erst mit Strg+Alt+H (20 / 120 MB)'),
    ]

    @classmethod
    def zeile(cls, pfad, klasse, rolle):
        """Ein Baustein mit Befund: gibt es die Datei, steht die Klasse darin, wie lang ist sie?"""
        datei = settings.TOOLS_ROOT / pfad
        zeile = {'pfad': pfad, 'klasse': klasse, 'rolle': rolle, 'zeilen': 0, 'fehlt': ''}
        try:
            text = datei.read_text(encoding='utf-8')
        except OSError as fehler:
            logger.warning('Architektur Genesis: %s nicht lesbar: %s', pfad, fehler)
            zeile['fehlt'] = 'Datei fehlt'
            return zeile
        zeile['zeilen'] = text.count('\n') + 1
        if klasse and not re.search(r'^(export\s+)?class\s+%s\b' % re.escape(klasse), text, re.MULTILINE):
            zeile['fehlt'] = 'Klasse fehlt'
        return zeile

    @classmethod
    def bausteine(cls):
        return [cls.zeile(*eintrag) for eintrag in cls.BAUSTEINE]

    @classmethod
    def kontext(cls):
        return {'stand': cls.STAND, 'bausteine': cls.bausteine()}
