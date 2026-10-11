# -*- coding: utf-8 -*-
"""Blender-Import, Schritt „haut": die Wahl „Lokal"/„Blender", die Nacharbeit im Speicher und die Fehlermeldungen des lokalen Weges (Edgar, 10.10.2026: „ich möchte blender für alle
Usecases ersetzt haben. Die Pipeline soll einstellbar sein … Option ‚Lokal' und ‚Blender'").

1. `Blendimportbackenwahl`: unbekannte oder fehlende Werte heißen Vorgabe (`lokal`); ohne lesbare Einstellungen die Vorgabe, mit Warnung im Log.
2. Verdrahtung `Blendimporthaut.backen`: mit „lokal" backt `Blendimporthautlokal`, Blender wird nicht gestartet, die Dateien schreibt die Haut einmal; mit „blender" startet Blender
   (`blendbacken.py`) und die Nacharbeit liest seine Bilder. Der Bericht nennt die Wahl.
3. `Blendimporthautnacharbeit` im Speicher: Fehlstellen werden flach/Median, die Deckung stimmt, lokal gebackenes Bild bekommt keinen Saum; die Eingabefelder bleiben unverändert.
4. Fehlermeldungen des lokalen Weges: ein Export ohne Materialgraph (älterer Export) sagt, was zu tun ist — kein stilles Schwarz; ein `Hautgraphfehler` wird zur Meldung mit dem
   Ausweg „Blender"; echte Verschiebung lehnt der Graph ab.
5. `Blendmaterialgraph.echte_verschiebung` (Export, läuft in Blender): nur mit verbundenem Displacement UND Methode ≠ Bump.

Sabotage-Gegenprobe (11.10.2026, danach rückgängig): in `Blendimporthaut.backen` `wahl == LOKAL` → `wahl != LOKAL` → Fall 6 und 7 rot; in `Blendimporthautnacharbeit.farbe_fuellen`
`if saum_schliessen:` → `if True:` → Fall 3 und 4 rot.
"""

import logging
from types import SimpleNamespace
from unittest import mock

import numpy as np
from django.test import SimpleTestCase

from core.dienste.blendimportbackenwahl import Blendimportbackenwahl
from core.dienste.blendimporthautnacharbeit import Blendimporthautnacharbeit


class _Ablage:
    """Eine Ablage ohne Dateien: jeder Pfad ist eine Attrappe."""
    kennung = '2026.10.11.00.00.00'

    def export(self, name=''):
        return mock.MagicMock(name='export/' + name)

    def arbeit(self, name=''):
        return mock.MagicMock(name='arbeit/' + name)

    def ergebnis(self, name=''):
        return mock.MagicMock(name='ergebnis/' + name)


class WahlTest(SimpleTestCase):
    databases = set()

    def test_1_unbekannte_und_fehlende_werte_sind_die_vorgabe(self):
        self.assertEqual(Blendimportbackenwahl.VORGABE, 'lokal')
        for prefs in (None, {}, {'blendimport_backen': ''}, {'blendimport_backen': 'quatsch'}, {'anderes': 'blender'}):
            self.assertEqual(Blendimportbackenwahl.aus(prefs), 'lokal', prefs)
        self.assertEqual(Blendimportbackenwahl.aus({'blendimport_backen': 'blender'}), 'blender')
        self.assertEqual(list(Blendimportbackenwahl.WAHLEN), ['lokal', 'blender'])

    def test_2_ohne_lesbare_einstellungen_gilt_die_vorgabe_mit_warnung(self):
        with mock.patch('core.models.AppSettings.load', side_effect=RuntimeError('keine Datenbank')):
            with self.assertLogs('core', level=logging.WARNING) as log:
                self.assertEqual(Blendimportbackenwahl.gewaehlt(), 'lokal')
        self.assertIn('Einstellung nicht lesbar', log.output[0])


