# -*- coding: utf-8 -*-
u"""Die ganze Funktionalität von UMAs Konformer — Stück für Stück belegt.

WARUM (08.09.2026, Edgar: „Für UMA und UMA Python mach testcases die ganze
Funktionalität von UMA abbilden, die sollen dann mit UMA Python auch
abgebildet werden und funktionieren")
=====================================================================
Vorher gab es 24 Testfälle für den Port. Sie prüften, was beim Bauen
schiefgegangen war — vier Originalfälle aus UMAs eigener NUnit-Datei, die
Einheitenfalle, die Entartungsschwelle, Nähte und Kollision. Was NICHT
geprüft war, sah man ihnen nicht an: Eine Liste von Tests sagt nichts
darüber, was fehlt.

Diese Datei dreht das um. `UMA_Python/abdeckung.py` führt je Mitglied des
C#-Originals einen Eintrag mit Gegenstück und Probe; hier wird

1. die Tabelle gegen die **echten .cs-Dateien** gehalten (`Vollstaendig`),
2. jedes Gegenstück als Attribut nachgewiesen,
3. jede Probe als wirklich vorhandene Testmethode nachgewiesen,
4. und alles nachgeholt, was noch keine hatte.

Punkt 1 ist der, der die Tabelle am Leben hält: Fügt der Upstream eine
Methode hinzu, wird dieser Test rot — nicht in zwei Jahren beim nächsten
Durchlesen. Dieselbe Bauart wie `test_zielbaum_gegen_upstream`
(MakeHuman, 07.09.2026).

DIE GEGENPROBE ZU PUNKT 1 IST TEIL DES TESTS
============================================
Ein Prüfer, der nichts findet und grün meldet, ist keiner
(`~/.claude/rules/analysewerkzeuge.md`). `test_der_leser_findet_ueberhaupt_
mitglieder` und `test_ein_erfundenes_mitglied_wuerde_auffallen` stellen
sicher, dass das Lesen der .cs-Dateien wirklich etwas liefert und dass ein
unbekannter Name gemeldet würde.
"""
import re
import sys
import unittest
from pathlib import Path

import numpy as np
from django.conf import settings

# `UMA_Python` liegt seit dem 08.09.2026 unter `Assets/` (Edgar: „alles was
# mit Garments zu tun hat soll direkt A:\3DTools\Assets hier kommen").
sys.path.insert(0, str(Path(settings.ASSETS_ROOT)))

from UMA_Python import (Bindung, Einstellungen,               # noqa: E402
                        Glaettung, Kleidungskonformer, Nahtgruppen,
                        Netzgeometrie)
from UMA_Python.abdeckung import Abdeckung                    # noqa: E402
from .test_umakonformer import zylinder                       # noqa: E402


#: Die Klassen, in denen ein Gegenstück stehen kann.
KLASSEN = {'Netzgeometrie': Netzgeometrie, 'Glaettung': Glaettung,
           'Nahtgruppen': Nahtgruppen, 'Bindung': Bindung,
           'Einstellungen': Einstellungen,
           'Kleidungskonformer': Kleidungskonformer}


def _quellordner():
    u"""Der UMA-Klon, oder `None`."""
    ordner = Path(str(settings.TOOLS_ROOT)).joinpath(*Abdeckung.QUELLORDNER)
    return ordner if ordner.is_dir() else None


def _mitglieder(text, klasse=None, privat=False):
    u"""Die Namen, die das Original nach aussen zeigt.

    Gelesen wird mit regulären Ausdrücken statt mit einem C#-Zerleger: Es
    geht um `public`-Zeilen einer bekannten Form, und ein Zerleger für C#
    wäre ein zweites Fremdprojekt in dieser Prüfung.
    """
    if klasse:
        teile = text.split('class %s' % klasse)
        if len(teile) < 2:
            return set()
        text = teile[1]
        # bis zur nächsten Klasse auf derselben Ebene
        naechste = re.search(
            r'\n    (?:public |internal )?(?:sealed |static )?'
            r'class \w', text)
        if naechste:
            text = text[:naechste.start()]
    namen = set()
    muster = _MUSTER + (_PRIVAT if privat else ())
    for eines in muster:
        for treffer in eines.finditer(text):
            namen.add(treffer.group(1))
    return namen


#: Nur `public`. Das ist die SCHNITTSTELLE — und nur die muss der Port
#: abdecken. Mit `private static` kamen 18 Hilfsnamen dazu (`Add`,
#: `Find`, `Union`, `EdgeKey`, `LaplacianPass` …), die im Original
#: Bausteine EINER Methode sind: UMAs `BuildWeldedVertexGroups` traegt
#: seine eigene Union-Find-Struktur im Rumpf. Sie einzeln zu fordern
#: hiesse, die INNERE Bauart nachzubauen statt das Verhalten.
_MUSTER = (
    re.compile(r'\bpublic\s+static\s+[\w\[\]<>,\.]+\s+(\w+)\s*\('),
    re.compile(r'\bpublic\s+(?!class|enum|struct|static)'
               r'[\w\[\]<>,\.]+\s+(\w+)\s*\('),
    re.compile(r'\bpublic\s+[\w\[\]<>,\.]+\s+(\w+)\s*[=;]'),
)

