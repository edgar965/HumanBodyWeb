# -*- coding: utf-8 -*-
u"""Eine UMA-Figur in Python bauen — ohne Unity.

WARUM (08.09.2026, Edgar: „Ich möchte ein UMA Python das ein UMA Modell
baut, so wie das Unity Projekt das macht!")
=====================================================================
Der Weg ist derselbe wie in Unity: Rasse → `baseRaceRecipe` →
`recipeString` → Slots → verschmelzen → DNA → häuten. Möglich ist er, weil
UMA seine Assets MIT Typbaum ablegt; 255 der 256 Slot-Assets sind binär.

DIE RUHE-PROBE IST DIE SCHARFE
==============================
Mit unverändertem Skelett muss das Häuten das Eingangsnetz auf
Rechengenauigkeit zurückgeben. Sie ist beim Bau dieses Ports DREIMAL
gefallen, und jedes Mal sah das Ergebnis nach etwas anderem aus:

    Gewichte durch `umaBones` statt `boneNameHashes`   2.073 mm, Höhe 0,47 m
    Wurzel `Global` als Einheit angenommen             2.066 mm, Höhe 0,35 m
    Ruhelage aus `umaBones` (T-Pose) statt Bindepose      53 mm, nur Arme

Keine dieser drei Fassungen hat einen Fehler geworfen. Die erste ergab ein
Knäuel, die zweite eine gekippte Figur, die dritte eine, die fast richtig
aussah — 132 von 229 Knochen daneben, alle unterhalb der Schulter, alle um
denselben Betrag (44,5 Grad, der Armwinkel).
"""
import sys
import unittest
from pathlib import Path

import numpy as np
from django.conf import settings

sys.path.insert(0, str(Path(settings.ASSETS_ROOT)))

from UMA_Python import Figur                                   # noqa: E402
from UMA_Python.haut import Haut                               # noqa: E402
from UMA_Python.skelett import Skelett  # noqa: E402
from UMA_Python.verschmelzen import Verschmelzen                         # noqa: E402
from UMA_Python.unity import Assetdatei, Serialisiert          # noqa: E402

#: Der UMA-Klon. Ohne ihn ist hier nichts zu prüfen.
PROJEKT = Path(str(settings.TOOLS_ROOT)) / 'UMA' / 'UMAProject'

#: Die Rasse, an der gemessen wurde. Sie ist im Klon vorhanden.
RASSE = 'Human Female 3.0'


def _da():
    return (PROJEKT / 'Assets' / 'UMA').is_dir()


