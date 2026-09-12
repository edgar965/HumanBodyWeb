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
import unittest

from ._umaabdeckung import Abdeckung, Umaquelle


class Vollstaendig(unittest.TestCase):
    u"""Die Tabelle gegen den echten C#-Quelltext."""

    databases = set()

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
        self.ordner = Umaquelle.quellordner()
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
            namen |= Umaquelle.mitglieder(text)
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
            namen |= Umaquelle.mitglieder(text, privat=True)
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