#: Zusaetzlich, wenn auch die privaten Schritte und die Klassennamen
#: zaehlen sollen. Die Klasse steht drin, weil die Tabelle
#: `ClothingConformerSpatialIndex` als GANZES fuehrt: Sie ist im Port
#: kein eigener Baustein, sondern in `cKDTree` aufgegangen — ein
#: Eintrag ohne Methodennamen, aber mit Vorbild.
_PRIVAT = (
    re.compile(r'\bprivate\s+static\s+[\w\[\]<>,\.]+\s+(\w+)\s*\('),
    re.compile(r'\bclass\s+(\w+)'),
)


class Vollstaendig(unittest.TestCase):
    u"""Die Tabelle gegen den echten C#-Quelltext."""

    databases = []

    #: Was in den .cs-Dateien steht, aber nicht zur Schnittstelle gehört.
    #: `Instance`/`get_`-Formen und Unity-Ereignisse; die Klassen- und
    #: Feldnamen der internen `struct`s sind Datenhalter ohne Verhalten.
    NICHT_SCHNITTSTELLE = {
        'UMAClothingConformer', 'ClothingConformerMeshUtility',
        'ClothingBindData', 'ClothingConformerSettings', 'BindVertexData',
        'umaAvatar', 'umaData', 'selectedSlotNames', 'baseSlotNames',
        'settings', 'bindData', 'bindDataAssets', 'preview',
        'LastStatus', 'UnboundVertexPositions', 'HasConformedResults',
        'BoundVertexCount', 'HasNearestVertexFallback',
        'sourceSlotName', 'sourceSlotAsset', 'clothingMeshOriginal',
        'sourceMaterial', 'originalUv', 'vertexCount', 'vertices',
        'triangles', 'weldedVertexGroups', 'weldedSeamTolerance',
        'baseSlotNames', 'baseTopologyHash', 'clothingTopologyHash',
        'sourceBounds', 'umaVersion', 'isComplete',
        'slotAsset', 'hadOverride', 'normals', 'slotNames', 'topologyHash',
        'renderer', 'sourceMesh', 'rootVertices', 'blendedVertexDeltas',
        'submeshTriangles', 'slot', 'rendererSnapshot', 'startVertex',
        'tangents', 'rootNormals', 'rootTangents', 'baseVertices',
        'localNormals', 'localTangents', 'IsValidVertexIndex',
        # Felder der internen `struct`s (ConformedSlotResult,
        # SurfaceSnapshot, SlotSnapshot) — Datenhalter ohne Verhalten.
        'count', 'mesh', 'originalMesh', 'previewMesh', 'rendererIndex',
        'shapeName', 'total', 'weight', 'boneIndex',
    }

    def setUp(self):
        self.ordner = _quellordner()
        if self.ordner is None:
            self.skipTest(u'UMA-Klon nicht vorhanden (%s)'
                          % '/'.join(Abdeckung.QUELLORDNER))

    def _quelltext(self):
        aus = []
        for datei in Abdeckung.DATEIEN:
            pfad = self.ordner / datei
            self.assertTrue(pfad.is_file(), u'%s fehlt' % pfad)
            aus.append(pfad.read_text(encoding='utf-8', errors='replace'))
        return aus

    def _gefunden(self):
        u"""Die OEFFENTLICHE Schnittstelle — sie muss abgedeckt sein."""
        namen = set()
        for text in self._quelltext():
            namen |= _mitglieder(text)
        return namen - self.NICHT_SCHNITTSTELLE

    def _alle_namen(self):
        u"""Auch die privaten — dafür, dass die Tabelle nichts erfindet.

        Die Tabelle FÜHRT vier private Methoden (`ApplyWeldedSeam-
        Displacements`, `InterpolateNormal`, `GetWeightedSurfacePoint`,
        `CalculateInverseDistanceWeights`): Sie sind Schritte des
        Verfahrens und im Port eigene Bausteine. Gefordert werden sie
        nicht, aber erfunden sind sie auch nicht.
        """
        namen = set()
        for text in self._quelltext():
            namen |= _mitglieder(text, privat=True)
        return namen

    def test_der_leser_findet_ueberhaupt_mitglieder(self):
        u"""GEGENPROBE: Ein Leser, der nichts findet, meldet grün — genau
        die Falle aus `~/.claude/rules/analysewerkzeuge.md`."""
        gefunden = self._gefunden()
        self.assertGreater(len(gefunden), 40,
                           u'Nur %d Mitglieder gelesen — der reguläre '
                           u'Ausdruck passt nicht mehr zur Quelle'
                           % len(gefunden))

    def test_jedes_mitglied_steht_in_der_tabelle(self):
        u"""Der eigentliche Test: nichts fällt unter den Tisch."""
        fehlt = sorted(self._gefunden() - Abdeckung.namen())
        self.assertEqual(
            fehlt, [],
            u'Diese Mitglieder des C#-Originals haben keinen Eintrag in '
            u'UMA_Python/abdeckung.py: %s' % ', '.join(fehlt))

    def test_die_tabelle_erfindet_nichts(self):
        u"""Die andere Richtung: kein Eintrag ohne Vorbild im Original.

        Sonst wächst die Tabelle mit Namen, die es nicht mehr gibt, und
        die Abdeckung sieht besser aus, als sie ist."""
        gefunden = self._alle_namen() | self.NICHT_SCHNITTSTELLE
        erfunden = sorted(Abdeckung.namen() - gefunden)
        self.assertEqual(erfunden, [],
                         u'Eintraege ohne Vorbild im Original: %s'
                         % ', '.join(erfunden))

    def test_ein_erfundenes_mitglied_wuerde_auffallen(self):
        u"""GEGENPROBE zum Abgleich selbst."""
        gefunden = self._gefunden()
        self.assertNotIn('DasGibtEsNicht', gefunden)
        self.assertTrue(
            {'ClosestPointOnTriangle', 'Smooth', 'maxSearchRadius'}
            <= gefunden,
            u'Der Leser findet die bekannten Mitglieder nicht mehr')


