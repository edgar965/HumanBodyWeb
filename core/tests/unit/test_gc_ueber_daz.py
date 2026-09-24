# -*- coding: utf-8 -*-
"""GarmentCode und Daz-Garderobe auf Genesis 9 kennen sich (24.09.2026).

Edgar: „GarmentCode Pants Harem zieht die Kleider bei Genesis nicht ueber
existierende Genesis-Kleider hoch" — die Nacharbeit legte die Hose auf 2 mm an
die HAUT (Median 2,0 mm), die Jeans stand 7 mm darueber. Gemessen an einer Kopie
des Baus (`ProjektTemp/gc_ueber_daz/`): Hosenpunkte unter der Daz-Kleidung
9.397 -> 258, Median −5,2 -> +2,0 mm; Shirt ueber der Hose 1.942 -> 176.

BDD - GEGEBEN / DANN
====================
    DieNacharbeit     ... nimmt Daz-Stuecke (`stoffe`) wie Rig-Dateien in die Haut
    DieNormalen       ... einer Hohlkehle zeigen gemittelt heraus, nicht seitwaerts
    DieSaumregel      ... ein Hemd mit dem Saum ueber dem Bund bleibt aussen, die Jeans innen
    DieLagenanfrage   ... ordnet ein getragenes GarmentCode-Stueck als innere Lage ein;
                          ein Pfad ausserhalb der Ablage zaehlt nicht

Kunstdaten: die Haut ist die Ebene y = 0 (`Kunsthaut`), Stuecke sind Gitter darueber.
Sabotagen: `stoffe` in `Stoffnacharbeit._haut` ignorieren -> DieNacharbeit rot;
`gemittelt` gibt die Eingabe zurueck -> DieNormalen rot; `saum_ueber_bund` mit
vertauschten Argumenten -> DieSaumregel rot; `self.gc` in
`vorbereiten` ueberspringen -> DieLagenanfrage rot.
"""

import json
import os
from unittest import mock

import numpy as np
from django.test import SimpleTestCase

from ..unit._humanbodypfad import Humanbodypfad

Humanbodypfad.setzen()

from GarmentCode.hautmitstoff import Hautmitstoff  # noqa: E402
from GarmentCode.stoffnacharbeit import Stoffnacharbeit  # noqa: E402

from core.dienste.g9lagenanfrage import G9lagenanfrage  # noqa: E402
from core.dienste.gcrigpfad import Gcrigpfad  # noqa: E402

from ._pruefablage import Pruefablage  # noqa: E402
from .test_genesis9_lagen import Kunsthaut, gitter  # noqa: E402
from .test_hautmitstoff import _kasten  # noqa: E402


class DieNacharbeit(SimpleTestCase):
    databases = set()

    def test_daz_stuecke_gehen_in_die_haut_wie_rig_dateien(self):
        haut, flaechen = _kasten()  # oben bei y = 0,1
        jeans = gitter(0.107, -0.3, 0.3, -0.3, 0.3)
        nacharbeit = Stoffnacharbeit(haut, flaechen, flaechen, stoffe=[('angie_jeans', jeans)])
        self.assertIsNotNone(nacharbeit.haut)
        self.assertEqual(nacharbeit.haut.stuecke, ['angie_jeans'])
        punkte, normalen = nacharbeit.haut.haut()
        self.assertEqual(len(punkte), len(haut) + len(jeans))
        self.assertTrue((normalen[len(haut) :][:, 1] > 0.9).all())  # Jeans oben: nach +y
        self.assertIsNone(Stoffnacharbeit(haut, flaechen, flaechen).haut)


class DieNormalen(SimpleTestCase):
    databases = set()

    def test_eine_flosse_in_der_falte_schiebt_heraus(self):
        bruecke = np.array(
            [[x, y, -0.12] for x in np.arange(-0.1, 0.1001, 0.01) for y in np.arange(0.0, 0.2001, 0.01)]
        )
        flosse = np.array(
            [[0.0, y, z] for y in np.arange(0.0, 0.2001, 0.01) for z in (-0.115, -0.11, -0.105)]
        )
        normalen = np.vstack(
            [
                np.tile([0.0, 0.0, -1.0], (len(bruecke), 1)),
                [[1.0 if i % 2 else -1.0, 0.0, 0.0] for i in range(len(flosse))],
            ]
        )
        aus = Hautmitstoff.gemittelt(np.vstack([bruecke, flosse]), normalen)[len(bruecke) :]
        self.assertTrue((np.abs(aus[:, 0]) < 0.5).all(), aus[:5])
        self.assertTrue((aus[:, 2] < -0.8).all(), aus[:5])


def zylinder(radius, unten, oben):
    """Ein Rohr um die z-Achse (Projektlage, z oben), 1 cm Raster, 36 Winkel."""
    winkel = np.linspace(0, 2 * np.pi, 36, endpoint=False)
    hoehen = np.arange(unten, oben + 1e-9, 0.01)
    return np.array([[radius * np.cos(w), radius * np.sin(w), z] for z in hoehen for w in winkel])


