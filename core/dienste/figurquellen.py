# -*- coding: utf-8 -*-
"""Figurquellen — hochauflösende, realistische Ganzkörper-Figuren im Vergleich.

Die Rangliste der Seite „Hilfe → Architektur → Andere Modelle". Edgar
(17.09.2026): „schau im Internet, github nach, ob wir hochauflösende meshes
kriegen für Frauen / Männer … Ziel wäre es, das HumanBody Mesh zu erweitern
mit fotorealistischer Qualität" — „Mach eine Tabelle absteigend nach
Qualität (Punkte, Dreiecke)" — „ich brauche ganze Körper, mach getrennte
Liste für nur Kopf" (`figurkoepfe.py`) — „schreibe in die Liste auch
MakeHuman, mein HumanBody, UMA, SMPL und SMPL-X, mach die alle rot und
vergib denen auch einen Rang" (`eigen`) — „mach getrennte Spalten für die
Punkte, Vierecke … mach irgendetwas, mit dem man alles vergleichen kann"
(`Netzmasse`: Vergleichsgröße Dreiecke der höchsten Stufe, Rang daraus).

Jede Zeile trägt die ROHEN Angaben, so wie die Quelle sie nennt (`punkte`,
`vierecke`, `dreiecke` des Basisnetzes, `stufen` Unterteilungen, `hoechste`
wenn der Hersteller die oberste Stufe beziffert); `Netzmasse.rangfolge`
rechnet Texte, Vergleichszahl und Rang. Die eigenen Figurarten sind aus den
Dateien gezählt: HumanBody `HumanBody/data/humanBody`, MakeHuman
`MakeHuman/makehuman/data/3dobjs/base.obj` (Gruppe `body`, ohne Helfer),
UMA `.claude/rules/uma.md` (lodRanges[0]), SMPL `VideoToBVH/models/smpl/
SMPL_NEUTRAL.pkl`, SMPL-X `3DObjects/Archiv/SMPL-X/SMPLX_NEUTRAL.npz`.
Adressen: `figurquellenlinks.py`; Bilder: `figurbilder.py`.
"""

from .netzmasse import Netzmasse

__all__ = ['Figurquellen']

_3DSS_STUFEN = 'ZBrush-Stufe 6 (5 Unterteilungen), OBJ/FBX bei Stufe 1'