class TabelleIstBelegt(unittest.TestCase):
    u"""Jedes Gegenstück existiert, jede Probe auch."""

    databases = []

    @staticmethod
    def _hat(klasse, name):
        u"""Gibt es das Attribut — auch, wenn es erst `__init__` setzt?

        `hasattr` allein reicht nicht: `Bindung.ausgangslage` und
        `Kleidungskonformer._baum` entstehen im Rumpf und stehen der
        KLASSE nicht an. Ein Test, der nur `hasattr` fragt, meldete
        neun echte Gegenstücke als fehlend.
        """
        if hasattr(klasse, name):
            return True
        import inspect
        try:
            quelle = inspect.getsource(klasse)
        except (OSError, TypeError):
            return False
        return ('self.%s =' % name) in quelle or (
            'self.%s:' % name) in quelle

    def test_jedes_gegenstueck_existiert(self):
        fehlt = []
        for eintrag in Abdeckung.eintraege():
            if not eintrag.gegenstueck:
                continue
            klasse, _, name = eintrag.gegenstueck.partition('.')
            ziel = KLASSEN.get(klasse)
            if ziel is None or not self._hat(ziel, name):
                fehlt.append('%s -> %s'
                             % (eintrag.uma, eintrag.gegenstueck))
        self.assertEqual(fehlt, [],
                         u'Gegenstücke, die es nicht gibt: %s'
                         % ', '.join(fehlt))

    def test_jede_probe_ist_eine_echte_testmethode(self):
        u"""Eine Probe, die es nicht gibt, ist eine Behauptung.

        Aufgelöst wird über das Testpaket dieses Ordners — `Bindung` und
        `Kleidungskonformer` sind Instanzattribute, deshalb steht ihr
        Nachweis über `hasattr` in `test_jedes_gegenstueck_existiert`
        getrennt.
        """
        import importlib
        fehlt = []
        for eintrag in Abdeckung.eintraege():
            if not eintrag.probe:
                continue
            modul, klasse, methode = eintrag.probe.split('.')
            try:
                geladen = importlib.import_module(
                    'core.tests.unit.%s' % modul)
            except ImportError:
                fehlt.append('%s (Modul %s)' % (eintrag.probe, modul))
                continue
            ziel = getattr(geladen, klasse, None)
            if ziel is None or not hasattr(ziel, methode):
                fehlt.append(eintrag.probe)
        self.assertEqual(fehlt, [],
                         u'Proben, die es nicht gibt: %s' % ', '.join(fehlt))

    def test_nichts_ist_unbegruendet_weggelassen(self):
        u"""`unity` und `intern` brauchen einen Grund — die Klasse erzwingt
        das schon beim Bauen; hier steht die Gegenprobe dazu."""
        from UMA_Python.abdeckung import Eintrag
        with self.assertRaises(ValueError):
            Eintrag('Irgendwas', 'unity')
        with self.assertRaises(ValueError):
            Eintrag('Irgendwas', 'portiert', 'Netzgeometrie.seite')
        with self.assertRaises(ValueError):
            Eintrag('Irgendwas', 'zauberei')

    def test_die_anteile_stimmen(self):
        u"""Eine Zahl, die man in den Bericht schreiben kann — und die rot
        wird, wenn jemand einen Eintrag stumm auf `unity` setzt."""
        gerechnet = (len(Abdeckung.nach_art('portiert'))
                     + len(Abdeckung.nach_art('anders')))
        self.assertGreaterEqual(gerechnet, 45)
        self.assertLessEqual(len(Abdeckung.nach_art('intern')), 5)


# ===================================================================== Proben