class DieSaumregel(SimpleTestCase):
    """`Stofflagen.teilen`: ein Hemd, dessen Saum ueber dem Bund der neuen Hose haengt,
    kommt nicht in die Nacharbeit (sonst steckt es in der Hose); die Jeans darunter schon."""

    databases = set()

    def test_das_hemd_bleibt_aussen_die_jeans_innen(self):
        from GarmentCode.stofflagen import Stofflagen

        hose = zylinder(0.155, 0.2, 1.0)
        hemd, jeans = zylinder(0.16, 0.95, 1.45), zylinder(0.15, 0.2, 0.98)
        innen, aussen = Stofflagen.teilen(hose, [('hemd', hemd), ('jeans', jeans)])
        self.assertEqual(([k for k, _p in innen], aussen), (['jeans'], ['hemd']))
        self.assertIs(innen[0][1], jeans)

    def test_ein_ganz_bedecktes_stueck_ist_kein_saum(self):
        """Edgar (24.09.2026): BH unter dem Anzug galt als „Saum ueber dem Bund" — seine
        Punkte sitzen meist unten (Koerbchen), die Traeger reichen hoch; er liegt aber
        GANZ in der Ueberlappung. Sabotage: `G9lagen.SAUM_ANTEIL` auf 1,0 -> rot."""
        from GarmentCode.stofflagen import Stofflagen

        anzug = zylinder(0.155, 0.2, 1.45)
        koerbchen = np.vstack([zylinder(0.16, 1.10, 1.18)] * 4)  # dicht unten
        bh = np.vstack([koerbchen, zylinder(0.16, 1.19, 1.40)[::6]])  # duenne Traeger
        innen, aussen = Stofflagen.teilen(anzug, [('bh', bh)])
        self.assertEqual(([k for k, _p in innen], aussen), (['bh'], []))

    def test_ohne_beruehrung_bleibt_alles_innen(self):
        from GarmentCode.stofflagen import Stofflagen

        innen, aussen = Stofflagen.teilen(zylinder(0.155, 0.2, 0.6), [('hut', zylinder(0.1, 1.6, 1.8))])
        self.assertEqual(([k for k, _p in innen], aussen), (['hut'], []))


class DieLagenanfrage(SimpleTestCase):
    databases = set()

    def _rig(self, ordner, punkte_three):
        """Eine Rig-Datei in Projektlage (x, -z, y) unter `ordner/hose_g9/`."""
        p = np.asarray(punkte_three)
        projekt = np.column_stack([p[:, 0], -p[:, 2], p[:, 1]])
        os.makedirs(os.path.join(ordner, 'hose_g9'))
        with open(os.path.join(ordner, 'hose_g9', 'hose_g9_sim_rig.json'), 'w', encoding='utf-8') as datei:
            json.dump({'punkte': projekt.tolist()}, datei)
        return {'stueck': 'hose', 'ordner': 'hose_g9', 'rig_datei': 'hose_g9_sim_rig.json'}

    def test_eine_garmentcode_hose_liegt_unter_dem_hemd(self):
        koerper = Kunsthaut.koerper()
        with (
            Pruefablage.ordner('gc_lage_') as ordner,
            mock.patch.object(Gcrigpfad, 'wurzel', return_value=ordner),
        ):
            eintrag = self._rig(ordner, gitter(0.007))
            anfrage = G9lagenanfrage(
                {}, formung=mock.Mock(fingerabdruck=lambda: 'f'), koerper=koerper, grob=koerper, gc=[eintrag]
            )
            np.testing.assert_allclose(anfrage._gc_kaefig(eintrag), gitter(0.007), atol=1e-12)
            flaeche, innen, aussen = anfrage.vorbereiten(
                'hemd', [(mock.Mock(koerperhaut=False), gitter(0.012))]
            )
        self.assertEqual((innen, aussen), (['gc:hose'], []))
        self.assertIsNone(flaeche[2])  # Haut plus Hose, Baum neu

    def test_mitgeschickte_punkte_gehen_vor_der_rig_datei(self):
        """Nach einem Reglerzug formt der Browser das Stueck nach (`Gcreglerfolge`) und
        schickt die Punkte mit (Three-Lage, float32, base64); die Rig-Datei kennt nur
        den Bau. Kaputtes wird verworfen, dann gilt wieder die Datei."""
        import base64

        with (
            Pruefablage.ordner('gc_lage_') as ordner,
            mock.patch.object(Gcrigpfad, 'wurzel', return_value=ordner),
        ):
            eintrag = self._rig(ordner, gitter(0.007))
            anfrage = G9lagenanfrage({}, None, None, gc=[eintrag])
            neu = gitter(0.02).astype(np.float32)
            mit = dict(eintrag, punkte=base64.b64encode(neu.tobytes()).decode())
            np.testing.assert_allclose(anfrage._gc_kaefig(mit), neu, atol=1e-7)
            kaputt = dict(eintrag, punkte='%%%')
            np.testing.assert_allclose(anfrage._gc_kaefig(kaputt), gitter(0.007), atol=1e-12)

    def test_ein_pfad_ausserhalb_der_ablage_zaehlt_nicht(self):
        with (
            Pruefablage.ordner('gc_lage_') as ordner,
            mock.patch.object(Gcrigpfad, 'wurzel', return_value=ordner),
        ):
            self._rig(ordner, gitter(0.007))
            boese = {'stueck': 'x', 'ordner': '..', 'rig_datei': 'hose_g9_sim_rig.json'}
            self.assertIsNone(Gcrigpfad.pfad(boese))
            self.assertIsNone(G9lagenanfrage({}, None, None, gc=[boese])._gc_kaefig(boese))