class UnityFormat(unittest.TestCase):
    u"""Der Leser für Unitys binäres Assetformat."""

    databases = set()

    def setUp(self):
        if not _da():
            self.skipTest(u'UMA-Klon nicht vorhanden (%s)' % PROJEKT)

    def test_ein_binaeres_slotasset_liest_sich(self):
        u"""Der Körper-Slot: 3.183 Punkte, 228 Knochen, 21 Formen.

        Die Zahlen stehen hier, weil sie die Probe SIND: Ein Leser, der
        sich um ein Byte verschiebt, liefert nicht weniger Daten, sondern
        andere — eine Punktzahl im Milliardenbereich oder Koordinaten von
        1e30. Beides sieht ohne Sollwert nach Daten aus.
        """
        pfad = (PROJEKT / 'Assets' / 'UMA' / 'UMA3' / 'Races' / 'Slots'
                / 'UMA30_Body' / 'UMA30_Body_UDIM1001_slot.asset')
        if not pfad.is_file():
            self.skipTest(u'%s fehlt' % pfad)
        self.assertFalse(Assetdatei.ist_text(pfad),
                         u'Der Slot sollte binär sein')
        datei = Serialisiert(pfad)
        self.assertTrue(datei.unity_fassung.startswith('6000.'))
        felder = datei.erstes().lesen()
        netz = felder['meshData']
        self.assertEqual(netz['vertexCount'], 3183)
        self.assertEqual(len(netz['vertices']), 3183)
        self.assertEqual(len(netz['umaBones']), 228)
        self.assertEqual(len(netz['boneNameHashes']), 229)
        self.assertEqual(len(netz['bindPoses']), 229)
        self.assertEqual(netz['RootBoneName'], 'Global')

    def test_die_guid_wird_mit_vertauschten_halbbytes_geschrieben(self):
        u"""GEGENPROBE zu einer Falle, die den ganzen Index leer lässt.

        `roh.hex()` findet KEINE der 24.033 `.meta`-Dateien des Projekts.
        Unity schreibt je Byte das untere Halbbyte zuerst.
        """
        from UMA_Python.unity.serialisiert import Verweis
        roh = bytes.fromhex('db97bf2f3814204191ce5534e7a40cd1')
        self.assertEqual(Verweis.als_text(roh),
                         'bd79fbf28341021419ec55437e4ac01d')
        self.assertNotEqual(Verweis.als_text(roh), roh.hex())

    def test_ein_textasset_wird_als_text_gelesen(self):
        u"""Beide Formate kommen in EINEM Projekt vor (1.023 Text, 588
        binär). Wer nur eines liest, läuft dem anderen in einen Fehler,
        der nach einer kaputten Datei aussieht."""
        dna = PROJEKT / 'Assets' / 'UMA' / 'UMA3' / 'DNA' / 'FemaleBody.asset'
        if not dna.is_file():
            self.skipTest(u'%s fehlt' % dna)
        self.assertTrue(Assetdatei.ist_text(dna))
        felder = Assetdatei.oeffnen(dna).erstes().lesen()
        self.assertEqual(felder.get('m_Name'), 'FemaleBody')
        self.assertTrue(felder.get('dnaList'))