class Geometriebausteine(unittest.TestCase):
    u"""Die vier Bausteine, die bisher nur mittelbar geprüft waren."""

    databases = []

    def setUp(self):
        self.ecken = np.array([[[0.0, 0.0, 0.0],
                                [1.0, 0.0, 0.0],
                                [0.0, 1.0, 0.0]]])

    def test_baryzentrisch_trifft_die_ecken_und_die_mitte(self):
        u"""`CalculateBarycentric`. Die drei Ecken müssen (1,0,0), (0,1,0)
        und (0,0,1) ergeben, der Schwerpunkt dreimal ein Drittel."""
        ecken = np.repeat(self.ecken, 4, axis=0)
        punkte = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0],
                           [0.0, 1.0, 0.0], [1 / 3, 1 / 3, 0.0]])
        bary = Netzgeometrie.baryzentrisch(punkte, ecken)
        np.testing.assert_allclose(bary[0], [1, 0, 0], atol=1e-12)
        np.testing.assert_allclose(bary[1], [0, 1, 0], atol=1e-12)
        np.testing.assert_allclose(bary[2], [0, 0, 1], atol=1e-12)
        np.testing.assert_allclose(bary[3], [1 / 3, 1 / 3, 1 / 3], atol=1e-12)
        # Die Summe ist immer 1 — das ist die Probe, die bei einem
        # Vorzeichenfehler fällt.
        np.testing.assert_allclose(bary.sum(axis=1), 1.0, atol=1e-12)

    def test_normale_wird_zur_bezugsrichtung_gedreht(self):
        u"""`OrientNormalToReference`: Eine Normale, die dem Bezug den
        Rücken kehrt, wird umgedreht — die andere bleibt.

        Ohne das kippt der ganze Stoff auf die Innenseite, sobald ein
        Körperdreieck falsch herum gewickelt ist."""
        normalen = np.array([[0.0, 1.0, 0.0], [0.0, -1.0, 0.0]])
        bezug = np.array([[0.0, 1.0, 0.0], [0.0, 1.0, 0.0]])
        gedreht = Netzgeometrie.normalen_ausrichten(normalen, bezug)
        np.testing.assert_allclose(gedreht[0], [0, 1, 0])
        np.testing.assert_allclose(gedreht[1], [0, 1, 0])

    def test_punktnormalen_sind_radial_und_normiert(self):
        u"""`CalculateNormals` auf einem Zylinder: Jede Punktnormale muss
        RADIAL stehen und die Länge 1 haben.

        Radial, nicht „nach aussen": Wohin sie zeigen, entscheidet die
        Wickelrichtung des Netzes, und die ist eine Eigenschaft der
        EINGABE. UMA sichert hier nichts zu — es dreht die Normalen erst
        in `OrientNormalToReference` auf eine Bezugsrichtung. Wer hier
        „nach aussen" prüft, prüft seine eigene Vorrichtung: Dieser
        Zylinder wickelt nach innen (gemessen Median −1,0).
        """
        punkte, dreiecke = zylinder(0.2)
        n = Netzgeometrie.punktnormalen(punkte, dreiecke)
        np.testing.assert_allclose(np.linalg.norm(n, axis=1), 1.0,
                                   atol=1e-9)
        radial = punkte.copy()
        radial[:, 1] = 0.0
        radial /= np.linalg.norm(radial, axis=1, keepdims=True)
        richtung = (n * radial).sum(axis=1)
        # Deckel und Boden fehlen, deshalb der Median statt des Minimums.
        self.assertGreater(abs(float(np.median(richtung))), 0.99)
        # Und alle in DERSELBEN Richtung — eine gemischte Wickelung
        # wäre ein echter Befund.
        self.assertGreater(abs(float(np.sign(richtung).mean())), 0.9)

    def test_nachbarschaft_ist_symmetrisch_und_ohne_selbstbezug(self):
        u"""`BuildAdjacency`. Zwei Eigenschaften, die eine Glättung
        stillschweigend verfälschen, wenn sie fehlen: Ein Punkt darf nicht
        sein eigener Nachbar sein (er zöge sich selbst an), und die
        Beziehung muss in beide Richtungen stehen."""
        punkte, dreiecke = zylinder(0.2, ringe=8, stufen=4)
        starts, nachbarn = Netzgeometrie.nachbarschaft(len(punkte), dreiecke)
        self.assertEqual(len(starts), len(punkte) + 1)
        paare = set()
        for i in range(len(punkte)):
            for j in nachbarn[starts[i]:starts[i + 1]]:
                self.assertNotEqual(i, int(j), u'Punkt %d ist sein eigener '
                                               u'Nachbar' % i)
                paare.add((i, int(j)))
        fehlend = [(a, b) for a, b in paare if (b, a) not in paare]
        self.assertEqual(fehlend, [], u'Nachbarschaft nicht symmetrisch')

    def test_interpolierte_normale_liegt_zwischen_den_ecken(self):
        u"""`InterpolateNormal`: In der Mitte eines Dreiecks das Mittel der
        drei Eckennormalen, an einer Ecke genau deren Normale."""
        pn = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
        dreiecke = np.array([[0, 1, 2]])
        bary = np.array([[1.0, 0.0, 0.0], [1 / 3, 1 / 3, 1 / 3]])
        n = Netzgeometrie.normale_interpolieren(pn, dreiecke,
                                                np.array([0, 0]), bary)
        np.testing.assert_allclose(n[0], [1, 0, 0], atol=1e-12)
        np.testing.assert_allclose(n[1], np.ones(3) / np.sqrt(3), atol=1e-12)


