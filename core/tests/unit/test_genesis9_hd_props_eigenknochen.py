# -*- coding: utf-8 -*-
"""Genesis 9, 18.09.2026 (Edgar: „Forsche wie das geht!"): HD-Morphs (`.dhdm`),
Props in der Hand (`G9requisit`), eigene Knochen eines Anhangs (Eirgrid,
`G9eigenknochen`), Stilarten der Garderobe, Detailnormalen fuer den Browser,
Verschiebung im Elternraum — alles OHNE Daz-Bibliothek (Kunstdaten).

Sabotage-Gegenproben (je ein Fall): `G9hdmorph._stufe` mit `idx >> (14 -
2·L)` fuer die Unterflaeche -> Fall 1 rot; `G9hdmorphe._rahmen` mit `+y`
statt `−y` in der dritten Spalte -> Fall 2 rot; `G9requisit.matrix` ohne
`T(−c)` -> Fall 4 rot; `G9knochenmatrizen._knochen` mit `t` im Weltraum ->
Fall 7 rot.
"""

import struct
from unittest import mock

import numpy as np
from django.test import SimpleTestCase

from Genesis9.browserbilder import G9browserbilder
from Genesis9.dson import G9dson
from Genesis9.eigenknochen import G9eigenknochen
from Genesis9.garderobeeintrag import G9garderobeeintrag
from Genesis9.hdmorph import G9hdmorph
from Genesis9.hdmorphe import G9hdmorphe
from Genesis9.knochenmatrizen import G9knochenmatrizen
from Genesis9.skelett import G9skelett
from Genesis9.requisit import G9requisit


def _dhdm(stufen):
    """Eine `.dhdm` aus `{stufe: [(flaeche, idx16, x, y, z)]}` bauen."""
    roh = struct.pack("<IIII", 0xD0D0D0D0, len(stufen), 0x3F800000, len(stufen))
    for stufe in sorted(stufen):
        daten = b""
        je_flaeche = {}
        for flaeche, idx, x, y, z in stufen[stufe]:
            je_flaeche.setdefault(flaeche, []).append((idx, x, y, z))
        for flaeche, eintraege in je_flaeche.items():
            daten += struct.pack("<II", flaeche, len(eintraege))
            for idx, x, y, z in eintraege:
                if stufe < 4:
                    daten += struct.pack("<fBBff", x, idx >> 8, (stufe + 1) * 16, y, z)
                else:
                    daten += struct.pack("<fBBBBff", x, 0, idx & 255, idx >> 8, (stufe + 1) * 16, y, z)
        roh += struct.pack("<IIII", 4, stufe, len(stufen[stufe]), len(daten)) + daten
    return roh