class Figurbau(unittest.TestCase):
    u"""Der ganze Weg, an der Rasse `Human Female 3.0`."""

    databases = set()
    gebaut = None

    @classmethod
    def setUpClass(cls):
        if not _da():
            return
        # EINMAL bauen: Der Lauf kostet gemessen 6–14 s (acht Slots, davon
        # fünf über 2 MB). Je Testfall neu zu bauen hiesse, dieselbe Datei
        # vierzigmal zu zerlegen.
        cls.gebaut = Figur(PROJEKT).bauen(RASSE)

    def setUp(self):
        if self.gebaut is None:
            self.skipTest(u'UMA-Klon nicht vorhanden (%s)' % PROJEKT)

    def test_die_figur_ist_vollstaendig(self):
        bilanz = self.gebaut.bilanz()
        self.assertEqual(bilanz['fehlend'], [],
                         u'Slots, die das Rezept nennt und die fehlen')
        self.assertEqual(bilanz['punkte'], 16277)
        # 29.430, NICHT 58.538: Bis zum 08.09.2026 stand hier die Summe
        # ALLER fünf LOD-Stufen, weil `Slot._dreiecke` sie übereinander
        # legte. Die Zahl ist gegen Unitys eigenen Export derselben Rasse
        # belegt (`test_uma_gegenprobe.NetzGegenUnity`), Slot für Slot.
        self.assertEqual(bilanz['dreiecke'], 29430)
        self.assertEqual(bilanz['knochen'], 229)
        self.assertEqual(bilanz['slots'], 8)
        self.assertGreater(bilanz['regler'], 50)

    def test_die_gewichte_summieren_sich_auf_eins(self):
        u"""Eine Zeile, die sich nicht auf 1 summiert, schrumpft oder
        bläht ihren Punkt — sichtbar erst beim Bewegen."""
        summe = self.gebaut.netz.gewichte.sum(axis=1)
        np.testing.assert_allclose(summe, 1.0, atol=1e-5)

    def test_ruhe_ist_das_eingangsnetz(self):
        u"""DIE SCHARFE PROBE. Ohne DNA muss das Häuten den Eingang
        zurückgeben — jeder Bindepose-, Reihenfolge- oder
        Zuordnungsfehler fällt hier (siehe Kopf: dreimal geschehen)."""
        netz = self.gebaut.netz
        skelett = Skelett(netz.knochen)
        matrizen = Haut.matrizen(skelett.weltmatrizen(), netz.bindeposen)
        ruhe = Haut.verformen(netz.punkte, netz.gewichte,
                              netz.knochenindex, matrizen)
        abweichung = float(np.abs(ruhe - netz.punkte).max()) * 1000.0
        self.assertLess(abweichung, 0.01,
                        u'Ruhefehler %.4f mm — das Skinning stimmt nicht'
                        % abweichung)

    def test_die_gegenprobe_zur_ruhe(self):
        u"""Ein VERDREHTER Knochen muss die Probe fallen lassen.

        Ohne diese Gegenprobe prüfte der Test darüber nichts: Wären alle
        Matrizen zufällig die Einheit, käme der Eingang ebenfalls
        unverändert zurück (MEMORY.md, „SkinnedMesh Debug Pattern").
        """
        netz = self.gebaut.netz
        skelett = Skelett(netz.knochen)
        welt = skelett.weltmatrizen()
        welt[10] = welt[10] @ Skelett.matrix([0.3, 0.0, 0.0],
                                             [0, 0, 0, 1], [1, 1, 1])
        matrizen = Haut.matrizen(welt, netz.bindeposen)
        verschoben = Haut.verformen(netz.punkte, netz.gewichte,
                                    netz.knochenindex, matrizen)
        self.assertGreater(float(np.abs(verschoben - netz.punkte).max()),
                           0.01, u'Ein verschobener Knochen bewegt nichts')

    def test_die_hoehe_stimmt(self):
        u"""1,99 m — und der Regler `height` verändert sie wirklich."""
        netz = self.gebaut.netz
        hoehe = float(netz.punkte[:, 2].max() - netz.punkte[:, 2].min())
        self.assertAlmostEqual(hoehe, 1.99, delta=0.05)

    def test_der_hoehenregler_wirkt(self):
        u"""Klein < Vorgabe < gross. Gemessen 1,45 / 1,99 / 3,18 m.

        Die Reihenfolge ist die Probe, nicht der Betrag: Ein Regler, der
        nichts tut, gibt dreimal denselben Wert — und das ist genau der
        Zustand, in dem eine falsch gelesene Kurve oder eine vergessene
        Abbildung nicht auffällt.
        """
        def hoehe(wert):
            punkte = self.gebaut.punkte({'height': wert})
            return float(punkte[:, 2].max() - punkte[:, 2].min())

        klein, mitte, gross = hoehe(0.0), hoehe(0.5), hoehe(1.0)
        self.assertLess(klein, mitte)
        self.assertLess(mitte, gross)
        self.assertGreater(gross - klein, 0.5)

    def test_zweimal_stellen_verdoppelt_nicht(self):
        u"""Das Skelett wird vor jedem Lauf zurückgesetzt.

        Ohne das addieren sich zwei Aufrufe: Wer denselben Wert zweimal
        setzt, bekäme die doppelte Verformung — und der erste Aufruf sah
        richtig aus.
        """
        erst = self.gebaut.punkte({'height': 0.8})
        zweit = self.gebaut.punkte({'height': 0.8})
        np.testing.assert_allclose(erst, zweit, atol=1e-9)

    def test_die_ruhelage_kommt_aus_den_bindeposen(self):
        u"""`welt @ bindepose` muss je Knochen die Einheit ergeben.

        Aus `umaBones` gerechnet stimmt das nur für Rumpf und Beine: Dort
        steht die T-POSE, und die Arme liegen 44,5 Grad daneben.

        AUSGENOMMEN SIND KNOCHEN OHNE ECHTE BINDEPOSE (08.09.2026): 73
        der 229 heißen `*_end` und tragen dort die Einheitsmatrix, ohne
        ein einziges Hautgewicht. Sie gegen diesen Platzhalter zu prüfen
        ergäbe 73 Fehlalarme — und die Ruhelage aus ihm zu rechnen schob
        sie in den Ursprung, was im Bild ein Fächer aus bis zu 1,59 m
        langen Knochenlinien war (`Verschmelzen.hat_bindepose`).
        """
        netz = self.gebaut.netz
        eigene = Verschmelzen.hat_bindepose(netz)
        self.assertGreater(int((~eigene).sum()), 0,
                           u'ohne solche Knochen prüft der Test nichts')
        skelett = Skelett(netz.knochen)
        produkt = skelett.weltmatrizen() @ netz.bindeposen
        einheit = np.tile(np.eye(4), (len(produkt), 1, 1))
        abweichung = np.abs(produkt - einheit).reshape(
            len(produkt), -1).max(axis=1)
        self.assertLess(float(abweichung[eigene[:len(abweichung)]].max()), 1e-4)

    def test_die_endknochen_behalten_ihre_lage(self):
        u"""Die Gegenprobe zum Vorigen: Sie stehen NICHT im Ursprung.

        Gemessen am 08.09.2026, als sie es taten: Linien von bis zu
        1,59 m aus Gesicht, Fingern und Zehen zum Boden — während alle
        229 echten Knochen auf 0,01 mm richtig saßen.
        """
        netz = self.gebaut.netz
        eigene = Verschmelzen.hat_bindepose(netz)
        welt = Skelett(netz.knochen).weltmatrizen()[:, :3, 3]
        ohne = welt[~eigene]
        self.assertGreater(len(ohne), 50)
        self.assertGreater(float(np.linalg.norm(ohne, axis=1).min()), 0.05,
                           u'ein Endknochen sitzt im Ursprung')