class Tangenten(unittest.TestCase):
    u"""`CalculateTangents` — am 08.09.2026 nachportiert."""

    databases = []

    def setUp(self):
        # Ein Quadrat in der XY-Ebene mit der üblichen UV-Belegung.
        self.punkte = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0],
                                [1.0, 1.0, 0.0], [0.0, 1.0, 0.0]])
        self.uv = np.array([[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0]])
        self.dreiecke = np.array([[0, 1, 2], [0, 2, 3]])
        self.normalen = np.tile([0.0, 0.0, 1.0], (4, 1))

    def test_standard_uv_ergibt_die_x_achse(self):
        u"""u wächst mit x — die Tangente MUSS +X sein, Händigkeit +1."""
        t = Netzgeometrie.tangenten(self.punkte, self.normalen, self.uv,
                                    self.dreiecke)
        self.assertEqual(t.shape, (4, 4))
        for zeile in t:
            np.testing.assert_allclose(zeile, [1, 0, 0, 1], atol=1e-12)

    def test_gespiegeltes_u_dreht_tangente_und_haendigkeit(self):
        u"""Die Händigkeit ist die Spalte, die man beim Portieren vergisst
        — und ohne sie steht eine Normal-Map seitenverkehrt."""
        uv = np.array([[1.0, 0.0], [0.0, 0.0], [0.0, 1.0], [1.0, 1.0]])
        t = Netzgeometrie.tangenten(self.punkte, self.normalen, uv,
                                    self.dreiecke)
        np.testing.assert_allclose(t[0], [-1, 0, 0, -1], atol=1e-12)

    def test_tangente_steht_senkrecht_auf_der_normale(self):
        u"""Gram-Schmidt: Das Skalarprodukt muss null sein, sonst ist die
        Orthogonalisierung nicht gelaufen."""
        gedreht = np.tile([0.0, 0.6, 0.8], (4, 1))
        t = Netzgeometrie.tangenten(self.punkte, gedreht, self.uv,
                                    self.dreiecke)
        np.testing.assert_allclose((t[:, :3] * gedreht).sum(axis=1), 0.0,
                                   atol=1e-12)
        np.testing.assert_allclose(np.linalg.norm(t[:, :3], axis=1), 1.0,
                                   atol=1e-12)

    def test_ohne_uv_kommen_einheitstangenten(self):
        u"""Wie im Original: `(1,0,0,1)`, keine Ausnahme. GarmentCode-Netze
        haben keine UV — eine Ausnahme mitten im Anwenden wäre hier der
        schlechtere Weg."""
        for uv in (None, self.uv[:2]):
            t = Netzgeometrie.tangenten(self.punkte, self.normalen, uv,
                                        self.dreiecke)
            self.assertEqual(t.shape, (4, 4))
            np.testing.assert_allclose(t[0], [1, 0, 0, 1])

    def test_entartete_uv_wird_uebergangen(self):
        u"""Ein Dreieck ohne UV-Fläche (alle drei Punkte auf demselben
        UV-Wert) darf nicht durch null teilen."""
        uv = np.zeros((4, 2))
        t = Netzgeometrie.tangenten(self.punkte, self.normalen, uv,
                                    self.dreiecke)
        self.assertTrue(np.isfinite(t).all())
        np.testing.assert_allclose(t[0], [1, 0, 0, 1])

    def test_tangenten_werden_nach_dem_anwenden_neu_gerechnet(self):
        u"""Der Unterschied zu UMA: Die Tangente wird nicht mitgeführt,
        sondern aus dem VERFORMTEN Netz gerechnet. Die Probe darauf ist,
        dass sie sich mit der Verformung ändert."""
        koerper, k_tri = zylinder(0.20)
        stoff, s_tri = zylinder(0.21, ringe=18, stufen=12)
        # UV: Winkel und Höhe des Zylinders.
        winkel = np.arctan2(stoff[:, 2], stoff[:, 0])
        uv = np.column_stack([(winkel + np.pi) / (2 * np.pi), stoff[:, 1]])

        k = Kleidungskonformer(koerper, k_tri)
        b = k.binden('huelle', stoff, s_tri)
        vorher = Netzgeometrie.tangenten(stoff, None, uv, s_tri)

        # Zylinder oben aufweiten -> die Fläche kippt, die Tangente auch.
        weit = koerper.copy()
        weit[:, [0, 2]] *= 1.0 + 0.5 * weit[:, 1:2]
        gelegt = k.anwenden(b, weit)
        nachher = Netzgeometrie.tangenten(gelegt, None, uv, s_tri)

        wanderung = np.linalg.norm(nachher[:, :3] - vorher[:, :3], axis=1)
        # Gemessen 0,028 bei dieser Verformung; die Schwelle liegt
        # darunter, aber deutlich über dem Rauschen (1e-9 bei
        # unverändertem Körper — die Gegenprobe steht darunter).
        self.assertGreater(float(wanderung.max()), 0.01,
                           u'Die Tangenten haben sich nicht bewegt — dann '
                           u'beschreiben sie die alte Oberfläche')
        # GEGENPROBE: Ohne Verformung dürfen sie sich NICHT bewegen.
        # Dazu muss die Glättung aus sein — sie ist in `Einstellungen`
        # VORGABE und verändert das Netz auch bei unverändertem Körper.
        still = Kleidungskonformer(
            koerper, k_tri,
            Einstellungen(glaetten=False, tangential_halten=True))
        b2 = still.binden('huelle', stoff, s_tri)
        ruhe = Netzgeometrie.tangenten(still.anwenden(b2), None, uv,
                                       s_tri)
        self.assertLess(
            float(np.linalg.norm(ruhe[:, :3] - vorher[:, :3],
                                 axis=1).max()), 1e-6)