class Figurquellen:
    """Rangliste der Ganzkörper, Stand von HumanBody und der Befund der Suche."""

    #: Das eigene Netz (MB-Lab), nachgezählt in `HumanBody/data/humanBody`.
    STAND = {'punkte': '18.210', 'vierecke': '17.288', 'haut': '2K Albedo, 4K Bump, 2K Rauheit (MB-Lab)'}

    BEFUND = (
        'Über 32.000 Basis-Vierecke mit echtem Scan-Detail bis Stufe 6, sauber '
        'retopologisiert und für beide Geschlechter, gibt es nur bei 3D Scan '
        'Store. Triplegangers und Ten24 liefern Rohscans mit 15 Mio. Dreiecken, '
        'die man selbst retopologisieren müsste (Wrap, ZBrush). Anatomy 360 '
        'verkauft Pose-Scans nur im eigenen Viewer, nicht als Netz. GitHub '
        'liefert dafür fast nichts — einen CC0-Spiegel des Blender-Bundles und '
        'Werkzeuge. Reine Kopfmodelle stehen in der zweiten Liste.'
    )

    #: Bildunterschriften der eigenen Workbench-Renderings (Ordner 00).
    RENDERINGS = {
        'humanbody_kopf_cc2.png': 'HumanBody (MB-Lab) + 2 Stufen Catmull-Clark',
        'genesis9_kopf_sub2.png': 'Daz Genesis 9 + 2 Stufen Unterteilung',
        'frau_kopf_stufe0.png': 'Blender Base Mesh Frau, Basis (Multires 0)',
        'frau_kopf_stufe3.png': 'Blender Base Mesh Frau, Multires 3',
        'frau_stufe3.png': 'Blender Base Mesh Frau, Multires 3',
        'mann_stufe3.png': 'Blender Base Mesh Mann, Multires 3',
        'vergleich_koepfe.png': 'MB-Lab + CC2 · Genesis 9 + SubD 2 · Blender CC0 + Multires 3',
    }

    ZEILEN = [
        {
            'ordner': '02_3DScanStore_Ultimate_Textured',
            'name': '3D Scan Store „Ultimate Textured Base Mesh"',
            'zusatz': '',
            'vierecke': 32_976,
            'stufen': 5,
            'stufen_text': _3DSS_STUFEN,
            'texturen': '16K-PSD / 8K Farbe + Hautdetail',
            'geschlecht': 'ja',
            'rig': 'A-/T-Pose; kein Rig',
            'preis': '29,99 £ / 49,99 £ beide',
            'lizenz': 'privat',
            'urteil': 'Der günstigste Weg zu Scan-Qualität beider Geschlechter; Rigify-Rig selbst bauen.',
        },
        {
            'ordner': '15_3DScanStore_AnimationReady_Scans',
            'name': '3D Scan Store „Animation Ready Body Scan"',
            'zusatz': '33 Frauen, 33 Männer — je eine echte Person',
            'vierecke': 32_076,
            'stufen': 5,
            'stufen_text': _3DSS_STUFEN,
            'texturen': '16K Farbe, Normal, Spec, Rauheit',
            'geschlecht': 'ja',
            'rig': 'A-Pose, Augen, Mund, Wimpern; kein Rig',
            'preis': '69,99 £ je Person',
            'lizenz': 'privat/nicht-kommerziell',
            'urteil': 'Die realistischste Quelle: jede Datei ist eine reale Person '
            'mit ihrer eigenen Haut (16K), kein Durchschnittskörper. '
            'Kein Einbau in „character maker programme" — nur privat.',
        },
        {
            'ordner': '01_3DScanStore_Morphable_Frau_Mann',
            'name': '3D Scan Store „Morphable Base Mesh"',
            'zusatz': '',
            'vierecke': 32_076,
            'stufen': 5,
            'stufen_text': _3DSS_STUFEN,
            'texturen': '16K Farbe, Normal, Spec, Rauheit, Cavity',
            'geschlecht': 'ja',
            'rig': '3 Körpertypen je Geschlecht; kein Rig',
            'preis': '69,99 £ Frau / 119,99 £ beide',
            'lizenz': 'privat',
            'urteil': 'Dasselbe Netz wie die Scans, als Durchschnittskörper in drei '
            'Statuen — die Basis, wenn Morphs wichtiger sind als eine '
            'bestimmte Person.',
        },
        {
            'ordner': '09_Eisko_Louise_FreakyHoody',
            'bildmuster': 'Freaky',
            'linkschluessel': 'eisko_freakyhoody',
            'name': 'Eisko FreakyHoody',
            'zusatz': 'ein tätowierter Mann',
            'dreiecke': 20_000_000,
            'stufen_text': 'roher Scan („20 Mio. Polygone")',
            'texturen': '8K PBR (Diffuse, Spec, Normal, Displacement, Gloss, Rauheit)',
            'geschlecht': 'nur Mann',
            'rig': 'MetaHuman-Rig',
            'preis': 'kostenlos',
            'lizenz': 'zur Evaluierung; Lizenztext auf der Seite nicht genannt',
            'urteil': 'Ein einzelner Mann in Scan-Qualität mit fertigem '
            'MetaHuman-Rig — als Referenz, nicht als Basis.',
        },
        {
            'ordner': '16_Triplegangers',
            'name': 'Triplegangers Ganzkörper',
            'zusatz': '474 Personen, 261 Frauen, je 23 BACS-Posen',
            'dreiecke': 15_000_000,
            'stufen_text': 'roher Scan, nicht retopologisiert',
            'texturen': '16K PNG roh (linear)',
            'geschlecht': 'ja',
            'rig': '23 Posen je Person; kein Rig',
            'preis': '29,99–49,99 $ je Pose',
            'lizenz': 'privat: eigene Projekte + Ableitungen; Gratis-Samples CC-BY-NC-ND',
            'urteil': 'Größte Auswahl an echten Personen, aber Rohscans in '
            'Scan-Kleidung: Retopologie wäre eigene Arbeit.',
        },
        {
            'ordner': '04_Ten24_SampleScan',
            'name': 'Ten24 Sample Scan',
            'zusatz': 'ein Mann (James Busby)',
            'dreiecke': 15_000_000,
            'stufen_text': 'roher Scan; retopologisiert 200k–2 Mio. Polygone',
            'texturen': '16K / 8K + Normal',
            'geschlecht': 'nur Mann',
            'rig': 'kein Rig',
            'preis': 'kostenlos',
            'lizenz': 'kommerziell, Namensnennung',
            'urteil': 'Der einzige freie Ganzkörper-Scan in dieser Qualität — nur '
            'männlich; seine 8K-Haut taugt zum Backen.',
        },
        # Seit 17.09.2026 eigene Figurart (Edgar: „baue das Genesis9 Modell
        # als zusätzliches neues Modell ein"): `Genesis9/` liest die
        # installierte Daz-Bibliothek — Szene, Studio, Retarget, Kleidung.
        {
            'ordner': '11_Daz_Genesis9',
            'name': 'Daz Genesis 9',
            'eigen': True,
            'zusatz': 'installiert; seit 17.09.2026 eigene Figurart (privat)',
            'punkte': 25_182,
            'vierecke': 25_156,
            'stufen': 4,
            'stufen_text': 'SubD bis 4 (51 HD-Morphs auf Stufe 3–4); hier das Basisnetz',
            'texturen': '4K je UDIM-Kachel + 8K Detail-Normalmaps',
            'geschlecht': 'ja',
            'rig': '138 Knochen, 1.490 Morphs',
            'preis': 'installiert',
            'lizenz': 'EULA, nicht extrahierbar',
            'urteil': 'Bestes Material, das schon da ist — als Figurart im Haus '
            '(`Genesis9/HERKUNFT.md`), nichts davon im Repo.',
        },
        {
            'ordner': '06_Blender_HumanBaseMeshes_CC0',
            'name': 'Blender Human Base Meshes v1.4.1',
            'zusatz': '',
            'punkte': 10_582,
            'stufen': 3,
            'stufen_text': 'Multires 3',
            'texturen': 'keine',
            'geschlecht': 'ja',
            'rig': 'kein Rig',
            'preis': 'kostenlos',
            'lizenz': 'CC0',
            'urteil': 'Saubere Anatomie, frei — aber ohne Texturen keine Fotoqualität.',
        },
        {
            'ordner': '17_Ten24_Shop',
            'name': 'Ten24 Shop-Scans',
            'zusatz': '',
            'dreiecke': 800_000,
            'stufen_text': 'dezimiert (750–800k); Pro: Quad-Netz',
            'texturen': '10K Farbe + 8K Normal (Pro)',
            'geschlecht': 'ja',
            'rig': 'kein Rig',
            'preis': '20 / 30 / 45 £',
            'lizenz': 'Shop-Lizenz',
            'urteil': 'Günstige, dezimierte Scans — weniger Detail als die Sample-Datei.',
        },
        {
            'ordner': '18_CharacterCreator5_HD',
            'name': 'Character Creator 5 HD',
            'zusatz': 'Reallusion, 08/2025; Basis „16,4k Polygone" (Vierecknetz)',
            'vierecke': 16_400,
            'stufen': 2,
            'stufen_text': 'SubD 2 („16× mehr Detail")',
            'texturen': '8K + Displacement (EXR)',
            'geschlecht': 'ja',
            'rig': '~400 Morphs, Rig, Auto-Rig',
            'preis': '299 $ (Kauf)',
            'lizenz': 'Export in eigene Projekte',
            'urteil': 'Fertiges Morph- und Rig-System mit sauberer Lizenz.',
        },
        {
            'ordner': '00_eigene_Renderings',
            'bildmuster': 'humanbody',
            'linkschluessel': 'humanbody',
            'eigen': True,
            'name': 'HumanBody (MB-Lab-Netz)',
            'zusatz': 'die eigene Figur',
            'punkte': 18_210,
            'vierecke': 17_288,
            'stufen': 3,
            'stufen_text': 'Catmull-Clark 2 Stufen im Browser, 3 im Film '
            '(Einstellungen → Modell); Hautverschiebung (Displace) '
            'im Browser und Film; Korrekturglättung im Film',
            'texturen': '2K Albedo, 4K Bump, 2K Rauheit, 2K Displacement (MB-Lab)',
            'geschlecht': 'ja',
            'rig': 'DEF-Skelett (176 Knochen), MB-Lab-Morphs',
            'preis': 'im Haus',
            'lizenz': 'MB-Lab (AGPL) / eigen',
            'urteil': 'Der Stand, den die anderen schlagen sollen. Seit dem '
            '17.09.2026 mit denselben drei Modifiern wie das MB-Lab-'
            'Original (SubSurf 2/3, Displace, Corrective Smooth) — die '
            'Glättung nur im Film, weil der Browser auf der Grafikkarte '
            'häutet.',
        },
        {
            'ordner': 'MB-Lab',
            'linkschluessel': 'humanbody',
            'markierung': 'ursprung',
            'name': 'MB-Lab in Blender (Original)',
            'zusatz': 'dasselbe Netz wie HumanBody, so wie MB-Lab es rendert',
            'punkte': 18_210,
            'vierecke': 17_288,
            'stufen': 3,
            'stufen_text': 'SubSurf 2 im Viewport, 3 beim Rendern; dazu Displace-'
            'Modifier (Textur aus Alter/Tonus/Masse, Stärke 0,01) '
            'und Corrective Smooth (außer Kopf)',
            'texturen': '2K Albedo, 4K Bump, 2K Rauheit, 2K Displacement-Datenbild '
            '(Kanäle: Grund, Alter, Tonus, Masse)',
            'geschlecht': 'ja',
            'rig': 'MB-Lab-Skelett; Finalize bäckt die Regler zu Shapekeys',
            'preis': 'kostenlos',
            'lizenz': 'AGPL (Code), Assets frei',
            'urteil': 'Zum Vergleich mit dem Port: Finalize erhöht das Netz nicht '
            '(es wandelt Regler in Shapekeys, rechnet die '
            'Displacement-Textur neu und lässt die Modifier stehen) — '
            'die Auflösung kommt aus SubSurf 3 + Displace. Bis zum '
            '17.09.2026 fehlten beide im Port; jetzt rechnet er sie.',
        },
        {
            'ordner': '05_MetaHuman',
            'name': 'MetaHuman',
            'zusatz': 'UE 5.6 Creator; Körper 60.816 Dreiecke gegeben, Gesicht ≈ 2 × 24.049 Punkte',
            'punkte': 56_391,
            'dreiecke': 108_914,
            'stufen_text': 'LOD0 (keine)',
            'texturen': '8K',
            'geschlecht': 'ja, beliebig',
            'rig': 'Skelett + Rig Logic (Gesicht)',
            'preis': 'kostenlos',
            'lizenz': 'frei unter 1 Mio. $, jede Software',
            'urteil': 'Seit 06/2025 außerhalb Unreal erlaubt; Export als FBX, das '
            'Gesicht ohne Morphs (MetaHumanMeshTools).',
        },
        {
            'ordner': 'MakeHuman',
            'linkschluessel': 'mpfb2',
            'eigen': True,
            'name': 'MakeHuman (MPFB2)',
            'zusatz': 'Gruppe „body" aus base.obj, ohne Helfer',
            'punkte': 13_380,
            'vierecke': 13_378,
            'stufen': 1,
            'stufen_text': '1 Stufe Catmull-Clark („Smooth" im Browser)',
            'texturen': 'MakeHuman-Häute (CC0)',
            'geschlecht': 'ja',
            'rig': '163 Knochen, 1.280 Targets',
            'preis': 'kostenlos',
            'lizenz': 'CC0 (Assets), AGPL (Code)',
            'urteil': 'Figurart im Haus; Regler und Kleider, aber kein Scan-Detail.',
        },
        {
            'ordner': '08_RenderPeople_frei',
            'name': 'RenderPeople (9 freie Modelle)',
            'zusatz': 'angezogen',
            'dreiecke': 100_000,
            'stufen_text': 'posiert; geriggt 10–15k',
            'texturen': '8K',
            'geschlecht': 'ja, angezogen',
            'rig': 'geriggt: ja',
            'preis': 'kostenlos',
            'lizenz': 'Renderings',
            'urteil': 'Angezogen, kein Grundkörper.',
        },
        {
            'ordner': '12_Reallusion_CC_Base',
            'name': 'Reallusion CC-Basis (frei)',
            'zusatz': '„16,4k Polygone" (Vierecknetz)',
            'vierecke': 16_400,
            'stufen_text': 'keine',
            'texturen': '–',
            'geschlecht': 'ja',
            'rig': 'ja',
            'preis': 'kostenlos',
            'lizenz': 'frei',
            'urteil': 'Zu grob.',
        },
        {
            'ordner': 'UMA',
            'linkschluessel': 'uma',
            'eigen': True,
            'name': 'UMA (Unity Multipurpose Avatar)',
            'zusatz': 'lodRanges[0]',
            'punkte': 16_277,
            'dreiecke': 29_430,
            'stufen_text': 'keine',
            'texturen': 'UMA-Overlays',
            'geschlecht': 'ja',
            'rig': '229 Knochen, DNA',
            'preis': 'kostenlos',
            'lizenz': 'MIT',
            'urteil': 'Figurart im Haus (UMA_Python); Spielauflösung.',
        },
        {
            'ordner': 'SMPL-X',
            'linkschluessel': 'smpl',
            'eigen': True,
            'name': 'SMPL-X',
            'zusatz': 'SMPLX_NEUTRAL.npz',
            'punkte': 10_475,
            'dreiecke': 20_908,
            'stufen_text': 'keine',
            'texturen': '–',
            'geschlecht': 'ja',
            'rig': '55 Gelenke, Hände, Mimik',
            'preis': 'kostenlos',
            'lizenz': 'nur nicht-kommerziell',
            'urteil': 'Figurart im Haus; Rückgrat der Video-Pipelines.',
        },
        {
            'ordner': 'SMPL',
            'linkschluessel': 'smpl',
            'eigen': True,
            'name': 'SMPL',
            'zusatz': 'SMPL_NEUTRAL.pkl',
            'punkte': 6_890,
            'dreiecke': 13_776,
            'stufen_text': 'keine',
            'texturen': '–',
            'geschlecht': 'ja',
            'rig': '24 Gelenke',
            'preis': 'kostenlos',
            'lizenz': 'nur nicht-kommerziell',
            'urteil': 'Figurart im Haus; das gröbste Netz der Liste.',
        },
        {
            'ordner': '10_HumanGenerator_Blender',
            'name': 'Human Generator (Blender)',
            'zusatz': '',
            'stufen_text': 'Dichte nicht dokumentiert',
            'texturen': '8K',
            'geschlecht': 'ja',
            'rig': 'Rigify',
            'preis': '68 $',
            'lizenz': 'in eigener Software erlaubt',
            'urteil': 'Alternative zu Daz mit sauberer Lizenz; die Dichte nennt '
            'der Hersteller nicht — ohne Zahl kein Rang.',
        },
        {
            'ordner': '07_Blender_Einar_CC-BY',
            'name': 'Blender Studio Einar',
            'zusatz': 'Charge',
            'stufen_text': 'Kopf 4.596 Punkte + SubSurf; Körper angezogen, nicht gezählt',
            'texturen': '4K Albedo/Rauheit/Displacement (Gesicht)',
            'geschlecht': 'Mann, angezogen',
            'rig': '66 Shapekeys',
            'preis': 'kostenlos',
            'lizenz': 'CC-BY',
            'urteil': 'Filmfigur, kein Grundkörper.',
        },
        {
            'ordner': '14_Anny_MPFB2',
            'bildmuster': 'anny',
            'linkschluessel': 'anny',
            'name': 'Anny (Naver Labs)',
            'zusatz': 'parametrisch, alle Altersstufen',
            'stufen_text': 'Zahl nicht veröffentlicht',
            'texturen': '–',
            'geschlecht': 'ja',
            'rig': 'ja',
            'preis': 'kostenlos',
            'lizenz': 'Apache 2.0; SMPL-X-Topologie nur nicht-kommerziell',
            'urteil': 'Ohne veröffentlichte Netzzahl kein Rang.',
        },
        {
            'ordner': '13_Forschung_THuman_2K2K',
            'name': 'Forschungsscans THuman2.1 / 2K2K',
            'zusatz': '',
            'dreiecke': 100_000,
            'stufen_text': 'Scans 100k+',
            'ohne_rang': 'nur Forschung',
            'texturen': 'ja',
            'geschlecht': 'ja',
            'rig': '–',
            'preis': '–',
            'lizenz': 'nur Forschung',
            'urteil': 'Nur für Forschung lizenziert — deshalb ohne Rang.',
        },
    ]

    @classmethod
    def rangliste(cls):
        """Alle Zeilen mit Texten, Vergleichszahl und Rang (`Netzmasse`)."""
        return Netzmasse.rangfolge(cls.ZEILEN)

    @classmethod
    def mit_rang(cls):
        return [e for e in cls.rangliste() if e['rang'] is not None]

    @classmethod
    def ohne_rang(cls):
        return [e for e in cls.rangliste() if e['rang'] is None]