class NacharbeitTest(SimpleTestCase):
    databases = set()

    def _nach(self, **kw):
        return Blendimporthautnacharbeit(_Ablage(), SimpleNamespace(ergebnis=None, kennung='x'), 64, None, kw.pop('grenze', 'aus'), kw.pop('form', 'bleibt'))

    @staticmethod
    def _bilder():
        farbe = np.full((64, 64, 3), (180, 120, 90), np.uint8)
        farbe[:, :20] = 0                                     # nicht getroffen: schwarz
        normal = np.full((64, 64, 3), (140, 120, 240), np.uint8)
        normal[:, :20] = (128, 128, 255)
        rauh = np.full((64, 64, 3), (100, 100, 100), np.uint8)
        rauh[:, :20] = 0
        return farbe, normal, rauh

    def test_3_fehlstellen_werden_flach_median_und_die_deckung_stimmt(self):
        farbe, normal, rauh = self._bilder()
        e = self._nach().kachel(1001, farbe, normal, rauh, saum_schliessen=False)
        self.assertEqual(e['deckung'], 68.8)                  # 44 von 64 Spalten getroffen: 68,75 %, auf eine Stelle gerundet
        self.assertTrue((e['normalen'][:, :20] == (128, 128, 255)).all())
        self.assertTrue((e['normalen'][:, 20:] == (140, 120, 240)).all())
        self.assertTrue((e['rauheit'] == 100).all(), 'die Rauheit der Fehlstellen ist der Median der getroffenen Texel')
        self.assertEqual(e['rauheit'].shape, (64, 64))
        # Ohne Ersatzkachel und ohne Umfeld bleiben die Fehlstellen der Farbe schwarz; die getroffenen Texel sind unberührt.
        self.assertTrue((e['farbe'][:, 20:] == (180, 120, 90)).all())
        self.assertTrue(e['farbe_geaendert'])

    def test_4_lokal_gebacken_hat_keinen_saum_und_die_eingabe_bleibt(self):
        farbe, normal, rauh = self._bilder()
        farbe[:, 20] = (40, 28, 20)                           # die Spalte neben der Fehlstelle: nur mit Saum würde sie überschrieben
        vorher = [a.copy() for a in (farbe, normal, rauh)]
        e = self._nach().kachel(1001, farbe, normal, rauh, saum_schliessen=False)
        for nachher, vor in zip((farbe, normal, rauh), vorher):
            self.assertTrue((nachher == vor).all(), 'die Eingabefelder müssen unverändert bleiben')
        self.assertTrue((e['farbe'][:, 20] == (40, 28, 20)).all())
        mit_saum = self._nach().kachel(1001, farbe, normal, rauh, saum_schliessen=True)
        self.assertFalse((mit_saum['farbe'][:, 20] == (40, 28, 20)).all(), 'mit Saum (Blenders Rand) wird die Randspalte geschlossen')

    def test_5_ohne_fehlstellen_aendert_sich_die_farbe_nicht(self):
        farbe = np.full((64, 64, 3), (180, 120, 90), np.uint8)
        e = self._nach().kachel(1001, farbe, np.full((64, 64, 3), (128, 128, 255), np.uint8), np.full((64, 64, 3), 50, np.uint8), saum_schliessen=False)
        self.assertEqual(e['deckung'], 100.0)
        self.assertFalse(e['farbe_geaendert'])
        self.assertTrue((e['farbe'] == farbe).all())