class Nachbarsuche(unittest.TestCase):
    u"""Was bei UMA `ClothingConformerSpatialIndex` leistet."""

    databases = []

    def setUp(self):
        self.koerper, self.k_tri = zylinder(0.20)
        self.konformer = Kleidungskonformer(self.koerper, self.k_tri)

    def test_das_naechste_dreieck_wird_gefunden(self):
        u"""Ein Punkt dicht über der Haut muss auf ein Dreieck fallen, das
        ihn wirklich trägt: Der Fusspunkt liegt radial unter ihm."""
        probe = np.array([[0.25, 0.5, 0.0], [0.0, 0.5, 0.25],
                          [-0.25, 0.5, 0.0]])
        tri, fuss, abstand2 = self.konformer._naechstes_dreieck(probe)
        self.assertEqual(len(tri), 3)
        self.assertTrue((tri >= 0).all())
        # DAS ABSTANDSQUADRAT, nicht der Abstand — so braucht `binden`
        # es (`abstand2 <= hoechstabstand_m ** 2`, ohne Wurzel je Punkt).
        # Wer die Zahl für einen Abstand hält, misst bei 5 cm 2,5 mm
        # und hält das Stück für anliegend.
        np.testing.assert_allclose(np.sqrt(abstand2), 0.05, atol=2e-3)
        # Der Fusspunkt liegt auf demselben Strahl vom Mittelpunkt.
        for p, f in zip(probe, fuss):
            richtung = np.array([p[0], 0.0, p[2]])
            richtung /= np.linalg.norm(richtung)
            fussrichtung = np.array([f[0], 0.0, f[2]])
            fussrichtung /= np.linalg.norm(fussrichtung)
            self.assertGreater(float(richtung @ fussrichtung), 0.99)

    def _koerper_mit_freiem_punkt(self):
        u"""Zylinder plus EIN Körperpunkt, der zu keinem Dreieck gehört.

        Genau dafür hat UMA den Rückfall: `binden` sucht unter den 32
        nächsten DREIECKSSCHWERPUNKTEN, und ein Punkt ohne Dreieck ist
        dort nie dabei — er liegt aber im Netz und trägt Haut. Bei UMA
        kommt das vor, wenn ein Slot Punkte mitbringt, deren Dreiecke in
        einem anderen Slot stehen.
        """
        frei = np.array([[0.0, 3.0, 0.0]])
        return np.vstack([self.koerper, frei]), self.k_tri

    def test_rueckfall_greift_wenn_kein_dreieck_trifft(self):
        u"""UMAs `FindNearestVertices`: Wo kein Dreieck im Höchstabstand
        liegt, treten die nächsten Körperpunkte an seine Stelle."""
        koerper, k_tri = self._koerper_mit_freiem_punkt()
        stoff = np.array([[0.0, 3.005, 0.0], [0.0, 3.01, 0.0]])
        s_tri = np.zeros((0, 3), dtype=np.int64)
        e = Einstellungen(hoechstabstand_m=0.1, suchradius_m=0.5)
        konformer = Kleidungskonformer(koerper, k_tri, e)
        b = konformer.binden('saum', stoff, s_tri)
        self.assertTrue((b.dreieck < 0).all(),
                        u'Kein Dreieck darf hier treffen')
        mit_rueckfall = b.nahe_punkte[:, 0] >= 0
        self.assertTrue(mit_rueckfall.all(),
                        u'Kein einziger Punkt über den Rückfall gebunden')
        # Die Gewichte einer Rückfallzeile summieren sich auf 1.
        zeilen = b.nahe_gewichte[mit_rueckfall]
        np.testing.assert_allclose(zeilen.sum(axis=1), 1.0, atol=1e-9)

    def test_gewichte_fallen_mit_dem_abstand(self):
        u"""`CalculateInverseDistanceWeights`: Der nächste Punkt bekommt
        das grösste Gewicht. Ohne diese Ordnung zieht der ENTFERNTESTE
        Nachbar am stärksten — ein Vorzeichenfehler, den kein Bild zeigt."""
        koerper, k_tri = self._koerper_mit_freiem_punkt()
        stoff = np.array([[0.0, 3.004, 0.0]])
        s_tri = np.zeros((0, 3), dtype=np.int64)
        e = Einstellungen(hoechstabstand_m=0.1, suchradius_m=5.0)
        konformer = Kleidungskonformer(koerper, k_tri, e)
        b = konformer.binden('einer', stoff, s_tri)
        gueltig = b.nahe_punkte[0] >= 0
        self.assertTrue(gueltig.any(),
                        u'Der Rückfall hat nicht gegriffen')
        abstaende = np.linalg.norm(
            koerper[b.nahe_punkte[0][gueltig]] - stoff[0], axis=1)
        gewichte = b.nahe_gewichte[0][gueltig]
        # Reihenfolge: kleinster Abstand -> grösstes Gewicht
        self.assertEqual(list(np.argsort(abstaende)),
                         list(np.argsort(-gewichte)))


class Zuruecknehmen(unittest.TestCase):
    u"""Was bei UMA `RevertChanges` ist."""

    databases = []

    def test_die_ausgangslage_ueberlebt_jedes_anwenden(self):
        u"""`anwenden` gibt ein neues Feld zurück und rührt die Bindung
        nicht an. Deshalb braucht es kein Zurücknehmen — aber die Probe
        darauf braucht es: Ein `+=` an der falschen Stelle würde die
        Ausgangslage überschreiben, und danach wäre jeder weitere Zug
        falsch, ohne dass etwas auffällt."""
        koerper, k_tri = zylinder(0.20)
        stoff, s_tri = zylinder(0.21, ringe=18, stufen=12)
        k = Kleidungskonformer(koerper, k_tri)
        b = k.binden('huelle', stoff, s_tri)
        ausgang = b.ausgangslage.copy()

        for faktor in (1.2, 1.5, 0.9, 1.0):
            weit = koerper.copy()
            weit[:, [0, 2]] *= faktor
            k.anwenden(b, weit)

        np.testing.assert_array_equal(b.ausgangslage, ausgang)
        # Und der Stoff selbst auch nicht.
        np.testing.assert_array_equal(stoff, b.ausgangslage)