class Genesis9HdMorph(SimpleTestCase):
    databases = set()

    def test_1_leser_zerlegt_adresse_und_vektor(self):
        # Stufe 1: Unterflaeche 2 (Bits 15–14), Ecke 3 (Bits 13–12) -> idx 0b1011 << 12.
        # Stufe 2: Unterflaeche 9 (Bits 15–12), Ecke 1 (Bits 11–10).
        roh = _dhdm(
            {
                1: [(5, 0b10_11 << 12, 1.0, 2.0, 3.0)],
                2: [(5, (9 << 12) | (1 << 10), 0.5, 0.0, -0.5), (7, (0 << 12) | (2 << 10), 0.0, 1.0, 0.0)],
                3: [(5, 0, 9.0, 9.0, 9.0)],
            }
        )
        m = G9hdmorph._zerlegen("x.dhdm", roh, 2)
        self.assertEqual(m.anzahl_stufen, 3)
        self.assertEqual(sorted(m.stufen), [1, 2])  # Stufe 3 bleibt liegen
        s1 = m.stufen[1]
        self.assertEqual((int(s1["flaeche"][0]), int(s1["unterflaeche"][0]), int(s1["ecke"][0])), (5, 2, 3))
        self.assertTrue(np.allclose(s1["vektor"][0], [1.0, 2.0, 3.0]))
        s2 = m.stufen[2]
        self.assertEqual(s2["unterflaeche"].tolist(), [9, 0])
        self.assertEqual(s2["ecke"].tolist(), [1, 2])
        self.assertEqual(s2["flaeche"].tolist(), [5, 7])

    def test_2_rahmen_der_flaechenecke(self):
        """Viereck in der xz-Ebene, Umlauf gegen den Uhrzeiger von oben: z-Achse
        des Rahmens = Flaechennormale, x = zur Ecke davor, dritte Spalte −y."""
        flaechen = np.array([[0, 1, 2, 3]])
        punkte = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [1.0, 0.0, -1.0], [0.0, 0.0, -1.0]])
        rahmen = G9hdmorphe._rahmen(flaechen, punkte)
        normale = rahmen[0, 0, :, 1]
        self.assertTrue(np.allclose(normale, [0, 1, 0]), normale)
        x0 = rahmen[0, 0, :, 0]  # Ecke 0: zur Ecke 3 (0,0,-1)
        self.assertTrue(np.allclose(x0, [0, 0, -1]), x0)
        dritte = rahmen[0, 0, :, 2]  # −y = −(z × x)
        self.assertTrue(np.allclose(dritte, [1, 0, 0]), dritte)
        # Dreieck: Ecke vor der 0 ist die 2.
        dreieck = np.array([[0, 1, 2, -1]])
        r = G9hdmorphe._rahmen(dreieck, punkte)
        self.assertTrue(np.allclose(r[0, 0, :, 0], [1, 0, -1] / np.sqrt(2)))
        self.assertEqual(
            G9hdmorphe._beginn(np.array([[0, 1, 2, -1], [0, 1, 2, 3], [0, 1, 2, 3]])).tolist(), [0, 3, 7]
        )


class Genesis9Requisit(SimpleTestCase):
    databases = set()

    KNOTEN = {
        "id": "Dolch",
        "parent": "name://@selection/r_hand:",
        "translation": [{"id": "x", "current_value": -50.0}, {"id": "y", "current_value": 70.0}],
        "rotation": [{"id": "z", "current_value": 90.0}],
        "center_point": [{"id": "y", "current_value": 20.0}],
        "rotation_order": "YXZ",
    }

    def test_3_knoten_lesen(self):
        definition = {"rotation_order": "XYZ", "center_point": [{"id": "y", "value": -38.0}]}
        lage = G9requisit.aus_knoten(self.KNOTEN, definition)
        self.assertEqual(lage.knochen, "r_hand")
        self.assertEqual(lage.translation.tolist(), [-50.0, 70.0, 0.0])
        self.assertEqual(lage.mitte.tolist(), [0.0, 20.0, 0.0])  # Szene vor .dsf
        self.assertEqual(lage.reihenfolge, "YXZ")
        self.assertIsNone(G9requisit.aus_knoten({"id": "frei"}))

    def test_4_ruhelage_dreht_um_den_drehpunkt_und_verschiebt(self):
        lage = G9requisit.aus_knoten(self.KNOTEN)
        # Der Drehpunkt selbst wandert nur um t; ein Punkt 10 cm ueber ihm
        # liegt nach Rz(90°) 10 cm links davon (x = −10).
        drehpunkt = np.array([[0.0, 0.20, 0.0]])
        oben = np.array([[0.0, 0.30, 0.0]])
        self.assertTrue(np.allclose(lage.ruhelage(drehpunkt), [[-0.5, 0.9, 0.0]]))
        self.assertTrue(np.allclose(lage.ruhelage(oben), [[-0.6, 0.9, 0.0]]))
        haut = lage.haut(3)
        self.assertEqual(haut.knochen, ["r_hand"])
        self.assertTrue((haut.gewicht[:, 0] == 1).all())

    def test_5_griffpose_ohne_skalierung_eins(self):
        doc = G9dson(
            "x.duf",
            {
                "scene": {
                    "animations": [
                        {"url": "name://@selection/r_thumb1:?rotation/x/value", "keys": [[0, -8.4]]},
                        {"url": "name://@selection/r_thumb1:?scale/general/value", "keys": [[0, 1]]},
                        {"url": "name://@selection/r_hand:?scale/x/value", "keys": [[0, 1]]},
                    ]
                }
            },
        )
        self.assertEqual(G9requisit.griff(doc), {"r_thumb1": {"rotation/x": -8.4}})