class SkelettRechnung(unittest.TestCase):
    u"""Die Bausteine ohne Assets — laufen auch ohne UMA-Klon."""

    databases = set()

    def test_zerlegen_ist_die_umkehrung_von_matrix(self):
        u"""Beide Richtungen, an einer Matrix mit Drehung UND Skala."""
        ort = np.array([0.1, -0.2, 0.3])
        drehung = Skelett.aus_achse([0.3, 0.9, 0.1], 47.0)
        skala = np.array([1.2, 0.8, 1.05])
        m = Skelett.matrix(ort, drehung, skala)
        zurueck = Skelett.zerlegen(m)
        np.testing.assert_allclose(zurueck[0], ort, atol=1e-12)
        np.testing.assert_allclose(zurueck[2], skala, atol=1e-12)
        np.testing.assert_allclose(Skelett.matrix(*zurueck), m, atol=1e-12)

    def test_zerlegen_haelt_auch_die_halbe_drehung(self):
        u"""180 Grad ist der Fall, an dem die einfache Formel durch null
        teilt — deshalb Shepperds Fallwahl in `aus_matrix`."""
        m = Skelett.matrix([0, 0, 0], Skelett.aus_achse([0, 1, 0], 180.0),
                           [1, 1, 1])
        zurueck = Skelett.zerlegen(m)
        np.testing.assert_allclose(Skelett.matrix(*zurueck), m, atol=1e-9)

    def test_die_reihenfolge_stellt_eltern_vor_kinder(self):
        u"""`umaBones` steht in keiner verwertbaren Ordnung — der erste
        Eintrag des Körper-Slots ist `Neck`, nicht `Global`."""
        eltern = np.array([2, 0, -1, 1], dtype=np.int64)
        folge = list(Skelett._reihenfolge(eltern))
        for kind, vater in enumerate(eltern):
            if vater >= 0:
                self.assertLess(folge.index(int(vater)), folge.index(kind))

    def test_ein_zyklus_haengt_nicht(self):
        u"""Kaputte Daten dürfen den Server nicht anhalten."""
        folge = Skelett._reihenfolge(np.array([1, 0], dtype=np.int64))
        self.assertEqual(sorted(int(i) for i in folge), [0, 1])