class Stellschrauben(unittest.TestCase):
    u"""Jede Einstellung muss WIRKEN — eine, die nichts tut, ist die
    stillste Sorte Fehler."""

    databases = []

    def setUp(self):
        self.koerper, self.k_tri = zylinder(0.20)
        self.stoff, self.s_tri = zylinder(0.21, ringe=18, stufen=12)

    def _binden(self, **abweichungen):
        e = Einstellungen(**abweichungen)
        k = Kleidungskonformer(self.koerper, self.k_tri, e)
        return k, k.binden('huelle', self.stoff, self.s_tri)

    def test_suchradius_begrenzt_die_bindung(self):
        u"""`maxSearchRadius`. Mit 1 mm findet kein Punkt mehr eine Fläche
        — mit 20 cm alle."""
        _, weit = self._binden(suchradius_m=0.2)
        _, eng = self._binden(suchradius_m=0.001, hoechstabstand_m=0.001)
        self.assertEqual(int(weit.gebunden.sum()), weit.punktzahl)
        self.assertLess(int(eng.gebunden.sum()), weit.punktzahl)

    def test_abstandsschwelle_entscheidet_ueber_die_kollision(self):
        u"""`normalOffsetEpsilon`: Ab welchem Abstand ein Punkt als „auf
        der Fläche" gilt. Wird sie grösser als der Stoffabstand, gilt der
        ganze Stoff als aufliegend."""
        k, b = self._binden(abstandsschwelle_m=0.001)
        eng = k.anwenden(b)
        k2 = Kleidungskonformer(self.koerper, self.k_tri,
                                Einstellungen(abstandsschwelle_m=0.05))
        b2 = k2.binden('huelle', self.stoff, self.s_tri)
        weit = k2.anwenden(b2)
        self.assertGreater(float(np.abs(eng - weit).max()), 1e-6,
                           u'Die Schwelle wirkt gar nicht')

    def _mit_glaettung(self, beheben, deckel=0.05):
        u"""Ein gezackter Stoff, stark geglättet — der Fall, in dem die
        Kollisionsbehebung ÜBERHAUPT etwas tut.

        GEMESSEN AM 08.09.2026, und das ist der Lehrsatz: Ohne
        Glättung feuert sie NIE. `binden` merkt sich je Punkt seinen
        Abstand zur Fläche, und `anwenden` stellt genau den wieder her
        — einsinken kann dabei nichts. Ein Test, der den Punkt vorher
        eindrückt oder den Körper weitet, misst mit und ohne Behebung
        denselben Wert (0,30949623684534955 gegen sich selbst).

        Erst die Glättung zieht Punkte von der Fläche weg — deshalb
        steht die Behebung in `anwenden` DANACH ein zweites Mal.
        """
        rau = self.stoff.copy()
        rau[::3] *= 1.10
        e = Einstellungen(kollision_beheben=beheben, glaetten=True,
                          glaettungsverfahren='laplace',
                          glaettungsdurchgaenge=20,
                          glaettungsstaerke=1.0, schub_deckel_m=deckel,
                          naehte_halten=False, tangential_halten=False)
        k = Kleidungskonformer(self.koerper, self.k_tri, e)
        ergebnis = k.anwenden(k.binden('huelle', rau, self.s_tri))
        return float(np.hypot(ergebnis[:, 0], ergebnis[:, 2]).min())

    def test_ohne_kollisionsbehebung_bleibt_der_punkt_drin(self):
        u"""`enableCollisionCorrection`. Gemessen: kleinster Radius
        0,101 ohne, 0,151 mit Behebung — bei einem Körperradius von
        0,20. Ohne sie steckt der geglättete Stoff im Körper."""
        self.assertGreater(self._mit_glaettung(True),
                           self._mit_glaettung(False) + 0.01,
                           u'Mit Behebung muss der Stoff deutlich weiter '
                           u'draussen liegen')

    def test_der_schub_ist_gedeckelt(self):
        u"""`maxCollisionDisplacement`. Ohne Deckel wanderte am
        06.09.2026 ein Kragenpunkt 123,65 mm — weil die ZÄHNE im Kopf
        in seinen Umkreis fielen.

        Gemessen wird der WEITESTE Punkt: Der Deckel greift je Punkt,
        und ein Mittelwert verdünnt ihn zu Unkenntlichkeit.
        """
        eng = self._mit_glaettung(True, deckel=0.002)
        weit = self._mit_glaettung(True, deckel=0.05)
        ohne = self._mit_glaettung(False)
        self.assertGreater(weit, eng,
                           u'Ein grösserer Deckel muss mehr herausholen')
        self.assertGreater(eng, ohne,
                           u'Auch ein kleiner Deckel muss etwas tun')

    def test_glaettung_laesst_sich_abschalten(self):
        u"""`enableSmoothing`."""
        rau = self.stoff.copy()
        rau[::3] += np.array([0.0, 0.004, 0.0])
        ergebnisse = {}
        for an in (True, False):
            e = Einstellungen(glaetten=an, naehte_halten=False)
            k = Kleidungskonformer(self.koerper, self.k_tri, e)
            ergebnisse[an] = k.anwenden(k.binden('h', rau, self.s_tri))
        self.assertGreater(float(np.abs(ergebnisse[True]
                                        - ergebnisse[False]).max()), 1e-6)

    def test_mehr_durchgaenge_glaetten_staerker(self):
        u"""`smoothingIterations`: Die Rauheit muss mit der Zahl der
        Durchgänge fallen — sonst ist die Schleife wirkungslos."""
        punkte, dreiecke = zylinder(0.2, ringe=16, stufen=8)
        rau = punkte.copy()
        rau[::2] *= 1.02
        starts, nachbarn = Netzgeometrie.nachbarschaft(len(punkte),
                                                       dreiecke)
        # GEMESSEN WIRD DIE RAUHEIT, nicht der Abstand zum Ausgangsnetz
        # und nicht die Streuung der Radien. Laplace SCHRUMPFT (sein
        # bekannter Nachteil), deshalb wächst der Abstand zum Original
        # mit jedem Durchgang, während die Rauheit fällt — zwei
        # gegenläufige Grössen, und nur eine davon ist gemeint.
        # Rauheit hier: der Abstand jedes Punktes zum Mittel seiner
        # Nachbarn. Genau das verkleinert eine Glättung.

        def rauheit(v):
            anzahl = np.diff(starts)
            summe = np.add.reduceat(v[nachbarn], starts[:-1], axis=0)
            mittel = summe / np.maximum(anzahl, 1)[:, None]
            return float(np.linalg.norm(v - mittel, axis=1).mean())

        werte = []
        for durchgaenge in (1, 4, 16):
            g = Glaettung.glaetten(rau, (starts, nachbarn), 'laplace',
                                   durchgaenge=durchgaenge, staerke=0.5)
            werte.append(rauheit(g))
        self.assertLess(werte[1], werte[0])
        self.assertLess(werte[2], werte[1])

    def test_staerke_null_bewegt_nichts(self):
        u"""`smoothingStrength = 0`. Die schärfste Probe auf die
        Parameterkette: Kommt hier etwas anderes heraus als die Eingabe,
        ist irgendwo eine feste Zahl eingebaut."""
        punkte, dreiecke = zylinder(0.2, ringe=12, stufen=6)
        rau = punkte.copy()
        rau[::2] *= 1.02
        starts, nachbarn = Netzgeometrie.nachbarschaft(len(punkte), dreiecke)
        g = Glaettung.glaetten(rau, (starts, nachbarn), 'laplace',
                               durchgaenge=8, staerke=0.0)
        np.testing.assert_allclose(g, rau, atol=1e-12)

    def test_hc_alpha_zieht_zur_ausgangslage(self):
        u"""`hcAlpha` = 1 hält die Ausgangslage fest — das ist der ganze
        Sinn von HC (Vollmer/Mencl/Müller): Es zieht zurück, was Laplace
        weggezogen hat."""
        punkte, dreiecke = zylinder(0.2, ringe=16, stufen=8)
        rau = punkte.copy()
        rau[::2] *= 1.03
        starts, nachbarn = Netzgeometrie.nachbarschaft(len(punkte), dreiecke)
        weg = {}
        for alpha in (0.0, 1.0):
            g = Glaettung.glaetten(rau, (starts, nachbarn), 'hc',
                                   durchgaenge=8, staerke=0.5,
                                   alpha=alpha, beta=0.5)
            weg[alpha] = float(np.abs(np.linalg.norm(g, axis=1)
                                      - np.linalg.norm(rau, axis=1)).mean())
        self.assertLess(weg[1.0], weg[0.0],
                        u'alpha=1 muss näher an der Ausgangslage bleiben')

    def test_hc_beta_zieht_zu_den_nachbarn(self):
        u"""`hcBeta`: der Gegenspieler von alpha. Zwei verschiedene Werte
        müssen zwei verschiedene Ergebnisse liefern."""
        punkte, dreiecke = zylinder(0.2, ringe=16, stufen=8)
        rau = punkte.copy()
        rau[::2] *= 1.03
        starts, nachbarn = Netzgeometrie.nachbarschaft(len(punkte), dreiecke)
        a = Glaettung.glaetten(rau, (starts, nachbarn), 'hc', 8, 0.5,
                               alpha=0.5, beta=0.0)
        b = Glaettung.glaetten(rau, (starts, nachbarn), 'hc', 8, 0.5,
                               alpha=0.5, beta=1.0)
        self.assertGreater(float(np.abs(a - b).max()), 1e-6)

    def test_nahttoleranz_entscheidet_ueber_die_gruppe(self):
        u"""`weldedSeamTolerance`: Zwei Punkte an fast derselben Stelle
        gehören zusammen — aber nur, wenn die Toleranz sie erreicht."""
        punkte = np.array([[0.0, 0.0, 0.0], [1e-5, 0.0, 0.0],
                           [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
        dreiecke = np.array([[0, 2, 3]])
        eng = Nahtgruppen.bauen(punkte, dreiecke, toleranz=1e-7)
        weit = Nahtgruppen.bauen(punkte, dreiecke, toleranz=1e-4)
        # −1 heisst „gehört zu keiner Gruppe" — zwei Punkte, die BEIDE
        # −1 tragen, sind NICHT zusammengefasst. Wer hier schlicht auf
        # Ungleichheit prüft, vergleicht −1 mit −1 und hält die
        # Toleranz für wirkungslos.
        self.assertEqual(int(eng[0]), -1,
                         u'1e-7 darf die beiden nicht zusammenfassen')
        self.assertEqual(int(eng[1]), -1)
        self.assertGreaterEqual(int(weit[0]), 0,
                                u'1e-4 muss sie zusammenfassen')
        self.assertEqual(int(weit[0]), int(weit[1]))