class Genesis9Eigenknochen(SimpleTestCase):
    databases = set()

    def _doc(self):
        return G9dson(
            "haar.dsf",
            {
                "node_library": [
                    {"id": "Haar", "type": "figure"},
                    {
                        "id": "spine4",
                        "type": "bone",
                        "parent": "#Haar",
                        "center_point": [{"id": "y", "value": 120}],
                        "end_point": [{"id": "y", "value": 140}],
                    },
                    {
                        "id": "Zopf",
                        "type": "bone",
                        "parent": "#spine4",
                        "center_point": [{"id": "y", "value": 160}],
                        "end_point": [{"id": "y", "value": 120}],
                        "rotation_order": "XYZ",
                        "inherits_scale": True,
                    },
                ],
                "modifier_library": [
                    {
                        "id": "SkinBinding",
                        "skin": {
                            "vertex_count": 2,
                            "joints": [
                                {
                                    "id": "spine4",
                                    "node": "#spine4",
                                    "node_weights": {"count": 1, "values": [[0, 1.0]]},
                                },
                                {
                                    "id": "Zopf",
                                    "node": "#Zopf",
                                    "node_weights": {"count": 1, "values": [[1, 1.0]]},
                                },
                            ],
                        },
                    }
                ],
            },
        )

    def test_6_eigene_knochen_drehen_ihre_punkte(self):
        eigene = G9eigenknochen.aus_dokument(self._doc(), ["spine4"])
        self.assertEqual(eigene.namen, ["Zopf"])
        self.assertEqual(eigene.knochen[0]["eltern"], "spine4")
        self.assertEqual(eigene.haut.knochen, ["spine4", "Zopf"])
        roh = [
            {
                "name": "spine4",
                "eltern": None,
                "kopf": np.array([0.0, 120.0, 0.0]),
                "schwanz": np.array([0.0, 140.0, 0.0]),
                "erbt": False,
                "orientation": np.zeros(3),
                "reihenfolge": "XYZ",
            }
        ] + eigene.knochen
        matrizen = G9knochenmatrizen({}, roh=roh, drehung={"Zopf": {"rotation/z": 90}})
        punkte = np.array([[0.0, 1.3, 0.0], [0.0, 1.2, 0.0]])  # Meter; Zopfspitze
        aus = matrizen.anwenden(punkte, eigene.haut)
        self.assertTrue(np.allclose(aus[0], punkte[0]))  # spine4 ruht
        # Die Spitze (40 cm unter dem Gelenk bei y = 1,6) dreht um z: nach +x.
        self.assertTrue(np.allclose(aus[1], [0.4, 1.6, 0.0], atol=1e-6), aus[1])
        # Fuer das Browser-Skelett: der Zopf in derselben Stellung (Meter), am
        # Elternknochen — Spitze gedreht nach +x, Kopf unveraendert.

        class Formung:
            drehung = {}

            class formeln:
                @staticmethod
                def posen():
                    return {}

                @staticmethod
                def knochen():
                    return {}

        with mock.patch.object(G9skelett, "roh", return_value=roh[:1]):
            gelenke = eigene.gelenke(Formung(), {"Zopf": {"rotation/z": 90}}, boden=0.1)
        self.assertEqual([g["name"] for g in gelenke], ["Zopf"])
        self.assertEqual(gelenke[0]["eltern"], "spine4")
        self.assertTrue(np.allclose(gelenke[0]["kopf"], [0.0, 1.5, 0.0]), gelenke[0])
        self.assertTrue(np.allclose(gelenke[0]["schwanz"], [0.4, 1.5, 0.0], atol=1e-6), gelenke[0])


