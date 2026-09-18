# -*- coding: utf-8 -*-
"""Genesis 9, 18.09.2026 abends (Edgar: „genesis 8 … kannst du das in Genesis9
mergen", „dForce-Stoff … kannst du das einbauen"): Auto-Fit ueber den Clone
(`G9autofit`) und die dForce-Daten fuer den Stoffschwung (`G9stoff`) — ohne
Daz-Bibliothek, mit Kunstdaten.

Sabotage-Gegenproben: `G9autofit.umrechnen` ohne `o9.T @ … @ o9` (Winkel
unveraendert uebernehmen) -> Fall 3 rot; `G9stoff._typ` liest nur
`current_value` -> Fall 5 rot (die `.dsf` traegt `value`); `G9stoff.kanten`
ohne Sortierung `a < b` -> Fall 7 rot.
"""

from unittest import mock

import numpy as np
from django.test import SimpleTestCase

from Genesis9.autofit import G9autofit
from Genesis9.dson import G9dson
from Genesis9.knochenmatrizen import G9knochenmatrizen
from Genesis9.netzstufe import G9netzstufe
from Genesis9.skelett import G9skelett
from Genesis9.stoff import G9stoff


def _knochen(kennung, eltern, orientation, reihenfolge="XYZ"):
    return {
        "id": kennung,
        "type": "bone",
        "parent": "#%s" % eltern if eltern else None,
        "center_point": [{"id": a, "value": w} for a, w in zip("xyz", (0, 0, 0))],
        "end_point": [{"id": a, "value": w} for a, w in zip("xyz", (0, 10, 0))],
        "orientation": [{"id": a, "value": w} for a, w in zip("xyz", orientation)],
        "rotation_order": reihenfolge,
    }


class Genesis9Autofit(SimpleTestCase):
    databases = set()

    def test_1_schablone_liest_skelett_und_drehung(self):
        roh, drehung = G9autofit.schablone(
            {
                "nodes": [
                    {"id": "ROOT_SKELETON", "center_point": [0, 0, 0]},
                    {
                        "id": "hip",
                        "parent": "ROOT_SKELETON",
                        "center_point": [0, 105, 1.8],
                        "end_point": [0, 88, 0],
                        "orientation": [0, 0, 0],
                        "rotation": [0, 0, 0],
                    },
                    {
                        "id": "lThighBend",
                        "parent": "hip",
                        "center_point": [7.9, 96.4, 0.4],
                        "end_point": [11.5, 75.8, -0.1],
                        "orientation": [1.2, 4.9, 7.9],
                        "rotation": [0, 0, -6],
                    },
                ]
            }
        )
        self.assertEqual([k["name"] for k in roh], ["hip", "lThighBend"])
        self.assertIsNone(roh[0]["eltern"])
        self.assertEqual(roh[1]["eltern"], "hip")
        self.assertEqual(drehung, {"lThighBend": {"rotation/z": -6.0}})

    def test_2_g9name_der_fuesse(self):
        self.assertEqual(G9autofit.g9name("lFoot"), "l_foot")
        self.assertEqual(G9autofit.g9name("rSmallToe2_2"), "r_midtoe2")
        self.assertEqual(G9autofit.g9name("lBigToe_2"), "l_bigtoe2")
        self.assertIsNone(G9autofit.g9name("lShldrBend"))
        self.assertIsNone(G9autofit.g9name("head"))

    def test_3_umrechnen_gleiche_drehung_in_der_welt(self):
        """Ein G8-Knochen mit 30° Orientierung um y und ein G9-Knochen ohne:
        25,9° um die G8-x-Achse muss in der Welt dieselbe Drehung bleiben."""
        g8 = _knochen("lFoot", "lShin", (0.0, 30.0, 0.0), "ZYX")
        g9 = {"name": "l_foot", "orientation": (0.0, 0.0, 0.0), "reihenfolge": "ZYX"}
        aus = G9autofit.umrechnen(g8, g9, [25.9, 0.0, 0.0])
        o8 = G9knochenmatrizen.euler((0.0, 30.0, 0.0), "XYZ")
        welt = o8 @ G9knochenmatrizen.euler([25.9, 0, 0], "ZYX") @ o8.T
        neu = G9knochenmatrizen.euler([aus.get("rotation/%s" % a, 0.0) for a in "xyz"], "ZYX")
        self.assertTrue(np.allclose(welt, neu, atol=1e-6), aus)
        # Ohne Orientierungsunterschied bleiben die Winkel, wie sie sind.
        g8 = _knochen("lFoot", "lShin", (0.0, 0.0, 0.0), "ZYX")
        self.assertEqual(G9autofit.umrechnen(g8, g9, [25.9, 0.0, 0.0]), {"rotation/x": 25.9})

    def test_4_figurpose_aus_einer_g8_pose(self):
        pose = G9dson(
            "p.duf",
            {
                "scene": {
                    "animations": [
                        {
                            "url": "lFoot:/data/x/Genesis8Female.dsf#lFoot?rotation/x/value",
                            "keys": [[0, 25.9]],
                        },
                        {"url": "lFoot:/data/x/Genesis8Female.dsf#lFoot?scale/x/value", "keys": [[0, 1]]},
                        {
                            "url": "lShldrBend:/data/x/Genesis8Female.dsf#lShldrBend?rotation/z/value",
                            "keys": [[0, 40]],
                        },
                    ]
                }
            },
        )
        rig = G9dson("r.dsf", {"node_library": [_knochen("lFoot", "lShin", (0, 0, 0))]})
        roh = [{"name": "l_foot", "orientation": (0.0, 0.0, 0.0), "reihenfolge": "ZYX"}]
        with mock.patch.object(G9skelett, "roh", return_value=roh):
            self.assertEqual(G9autofit.figurpose(pose, rig), {"l_foot": {"rotation/x": 25.9}})


