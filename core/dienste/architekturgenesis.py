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
        ('meshto3d/meshfigur_modell.py', 'Meshfigurmodell',
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

    #: Die Bausteine des Fittings (11.10.2026, Abschnitt „Fitting der Kleider" der Seite) — dieselbe Prüfung wie bei `BAUSTEINE`.
    FITTING = [
        ('Genesis9/kollision.py', 'G9kollision',
         'Heben aus der Fläche: Punkt entlang der Normale des nächsten Flächenpunkts auf ABSTAND 3 mm, `DURCHGAENGE` 2 (Dazs Collision Iterations), '
         'zuerst der Käfig, danach ein feiner Durchgang nur nahe Käfigpunkten (`stufenweise`)'),
        ('Genesis9/lagen.py', 'G9lagen', 'Stück gegen Stück: welches liegt unter welchem (Tiefenregel, Saum über Bund); `kaefig` = was die Lagenrechnung vom Stück sieht'),
        ('Genesis9/lagenflaeche.py', 'G9lagenflaeche',
         'Kollisionsfläche des äußeren Stücks: Haut, wo nackt, sonst der Käfig der inneren Stücke; bei einer Anatomie nur die Haut unter ihrem Fußabdruck ersetzt'),
        ('Genesis9/stueckstarr.py', 'G9stueckstarr',
         'Ein Stück mit Hauttiefe (Anatomie) liegt starr in seiner Ruhelage — dieselben Punkte für Anzeige und Lagenrechnung'),
        ('HumanBodyWeb/core/dienste/g9lagenanfrage.py', 'G9lagenanfrage',
         'Die getragenen Stücke einer Anfrage einordnen; die Anatomie liegt unter jedem Stück'),
        ('HumanBodyWeb/core/dienste/g9stueckteile.py', 'G9stueckteile', 'Die Rechnung hinter einer Stückantwort: Käfig, Lagen, Browsernetz'),
        ('Genesis9/koerpernetz.py', 'G9koerpernetz', 'Körperfläche (mit HD) und `folgernetz`: das Stück auf die Kollisionsfläche heben'),
        ('Genesis9/stueckersatz.py', 'G9stueckersatz', 'Die `.ersetzt.json` eines Stücks: `haut_tiefe_mm`, `loch` (die entfallenden Hautdreiecke), `anatomie`'),
    ]

    #: Mesh → Genesis (28.10.2026, Abschnitt 12 der Seite): die zwei Portierungen und ihre Teile — dieselbe Prüfung.
    MESH = [
        ('Genesis9/meshgenesis.py', 'G9meshgenesis', 'Ablauf: Verfahren aus Einstellungen → 2d-3d-AI, Ableitung im Speicher, Einpassen, nach innen, Mesh-Regler'),
        ('Genesis9/meshipnet.py', 'G9meshipnet', 'IPNet fit_SMPL_IPNet + fit_SMPLD (Adam, Abstand Punkt ↔ Fläche, Chamfer je Teil, Versatz mit Laplace)'),
        ('Genesis9/meshtransfer.py', 'G9meshtransfer', 'smplx transfer_model (Kantenstufe, Punktstufe, minimize)'),
        ('Genesis9/trustregion.py', 'G9trustregion', 'torch-trust-ncg, Weg cg (Steihaug)'),
        ('Genesis9/meshkoerper.py', 'G9meshkoerper', 'Genesis als SMPL-artiges Körpermodell: Regler, Haltung (Rodrigues, Kette), Versatz, Haut'),
        ('Genesis9/meshflaeche.py', 'G9meshflaeche', 'kaolin point_to_surface, laplacian_loss; IPNet chamfer_distance'),
        ('Genesis9/meshformung.py', 'G9meshformung', 'G9formung auf der Karte: Mesh-Morph geschlossen, Null-Probe'),
        ('Genesis9/meshableitung.py', 'G9meshableitung', 'Ableitung aller Regler in einem Stapel auf der Karte: Formgraph, Knochenmatrizen Ebene für Ebene mit Drehung, Haut'),
        ('Genesis9/meshgrundstellung.py', 'G9meshgrundstellung', 'genauer Weg (CPU) für Regler, deren Drehung aus Faktor- oder seltenen Formeln kommt'),
        ('Genesis9/meshinnen.py', 'G9meshinnen', 'Ziel nach innen, Hülle ohne vergrabene Dreiecke, Abstand mit Vorzeichen, Zahlen, Rest „nach innen“'),
        ('Genesis9/meshvorzeichen.py', 'G9meshvorzeichen', 'innen/außen: Pseudo-Normale am nächsten Punkt, Windungszahl, vergrabene Dreiecke'),
        ('Genesis9/meshinnenstufe.py', 'G9meshinnenstufe', 'Versatzfeld glatt ins Ziel (Adam, Laplace, Strafverfahren)'),
        ('Genesis9/reglersperre.py', 'G9reglersperre', 'Regler, die eine KI nicht stellen darf — nur im Bedienfeld'),
        ('Genesis9/meshgrenzen.py', 'G9meshgrenzen', 'Haltung in Daz\' Gelenkgrenzen (Genesis9.dsf), Euler je Reihenfolge'),
        ('Genesis9/meshziel.py', 'G9meshziel', 'Das Ziel: Punkte, Normalen, Klasse je Punkt, Teile'),
        ('Genesis9/meshregler.py', 'G9meshregler', 'Kategorie „Mesh“: je Körperteil ein Eigenmorph'),
        ('HumanBodyWeb/core/dienste/ai2d3dmeshwahl.py', 'Ai2d3dmeshwahl', 'Einstellung: welche Portierung'),
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
    def fitting(cls):
        return [cls.zeile(*eintrag) for eintrag in cls.FITTING]

    @classmethod
    def mesh(cls):
        return [cls.zeile(*eintrag) for eintrag in cls.MESH]

    @classmethod
    def kontext(cls):
        return {'stand': cls.STAND, 'bausteine': cls.bausteine(), 'fitting': cls.fitting(), 'mesh_bausteine': cls.mesh()}