class Genesis9Verschiebung(SimpleTestCase):
    databases = set()

    def test_7_verschiebung_im_elternraum(self):
        """`hip?translation/y` unter der um 25 % skalierten Figur: Daz waechst
        die Verschiebung mit (`W = W_eltern · T(t) · …`)."""
        roh = [
            {
                "name": "hip",
                "eltern": None,
                "kopf": np.array([0.0, 100.0, 0.0]),
                "schwanz": np.array([0.0, 80.0, 0.0]),
                "erbt": True,
                "orientation": np.zeros(3),
                "reihenfolge": "XYZ",
            }
        ]
        m = G9knochenmatrizen({"Genesis9": {"scale/general": 1.25}, "hip": {"translation/y": 20.0}}, roh=roh)
        gelenk = (m.matrizen()["hip"] @ np.array([0.0, 100.0, 0.0, 1.0]))[:3]
        self.assertTrue(np.allclose(gelenk, [0.0, 150.0, 0.0]), gelenk)  # 1,25·(100+20)


class Genesis9Stilarten(SimpleTestCase):
    databases = set()

    def test_8_stil_pose_laenge(self):
        def doc(zeilen):
            return G9dson(
                "s.duf", {"scene": {"animations": [{"url": u, "keys": [[0, w]]} for u, w in zeilen]}}
            )

        eigene, knochen = {"Frizz"}, {"Zopf"}
        werte, gedreht, fremd = G9garderobeeintrag._stilwerte(
            doc(
                [
                    ("name://@selection/Zopf:?rotation/x/value", 10.7),
                    ("name://@selection/Zopf:?scale/general/value", 1),
                    ("name://@selection#Frizz:?value/value", 0.45),
                ]
            ),
            eigene,
            knochen,
        )
        self.assertEqual((werte, gedreht, fremd), ({"Frizz": 0.45}, {"Zopf": {"rotation/x": 10.7}}, False))
        self.assertEqual(G9garderobeeintrag._stilart(gedreht), "pose")
        _w, laenge, _f = G9garderobeeintrag._stilwerte(
            doc([("name://@selection/Zopf:?scale/y/value", 1.07)]), eigene, knochen
        )
        self.assertEqual(G9garderobeeintrag._stilart(laenge), "laenge")
        self.assertEqual(G9garderobeeintrag._stilart({}), "stil")
        _w, _g, fremd = G9garderobeeintrag._stilwerte(
            doc([("name://@selection/r_thumb1:?rotation/x/value", -8.4)]), eigene, knochen
        )
        self.assertTrue(fremd)  # Griffpose: Figur


class Genesis9Browserbilder(SimpleTestCase):
    databases = set()

    def test_9_detailnormalen_nur_hoch(self):
        gross = {"Runtime/Textures/x/8k_NM.jpg"}

        def tragbar(relativ, grenze=None):
            grenze = grenze or G9browserbilder.SCHWER_MB * 1024 * 1024
            return not (relativ in gross and grenze <= 20 * 1024 * 1024)

        bilder = {
            "albedo": "Runtime/Textures/x/A_D_1001.jpg",
            "normalen": "Runtime/Textures/x/N.jpg",
            "detailnormalen": "Runtime/Textures/x/8k_NM.jpg",
            "detailgewicht": 1.0,
            "farbe": [1, 1, 1],
        }
        with mock.patch.object(G9browserbilder, "tragbar", side_effect=tragbar):
            tief = G9browserbilder.fuer(bilder, hoch=False)
            self.assertNotIn("detailnormalen", tief)
            self.assertNotIn("detailgewicht", tief)
            self.assertEqual(tief["normalen"], "Runtime/Textures/x/N.jpg")
            hoch = G9browserbilder.fuer(bilder, hoch=True)
            self.assertEqual(hoch["detailnormalen"], "Runtime/Textures/x/8k_NM.jpg")
            self.assertEqual(hoch["detailgewicht"], 1.0)
            # Ohne Grundnormalen wird das Detailbild die einzige Normale (Amala);
            # ohne alles der 4K-Nachbar der Albedo.
            ohne = dict(bilder)
            del ohne["normalen"]
            self.assertEqual(
                G9browserbilder.fuer(ohne, hoch=True)["normalen"], "Runtime/Textures/x/8k_NM.jpg"
            )
            self.assertEqual(
                G9browserbilder.fuer(ohne, hoch=False)["normalen"], "Runtime/Textures/x/A_NM_1001.jpg"
            )