class Genesis9Stoff(SimpleTestCase):
    databases = set()

    @staticmethod
    def _doc(typ, szene=None, gewichte=None):
        extra = [{"type": G9stoff.MODIFIKATOR, "vertex_count": 4}]
        if gewichte is not None:
            extra[0]["influence_weights"] = {"count": len(gewichte), "values": gewichte}
        extra.append(
            {
                "type": "studio_modifier_channels",
                "channels": [{"channel": {"id": G9stoff.KANAL, "type": "enum", "value": typ}}],
            }
        )
        doc = G9dson("n.dsf", {"modifier_library": [{"id": "dForce Simulation", "extra": extra}]})
        if szene is None:
            return doc, None
        return doc, G9dson(
            "s.duf",
            {
                "scene": {
                    "modifiers": [
                        {
                            "id": "dForce Simulation",
                            "extra": [
                                {
                                    "type": "studio_modifier_channels",
                                    "channels": [{"channel": {"id": G9stoff.KANAL, "current_value": szene}}],
                                }
                            ],
                        }
                    ]
                }
            },
        )

    def test_5_dynamisch_aus_dsf_und_szene(self):
        doc, _ = self._doc(1)
        self.assertTrue(G9stoff.dynamisch(doc))
        doc, _ = self._doc(0)
        self.assertFalse(G9stoff.dynamisch(doc))
        # Angie Jeans: 0 in der Datei, 1 in der Szene.
        doc, szene = self._doc(0, szene=1)
        self.assertTrue(G9stoff.dynamisch(doc, szene))
        ohne = G9dson("o.dsf", {"modifier_library": [{"id": "SkinBinding", "extra": []}]})
        self.assertFalse(G9stoff.dynamisch(ohne))

    def test_6_dynamik_und_freiheit(self):
        doc, _ = self._doc(1, gewichte=[[1, 0.5], [3, 0.0], [9, 0.7]])
        dynamik = G9stoff.dynamik(doc, 4)
        self.assertEqual(dynamik.tolist(), [1.0, 0.5, 1.0, 0.0])
        # Haftung: 0 an der Haut, 1 ab 2 cm.
        fein = np.array([[0, 0, 0], [0.01, 0, 0], [0.05, 0, 0], [0.5, 0, 0]])
        koerper = np.array([[0, 0, 0], [0, 1, 0]])
        frei = G9stoff.freiheit(dynamik, None, fein, koerper)
        self.assertEqual([round(float(w), 2) for w in frei], [0.0, 0.25, 1.0, 0.0])

    def test_7_kanten_und_bauplan(self):
        kanten = G9stoff.kanten([[0, 0, 2, 1, 0], [0, 0, 1, 3, 0, 2]])
        # Dreieck (2,1,0) und Viereck (1,3,0,2): fuenf Kanten, jede einmal.
        self.assertEqual(kanten.tolist(), [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3]])
        folger = mock.Mock(punkte=np.zeros((4, 3)), polys=[[0, 0, 0, 1, 2, 3]], haut=None)
        # Stufe 0: die Matrix ist eine Eins je Browserpunkt auf seinen Ursprung
        # (`G9netzstufe.matrix`, seit 18.09.2026 abends dort statt im Bauplan).
        stufe = G9netzstufe.__new__(G9netzstufe)
        stufe._cc = None
        stufe.ursprung = np.array([0, 1, 2, 3, 1])
        plan = G9stoff.bauplan(folger, stufe)
        self.assertEqual((plan["punkte"], plan["zeilen"]), (4, 5))
        self.assertEqual(plan["indices"].tolist(), [0, 1, 2, 3, 1])
        self.assertEqual(plan["data"].tolist(), [1.0] * 5)
        self.assertEqual(plan["kanten"].tolist(), [[0, 1], [0, 3], [1, 2], [2, 3]])
