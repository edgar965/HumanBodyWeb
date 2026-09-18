# -*- coding: utf-8 -*-
"""Genesis 9 gegen die installierte Daz-Bibliothek (18.09.2026, „Forsche wie
das geht!"): HD-Morphs auf Stufe 1 und 2, 8K-Detailnormalen nur mit
Strg+Alt+H, Eirgrid-Posen und -Laengen ueber die Zopfknochen, Props in der
Hand mit Griffpose, Makeup-System aus den Script-Load-Presets.

LongRunner: Netze mit Stufe 2 (410.202 Punkte, ~2 s), Eirgrid 428.373
Punkte. Ohne Bibliothek uebersprungen.

Sabotage-Gegenproben: `G9hdmorphe.beitrag` -> `return None` laesst
`test_hd_beitrag_allein` rot werden; `G9requisit.ruhelage`
ohne Verschiebung -> `test_prop_haengt_an_der_hand` rot.
"""

import base64
import json
import unittest

import numpy as np
from django.test import Client, SimpleTestCase

from Genesis9.garderobe import G9garderobe
from Genesis9.hdmorphe import G9hdmorphe
from Genesis9.morphablage import G9morphablage
from Genesis9.pfade import G9pfade
from Genesis9.schminke import G9schminke
from Genesis9.skelett import G9skelett


def bibliothek_da():
    return G9pfade.vorhanden()


def _punkte(antwort):
    roh = base64.b64decode(antwort["vertices"])
    return np.frombuffer(roh, dtype=np.float32).reshape(-1, 3).astype(np.float64)


@unittest.skipUnless(bibliothek_da(), "Daz-Bibliothek mit Genesis 9 fehlt")
class HdUndDetailTest(SimpleTestCase):
    databases = set()

    def setUp(self):
        self.client = Client()

    def _netz(self, name, rumpf, hoch=False):
        if hoch:
            self.client.cookies["netzstufen"] = "3"
        else:
            self.client.cookies.pop("netzstufen", None)
        antwort = self.client.post(
            "/api/character/genesis9-figur/%s/netz/" % name,
            data=json.dumps(rumpf),
            content_type="application/json",
        )
        self.assertEqual(antwort.status_code, 200, antwort.content[:300])
        return antwort.json()

    def test_hd_kanaele_in_der_ablage(self):
        kanaele = G9hdmorphe.kanaele(G9morphablage.holen())
        self.assertGreaterEqual(len(kanaele), 50)
        self.assertIn("body_bs_Navel_HD3", kanaele)
        self.assertTrue(kanaele["body_bs_Navel_HD3"].endswith("body_bs_Navel_HD3.dhdm"))

    def test_hd_beitrag_allein(self):
        """Der HD-Anteil ohne die Kaefigdeltas: Nabel HD3 auf Stufe 1 — einige
        hundert Punkte, hoechstens 2 mm (gemessen 1,6 mm)."""
        from Genesis9.basisnetz import G9basisnetz
        from Genesis9.formung import G9formung

        formung = G9formung({"body_bs_Navel_HD3": 1.0})
        stufe1 = G9basisnetz.holen().netzstufe(1)
        beitrag = G9hdmorphe.beitrag(formung.formeln, stufe1, stufe1, formung.punkte())
        self.assertIsNotNone(beitrag)
        n = np.linalg.norm(beitrag, axis=1)
        self.assertTrue(100 < (n > 1e-6).sum() < 1000, (n > 1e-6).sum())
        self.assertTrue(0.0005 < n.max() < 0.002, n.max())

    def test_hd_morph_bewegt_stufe_1_und_2(self):
        ohne = self._netz("basis", {"anhaenge": False})
        mit = self._netz("basis", {"anhaenge": False, "regler": {"body_bs_Navel_HD3": 1.0}})
        self.assertEqual(mit["hdkanaele"], ["body_bs_Navel_HD3"])
        self.assertEqual(ohne["stufen"], 1)
        d = np.linalg.norm(_punkte(mit) - _punkte(ohne), axis=1)
        # Stufe 1: einige hundert Punkte am Nabel; Kaefigdeltas (72) plus HD
        # (gemessen: HD allein 1,6 mm, zusammen 6,5 mm).
        self.assertTrue(100 < (d > 1e-5).sum() < 2000, (d > 1e-5).sum())
        self.assertLess(d.max(), 0.01)
        hoch = self._netz("basis", {"anhaenge": False, "regler": {"body_bs_Navel_HD3": 1.0}}, hoch=True)
        hoch_ohne = self._netz("basis", {"anhaenge": False}, hoch=True)
        self.assertEqual(hoch["stufen"], 2)
        d2 = np.linalg.norm(_punkte(hoch) - _punkte(hoch_ohne), axis=1)
        self.assertGreater((d2 > 1e-5).sum(), (d > 1e-5).sum())  # mehr Punkte, Stufe 2
        self.assertLess(d2.max(), 0.012)

    def test_detailnormalen_nur_mit_hoher_stufe(self):
        tief = self._netz("p3d_ursula", {"anhaenge": False})
        kopf = next(g for g in tief["gruppen"] if g["name"] == "Head")
        self.assertNotIn("detailnormalen", kopf["bilder"])
        self.assertIn("P3DUrsula_Head_N_1001", kopf["bilder"]["normalen"])
        hoch = self._netz("p3d_ursula", {"anhaenge": False}, hoch=True)
        kopf = next(g for g in hoch["gruppen"] if g["name"] == "Head")
        self.assertIn("skin_details/genesis9_head_nm_1001", kopf["bilder"]["detailnormalen"])
        self.assertEqual(kopf["bilder"]["detailgewicht"], 1.0)
        # Amala hat keine Grundnormalen: die 8K werden die einzige Normale.
        amala = self._netz("amala", {"anhaenge": False}, hoch=True)
        kopf = next(g for g in amala["gruppen"] if g["name"] == "Head")
        self.assertIn("Skin_Details/Genesis9_Head_NM_1001", kopf["bilder"]["normalen"])
        self.assertNotIn("detailnormalen", kopf["bilder"])