class VerdrahtungTest(SimpleTestCase):
    """`Blendimporthaut.backen` mit Attrappen: wer backt, wer schreibt, was steht im Bericht."""
    databases = set()

    def _fahren(self, wahl):
        """`(kacheln, bericht, Blender-Attrappe, nacharbeiten, _backen_lokal)` eines Laufs von `backen` ohne Dateien, GPU und Blender."""
        from contextlib import ExitStack

        from core.dienste.blendimporthaut import Blendimporthaut

        inventar = {'netze': [{'name': 'body', 'datei': '00.npz', 'materialien': [{'name': 'm', 'graph': 'g.json'}]}]}
        haut = Blendimporthaut(_Ablage(), SimpleNamespace(ergebnis=None, kennung='x'), inventar, [{'rolle': 'koerper', 'name': 'body'}], 64)
        punkte = np.zeros((3, 3))
        dreiecke = np.array([[0, 1, 2]])
        stand = {'punkte': punkte, 'dreiecke': dreiecke, 'uv': np.zeros((3, 2)), 'kachel': np.array([1001])}
        lage = mock.Mock(koerper_ruhelage=mock.Mock(return_value=punkte), genesis_objs=mock.Mock(return_value={1001: 'x.obj'}), genesis=mock.Mock(return_value=stand))
        with ExitStack() as s:
            s.enter_context(mock.patch.object(Blendimporthaut, 'gpu_geraet', return_value=None))
            s.enter_context(mock.patch.object(haut, '_koerper', return_value=('body', punkte, dreiecke)))
            s.enter_context(mock.patch.object(haut, '_umfeld', return_value=None))
            s.enter_context(mock.patch.object(haut, 'abstand', return_value={'median_mm': 1.0}))
            s.enter_context(mock.patch('core.dienste.blendimporthaut.Blendimportlage', return_value=lage))
            s.enter_context(mock.patch('core.dienste.blendimporthaut.Schammessungablage.nachtragen', return_value={}))
            s.enter_context(mock.patch('numpy.save'))
            blender = s.enter_context(mock.patch('core.dienste.blendimporthaut.Blendimportblender'))
            nach = s.enter_context(mock.patch.object(haut, 'nacharbeiten', return_value={'1001': 99.0}))
            lokal = s.enter_context(mock.patch.object(haut, '_backen_lokal', return_value={'1001': 98.0}))
            kacheln, bericht = haut.backen('x.blend', wahl=wahl)
        return kacheln, bericht, blender, nach, lokal

    def test_6_lokal_startet_blender_nicht(self):
        kacheln, bericht, blender, nach, lokal = self._fahren('lokal')
        blender.assert_not_called()
        nach.assert_not_called()
        lokal.assert_called_once()
        self.assertEqual(bericht['backen'], 'lokal')
        self.assertEqual(bericht['deckung'], {'1001': 98.0})
        self.assertEqual(kacheln['1001:normalen'], 'haut_1001_normalen.png')

    def test_7_blender_startet_blendbacken_und_arbeitet_nach(self):
        kacheln, bericht, blender, nach, lokal = self._fahren('blender')
        lokal.assert_not_called()
        blender.return_value.laufen.assert_called_once()
        self.assertEqual(blender.return_value.laufen.call_args[0][0], 'blendbacken.py')
        nach.assert_called_once()
        self.assertEqual(bericht['backen'], 'blender')
        self.assertEqual(bericht['deckung'], {'1001': 99.0})


