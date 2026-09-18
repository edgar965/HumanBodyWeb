# -*- coding: utf-8 -*-
"""Mimik: MB-Lab-Ausdrücke → DEF-Gesichtsknochen, Nebendatei, Verdrahtung im Studio.

WARUM (Edgar, 13.09.2026: „ich brauch eine Mimik für mein Modell, das tanzt …
MB-Lab-Ausdrücke sind gut … die letzte Mimik bleibt am Modell"):

1. `MblabAusdruecke.gewichte`: MB-Labs 0…1 mit Ruhe 0,5 → −1…+1, Ruhewerte und
   Rumpfeinheiten fallen weg.
2. `Knochendeltas` an einem Kunstfall: ein Knochen mit Punkten auf einer Geraden,
   die um seinen Kopf gedreht werden → die Drehung kommt (in Three.js-Achsen)
   heraus, ohne Versatz; verschobene Punkte → Versatz ohne Drehung. Kinder
   bekommen nur den Rest, den der Elternknochen nicht erklärt (am Kinn bleibt
   unter 1 mrad / 0,5 mm — die Kleinwinkel-Näherung).
3. Die gebauten Dateien: `posen.json` hat 76 Posen in 9 gefüllten Gruppen +
   „Eigene", jede mit deutschem Namen; `basis.json` bewegt für `eyeClosedL`
   die linken Lider und für `mouthOpen` den Kiefer.
4. `Mimikspuren.spuren`: Gewichte je Bild → Delta-Quaternionen je Knochen;
   Bild ohne Gewichte = Einheit; `schreiben` legt die Nebendatei, leer löscht sie.
5. Studio-Verdrahtung: `applyPlayhead` ruft `Mimikanwendung.alle(t)` NACH der
   Spurschleife; Speichern/Laden führen `_modellIdx` (Mimik UND Script);
   `Retargetdaten.holen` mischt die Mimik; das Menü hat die fünf Einträge.

Sabotage-Gegenprobe: in `Knochendeltas._nach_threejs` `-t_eltern[1]` →
`t_eltern[1]` → Fall 2 rot; `Mimikanwendung.alle(t)` in `playback.js` in die
Schleife ziehen → Fall 5 rot.
"""

import json
import os

import numpy as np
from django.conf import settings
from django.test import SimpleTestCase

from humanbody_core.mimik.knochendeltas import Knochendeltas
from humanbody_core.mimik.mblab_ausdruecke import MblabAusdruecke
from ._pruefablage import Pruefablage
from ._studiovorlage import Studiovorlage

STUDIO = settings.BASE_DIR / "static" / "viewer" / "bvh_studio"
MIMIK = settings.BASE_DIR / "static" / "mimik"


class KunstSkelett:
    """Kopf `DEF-spine.006` in Ruhe, Kiefer `DEF-jaw` darunter, Kinn am Kiefer."""

    @staticmethod
    def bauen(ordner):
        bones = [
            {
                "name": "DEF-spine.006",
                "parent": None,
                "local_position": [0, 0, 1.5],
                "local_quaternion": [1, 0, 0, 0],
            },
            {
                "name": "DEF-jaw",
                "parent": "DEF-spine.006",
                "local_position": [0, 0, -0.05],
                "local_quaternion": [1, 0, 0, 0],
            },
            {
                "name": "DEF-chin",
                "parent": "DEF-jaw",
                "local_position": [0, 0.05, 0],
                "local_quaternion": [1, 0, 0, 0],
            },
        ]
        # Punkte: Kiefer 0–3 auf der y-Achse vor dem Kieferkopf, Kinn 4–5 weiter vorn.
        netz = np.array(
            [
                [0, 0.02, 1.45],
                [0, 0.04, 1.45],
                [0, 0.06, 1.45],
                [0, 0.08, 1.45],
                [0, 0.07, 1.45],
                [0, 0.09, 1.45],
            ],
            dtype=float,
        )
        gewichte = {
            "vertex_count": 6,
            "bone_names": ["DEF-spine.006", "DEF-jaw", "DEF-chin"],
            "weights": [[[1, 1.0]]] * 4 + [[[2, 1.0]]] * 2,
        }
        skelett = os.path.join(ordner, "skelett.json")
        haut = os.path.join(ordner, "haut.json")
        punkte = os.path.join(ordner, "netz.npy")
        with open(skelett, "w", encoding="utf-8") as f:
            json.dump({"bone_count": 3, "bones": bones}, f)
        with open(haut, "w", encoding="utf-8") as f:
            json.dump(gewichte, f)
        np.save(punkte, netz)
        return Knochendeltas(skelett, haut, punkte), netz