@unittest.skipUnless(bibliothek_da(), "Daz-Bibliothek mit Genesis 9 fehlt")
class EirgridUndPropsTest(SimpleTestCase):
    databases = set()

    def setUp(self):
        self.client = Client()

    def _stueck(self, kennung, rumpf):
        antwort = self.client.post(
            "/api/character/genesis9-figur/garderobe/%s/netz/" % kennung,
            data=json.dumps(rumpf),
            content_type="application/json",
        )
        self.assertEqual(antwort.status_code, 200, antwort.content[:300])
        return antwort.json()

    def test_eirgrid_stilarten_und_zopfknochen(self):
        eintrag = G9garderobe.eintrag("eirgrid_hair_g9")
        arten = {s["art"] for s in eintrag["stile"]}
        self.assertEqual(arten, {"stil", "pose", "laenge"})
        pose = next(s for s in eintrag["stile"] if s["id"] == "eirgrid_51_pose_01_back")
        self.assertEqual(len(pose["knochen"]), 14)
        self.assertIn("FrontLeftBraid", pose["knochen"])
        kennungen = [s["id"] for s in eintrag["stile"]]
        self.assertNotIn("eirgrid_51_pose_00_reset", kennungen)
        folger = G9garderobe.folger("eirgrid_hair_g9")[0]
        self.assertEqual(len(folger.eigene), 14)
        self.assertFalse(folger.koerperhaut)
        # Volle Bindung: die Zoepfe sind Knochen des Browser-Skeletts (18.09.).
        self.assertIn("FrontLeftBraid", folger.haut.knochen)
        self.assertEqual(eintrag["eigene_knochen"], 14)
        ruhe = self._stueck("eirgrid_hair_g9", {})
        gedreht = self._stueck(
            "eirgrid_hair_g9", {"stil": ["eirgrid_51_pose_01_back", "eirgrid_52_length_03_long"]}
        )
        d = np.linalg.norm(_punkte(gedreht["teile"][0]) - _punkte(ruhe["teile"][0]), axis=1)
        # Zoepfe nach hinten und 14,5 % laenger: gemessen 90 mm Mittel, 38 cm Spitze.
        self.assertGreater(d.max(), 0.2)
        self.assertGreater((d > 0.01).sum(), 100000)

    def test_zopfknochen_im_browser_skelett(self):
        """Der Koerper-Endpunkt haengt die eigenen Knochen der getragenen
        Stuecke ins Skelett — in der Stellung des Stils (Pose Back: die
        Zopfspitze wandert nach hinten)."""
        client = self.client
        ohne = client.post(
            "/api/character/genesis9-figur/basis/netz/",
            data=json.dumps({"anhaenge": False}),
            content_type="application/json",
        ).json()
        self.assertNotIn("eigene", ohne["skelett"])
        adresse = "/api/character/genesis9-figur/basis/netz/"
        ruhe = client.post(
            adresse,
            data=json.dumps({"anhaenge": False, "kleidung": [{"kennung": "eirgrid_hair_g9"}]}),
            content_type="application/json",
        ).json()
        back = client.post(
            adresse,
            data=json.dumps(
                {
                    "anhaenge": False,
                    "kleidung": [{"kennung": "eirgrid_hair_g9", "stil": ["eirgrid_51_pose_01_back"]}],
                }
            ),
            content_type="application/json",
        ).json()
        self.assertEqual(len(ruhe["skelett"]["eigene"]), 14)
        # 138 Knochen + 14 Zoepfe, je Blatt ein Endknochen.
        self.assertEqual(len(back["skelett"]["knochen"]) - len(ohne["skelett"]["knochen"]), 28)
        r = {k["name"]: k for k in ruhe["skelett"]["knochen"]}
        b = {k["name"]: k for k in back["skelett"]["knochen"]}
        self.assertEqual(r["BackRight3"]["eltern"], "spine4")
        self.assertLess(b["BackRight3"]["schwanz"][2], r["BackRight3"]["schwanz"][2] - 0.1)
        self.assertEqual(r["BackRight3"]["kopf"], b["BackRight3"]["kopf"])

    def test_prop_haengt_an_der_hand(self):
        eintrag = G9garderobe.eintrag("tubal_dagger_feminine_rt")
        self.assertEqual((eintrag["art"], eintrag["knochen"], eintrag["griff"]), ("requisit", "r_hand", True))
        antwort = self._stueck("tubal_dagger_feminine_rt", {})
        teil = antwort["teile"][0]
        self.assertEqual(teil["knochen"], "r_hand")
        self.assertEqual(teil["hautgewichte"]["knochen"], ["r_hand"])
        hand = next(k for k in G9skelett.roh() if k["name"] == "r_hand")
        mitte = _punkte(teil).mean(axis=0)
        self.assertLess(np.linalg.norm(mitte - hand["kopf"] * 0.01), 0.15)
        # Mit Griff: die Figur schliesst die Finger (Daumen dreht).
        client = self.client
        offen = client.post(
            "/api/character/genesis9-figur/feminine/netz/",
            data=json.dumps({"anhaenge": False}),
            content_type="application/json",
        ).json()
        griff = client.post(
            "/api/character/genesis9-figur/feminine/netz/",
            data=json.dumps({"anhaenge": False, "griffe": ["tubal_dagger_feminine_rt"]}),
            content_type="application/json",
        ).json()
        daumen = {k["name"]: np.asarray(k["kopf"]) for k in offen["skelett"]["knochen"]}
        daumen_griff = {k["name"]: np.asarray(k["kopf"]) for k in griff["skelett"]["knochen"]}
        bewegt = np.linalg.norm(daumen["r_index3"] - daumen_griff["r_index3"])
        self.assertGreater(bewegt, 0.01)
        self.assertLess(np.linalg.norm(daumen["l_index3"] - daumen_griff["l_index3"]), 1e-6)

    def test_makeup_system_aus_script_loads(self):
        kategorien = {k["kategorie"]: k["eintraege"] for k in G9schminke.katalog()}
        self.assertIn("grundierung", kategorien)
        # 30 Basic Foundations, dazu Amelia und Snow Queen.
        self.assertGreaterEqual(len(kategorien["grundierung"]), 40)
        lidschatten = G9schminke.eintrag("amelia9:amelia_9_mu_02_eyeshadow")
        ebene = lidschatten["ebenen"][0]
        self.assertEqual((ebene["deckkraft"], ebene["farbdeckkraft"]), (0.9, 0.7))
        self.assertTrue(ebene["rauheit"].endswith("Amelia9_MUEyeshadow02_R_1001.png"))
        grundierung = G9schminke.eintrag("basic:basicfoundation_mu_01_foundation")
        self.assertEqual(grundierung["ebenen"][0]["deckkraft"], 0.6)
        self.assertEqual(len(grundierung["ebenen"][0]["farbwert"]), 3)
        # Lips-Glossy: nur Top Coat (Klarlack), Lidschatten 02 mit Metall.
        glossy = G9schminke.eintrag("amelia9:amelia_9_mu_01_lips_glossy")
        self.assertEqual(glossy["kategorie"], "lipgloss")
        ebene = glossy["ebenen"][0]
        self.assertEqual((ebene["klarlackdeckkraft"], ebene["klarlackrauheit"]), (0.35, 0.0))
        self.assertNotIn("farbe", ebene)
        metall = G9schminke.eintrag("amelia9:amelia_9_mu_02_eyeshadow")["ebenen"][0]
        self.assertTrue(metall["metall"].endswith("Amelia9_MUEyeshadow02_M_1001.png"))
        lips = G9schminke.eintrag("amelia9:amelia_9_mu_02_lips")["ebenen"][0]
        self.assertTrue(lips.get("rauheitinvers"))

    def test_glanzbild_und_hd_der_anhaenge(self):
        """Lipgloss im Netz: `schminke.glanz` (PNG) am Kopf; Mund HD3 bewegt
        die Mundpunkte auf Stufe 1 (gemessen 1,3 mm); Angie-Jeans stellen
        `HD Wrinkles` aus dem Preset (4,1 mm); Tubal-Normalen DirectX."""
        from Genesis9.ebenen import G9ebenen

        glossy = G9schminke.eintrag("amelia9:amelia_9_mu_01_lips_glossy")
        fertig = G9ebenen.komponieren(glossy["ebenen"])
        # Seit dem Abend auch `werte` (Top Coat Color/Bump, `G9glanz.werte`).
        self.assertEqual(sorted(fertig), ["glanz", "werte"])
        self.assertTrue(fertig["glanz"].endswith("_k.png"))
        adresse = "/api/character/genesis9-figur/basis/netz/"
        netz = self.client.post(
            adresse,
            data=json.dumps({"praesets": {"lipgloss": glossy["id"]}}),
            content_type="application/json",
        ).json()
        kopf = next(g for g in netz["gruppen"] if g["name"] == "Head")
        self.assertIn("glanz", kopf["bilder"]["schminke"])
        mund_ohne = next(a for a in netz["anhaenge"] if a["schluessel"] == "mund")
        hd = self.client.post(
            adresse,
            data=json.dumps({"regler": {"head_bs_MouthRealism_HD3": 1.0}}),
            content_type="application/json",
        ).json()
        mund_hd = next(a for a in hd["anhaenge"] if a["schluessel"] == "mund")
        d = np.linalg.norm(_punkte(mund_hd) - _punkte(mund_ohne), axis=1)
        self.assertGreater((d > 1e-5).sum(), 1000)
        self.assertLess(d.max(), 0.01)
        jeans = G9garderobe.eintrag("angie_jeans")
        self.assertEqual(jeans["vorgaben"], {"HD Wrinkles": 1.0})
        dolch = self.client.post(
            "/api/character/genesis9-figur/garderobe/tubal_dagger_feminine_rt/netz/",
            data=json.dumps({}),
            content_type="application/json",
        ).json()
        bilder = dolch["teile"][0]["gruppen"][0]["bilder"]
        self.assertIn("DirectX", bilder["normalen"])
        self.assertEqual(bilder["normalenachse"], -1)