class LokalFehlerTest(SimpleTestCase):
    databases = set()

    def test_8_export_ohne_materialgraph_sagt_was_zu_tun_ist(self):
        from core.dienste.blendimporthautlokal import Blendimporthautlokal
        from core.dienste.hautbacken.graph import Hautgraphfehler

        netz = {'materialien': [{'name': 'Haut'}]}                      # weder `graph` noch `graph_grund`: ein älterer Export
        lokal = Blendimporthautlokal(_Ablage(), netz, self._npz(), np.zeros((3, 3)), {'punkte': np.zeros((1, 3))}, 64)
        with mock.patch('core.dienste.blendimporthautlokal.Hautbackenquelle'), mock.patch('core.dienste.blendimporthautlokal.Hautschattungbau'):
            with self.assertRaises(Hautgraphfehler) as ctx:
                lokal.vorbereiten()
        self.assertIn('Schritt „export" neu laufen lassen', ctx.exception.gruende[0])
        self.assertIn('Haut', ctx.exception.gruende[0])

    def test_8b_export_ohne_polygondaten_sagt_was_zu_tun_ist(self):
        from core.dienste.blendimporthautlokal import Blendimporthautlokal
        from core.dienste.hautbacken.graph import Hautgraphfehler

        npz = {k: v for k, v in self._npz().items() if k != 'poly_start'}
        lokal = Blendimporthautlokal(_Ablage(), {'materialien': []}, npz, np.zeros((3, 3)), {'punkte': np.zeros((1, 3))}, 64)
        with self.assertRaises(Hautgraphfehler) as ctx:
            lokal.vorbereiten()
        self.assertIn('Polygon-Daten', ctx.exception.gruende[0])
        self.assertIn('Schritt „export" neu laufen lassen', ctx.exception.gruende[0])

    @staticmethod
    def _npz():
        """Die Arrays eines Exports mit einem einzigen Dreieck."""
        return {'dreiecke': np.array([[0, 1, 2]]), 'uv_ecken': np.zeros((1, 3, 2)), 'poly_start': np.array([0, 3]), 'poly_punkte': np.array([0, 1, 2]), 'dreieck_poly': np.array([0])}

    def test_9_material_ohne_principled_bleibt_schwarz_aber_ohne_fehler(self):
        from core.dienste.blendimporthautlokal import Blendimporthautlokal

        netz = {'materialien': [{'name': 'Kleid', 'graph_grund': 'kein Principled BSDF auf oberster Ebene'}]}
        lokal = Blendimporthautlokal(_Ablage(), netz, self._npz(), np.zeros((3, 3)), {'punkte': np.zeros((1, 3))}, 64)
        with mock.patch('core.dienste.blendimporthautlokal.Hautbackenquelle'), mock.patch('core.dienste.blendimporthautlokal.Hautschattungbau'):
            lokal.vorbereiten()
        self.assertEqual(lokal.treiber.graphen, {0: None})

    def test_10_hautgraphfehler_wird_zur_meldung_mit_dem_ausweg_blender(self):
        from core.dienste.blendimporthaut import Blendimporthaut
        from core.dienste.hautbacken.graph import Hautgraphfehler

        haut = Blendimporthaut(_Ablage(), SimpleNamespace(ergebnis=None, kennung='x'), {'netze': [{'name': 'body', 'datei': '00.npz'}]}, [], 64)
        with mock.patch('numpy.load'), mock.patch('core.dienste.blendimporthautlokal.Blendimporthautlokal') as klasse, \
                mock.patch('core.dienste.blendimporthaut.Blendimportlage.blender', side_effect=lambda p: p):
            klasse.return_value.vorbereiten.side_effect = Hautgraphfehler(['Knoten „Noise" (TEX_NOISE) ist nicht übernommen'])
            with self.assertRaises(RuntimeError) as ctx:
                haut._backen_lokal('body', np.zeros((3, 3)), {}, [1001], {})
        text = str(ctx.exception)
        self.assertIn('TEX_NOISE', text)
        self.assertIn('„Blender" wählen', text)

    def test_11_echte_verschiebung_lehnt_der_graph_ab(self):
        from core.dienste.hautbacken.graph import Hautgraph, Hautgraphfehler

        spec = {'ziel': {}, 'knoten': {}, 'bilder': {}, 'echte_verschiebung': True}
        with self.assertRaises(Hautgraphfehler) as ctx:
            Hautgraph('Haut', spec, texturen={})
        self.assertIn('echte Verschiebung', ctx.exception.gruende[0])


class EchteVerschiebungTest(SimpleTestCase):
    """`Blendmaterialgraph.echte_verschiebung` (läuft in Blender; hier mit Attrappen der Blender-Objekte)."""
    databases = set()

    @staticmethod
    def _material(verbunden, methode, stumm=False, gueltig=True):
        link = SimpleNamespace(is_valid=gueltig, is_muted=stumm)
        eingang = SimpleNamespace(links=[link] if verbunden else [])
        ausgang = SimpleNamespace(type='OUTPUT_MATERIAL', is_active_output=True, inputs={'Displacement': eingang})
        return SimpleNamespace(displacement_method=methode), SimpleNamespace(nodes=[ausgang])

    def test_12_nur_verbunden_und_nicht_bump(self):
        import sys

        sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parents[3] / 'effekte' / 'blender' / 'blendimport'))
        from blendmaterialgraph import Blendmaterialgraph

        f = Blendmaterialgraph.echte_verschiebung
        self.assertTrue(f(*self._material(True, 'DISPLACEMENT')))
        self.assertTrue(f(*self._material(True, 'BOTH')))
        self.assertFalse(f(*self._material(True, 'BUMP')))
        self.assertFalse(f(*self._material(False, 'DISPLACEMENT')))
        self.assertFalse(f(*self._material(True, 'DISPLACEMENT', stumm=True)))
        self.assertFalse(f(*self._material(True, 'DISPLACEMENT', gueltig=False)))