class MimikTest(SimpleTestCase):
    databases = set()

    def test_mblab_gewichte(self):
        g = MblabAusdruecke.gewichte(
            {
                "Expressions_mouthSmile": 1.0,
                "Expressions_browsMidVert": 0.2,
                "Expressions_eyeSquintL": 0.5,
                "Expressions_chestExpansion": 0.9,
            }
        )
        self.assertEqual(g, {"mouthSmile": 1.0, "browsMidVert": -0.6})

    def test_knochendeltas_drehung_und_versatz(self):
        with Pruefablage.ordner() as ordner:
            deltas, netz = KunstSkelett.bauen(str(ordner))
            self.assertEqual(deltas.gesicht, ["DEF-jaw", "DEF-chin"])
            # Kieferpunkte um 5° um die x-Achse (Blender) um den Kieferkopf drehen.
            kopf = np.array([0, 0, 1.45])
            winkel = np.radians(5)  # klein genug für die Kleinwinkel-Näherung
            rot = np.array(
                [[1, 0, 0], [0, np.cos(winkel), -np.sin(winkel)], [0, np.sin(winkel), np.cos(winkel)]]
            )
            gedreht = (rot @ (netz[:4] - kopf).T).T + kopf
            morph = [[i, *(gedreht[i] - netz[i])] for i in range(4)]
            aus = deltas.bewegungen(morph)
            tx, ty, tz, px, py, pz = aus["DEF-jaw"]
            # Blender-x-Drehung bleibt Three.js-x; Versatz nahe null.
            self.assertAlmostEqual(tx, winkel, places=3)
            self.assertAlmostEqual(abs(ty) + abs(tz), 0, places=3)
            self.assertLess(abs(px) + abs(py) + abs(pz), 1e-3)
            # Reiner Versatz: alle Kieferpunkte 1 cm nach +z (Blender) = +y (Three.js).
            aus = deltas.bewegungen([[i, 0, 0, 0.01] for i in range(4)])
            tx, ty, tz, px, py, pz = aus["DEF-jaw"]
            self.assertLess(abs(tx) + abs(ty) + abs(tz), 1e-3)
            self.assertAlmostEqual(py, 0.01, places=4)
            # Kinnpunkte, die die Kieferdrehung schon erklärt, bewegen das Kinn nicht.
            gedreht_alle = (rot @ (netz - kopf).T).T + kopf
            morph = [[i, *(gedreht_alle[i] - netz[i])] for i in range(6)]
            aus = deltas.bewegungen(morph)
            self.assertAlmostEqual(aus["DEF-jaw"][0], winkel, places=3)
            kinn = aus.get("DEF-chin", [0] * 6)  # Rest der Kleinwinkel-Näherung
            self.assertLess(max(abs(w) for w in kinn[:3]), 1e-3)
            self.assertLess(max(abs(w) for w in kinn[3:]), 5e-4)

    def test_gebaute_bibliothek(self):
        posen = json.loads(MimikTest._text(MIMIK / "posen.json"))
        basis = json.loads(MimikTest._text(MIMIK / "basis.json"))
        self.assertEqual(len(posen["posen"]), 76)  # 78 minus Ein-/Ausatmen (Rumpf)
        self.assertEqual([g["id"] for g in posen["gruppen"]][-1], "eigene")
        gefuellt = {p["gruppe"] for p in posen["posen"]}
        self.assertEqual(len(gefuellt), 9)
        self.assertTrue(all(p["name"] and p["gewichte"] for p in posen["posen"]))
        self.assertIn("Glücklich", [p["name"] for p in posen["posen"]])
        lider = [k for k in basis["eyeClosedL"]["plus"] if k.startswith("DEF-lid.T.L")]
        self.assertGreaterEqual(len(lider), 3)
        self.assertIn("DEF-jaw", basis["mouthOpen"]["plus"])
        self.assertNotIn("chestExpansion", basis)

    def test_mimikspuren_und_nebendatei(self):
        from core.dienste.mimikspuren import Mimikspuren

        basis = {
            "e1": {"plus": {"DEF-jaw": [0.2, 0, 0, 0, 0.01, 0]}, "minus": {"DEF-jaw": [-0.1, 0, 0, 0, 0, 0]}}
        }
        spuren = Mimikspuren.spuren({"fps": 30, "einheiten": ["e1"], "bilder": [[0], [1], [-1]]}, basis)
        self.assertEqual(spuren.frame_count, 3)
        q = np.asarray(spuren.tracks["DEF-jaw"]).reshape(-1, 4)
        np.testing.assert_allclose(q[0], [0, 0, 0, 1], atol=1e-9)
        self.assertAlmostEqual(q[1][0], np.sin(0.1), places=6)  # Drehvektor 0,2 um x
        self.assertAlmostEqual(q[2][0], -np.sin(0.05), places=6)  # minus: 0,1 zurück
        with Pruefablage.ordner() as ordner:
            bvh = os.path.join(str(ordner), "probe.bvh")
            neben = Mimikspuren.schreiben(bvh, {"fps": 30, "einheiten": ["e1"], "bilder": [[0.5]]})
            self.assertTrue(neben.endswith("probe_mimik.json"))
            self.assertTrue(os.path.isfile(neben))
            self.assertIsNone(Mimikspuren.laden(os.path.join(str(ordner), "andere.bvh")))
            Mimikspuren.schreiben(bvh, None)
            self.assertFalse(os.path.isfile(neben))

    def test_verdrahtung_im_studio(self):
        playback = MimikTest._text(STUDIO / "playback.js")
        rumpf = playback[
            playback.index("export function applyPlayhead") : playback.index(
                "export function updatePlaybackUI"
            )
        ]
        schleife_ende = rumpf.rindex("applySceneObjectTrack(track, t);\n    }")
        self.assertGreater(rumpf.index("Mimikanwendung.alle(t);"), schleife_ende)
        speichern = MimikTest._text(STUDIO / "projekt_daten.js")
        self.assertIn("td._modellIdx = Projektdaten._stelle(t._modellIdx)", speichern)
        # dieselbe Rechnung für Modell → Animation (15.09.2026)
        self.assertIn("td._linkedAnimIdx = Projektdaten._stelle(t._linkedAnimIdx)", speichern)
        self.assertIn("t.type === 'mimik' || t.type === 'script'", speichern)
        self.assertNotIn("td.lebendigkeit", speichern)  # seit 15.09.2026 am Script-Clip
        laden = MimikTest._text(STUDIO / "projekt_wiederherstellung.js")
        self.assertIn("_zuordnen(eingang, angelegt)", laden)
        self.assertIn("AM_MODELL = ['mimik', 'script']", MimikTest._text(STUDIO / "modellgruppen.js"))
        retarget = MimikTest._text(settings.BASE_DIR / "core" / "dienste" / "retargetdaten.py")
        self.assertIn("self._mimik_dazu(self._gesicht_dazu(", retarget)
        vorlage = Studiovorlage.text()
        for aktion in (
            "ctx-mimik-pose",
            "ctx-mimik-neutral",
            "ctx-mimik-loeschen",
            "ctx-mimik-einrechnen",
            "ctx-mimik-track",
            "ctx-script-track",
            "ctx-script-clip",
        ):
            self.assertIn('data-action="%s"' % aktion, vorlage)
        menue = MimikTest._text(STUDIO / "zeitleiste_menue.js")
        self.assertLess(menue.index("spur.type === 'mimik'"), menue.index("_leereSpur(e, spur"))

    @staticmethod
    def _text(pfad):
        return pfad.read_text(encoding="utf-8")
